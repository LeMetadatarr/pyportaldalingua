# Transport

Every request goes through the org transport
`unblock_requests.CloudflareSession` — a drop-in `requests.Session` subclass —
wrapped by `pyportaldalingua.Transport`. The portal is a plain old PHP site, so
a bypass is rarely needed, but the same transport gives you TLS impersonation, a
FlareSolverr proxy and an Internet-Archive fallback for free.

## Modes

| Mode | What it does |
|---|---|
| `curl_cffi` *(default)* | live fetch with Chrome TLS impersonation when the `stealth` extra is installed, else plain `requests` |
| `requests` | live fetch with plain `requests` |
| `wayback` | fetch the latest Internet Archive snapshot |
| `flaresolverr` | fetch through a FlareSolverr proxy |

## Configuring

Explicit kwargs win over environment variables.

```python
import pyportaldalingua as pdl

# polite delay between requests
t = pdl.Transport(delay=1.5)
pdl.phonetics("palavra", transport=t)

# pin a mode / force the archive / route through FlareSolverr
client = pdl.PortalDaLingua(transport="requests")
client = pdl.PortalDaLingua(wayback=True)
client = pdl.PortalDaLingua(flaresolverr_url="http://192.168.1.116:8191")
```

A `Transport` reuses one session (and any solved challenge) and sleeps its
configured `delay` after each request.

## Environment fallbacks

Prefix `PYPORTALDALINGUA_`:

| Variable | Meaning |
|---|---|
| `PYPORTALDALINGUA_TRANSPORT` | default mode |
| `PYPORTALDALINGUA_FLARESOLVERR_URL` | FlareSolverr base URL |
| `PYPORTALDALINGUA_FLARESOLVERR_TIMEOUT` | per-request solve budget (ms) |
| `PYPORTALDALINGUA_WAYBACK_FALLBACK` | fall back to the archive on a live failure |

## Politeness

The portal is shared, unauthenticated infrastructure. A descriptive
`User-Agent` is set automatically; keep the `delay` non-zero for bulk crawls
(`scrape_variant`, `dataset.build_ipa_corpus`) and prefer running them as a
homelab job rather than a tight interactive loop.
