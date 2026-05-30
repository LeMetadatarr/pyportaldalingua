---
name: pyportaldalingua
description: Look up Portuguese IPA/AFI pronunciation, lexicon and orthography from Portal da Língua Portuguesa for accessible voice-first access on behalf of users who cannot navigate the website.
---
# pyportaldalingua — Portal da Língua Portuguesa for agents

## When to use

Use this skill when a Portuguese-speaking user (or an assistant acting on their behalf) needs:

- pronunciation of a word read aloud — IPA/AFI per accent (Lisboa, Rio de Janeiro, São Paulo, Luanda, Maputo, Díli)
- syllabification or grammatical class of a Portuguese word
- inflection/conjugation tables (how a word declines or conjugates)
- foreign-origin word (estrangeirismo) meaning, source language or adaptation
- the Portuguese demonym for a place name (topónimo → gentílico)
- Acordo Ortográfico de 1990 (AO90) before/after spellings for pt_PT or pt_BR

This is particularly valuable for blind or voice-only users who cannot navigate the portal's web interface.

## Install

```bash
pip install pyportaldalingua
pip install pyportaldalingua[stealth]   # adds curl-cffi TLS impersonation (recommended)
```

## Core operations

### `phonetics(word)` — standard IPA string
Returns the Lisboa (padrão) IPA transcription as a plain string, or `None` if not found.

```python
import pyportaldalingua as pdl

ipa = pdl.phonetics("saudade")
# 'sɐw.ˈda.də'
print(f"A pronúncia de 'saudade' é: {ipa}")
```

Returned value: `str | None`

---

### `phonetics_detail(word)` — full `Lemma` with per-region IPA
Returns a `Lemma` dataclass with all regional transcriptions, syllabification and grammatical class.

```python
lm = pdl.phonetics_detail("saudade")
# lm.ipa                → 'sɐw.ˈda.də'  (Lisboa padrão)
# lm.syllabification    → 'sau.da.de'
# lm.grammatical_class  → 'substantivo'
# lm.ipa_by_region      → dict of accent → IPA string
print(lm.ipa_by_region["Rio de Janeiro (padrão)"])
```

Key `Lemma` fields: `word`, `ipa`, `syllabification`, `grammatical_class`, `ipa_by_region` (keys: `REGIONS`), `syllables` (list property), `detail_id`.

Available region keys (`pdl.REGIONS`): `"Lisboa (padrão)"`, `"Lisboa (não padrão)"`, `"Rio de Janeiro (padrão)"`, `"Rio de Janeiro (não padrão)"`, `"São Paulo (padrão)"`, `"São Paulo (não padrão)"`, `"Luanda"`, `"Maputo (padrão)"`, `"Maputo (não padrão)"`, `"Díli"`.

---

### `vop_search(query, mode="any")` — fuzzy headword lookup (VOP)
Fuzzy/partial search over the Vocabulário Ortográfico do Português. Useful for "words like X" or when the exact spelling is unknown.

```python
results = pdl.vop_search("casament")
for r in results:
    print(r.word, r.grammatical_class, r.lemma_id)
# casamento  substantivo  67445
# casamentos substantivo  67446

# prefix search
prefix_results = pdl.vop_search("casa", mode="start")
```

`mode` values: `"any"` (substring), `"start"` (prefix), `"end"` (suffix), `"exact"`.

Key `VopResult` fields: `word`, `grammatical_class`, `lemma_id`.

---

### `lemma_entry(lemma_id)` — inflection/conjugation table (VOP)
Fetches the full VOP lexicon entry for a lemma ID (from `vop_search`). Returns inflection tables, conjugation tables (for verbs), and related forms (diminutives, augmentatives, past participles, nominal forms).

```python
entry = pdl.lemma_entry("67444")   # casa
# entry.inflection  → {'singular': 'casa', 'plural': 'casas'}
# entry.related     → {'diminutivo': [('casinha', '107833')], ...}
print(entry.inflection)
print(entry.related)
```

Key `LemmaEntry` fields: `word`, `inflection` (dict), `conjugation` (dict, verbs), `related` (dict of form-type → list of (word, id) tuples).

---

### `loanword_search(query)` — Dicionário de Estrangeirismos
Look up foreign-origin words: source language, domain, recommended Portuguese adaptation, and synonyms.

```python
for e in pdl.loanword_search("jazz"):
    print(e.word, e.source_language, e.adaptation)
# jazz  inglês  jazz
```

Key `LoanwordEntry` fields: `word`, `source_language`, `domain`, `adaptation`, `synonyms`.

---

### `toponym_search(query)` — place names → Portuguese demonyms
Maps a place name to its Portuguese gentílico (demonym), place type, and administrative parent.

```python
for g in pdl.toponym_search("lisboa"):
    print(g.toponym, g.place_type, [d.demonym for d in g.demonyms])
# Lisboa  cidade  ['lisboeta', 'lisbonense']
```

Key `ToponymResult` fields: `toponym`, `place_type`, `demonyms` (list of `GentilicoEntry` with `.demonym`).

---

### `scrape_letter(letter, variant)` / `load_changes_csv(variant)` — AO90 spelling changes
Live or offline Acordo Ortográfico de 1990 change list.

```python
# live (one letter)
for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
    print(ch.old, "->", ch.new)
# abjecto -> abjeto

# offline bundled CSV (full list, ~3200 entries)
changes = pdl.load_changes_csv("pt_PT")
changes_br = pdl.load_changes_csv("pt_BR")
```

`variant`: `"pt_PT"` or `"pt_BR"`.

Key `AOChange` fields: `old`, `new`, `variant`, `note`.

## Access notes

All lookups hit `portaldalinguaportuguesa.org` live. The library handles latin-1 encoding quirks from the portal's HTML internally. Install with `[stealth]` for curl-cffi TLS impersonation to avoid bot blocks. Bundled offline data (`load_changes_csv`, `load_wordlists`) requires no network.

## Speaking the results (accessibility)

- Read IPA per accent: prefer the user's regional accent key; fall back to `"Lisboa (padrão)"` — say e.g. "Em Lisboa pronuncia-se /sɐw.ˈda.də/; no Rio de Janeiro /saw.ˈda.dʒi/."
- Offer syllabification alongside IPA: "Saudade divide-se em sau·da·de" — useful when the user needs to spell or type.
- Always include grammatical class when present: "substantivo feminino" gives screen-reader users the morphological context.
- Support natural-language queries: map "como se pronuncia X" → `phonetics_detail(X)`; "palavras parecidas com X" or "words like X" → `vop_search(X)`; "como se chama quem é de X" → `toponym_search(X)`.
