"""External-ID helpers for portal lemmas.

These convert a :class:`~pyportaldalingua.models.Lemma` into a flat ``str ->
str`` dict of namespaced external IDs for cross-referencing across data sources.
Keys are namespaced with the ``portaldalingua_`` prefix.

A phonetic-dictionary entry is identified by its **lemma word** (the portal's
pt orthography headword); when the detail-page numeric id is known it is carried
alongside, but the word is the stable anchor.
"""
from __future__ import annotations

from typing import Optional

from pyportaldalingua.models import Lemma


def lemma_id(word: str) -> str:
    """The canonical lemma anchor: the pt-orthography headword itself."""
    return word.strip()


def id_from_url(url: str) -> Optional[str]:
    """Extract the detail-page numeric id from a Dicionário Fonético URL.

    Returns the ``id=<N>`` value, or ``None`` when the URL carries none.
    """
    if not url or "id=" not in url:
        return None
    tail = url.split("id=", 1)[1]
    num = tail.split("&", 1)[0].strip()
    return num or None


def lemma_to_extra(lemma: Lemma) -> dict:
    """Convert a :class:`Lemma` to a flat external-IDs dict.

    Keys written (those present on the lemma):

    - ``portaldalingua_word`` — the pt-orthography lemma anchor
    - ``portaldalingua_id`` — Dicionário Fonético detail id, when known
    - ``portaldalingua_url`` — detail-page URL, when known
    - ``portaldalingua_ipa`` — standard (Lisboa padrão) IPA
    - ``portaldalingua_syllables`` — dot-separated syllabification
    - ``portaldalingua_class`` — grammatical class
    """
    extra: dict = {"portaldalingua_word": lemma_id(lemma.word)}
    if lemma.detail_id:
        extra["portaldalingua_id"] = lemma.detail_id
    if lemma.url:
        extra["portaldalingua_url"] = lemma.url
    if lemma.ipa:
        extra["portaldalingua_ipa"] = lemma.ipa
    if lemma.syllabification:
        extra["portaldalingua_syllables"] = lemma.syllabification
    if lemma.grammatical_class:
        extra["portaldalingua_class"] = lemma.grammatical_class
    return extra
