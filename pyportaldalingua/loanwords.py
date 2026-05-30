"""Dicionário de Estrangeirismos — ``index.php?action=loanwords&act=list``.

The portal's **Dicionário de Estrangeirismos** records foreign-origin words used
in Portuguese, with their source language, subject domain, recommended Portuguese
adaptation, and a near-synonym equivalent if one exists.

A search against this dictionary uses::

    GET index.php?action=loanwords&act=list&search=<word>

which returns an HTML table with columns:

    Palavra | Categoria gramatical | Língua de origem | Domínio | Adaptação | Equivalente

Each ``Palavra`` cell is an anchor to ``action=lemma&lemma=<id>``, so the
lemma id for further lookup is always available.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from pyportaldalingua._clean import clean, clean_or_none
from pyportaldalingua.transport import Transport, default_transport


@dataclass
class LoanwordEntry:
    """One row from the Dicionário de Estrangeirismos.

    ``word``         — the foreign-origin Portuguese word;
    ``grammatical_class`` — e.g. ``"nome"``, ``"adjetivo"``;
    ``source_language``  — e.g. ``"inglês"``, ``"italiano"``;
    ``domain``       — subject domain (may be empty);
    ``adaptation``   — recommended Portuguese spelling adaptation (may be empty);
    ``equivalent``   — Portuguese synonym (may be empty);
    ``lemma_id``     — site-internal id for :func:`pyportaldalingua.lexicon.lemma_entry`.
    """

    word: str
    grammatical_class: Optional[str] = None
    source_language: Optional[str] = None
    domain: Optional[str] = None
    adaptation: Optional[str] = None
    equivalent: Optional[str] = None
    lemma_id: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"word": self.word}
        for key in ("grammatical_class", "source_language", "domain",
                    "adaptation", "equivalent", "lemma_id"):
            val = getattr(self, key)
            if val:
                d[key] = val
        return d


# --------------------------------------------------------------------------- #
# parsing                                                                       #
# --------------------------------------------------------------------------- #

_ROW = re.compile(
    r'<tr>\s*<td>\s*<a\s+href=["\']?[^>]+action=lemma&(?:amp;)?lemma=(?P<id>\d+)[^>]*>'
    r'(?:<b>)?(?P<word>[^<]+)(?:</b>)?</a>.*?</td>'  # Palavra
    r'\s*<td[^>]*>(?P<gclass>[^<]*)</td>'              # gclass
    r'\s*<td[^>]*>(?P<lang>[^<]*(?:<a[^>]+>[^<]+</a>[^<]*)?)</td>'  # língua
    r'\s*<td[^>]*>(?P<domain>[^<]*)</td>'              # domínio
    r'\s*<td[^>]*>(?P<adapt>[^<]*)</td>'               # adaptação
    r'\s*<td[^>]*>(?P<equiv>[^<]*)</td>',
    re.S | re.I,
)


def parse_loanwords(html: str) -> List[LoanwordEntry]:
    """Parse a loanwords search result page into :class:`LoanwordEntry`\\s."""
    out: List[LoanwordEntry] = []
    for m in _ROW.finditer(html):
        word = clean(m.group("word"))
        if not word:
            continue
        # language cell may contain an anchor
        lang_raw = re.sub(r'<[^>]+>', '', m.group("lang"))
        out.append(LoanwordEntry(
            word=word,
            grammatical_class=clean_or_none(m.group("gclass")),
            source_language=clean_or_none(lang_raw),
            domain=clean_or_none(m.group("domain")),
            adaptation=clean_or_none(m.group("adapt")),
            equivalent=clean_or_none(m.group("equiv")),
            lemma_id=m.group("id"),
        ))
    return out


# --------------------------------------------------------------------------- #
# fetch                                                                         #
# --------------------------------------------------------------------------- #

def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def loanword_search(
    word: str,
    *,
    limit: int = 50,
    transport: Optional[Transport] = None,
) -> List[LoanwordEntry]:
    """Search the Dicionário de Estrangeirismos for *word*.

    The portal matches by substring against the headword.  Results are returned
    in page order, capped at *limit*.

    Example::

        import pyportaldalingua as pdl
        for entry in pdl.loanword_search("jazz"):
            print(entry.word, entry.source_language, entry.adaptation)
    """
    t = _t(transport)
    html = t.get_html(params={"action": "loanwords", "act": "list", "search": word})
    return parse_loanwords(html)[:limit]
