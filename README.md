# pyportaldalingua

Typed Python client for the **Portal da Língua Portuguesa**
(`portaldalinguaportuguesa.org`), the Portuguese **IPA / AFI** pronunciation
source, the **Acordo Ortográfico de 1990** change set, and three more
linguistic dictionaries the portal exposes.

It reads five of the portal's resources into dataclasses:

- the **Dicionário Fonético**: per-lemma IPA transcription in several
  regional accents (Lisboa, Luanda, Rio de Janeiro, São Paulo, Maputo, Díli),
  with syllabification and grammatical class.
- the **Acordo Ortográfico** spelling-change lists (`pt_PT` / `pt_BR`), plus
  the word-lists bundled in `data/`.
- the **Vocabulário Ortográfico do Português (VOP)**: fuzzy and partial
  headword search (exact, prefix, suffix, substring) and per-lemma lexicon
  entries with inflection and conjugation tables, and related-form links
  (diminutives, augmentatives, past participles, nominal forms).
- the **Dicionário de Estrangeirismos**: foreign-origin words with source
  language, domain, recommended Portuguese adaptation, and synonyms.
- the **Dicionário de Gentílicos e Topónimos**: place names mapped to their
  Portuguese demonyms, with place type and administrative parent.

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

# fuzzy / partial headword resolution (VOP vocabulary)
for r in pdl.vop_search("casament"):
    print(r.word, r.grammatical_class, r.lemma_id)

# VOP lexicon entry: inflection table and related forms
entry = pdl.lemma_entry("67444")      # casa
print(entry.inflection)               # {'singular': 'casa', 'plural': 'casas'}
print(entry.related)                  # {'diminutivo': [('casinha', '107833')], ...}

# Dicionário de Estrangeirismos
for e in pdl.loanword_search("jazz"):
    print(e.word, e.source_language, e.adaptation)

# Dicionário de Gentílicos e Topónimos
for g in pdl.toponym_search("lisboa"):
    print(g.toponym, g.place_type, [d.demonym for d in g.demonyms])

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
| `vop_search("casament")` | `List[VopResult]` | VOP fuzzy/partial headword search |
| `vop_search("casa", mode="start")` | `List[VopResult]` | VOP prefix search |
| `lemma_entry("67444")` | `LemmaEntry` / `None` | VOP lexicon entry: inflection, conjugation, related forms |
| `loanword_search("jazz")` | `List[LoanwordEntry]` | Dicionário de Estrangeirismos |
| `toponym_search("lisboa")` | `List[ToponymResult]` | Dicionário de Gentílicos e Topónimos |
| `scrape_letter("a", "pt_PT")` | `List[AOChange]` | live AO90 list |
| `scrape_variant("pt_BR")` | `List[AOChange]` | live AO90, a-z |
| `load_changes_csv("pt_PT")` | `List[AOChange]` | bundled CSV (offline) |
| `load_wordlists("ao")` | `Iterator[str]` | bundled word-list (offline) |

## Dataset corpora

```python
from pyportaldalingua import dataset
dataset.export_all(pdl.lemmas("casa"), pdl.load_changes_csv("pt_PT"), "corpus/")
```

This produces two Hugging-Face-shaped JSONL configs. **`ipa`** holds `word,
ipa, syllables, class, source`, the Portuguese IPA pronunciation dataset.
**`acordo`** holds the AO90 `pt_PT`/`pt_BR` change set. Together they form a
Portuguese grapheme-to-phoneme corpus for pronunciation modeling and
phonemics research. See [docs/dataset.md](docs/dataset.md).

## Documentation

- [docs/quickstart.md](docs/quickstart.md): the essentials
- [docs/phonetics.md](docs/phonetics.md): how IPA / AFI is found and parsed
- [docs/orthography.md](docs/orthography.md): Acordo Ortográfico and word-lists
- [docs/transport.md](docs/transport.md): transport modes, anti-bot handling, Wayback fallback
- [docs/dataset.md](docs/dataset.md): the dataset configs this client produces
- [docs/external_ids.md](docs/external_ids.md): external-IDs dict for cross-referencing across data sources
- [docs/reverse-engineering.md](docs/reverse-engineering.md): the reverse-engineered endpoints (phonetics two-hop, VOP search, lemma entry, loanwords, toponyms) and the sections not yet covered

Runnable, numbered scripts live in [examples/](examples/). Source, citation,
and licensing are in [PROVENANCE.md](PROVENANCE.md).
