"""Internal HTML / text cleaning helpers for portal pages.

The Portal da Língua Portuguesa is an old PHP site whose pages mix unclosed
tags, ``&entity;`` references and inline markup. These pure-string helpers strip
that down to plain text while preserving the linguistic content: the lemma word,
its syllable dots, the stressed-syllable marker, and the IPA transcription
strings exactly as served (with their stress ``ˈ`` and length ``ː`` marks).
"""
from __future__ import annotations

import html as _html
import re
import unicodedata
from typing import Optional

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"[ \t\r\n]+")


def strip_tags(fragment: str) -> str:
    """Remove HTML tags from *fragment* and unescape entities."""
    if not fragment:
        return ""
    return _html.unescape(_TAG.sub("", fragment))


def normalize(text: str) -> str:
    """Unicode-normalise (NFC) and collapse whitespace runs to single spaces."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    return _WS.sub(" ", text).strip()


def clean(fragment: str) -> str:
    """Strip tags + entities, then normalise. The common one-shot cleaner."""
    return normalize(strip_tags(fragment))


def clean_or_none(fragment: str) -> Optional[str]:
    """Like :func:`clean` but returns ``None`` for an empty result."""
    return clean(fragment) or None


def syllabify(lemma_cell_html: str) -> Optional[str]:
    """Turn a portal *Palavra* cell into a dot-separated syllabification.

    The cell renders syllable breaks as ``<b>&middot;</b>`` and the stressed
    syllable wrapped in ``<u><b>…</b></u>``. We map every ``·`` (middot) to a
    ``.`` and drop the rest of the markup — yielding e.g. ``"a.ca.sa.la.do"`` for
    ``a·ca·sa·<u>la</u>·do``. Returns ``None`` when no syllable break is present.
    """
    if not lemma_cell_html:
        return None
    # the anchor text holds the word; middots separate syllables
    text = _html.unescape(lemma_cell_html)
    if "·" not in text and "&middot;" not in text:
        # already unescaped above; if still no middot, no syllabification
        if "·" not in text:
            return None
    # strip tags but keep the middot characters, then map to dots
    bare = _TAG.sub("", text)
    syl = bare.replace("·", ".")
    syl = normalize(syl)
    return syl or None
