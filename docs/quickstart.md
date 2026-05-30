# Quickstart

`pyportaldalingua` is a typed client for the **Portal da Língua Portuguesa**
(`portaldalinguaportuguesa.org`). It reads two resources: the **Dicionário
Fonético** (per-lemma IPA/AFI) and the **Acordo Ortográfico de 1990** change
lists, plus the bundled word-lists.

## Install

```bash
pip install pyportaldalingua
pip install pyportaldalingua[stealth]   # adds curl-cffi TLS impersonation
pip install pyportaldalingua[test]      # adds pytest
```

## IPA / AFI for a word

```python
import pyportaldalingua as pdl

# standard (Lisboa padrão) transcription
pdl.phonetics("acasalado")            # 'ɐ.kɐ.zɐ.lˈa.du'

# full lemma: IPA in every transcribed region + syllabification + class
lm = pdl.phonetics_detail("acasalado")
print(lm.grammatical_class)           # 'adjetivo'
print(lm.syllabification)             # 'a.ca.sa.la.do'
print(lm.ipa_by_region["Rio de Janeiro (padrão)"])   # 'a.ka.za.lˈa.dʊ'
```

`lemmas(word)` returns every matching headword (including inflected forms the
portal indexes) as `Lemma` objects.

## Acordo Ortográfico changes

```python
# live, one letter
for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
    print(ch.old, "->", ch.new)       # abjecto -> abjeto

# the whole pre-built change set, offline, from the bundled CSVs
pt = pdl.load_changes_csv("pt_PT")    # ~3200 changes
br = pdl.load_changes_csv("pt_BR")    # ~2000 changes
```

## Word-lists

```python
for w in pdl.load_wordlists("ao"):    # post-AO90; also "preao", "big"
    ...                               # streamed, one word per line
```

## A configured client

```python
client = pdl.PortalDaLingua(delay=1.5)   # politer crawl
client.phonetics("palavra")
client.scrape_variant("pt_BR")
```

See [transport.md](transport.md) for modes and anti-bot, [phonetics.md](phonetics.md)
for how IPA is parsed, [orthography.md](orthography.md) for AO + word-lists, and
[dataset.md](dataset.md) for the HF corpora this client produces.
