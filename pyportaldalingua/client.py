"""High-level :class:`PortalDaLingua` client with a configurable transport.

Mirrors the module-level functions in :mod:`pyportaldalingua.phonetics` and
:mod:`pyportaldalingua.orthography`, but every call reuses the transport you
configure here (mode, polite delay, FlareSolverr, Wayback).
"""
from __future__ import annotations

from typing import List, Optional

from pyportaldalingua import orthography, phonetics
from pyportaldalingua.models import AOChange, Lemma
from pyportaldalingua.transport import Transport


class PortalDaLingua:
    """Client for the Portal da Língua Portuguesa.

    Args:
        transport:        ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                          ``"flaresolverr"``, or a ready :class:`Transport`.
        delay:            polite inter-request delay (seconds), when building a
                          transport for you.
        flaresolverr_url: FlareSolverr base URL; setting it selects that mode.
        wayback:          force the Internet Archive.
        wayback_fallback: fall back to the archive on any live failure.

    Example::

        import pyportaldalingua as pdl
        client = pdl.PortalDaLingua(delay=1.0)
        print(client.phonetics("acasalado"))
        for ch in client.scrape_letter("a", "pt_PT")[:3]:
            print(ch.old, "->", ch.new)
    """

    def __init__(self, transport=None, *, delay: float = 1.0,
                 flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback: bool = False,
                 wayback_fallback: Optional[bool] = None) -> None:
        if isinstance(transport, Transport):
            self.transport = transport
        else:
            mode = "wayback" if wayback else transport
            self.transport = Transport(
                mode=mode, delay=delay,
                flaresolverr_url=flaresolverr_url,
                flaresolverr_timeout_ms=flaresolverr_timeout_ms,
                wayback_fallback=wayback_fallback,
            )

    # -- phonetics --------------------------------------------------------

    def phonetics(self, word: str) -> Optional[str]:
        return phonetics.phonetics(word, transport=self.transport)

    def phonetics_detail(self, word: str) -> Optional[Lemma]:
        return phonetics.phonetics_detail(word, transport=self.transport)

    def lemmas(self, word: str, *, limit: int = 20) -> List[Lemma]:
        return phonetics.lemmas(word, limit=limit, transport=self.transport)

    # -- orthography ------------------------------------------------------

    def scrape_letter(self, letter: str, variant: str = "pt_PT") -> List[AOChange]:
        return orthography.scrape_letter(letter, variant, transport=self.transport)

    def scrape_variant(self, variant: str = "pt_PT", *,
                       letters: Optional[str] = None) -> List[AOChange]:
        return orthography.scrape_variant(variant, letters=letters,
                                          transport=self.transport)
