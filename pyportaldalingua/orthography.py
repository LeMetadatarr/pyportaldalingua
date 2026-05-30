"""Acordo Ortográfico de 1990 (AO90) spelling changes + the bundled word-lists.

The portal lists the AO90 spelling changes per letter, per variant, at
``index.php?action=novoacordo&act=list&letter=<a-z>&version=<pe|pb>`` — a
``Ortografia Antiga | Ortografia Nova | Notas`` table. ``pe`` is European
Portuguese (``pt_PT``), ``pb`` is Brazilian (``pt_BR``).

- :func:`scrape_letter` parses one letter+variant into :class:`AOChange`\\ s;
- :func:`scrape_variant` walks ``a``–``z`` for one variant (polite delay);
- :func:`load_wordlists` / :func:`load_changes_csv` read the corpora shipped in
  the package ``data/`` directory (``acordo_ortografico_pt_{BR,PT}.csv`` and the
  ``wordlist-*.txt.xz`` lists) without any network access.
"""
from __future__ import annotations

import csv
import lzma
import re
import string
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from pyportaldalingua._clean import clean, clean_or_none
from pyportaldalingua.models import AOChange
from pyportaldalingua.transport import Transport, default_transport

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# variant name -> portal version code
_VERSION = {"pt_PT": "pe", "pt_BR": "pb"}
_VARIANT = {v: k for k, v in _VERSION.items()}

# a change row: <td title='forma antiga'>OLD<td>NEW<td> <notes>
_ROW = re.compile(
    r"<td\s+title=['\"]forma antiga['\"]\s*>(?P<old>.*?)"
    r"<td\s*>(?P<new>.*?)"
    r"<td\s*>(?P<note>.*?)(?=<tr|</table)",
    re.S | re.I)


def parse_changes(html: str, variant: str) -> List[AOChange]:
    """Parse an AO list page into :class:`AOChange`\\ s for *variant*."""
    out: List[AOChange] = []
    # the table starts after the header row
    if "Ortografia Antiga" in html:
        html = html.split("Ortografia Antiga", 1)[1]
        html = html.split("</table>", 1)[0]
    for m in _ROW.finditer(html):
        old = clean(m.group("old"))
        new = clean(m.group("new"))
        if not old or not new:
            continue
        out.append(AOChange(old=old, new=new, variant=variant,
                            note=clean_or_none(m.group("note"))))
    return out


def _t(transport: Optional[Transport]) -> Transport:
    return transport or default_transport()


def _version(variant: str) -> str:
    if variant in _VERSION:
        return _VERSION[variant]
    if variant in _VARIANT:
        return variant
    raise ValueError(f"variant must be one of {sorted(_VERSION)} (or 'pe'/'pb'), "
                     f"got {variant!r}")


def scrape_letter(letter: str, variant: str = "pt_PT", *,
                  transport: Optional[Transport] = None) -> List[AOChange]:
    """Scrape AO90 changes for one *letter* and *variant* (``pt_PT``/``pt_BR``).

    Example::

        import pyportaldalingua as pdl
        for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
            print(ch.old, "->", ch.new)
    """
    t = _t(transport)
    version = _version(variant)
    html = t.get_html(params={"action": "novoacordo", "act": "list",
                              "letter": letter.lower(), "version": version})
    return parse_changes(html, _VARIANT.get(version, variant))


def scrape_variant(variant: str = "pt_PT", *, letters: Optional[str] = None,
                   transport: Optional[Transport] = None) -> List[AOChange]:
    """Scrape every letter ``a``–``z`` for *variant*. Polite (one shared
    transport, delay between requests). Pass *letters* to limit the range."""
    t = _t(transport)
    out: List[AOChange] = []
    for letter in (letters or string.ascii_lowercase):
        out.extend(scrape_letter(letter, variant, transport=t))
    return out


# -- bundled corpora (offline) --------------------------------------------

_WORDLISTS = {
    "ao": "wordlist-ao-latest.txt.xz",       # post-AO90 orthography
    "preao": "wordlist-preao-latest.txt.xz",  # pre-AO90 orthography
    "big": "wordlist-big-latest.txt.xz",     # combined large list
}


def load_changes_csv(variant: str = "pt_PT", *,
                     data_dir: Optional[Path] = None) -> List[AOChange]:
    """Load the bundled AO change CSV for *variant* from the package ``data/``.

    These are the pre-built corpora the live scraper reproduces — no network.
    """
    d = Path(data_dir) if data_dir else DATA_DIR
    name = "acordo_ortografico_pt_BR.csv" if variant in ("pt_BR", "pb") \
        else "acordo_ortografico_pt_PT.csv"
    canon = "pt_BR" if variant in ("pt_BR", "pb") else "pt_PT"
    path = d / name
    out: List[AOChange] = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            old = (row.get("old_form") or "").strip()
            new = (row.get("new_form") or "").strip()
            if old and new:
                out.append(AOChange(old=old, new=new, variant=canon))
    return out


def load_wordlists(which: str = "ao", *,
                   data_dir: Optional[Path] = None) -> Iterator[str]:
    """Stream the bundled word-list *which* (``"ao"``/``"preao"``/``"big"``).

    Lists ship xz-compressed (latin-1 text); this decompresses and yields one
    word per line lazily, so a multi-megabyte list never sits fully in memory.
    """
    if which not in _WORDLISTS:
        raise ValueError(f"which must be one of {sorted(_WORDLISTS)}, got {which!r}")
    d = Path(data_dir) if data_dir else DATA_DIR
    path = d / _WORDLISTS[which]
    with lzma.open(path, "rt", encoding="latin-1") as fh:
        for line in fh:
            w = line.strip()
            if w:
                yield w


def wordlist_names() -> Dict[str, str]:
    """Map of available word-list keys to their bundled filenames."""
    return dict(_WORDLISTS)
