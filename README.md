# pyportaldalingua

Typed Python client for the **Portal da Língua Portuguesa**
(`portaldalinguaportuguesa.org`) — the Portuguese **IPA / AFI** pronunciation
source and the **Acordo Ortográfico de 1990** change set.

It reads two of the portal's resources into dataclasses:

- the **Dicionário Fonético** — per-lemma IPA transcription in several regional
  accents (Lisboa, Luanda, Rio de Janeiro, São Paulo, Maputo, Díli), with
  syllabification and grammatical class;
- the **Acordo Ortográfico** spelling-change lists (`pt_PT` / `pt_BR`), plus the
  bundled word-lists shipped in `data/`.

## Install

```bash
pip install pyportaldalingua
pip install pyportaldalingua[stealth]   # adds curl-cffi TLS impersonation
pip install pyportaldalingua[test]      # adds pytest
```

## 30-second tour

```python
import pyportaldalingua as pdl

# IPA / AFI for a Portuguese word (Lisboa padrão)
pdl.phonetics("acasalado")            # 'ɐ.kɐ.zɐ.lˈa.du'

# the full lemma in every transcribed region
lm = pdl.phonetics_detail("acasalado")
print(lm.grammatical_class)           # 'adjetivo'
print(lm.syllabification)             # 'a.ca.sa.la.do'
print(lm.ipa_by_region["Rio de Janeiro (padrão)"])   # 'a.ka.za.lˈa.dʊ'

# Acordo Ortográfico spelling changes
for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
    print(ch.old, "->", ch.new)       # abjecto -> abjeto

# bundled corpora (offline)
pt = pdl.load_changes_csv("pt_PT")    # ~3200 AO changes
words = pdl.load_wordlists("ao")      # streamed word-list
```

## What you can fetch

| Function | Returns | Source |
|---|---|---|
| `phonetics("palavra")` | IPA `str` / `None` | Dicionário Fonético (standard accent) |
| `phonetics_detail("palavra")` | `Lemma` / `None` | per-region IPA table |
| `lemmas("casa")` | `List[Lemma]` | phonetic-dictionary search |
| `scrape_letter("a", "pt_PT")` | `List[AOChange]` | live AO90 list |
| `scrape_variant("pt_BR")` | `List[AOChange]` | live AO90, a–z |
| `load_changes_csv("pt_PT")` | `List[AOChange]` | bundled CSV (offline) |
| `load_wordlists("ao")` | `Iterator[str]` | bundled word-list (offline) |

## Dataset corpora

```python
from pyportaldalingua import dataset
dataset.export_all(pdl.lemmas("casa"), pdl.load_changes_csv("pt_PT"), "corpus/")
```

Two Hugging-Face-shaped JSONL configs: **`ipa`** (`word, ipa, syllables, class,
source` — the Portuguese IPA pronunciation dataset) and **`acordo`** (the AO90
`pt_PT`/`pt_BR` change set). This feeds the Lusophone phonemics flagship
(`ml/phonemes`, `ml/portuguese/tugaphone`). See [docs/dataset.md](docs/dataset.md).

## Documentation

- [docs/quickstart.md](docs/quickstart.md) — the essentials
- [docs/phonetics.md](docs/phonetics.md) — how IPA / AFI is found and parsed
- [docs/orthography.md](docs/orthography.md) — Acordo Ortográfico + word-lists
- [docs/transport.md](docs/transport.md) — transport modes / anti-bot / Wayback
- [docs/dataset.md](docs/dataset.md) — the dataset configs this client produces
- [docs/external_ids.md](docs/external_ids.md) — external-IDs dict for cross-referencing across data sources
- [docs/reverse-engineering.md](docs/reverse-engineering.md) — the reverse-engineered AFI/IPA endpoint: params, response, 10-accent table, two-hop flow

Runnable, numbered scripts live in [examples/](examples/). Source, citation and
licensing are in [PROVENANCE.md](PROVENANCE.md).
