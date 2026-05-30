"""HTTP transport for the Portal da Língua Portuguesa.

``pyportaldalingua`` talks to one surface: the portal's old PHP site at
``http://www.portaldalinguaportuguesa.org/`` — ``index.php?action=…`` pages that
serve HTML. Every request travels through the org transport
:class:`unblock_requests.CloudflareSession`, a drop-in ``requests.Session``
subclass that handles anti-bot challenges (curl_cffi TLS impersonation, a
FlareSolverr proxy, or a Wayback fallback).

Transport is configurable two ways — **constructor kwargs** on
:class:`Transport` (or the high-level clients), or **environment variables** as
fallback defaults (prefix ``PYPORTALDALINGUA_``). Explicit kwargs always win.

Modes (passed straight to ``CloudflareSession``):

- ``curl_cffi`` *(default)* — live fetch with Chrome TLS impersonation when the
  ``stealth`` extra is installed, else plain ``requests``;
- ``requests`` — live fetch with plain ``requests``;
- ``wayback`` — fetch the latest Internet Archive snapshot;
- ``flaresolverr`` — fetch through a FlareSolverr proxy.

The portal is shared, unauthenticated infrastructure; the transport carries a
descriptive ``User-Agent``, reuses one session, and the bulk scrapers sleep a
polite ``delay`` between requests.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

from unblock_requests import CloudflareSession

BASE_URL = "http://www.portaldalinguaportuguesa.org/"
INDEX = "http://www.portaldalinguaportuguesa.org/index.php"
ENV_PREFIX = "PYPORTALDALINGUA"

_USER_AGENT = (
    "pyportaldalingua/0.0.1 (TigreGotico language client; "
    "https://github.com/TigreGotico/pyportaldalingua)"
)

_VALID_MODES = {"requests", "curl_cffi", "wayback", "flaresolverr"}


class Transport:
    """Resolves *how* the portal is fetched, from explicit kwargs with
    environment fallbacks. Wraps a single :class:`CloudflareSession` and adds a
    polite inter-request delay.

    Args:
        mode:                 ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                              ``"flaresolverr"``. ``None`` → resolve from the
                              environment, then auto.
        delay:                seconds to sleep after each request (politeness).
        flaresolverr_url:     FlareSolverr base URL; setting it alone selects the
                              ``flaresolverr`` mode.
        flaresolverr_timeout_ms: per-request solve budget (default 60000).
        wayback_fallback:     fall back to the Wayback Machine on any live
                              failure. ``None`` → read the env flag.

    Example::

        from pyportaldalingua import Transport
        t = Transport(delay=1.0)
        t = Transport(mode="wayback")          # force the Internet Archive
        t = Transport(flaresolverr_url="http://localhost:8191")
    """

    def __init__(self, *, mode: Optional[str] = None, delay: float = 1.0,
                 flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback_fallback: Optional[bool] = None) -> None:
        if mode is not None and mode.lower() not in _VALID_MODES:
            raise ValueError(
                f"mode must be one of {sorted(_VALID_MODES)} or None, got {mode!r}")
        self.mode = mode.lower() if mode else None
        self.delay = delay
        self.flaresolverr_url = flaresolverr_url
        self.flaresolverr_timeout_ms = flaresolverr_timeout_ms
        self.wayback_fallback = wayback_fallback
        self._session: Optional[CloudflareSession] = None

    # -- session ----------------------------------------------------------

    @property
    def session(self) -> CloudflareSession:
        """The shared, lazily-built :class:`CloudflareSession`."""
        if self._session is None:
            self._session = CloudflareSession(
                mode=self.mode,
                flaresolverr_url=self.flaresolverr_url,
                flaresolverr_timeout_ms=self.flaresolverr_timeout_ms,
                wayback_fallback=self.wayback_fallback,
                env_prefix=ENV_PREFIX,
            )
            self._session.headers.update({"User-Agent": _USER_AGENT})
        return self._session

    def _resolved_mode(self) -> str:
        """The transport mode that will actually be used (for introspection)."""
        return self.session._resolved_mode()

    # -- fetch ------------------------------------------------------------

    def get_html(self, url: Optional[str] = None, *,
                 params: Optional[Dict[str, Any]] = None,
                 sleep: bool = True) -> str:
        """GET *url* (default the ``index.php`` endpoint) and return its text.

        ``None``-valued params are dropped. When *sleep* is true the configured
        :attr:`delay` is applied after the request.
        """
        query = {k: v for k, v in (params or {}).items() if v is not None}
        r = self.session.get(url or INDEX, params=query, timeout=30)
        r.raise_for_status()
        if sleep and self.delay:
            time.sleep(self.delay)
        return r.text


_DEFAULT_TRANSPORT: Optional[Transport] = None


def default_transport() -> Transport:
    """Return the shared, environment-driven :class:`Transport`."""
    global _DEFAULT_TRANSPORT
    if _DEFAULT_TRANSPORT is None:
        _DEFAULT_TRANSPORT = Transport()
    return _DEFAULT_TRANSPORT
