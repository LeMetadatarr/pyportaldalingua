"""Phonetic (IPA / AFI) lookup against the portal's Dicionário Fonético.

The **Dicionário Fonético** (``index.php?action=fonetica``) is the portal's
phonetic dictionary — the Portuguese IPA transcription source. The reachable
flow, reverse-engineered from the live site, is two hops:

1. **search list** — ``action=fonetica&act=list&region=lbx&search=<word>``
   returns a ``Palavra | Classe Gramatical | Fonética`` table. Each row already
   carries the lemma (with ``·`` syllable breaks and the stressed syllable
   underlined), its grammatical class, and the standard (Lisboa padrão) IPA, plus
   a link ``act=details&id=<N>`` to the lemma's detail page.
2. **detail page** — ``action=fonetica&act=details&id=<N>`` renders the same
   lemma with its IPA in *every* transcribed regional accent (Luanda, Lisboa,
   Maputo, Rio de Janeiro, São Paulo, Díli — padrão and não-padrão).

:func:`phonetics` does hop 1 and returns the standard IPA string for an exact
match. :func:`lemmas` returns every matching :class:`Lemma` from the list.
:func:`phonetics_detail` follows to hop 2 and fills :attr:`Lemma.ipa_by_region`.

Transcriptions are returned verbatim, including stress (``ˈ``), length (``ː``)
and syllable-dot (``.``) marks.
"""
from __future__ import annotations

import re
from typing import List, Optional

from pyportaldalingua._clean import clean, clean_or_none, syllabify
from pyportaldalingua.models import Lemma
from pyportaldalingua.transport import Transport, default_transport

# a search-list row: <td title='Palavra'>…</td> <td>class</td>
#                    <td title='Fonética'><a href='…id=N'>IPA</a></td>
_ROW = re.compile(
    r"<td\s+title=['\"]Palavra['\"]\s*>(?P<word>.*?)"
    r"<td\s*>(?P<gclass>.*?)"
    r"<td\s+title=['\"]Fon[^'\"]*['\"]\s*>(?P<fon>.*?)(?=<tr|</table)",
    re.S | re.I)
_DETAIL_ID = re.compile(r"act=details&(?:amp;|&)?id=(\d+)", re.I)

# detail page: <h2>Palavra: <a …>word</a> (gclass)</h2> then a region/IPA table
_DETAIL_HEAD = re.compile(
    r"Palavra:\s*(?P<word>.*?)\s*\((?P<gclass>[^)]*)\)\s*</h2>", re.S | re.I)
_DETAIL_ROW = re.compile(
    r"<td[^>]*>(?P<region>[^<]+?)\s*<td[^>]*>(?P<ipa>[^<\s][^<]*?)\s*(?=<tr|</table)",
    re.S | re.I)


def _row_to_lemma(word_cell: str, gclass_cell: str, fon_cell: str) -> Optional[Lemma]:
    # the word cell renders syllable breaks as middots; the plain word drops them
    word = clean(word_cell).replace("·", "").replace(" ", "")
    if not word:
        return None
    # the portal serves a malformed anchor: href='>?action=…id=N'>IPA</a>.
    # the IPA is the text between the link's real close '>' and '</a>'.
    fon_text = fon_cell.split("</a>", 1)[0]
    fon_text = fon_text.rsplit(">", 1)[-1] if ">" in fon_text else fon_text
    ipa = clean_or_none(fon_text)
    m = _DETAIL_ID.search(fon_cell)
    return Lemma(
        word=word,
        ipa=ipa,
        syllabification=syllabify(word_cell),
        grammatical_class=clean_or_none(gclass_cell),
        detail_id=m.group(1) if m else None,
    )


def parse_search(html: str) -> List[Lemma]:
    """Parse a Dicionário Fonético *search list* page into :class:`Lemma`\\ s."""
    out: List[Lemma] = []
    for m in _ROW.finditer(html):
        lemma = _row_to_lemma(m.group("word"), m.group("gclass"), m.group("fon"))
        if lemma is not None:
            out.append(lemma)
    return out


def parse_detail(html: str) -> Optional[Lemma]:
    """Parse a Dicionário Fonético *detail* page into one :class:`Lemma` with
    its per-region IPA filled in (:attr:`Lemma.ipa_by_region`)."""
    head = _DETAIL_HEAD.search(html)
    if head is None:
        return None
    word = clean(head.group("word"))
    if not word:
        return None
    # the region/IPA table sits right after the headword. Keep the closing
    # </table> tag in the slice — _DETAIL_ROW's lookahead matches on it to
    # find the boundary of the *last* region row (e.g. "Díli"); stripping it
    # silently dropped that row.
    body = html[head.end():]
    body = body.split("</table>", 1)[0] + "</table>"
    by_region = {}
    for m in _DETAIL_ROW.finditer(body):
        region = clean(m.group("region"))
        ipa = clean(m.group("ipa"))
        if region and ipa:
            by_region[region] = ipa
    std = by_region.get("Lisboa (padrão)") or (next(iter(by_region.values()), None))
    mid = _DETAIL_ID.search(html)
    return Lemma(
        word=word,
        ipa=std,
        grammatical_class=clean_or_none(head.group("gclass")),
        ipa_by_region=by_region,
        detail_id=mid.group(1) if mid else None,
    )


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def lemmas(word: str, *, limit: int = 20,
           transport: Optional[Transport] = None) -> List[Lemma]:
    """Search the Dicionário Fonético and return matching :class:`Lemma`\\ s.

    The portal's exact-search returns the headword and any inflected/related
    forms it indexes. Results are returned in page order, capped at *limit*.

    Example::

        import pyportaldalingua as pdl
        for lm in pdl.lemmas("casa"):
            print(lm.word, lm.ipa, lm.grammatical_class)
    """
    t = _t(transport)
    html = t.get_html(params={"action": "fonetica", "act": "list",
                              "region": "lbx", "search": word})
    return parse_search(html)[:limit]


def phonetics(word: str, *,
              transport: Optional[Transport] = None) -> Optional[str]:
    """Return the standard (Lisboa padrão) IPA for *word*, or ``None``.

    Exact, case-insensitive match against the lemma headword. For all regional
    accents use :func:`phonetics_detail`.

    Example::

        import pyportaldalingua as pdl
        pdl.phonetics("acasalado")     # 'ɐ.kɐ.zɐ.lˈa.du'
    """
    low = word.strip().lower()
    for lm in lemmas(word, transport=transport):
        if lm.word.lower() == low and lm.ipa:
            return lm.ipa
    return None


def phonetics_detail(word: str, *,
                     transport: Optional[Transport] = None) -> Optional[Lemma]:
    """Return the full :class:`Lemma` for *word*, with IPA in every region.

    Searches for an exact match, follows its detail link, and parses the
    per-region transcription table into :attr:`Lemma.ipa_by_region`. Returns
    ``None`` when no exact match with a detail page is found.

    Example::

        import pyportaldalingua as pdl
        lm = pdl.phonetics_detail("acasalado")
        print(lm.ipa_by_region["Rio de Janeiro (padrão)"])
    """
    t = _t(transport)
    low = word.strip().lower()
    match = None
    for lm in lemmas(word, transport=t):
        if lm.word.lower() == low and lm.detail_id:
            match = lm
            break
    if match is None:
        return None
    html = t.get_html(params={"action": "fonetica", "region": "lbx",
                              "act": "details", "id": match.detail_id})
    detail = parse_detail(html)
    if detail is not None:
        detail.detail_id = detail.detail_id or match.detail_id
        detail.syllabification = detail.syllabification or match.syllabification
    return detail
