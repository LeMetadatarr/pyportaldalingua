# Dataset export

`pyportaldalingua.dataset` turns the portal's two resources into
Hugging-Face-shaped JSON Lines: a Portuguese grapheme-to-phoneme (IPA)
supervision corpus for pronunciation modeling, TTS, and phonemics research.

## Configs

### `ipa`: the Portuguese IPA pronunciation dataset

One row per lemma that has a transcription. The core training signal for
grapheme-to-phoneme (G2P) and TTS front-ends.

```json
{"word": "acasalado", "ipa": "ɐ.kɐ.zɐ.lˈa.du",
 "syllables": ["a", "ca", "sa", "la", "do"],
 "class": "adjetivo", "source": "portaldalinguaportuguesa.org"}
```

### `acordo`: the Acordo Ortográfico de 1990 change set

One row per spelling change, both variants.

```json
{"old": "abjecto", "new": "abjeto", "variant": "pt_PT",
 "note": null, "source": "portaldalinguaportuguesa.org"}
```

## Writing

```python
from pyportaldalingua import dataset, load_changes_csv, lemmas

lems = lemmas("casa")
changes = load_changes_csv("pt_PT")

# one config to a single file
dataset.export_jsonl(lems, "ipa.jsonl", "ipa")
dataset.export_jsonl(changes, "acordo.jsonl", "acordo")

# both configs + a manifest.json under a directory
dataset.export_all(lems, changes, "corpus/")
```

`export_*` returns row counts. JSON Lines loads directly with
`datasets.load_dataset("json", data_files="corpus/ipa.jsonl")` and streams
without holding the corpus in memory. Rows with no IPA are skipped from the
`ipa` config.

## Crawling

```python
from pyportaldalingua import dataset, load_wordlists
import itertools

# seed words from the bundled word-list, build the IPA corpus politely
words = itertools.islice(load_wordlists("ao"), 500)
n = dataset.build_ipa_corpus("ipa.jsonl", words, delay=1.0)

# the AO change set, straight from the bundled CSV (no network)
dataset.build_acordo_corpus("acordo.jsonl", variant="pt_BR")
```

Use `detail=True` on `build_ipa_corpus` to also fetch each lemma's per-region
table (a second request per word). Seed `words` from `load_wordlists` or a
frequency list.

## ML tasks this serves

- **Grapheme-to-phoneme (G2P) / TTS front-ends**: `word -> ipa`, the core
  supervision for predicting Portuguese pronunciation from spelling, with
  syllable boundaries included.
- **Regional accent modeling**: the detail-page `ipa_by_region` gives
  parallel transcriptions across European, Brazilian, African, and Timorese
  accents.
- **Orthographic normalization**: the `acordo` config (and the `ao` / `preao`
  word-lists) is a parallel pre-reform/post-reform spelling corpus.

See [PROVENANCE.md](../PROVENANCE.md) for source, citation, and licensing.

---
[← Transport](transport.md) · [Home](../README.md) · [External IDs →](external_ids.md)
