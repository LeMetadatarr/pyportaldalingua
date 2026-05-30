"""Lexicon entry lookup — ``index.php?action=lemma&lemma=<id>``.

The portal's **Vocabulário Ortográfico do Português** (VOP) stores the canonical
lexicon. Each lemma has a numeric id that appears in links across the site
(fonetica detail pages, VOP search results, loanwords, toponyms).  Given that
id, ``action=lemma`` returns a page with:

- the headword and its grammatical class (e.g. ``nome feminino``, ``verbo``);
- the syllabification with middot markers;
- an inflection table for nouns/adjectives (gender × number) or a full
  conjugation table for verbs (Indicativo, Conjuntivo, Imperativo, …);
- links to morphologically related lemmas (diminutives, augmentatives, past
  participles, infinitives, nominal forms).

The VOP vocabulary search — a separate PHP file,
``simplesearch.php?sel=<mode>&query=<word>`` — accepts four match modes:
``exact``, ``contain``, ``start``, ``end``.  This is used to implement
**fuzzy / partial headword resolution**: :func:`vop_search` returns ranked
:class:`VopResult` candidates.

``action=lemma`` pages are keyed by the *lemma id*, not a headword string.
Headword→id resolution goes through :func:`vop_search` (for VOP entries) or
the fonetica list endpoint (for phonetics — see :mod:`pyportaldalingua.phonetics`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from pyportaldalingua._clean import clean, clean_or_none, syllabify
from pyportaldalingua.transport import Transport, default_transport

# --------------------------------------------------------------------------- #
# models                                                                        #
# --------------------------------------------------------------------------- #

@dataclass
class VopResult:
    """One hit from the VOP ``simplesearch.php`` vocabulary search.

    ``lemma_id`` is the site-internal numeric key usable with
    :func:`lemma_entry`; ``inflected_from`` is non-empty when the hit is an
    inflected form indexed under a different headword (the search may return it
    alongside the canonical lemma row).
    """
    word: str
    grammatical_class: Optional[str] = None
    lemma_id: Optional[str] = None
    inflected_from: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"word": self.word}
        if self.grammatical_class:
            d["grammatical_class"] = self.grammatical_class
        if self.lemma_id:
            d["lemma_id"] = self.lemma_id
        if self.inflected_from:
            d["inflected_from"] = self.inflected_from
        return d


@dataclass
class LemmaEntry:
    """Lexicon entry from ``action=lemma``.

    ``inflection`` maps table row headers to their cell values, e.g.::

        {"singular": "casa", "plural": "casas"}

    For verbs the keys are mood+tense labels
    (``"Indicativo Presente"``, ``"Conjuntivo Presente"``, …) and values are
    newline-joined conjugated forms.

    ``related`` maps relation labels (``"diminutivo"``, ``"aumentativo"``,
    ``"adjetivo PP de"``, …) to lists of ``(headword, lemma_id)`` tuples.
    """
    lemma_id: str
    word: str
    grammatical_class: Optional[str] = None
    syllabification: Optional[str] = None
    inflection: Dict[str, str] = field(default_factory=dict)
    related: Dict[str, List[tuple]] = field(default_factory=dict)  # label -> [(word, id)]
    paradigm: Optional[str] = None  # e.g. "lindo", "amar"

    @property
    def syllables(self) -> List[str]:
        return self.syllabification.split(".") if self.syllabification else []

    def to_dict(self) -> dict:
        d: dict = {"lemma_id": self.lemma_id, "word": self.word}
        if self.grammatical_class:
            d["grammatical_class"] = self.grammatical_class
        if self.syllabification:
            d["syllabification"] = self.syllabification
        if self.inflection:
            d["inflection"] = self.inflection
        if self.related:
            d["related"] = {k: [{"word": w, "lemma_id": i} for w, i in v]
                            for k, v in self.related.items()}
        if self.paradigm:
            d["paradigm"] = self.paradigm
        return d


# --------------------------------------------------------------------------- #
# parsing — VOP search                                                          #
# --------------------------------------------------------------------------- #

_VOP_ROW = re.compile(
    r'<td\s+label=["\']([^"\']+)["\'][^>]*>.*?'  # label attr = lemma key
    r'<span[^>]*>(?P<gclass>[^<]+)</span>'        # grammatical class
    r'.*?<a\s+href=["\']?[^>]*action=lemma&(?:amp;)?lemma=(?P<id>\d+)[^>]*>'
    r'(?:<b>)?(?P<word>[^<]+)',
    re.S | re.I,
)

_VOP_INFLECTED = re.compile(
    r'</td>\s*<td>(?P<inf>[^<\s][^<]*?)\s*</td>',
    re.S | re.I,
)


def parse_vop_search(html: str) -> List[VopResult]:
    """Parse a ``simplesearch.php`` result page into :class:`VopResult`\\s."""
    out: List[VopResult] = []
    for m in _VOP_ROW.finditer(html):
        word = clean(m.group("word"))
        if not word:
            continue
        gclass = clean_or_none(m.group("gclass"))
        lid = m.group("id")
        # The cell after the gclass td may contain an inflected-form note
        rest = html[m.start():m.start() + 600]
        inf_m = _VOP_INFLECTED.search(rest)
        inflected_from = clean_or_none(inf_m.group("inf")) if inf_m else None
        out.append(VopResult(word=word, grammatical_class=gclass,
                             lemma_id=lid, inflected_from=inflected_from))
    return out


# --------------------------------------------------------------------------- #
# parsing — lemma entry page                                                    #
# --------------------------------------------------------------------------- #

_LEMMA_HEAD = re.compile(
    r'<h1>(?P<word>[^<]+?)\s*-\s*(?P<gclass>[^<]+?)\s*</h1>',
    re.S | re.I,
)
_LEMMA_ID_SELF = re.compile(
    r'action=lemma&(?:amp;)?lemma=(?P<id>\d+)&(?:amp;)?template=print',
    re.I,
)
_SYLLABLE_P = re.compile(
    r"title=['\"]Divis[^'\"]+['\"][^>]*>(.*?)</a>",
    re.S | re.I,
)
_PARADIGM = re.compile(
    r'Flexiona como\s*:\s*<a[^>]+>(?P<para>[^<]+)</a>',
    re.I,
)
# noun/adj inflection table: <tr><th>label<td>value
_NOUN_ROW = re.compile(
    r'<tr[^>]*>\s*<th[^>]*>(?P<header>[^<]+?)\s*(?:<td[^>]*>(?P<val>[^<]+))+',
    re.S | re.I,
)
# verb conjugation: structured table with <th colspan=6>Indicativo etc.
_VERB_MOOD = re.compile(
    r'<th[^>]+colspan[^>]+>(?P<mood>[A-ZÁÉÍÓÚÂÊÔÃÕÇ][^<]+?)\s*</th>',
    re.S | re.I,
)
_VERB_TENSE_ROW = re.compile(
    r'<td\s+class=subh[^>]*>(?P<tense>[^<]+?)\s*</td>',
    re.S | re.I,
)
_VERB_FORMS_TD = re.compile(
    r'<td>(?P<forms>[a-záéíóúâêôãõçàüñ][^<]*(?:<br[^>]*>[^<]*)*)</td>',
    re.S | re.I,
)
_RELATED = re.compile(
    r'(?P<label>[a-záéíóúâêôãõç][a-záéíóúâêôãõç\s]+?)\s*:\s*'
    r'(?:<a[^>]+action=lemma&(?:amp;)?lemma=(?P<id>\d+)[^>]*>(?P<word>[^<]+)</a>[,\s]*)+',
    re.I,
)
_RELATED_LINKS = re.compile(
    r'action=lemma&(?:amp;)?lemma=(?P<id>\d+)[^>]*>(?P<word>[^<]+)</a>',
    re.I,
)


def parse_lemma_entry(html: str, lemma_id: str = "") -> Optional[LemmaEntry]:
    """Parse an ``action=lemma`` detail page into a :class:`LemmaEntry`."""
    head_m = _LEMMA_HEAD.search(html)
    if head_m is None:
        return None
    word = clean(head_m.group("word"))
    gclass = clean_or_none(head_m.group("gclass"))

    # self id
    id_m = _LEMMA_ID_SELF.search(html)
    lid = id_m.group("id") if id_m else lemma_id

    # syllabification
    syl_m = _SYLLABLE_P.search(html)
    syl = syllabify(syl_m.group(1)) if syl_m else None

    # main content region
    content_m = re.search(r'id=maintext[^>]*>(.*?)</td>', html, re.S | re.I)
    content = content_m.group(1) if content_m else html

    # paradigm
    para_m = _PARADIGM.search(content)
    paradigm = clean_or_none(para_m.group("para")) if para_m else None

    # inflection table (nouns/adjectives: classtable without broad tenses)
    inflection: Dict[str, str] = {}
    classtable_m = re.search(r'id=classtable[^>]*>(.*?)</table>', content, re.S | re.I)
    if classtable_m:
        table_html = classtable_m.group(1)
        # check if it's a verb table (has colspan mood headers)
        if _VERB_MOOD.search(table_html):
            inflection = _parse_verb_table(table_html)
        else:
            for row_m in _NOUN_ROW.finditer(table_html):
                header = clean(row_m.group("header"))
                # extract all <td> values in the row
                vals = re.findall(r'<td[^>]*>([^<]+)', row_m.group(0), re.I)
                if header and vals:
                    inflection[header] = " / ".join(clean(v) for v in vals if clean(v))

    # related links (diminutives, augmentatives, etc.)
    related: Dict[str, List[tuple]] = {}
    # search in the paragraph text below the table
    after_table = content.split("</table>", 1)[-1] if "</table>" in content else content
    for p_m in re.finditer(r'<p>([^<]{3,}(?:<a[^>]+>[^<]+</a>[^<]*)+)', after_table, re.I):
        chunk = p_m.group(0)
        label_m = re.match(r'<p>\s*([a-záéíóúâêôãõçA-Z][^:<]{2,40}?)\s*(?:PP de|:)',
                           chunk, re.I)
        if label_m:
            label = clean(label_m.group(1))
            links = [(clean(lm.group("word")), lm.group("id"))
                     for lm in _RELATED_LINKS.finditer(chunk)]
            if links:
                related.setdefault(label, []).extend(links)

    return LemmaEntry(
        lemma_id=lid,
        word=word,
        grammatical_class=gclass,
        syllabification=syl,
        inflection=inflection,
        related=related,
        paradigm=paradigm,
    )


def _parse_verb_table(table_html: str) -> Dict[str, str]:
    """Extract conjugation forms from a verb classtable."""
    result: Dict[str, str] = {}
    # Split by mood headers
    moods = list(_VERB_MOOD.finditer(table_html))
    if not moods:
        return result
    for i, mood_m in enumerate(moods):
        mood = clean(mood_m.group("mood"))
        end = moods[i + 1].start() if i + 1 < len(moods) else len(table_html)
        section = table_html[mood_m.end():end]
        # tense headers
        tenses = [clean(t.group("tense")) for t in _VERB_TENSE_ROW.finditer(section)]
        # form cells
        form_cells = [m.group("forms") for m in _VERB_FORMS_TD.finditer(section)]
        for j, forms_html in enumerate(form_cells):
            tense = tenses[j] if j < len(tenses) else f"tense{j}"
            forms = re.sub(r'<br\s*/?>', "\n", forms_html, flags=re.I)
            forms = clean(re.sub(r'<[^>]+>', '', forms))
            if forms:
                key = f"{mood} {tense}".strip()
                result[key] = forms
    return result


# --------------------------------------------------------------------------- #
# fetch helpers                                                                  #
# --------------------------------------------------------------------------- #

def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


VOP_SEARCH_URL = "http://www.portaldalinguaportuguesa.org/simplesearch.php"


def vop_search(
    query: str,
    *,
    mode: str = "contain",
    limit: int = 20,
    transport: Optional[Transport] = None,
) -> List[VopResult]:
    """Search the VOP vocabulary and return ranked :class:`VopResult`\\s.

    *mode* selects the match strategy:

    - ``"exact"``   — headword equals *query* (case-insensitive);
    - ``"contain"`` — headword contains *query* anywhere (fuzzy substring);
    - ``"start"``   — headword starts with *query* (prefix);
    - ``"end"``     — headword ends with *query* (suffix).

    Results are returned in page order, capped at *limit*.

    Example::

        import pyportaldalingua as pdl
        pdl.vop_search("casament")          # fuzzy: casamento, casamentar, …
        pdl.vop_search("casa", mode="start")  # prefix: casa, casabeque, …
    """
    if mode not in ("exact", "contain", "start", "end"):
        raise ValueError(f"mode must be 'exact', 'contain', 'start', or 'end'; got {mode!r}")
    t = _t(transport)
    html = t.get_html(
        VOP_SEARCH_URL,
        params={"sel": mode, "action": "simplesearch", "base": "form", "query": query},
    )
    return parse_vop_search(html)[:limit]


def lemma_entry(
    lemma_id: str,
    *,
    transport: Optional[Transport] = None,
) -> Optional[LemmaEntry]:
    """Fetch the VOP lexicon entry for *lemma_id* and return a :class:`LemmaEntry`.

    The numeric id is obtained from :func:`vop_search` results, from
    :attr:`pyportaldalingua.phonetics.Lemma.detail_id` (which equals the fonetica id
    and often equals the VOP lemma id), or from any portal link of the form
    ``action=lemma&lemma=<id>``.

    Example::

        import pyportaldalingua as pdl
        results = pdl.vop_search("casa", mode="exact")
        if results:
            entry = pdl.lemma_entry(results[0].lemma_id)
            print(entry.inflection)
    """
    t = _t(transport)
    html = t.get_html(params={"action": "lemma", "lemma": lemma_id})
    return parse_lemma_entry(html, lemma_id=lemma_id)
