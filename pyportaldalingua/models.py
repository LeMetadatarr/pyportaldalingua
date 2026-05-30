"""Typed dataclass models for pyportaldalingua.

The portal exposes two distinct linguistic resources, each with its own record:

- :class:`Lemma` — one headword from the **Dicionário Fonético**: its
  IPA / AFI transcription, syllabification, grammatical class, and the IPA in
  each regional accent the portal transcribes (Lisboa, Luanda, Rio de Janeiro,
  São Paulo, Maputo, Díli, …);
- :class:`AOChange` — one spelling change from the **Acordo Ortográfico de
  1990**: the pre-AO (``old``) and post-AO (``new``) forms, the variant the
  change applies to (``pt_PT`` / ``pt_BR``), and any note.

The portal serves a single padrão (standard) IPA inline in its search list and
the full per-region table on a lemma's detail page; :class:`Lemma` carries both.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

INDEX = "http://www.portaldalinguaportuguesa.org/index.php"

# region codes / labels the Dicionário Fonético transcribes
REGIONS = (
    "Luanda", "Lisboa (não padrão)", "Lisboa (padrão)",
    "Maputo (não padrão)", "Maputo (padrão)",
    "Rio de Janeiro (não padrão)", "Rio de Janeiro (padrão)",
    "São Paulo (não padrão)", "São Paulo (padrão)", "Díli",
)


@dataclass
class Lemma:
    """A headword from the portal's phonetic dictionary.

    ``ipa`` is the standard (Lisboa padrão) transcription — the convenience
    accessor most callers want. ``ipa_by_region`` maps every transcribed accent
    label to its transcription (populated only by a detail-page fetch).
    ``syllabification`` is dot-separated (``"a.ca.sa.la.do"``);
    ``grammatical_class`` is the portal's label (``"adjetivo"``, ``"verbo"``, …).
    """

    word: str
    ipa: Optional[str] = None
    syllabification: Optional[str] = None
    grammatical_class: Optional[str] = None
    ipa_by_region: Dict[str, str] = field(default_factory=dict)
    detail_id: Optional[str] = None
    region: str = "Lisboa (padrão)"

    @property
    def url(self) -> Optional[str]:
        """The lemma's Dicionário Fonético detail page, when its id is known."""
        if self.detail_id is None:
            return None
        q = urlencode({"action": "fonetica", "region": "lbx",
                       "act": "details", "id": self.detail_id})
        return f"{INDEX}?{q}"

    @property
    def syllables(self) -> List[str]:
        """The syllabification split into a list, or ``[]`` when unknown."""
        return self.syllabification.split(".") if self.syllabification else []

    def to_dict(self) -> Dict[str, Any]:
        d = {k: v for k, v in dataclasses.asdict(self).items() if v not in (None, {})}
        if self.url:
            d["url"] = self.url
        return d


@dataclass
class AOChange:
    """A single Acordo Ortográfico de 1990 spelling change.

    ``variant`` is ``"pt_PT"`` or ``"pt_BR"`` (the portal's ``pe`` / ``pb``
    version codes). ``note`` is the optional *Notas* column text.
    """

    old: str
    new: str
    variant: str
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"old": self.old, "new": self.new,
                             "variant": self.variant}
        if self.note:
            d["note"] = self.note
        return d


__all__ = ["Lemma", "AOChange", "REGIONS"]
