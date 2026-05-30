"""Dicionário de Gentílicos e Topónimos — ``index.php?action=toponyms&act=list``.

The portal's **Dicionário de Gentílicos e Topónimos** maps place-names to their
corresponding demonyms (*gentílicos*) in Portuguese, with the place type (city,
district, country, …) and the administrative parent it belongs to.

A search uses::

    GET index.php?action=toponyms&act=list&search=<toponym>

which returns an HTML table with columns:

    Topónimo | Tipo | Gentílico | Parte de

Each ``Gentílico`` cell is an anchor to ``action=lemma&lemma=<id>``, so the
lemma id is available for further lookup.

The portal allows searching by toponym string; partial matches are returned.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from pyportaldalingua._clean import clean, clean_or_none
from pyportaldalingua.transport import Transport, default_transport


@dataclass
class GentilicoEntry:
    """One demonym row from the Dicionário de Gentílicos e Topónimos.

    A single toponym may appear on multiple rows when it has more than one
    demonym form (e.g. ``adjetivo`` and ``nome`` variants).

    ``toponym``      — the place name (may be empty on continuation rows);
    ``place_type``   — e.g. ``"cidade"``, ``"país"``, ``"distrito"`` (may be empty);
    ``demonym``      — the Portuguese demonym word;
    ``grammatical_class`` — e.g. ``"adjetivo"``, ``"nome"`` (from the link text);
    ``part_of``      — the administrative parent (e.g. ``"Portugal"``, ``"Brasil"``);
    ``lemma_id``     — site-internal id for :func:`pyportaldalingua.lexicon.lemma_entry`.
    """

    toponym: str
    place_type: Optional[str] = None
    demonym: Optional[str] = None
    grammatical_class: Optional[str] = None
    part_of: Optional[str] = None
    lemma_id: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"toponym": self.toponym}
        for key in ("place_type", "demonym", "grammatical_class",
                    "part_of", "lemma_id"):
            val = getattr(self, key)
            if val:
                d[key] = val
        return d


@dataclass
class ToponymResult:
    """All demonyms for a single toponym from a search result.

    ``toponym``  — the place name;
    ``place_type`` — city / país / etc.;
    ``part_of``  — administrative parent;
    ``demonyms`` — list of :class:`GentilicoEntry` (one per grammatical form).
    """

    toponym: str
    place_type: Optional[str] = None
    part_of: Optional[str] = None
    demonyms: List[GentilicoEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "toponym": self.toponym,
            "place_type": self.place_type,
            "part_of": self.part_of,
            "demonyms": [d.to_dict() for d in self.demonyms],
        }


# --------------------------------------------------------------------------- #
# parsing                                                                       #
# --------------------------------------------------------------------------- #

_TR = re.compile(r'<tr[^>]*>(.*?)(?=<tr|</table>|$)', re.S | re.I)
# match a single <td …> cell — content is everything up to next <td or <tr
_TD = re.compile(r'<td[^>]*>(.*?)(?=<td|<tr|</tr>|</table>|$)', re.S | re.I)

_GENT_LINK = re.compile(
    r'<a[^>]+action=lemma&(?:amp;)?lemma=(?P<id>\d+)[^>]*>(?P<word>[^<]+)</a>'
    r'\s*-\s*(?P<gclass>[a-z ]+)',
    re.I,
)

_PARENT_TEXT = re.compile(r'<i>([^<]+)</i>', re.I)


def parse_toponyms(html: str) -> List[GentilicoEntry]:
    """Parse a toponyms search page into a flat list of :class:`GentilicoEntry`\\s."""
    out: List[GentilicoEntry] = []
    current_toponym = ""
    current_ptype: Optional[str] = None
    current_parent: Optional[str] = None

    # Narrow to the results table
    table_m = re.search(r'rollovertable[^>]*>(.*?)(?:</table>|$)', html, re.S | re.I)
    body = table_m.group(1) if table_m else html

    for tr_m in _TR.finditer(body):
        row_html = tr_m.group(1)
        # skip header rows (contain <th>)
        if re.search(r'<th', row_html, re.I):
            continue
        cells = [m.group(1) for m in _TD.finditer(row_html)]
        if len(cells) < 3:
            continue

        top_raw = clean(cells[0])
        ptype_raw = clean_or_none(cells[1])
        gent_cell = cells[2]
        parent_cell = cells[3] if len(cells) > 3 else ""

        if top_raw:
            current_toponym = top_raw
        if ptype_raw:
            current_ptype = ptype_raw

        parent_texts = _PARENT_TEXT.findall(parent_cell)
        if parent_texts:
            current_parent = clean(parent_texts[-1]) or current_parent

        for gm in _GENT_LINK.finditer(gent_cell):
            demonym = clean(gm.group("word"))
            gclass = clean_or_none(gm.group("gclass"))
            lid = gm.group("id")
            out.append(GentilicoEntry(
                toponym=current_toponym,
                place_type=current_ptype,
                demonym=demonym,
                grammatical_class=gclass,
                part_of=current_parent,
                lemma_id=lid,
            ))

    return out


def group_by_toponym(entries: List[GentilicoEntry]) -> List[ToponymResult]:
    """Group flat :class:`GentilicoEntry` rows into :class:`ToponymResult`\\s."""
    seen: dict = {}
    order: List[str] = []
    for e in entries:
        if e.toponym not in seen:
            seen[e.toponym] = ToponymResult(
                toponym=e.toponym,
                place_type=e.place_type,
                part_of=e.part_of,
            )
            order.append(e.toponym)
        seen[e.toponym].demonyms.append(e)
    return [seen[k] for k in order]


# --------------------------------------------------------------------------- #
# fetch                                                                         #
# --------------------------------------------------------------------------- #

def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def toponym_search(
    toponym: str,
    *,
    grouped: bool = True,
    limit: int = 20,
    transport: Optional[Transport] = None,
):
    """Search the Dicionário de Gentílicos e Topónimos for *toponym*.

    When *grouped* is ``True`` (default) returns a list of
    :class:`ToponymResult`, each collecting all demonyms for one place name.
    When *grouped* is ``False`` returns the flat list of :class:`GentilicoEntry`.

    Results are capped at *limit* (counted in :class:`ToponymResult` groups, or
    in flat rows when *grouped* is ``False``).

    Example::

        import pyportaldalingua as pdl
        for result in pdl.toponym_search("lisboa"):
            print(result.toponym, result.place_type)
            for d in result.demonyms:
                print(" ", d.demonym, d.grammatical_class)
    """
    t = _t(transport)
    html = t.get_html(params={"action": "toponyms", "act": "list", "search": toponym})
    entries = parse_toponyms(html)
    if grouped:
        return group_by_toponym(entries)[:limit]
    return entries[:limit]
