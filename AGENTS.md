# AGENTS.md — pyportaldalingua

Typed Python client for the **Portal da Língua Portuguesa**
(`http://www.portaldalinguaportuguesa.org/`, no key). An old PHP site
(`index.php?action=…`). It reads the Dicionário Fonético (per-lemma IPA/AFI) and
the Acordo Ortográfico change lists into dataclasses, and ships the pre-built
corpora in `data/`.

## Setup

```bash
pip install -e .
pip install -e ".[stealth]"   # adds curl-cffi TLS impersonation
pip install -e ".[test]"      # adds pytest
```

Pure-Python, Python >= 3.9. Runtime deps: `requests`, `unblock_requests`.
`curl-cffi` is the optional stealth backend. Parsing is stdlib `re` only — the
portal's HTML is too malformed for a strict parser, so the modules target its
exact (broken) tag shapes.

## Test

```bash
pytest -m "not live"     # offline: fixture- and CSV-driven, no network
pytest -m live           # live smoke test (hits the real portal)
```

Offline tests run against captured fixtures in `tests/fixtures/` and the bundled
`data/` CSVs/word-lists — no network. The `live` tests in `tests/test_live.py`
are the only ones that touch the portal.

A pytest plugin in the shared `~/.venvs/ovos` env can fail to import; run with
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` if collection errors on an unrelated package.

## Layout

- `pyportaldalingua/__init__.py` — public API surface.
- `pyportaldalingua/transport.py` — `Transport` wrapping one
  `unblock_requests.CloudflareSession`; `get_html(params=…)` + polite `delay`.
  Modes: `curl_cffi` (default) / `requests` / `wayback` / `flaresolverr`. Env
  prefix `PYPORTALDALINGUA_`.
- `pyportaldalingua/models.py` — `Lemma` (word, ipa, syllabification,
  grammatical_class, ipa_by_region, detail_id) and `AOChange` (old, new,
  variant, note), each with `to_dict()`; `REGIONS`.
- `pyportaldalingua/_clean.py` — tag/entity strip, NFC normalise, `syllabify`
  (`·` middots → `.`).
- `pyportaldalingua/phonetics.py` — Dicionário Fonético: `phonetics`,
  `phonetics_detail`, `lemmas`, and the `parse_search` / `parse_detail` parsers.
- `pyportaldalingua/orthography.py` — AO90: `scrape_letter`, `scrape_variant`,
  `parse_changes`; bundled `load_changes_csv`, `load_wordlists`, `wordlist_names`.
- `pyportaldalingua/client.py` — `PortalDaLingua` high-level client.
- `pyportaldalingua/ids.py` — `lemma_id` / `id_from_url` / `lemma_to_extra`:
  convert a lemma into a flat external-IDs dict, keys namespaced
  `portaldalingua_`, anchored on the lemma word.
- `pyportaldalingua/dataset.py` — HF export: configs `ipa` and `acordo`;
  `export_jsonl` / `export_all` / `build_ipa_corpus` / `build_acordo_corpus`.
- `data/` — pre-built corpora (AO CSVs, xz word-lists, proverbs, loanwords PDF).
- `examples/` — runnable numbered scripts; `docs/` — usage docs.

## The reverse-engineered endpoints

- **IPA search**: `index.php?action=fonetica&act=list&region=lbx&search=<word>`
  → `Palavra | Classe Gramatical | Fonética` table. Each row carries the lemma
  (with `·` syllable breaks, stressed syllable underlined), class, standard IPA,
  and a link `act=details&id=<N>`. The portal serves a **malformed anchor**
  (`href='>?action=…'>IPA</a>`) — the parser takes the text between the close
  `>` and `</a>`.
- **IPA detail**: `index.php?action=fonetica&act=details&id=<N>` → the lemma's
  IPA in 9 regional accents (`<td>region<td>ipa` rows).
- **AO list**: `index.php?action=novoacordo&act=list&letter=<a-z>&version=<pe|pb>`
  → `Ortografia Antiga | Ortografia Nova | Notas` table. `pe`=`pt_PT`, `pb`=`pt_BR`.

## Conventions (org hard rules)

- Branches: work on `dev`, stable on `master`; `dev` is the GitHub default.
  Never `main`.
- Never edit `pyportaldalingua/version.py`; gh-automations bumps semver from
  conventional-commit prefixes.
- New repos are private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- Reference `OpenVoiceOS/gh-automations` reusable workflows at `@dev`.
- No Neon / `neon-*` references.
- No meta-commentary in code/docs/commits/PRs.

## Gotchas

- Word-lists are **latin-1**, not utf-8 (`load_wordlists` decodes accordingly).
- The phonetic dictionary is a research resource (Ashby et al. 2012,
  rule-generated per accent) — high-quality reference, not a hand-curated gold
  standard; coverage is its lemma set, not the full vocabulary.
- `phonetics()` matches the exact headword case-insensitively; `lemmas()`
  returns every indexed form (including inflections / multi-word entries).
