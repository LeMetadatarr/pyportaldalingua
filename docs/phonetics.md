# Phonetics (IPA / AFI)

The portal's **Dicionário Fonético** is the Portuguese IPA / AFI transcription
source. `pyportaldalingua.phonetics` reads it in two hops.

## The endpoint

1. **search list** — `index.php?action=fonetica&act=list&region=lbx&search=<word>`
   returns a `Palavra | Classe Gramatical | Fonética` table. Each row already
   carries the lemma (with `·` syllable breaks and the stressed syllable
   underlined), its grammatical class, the standard (Lisboa padrão) IPA, and a
   link `act=details&id=<N>`.
2. **detail page** — `index.php?action=fonetica&act=details&id=<N>` renders the
   same lemma with its IPA in **every transcribed regional accent**.

## Functions

| Function | Requests | Returns |
|---|---|---|
| `phonetics(word)` | 1 | standard IPA `str` for an exact match, or `None` |
| `lemmas(word, limit=20)` | 1 | every matching `Lemma` from the search list |
| `phonetics_detail(word)` | 2 | one `Lemma` with `ipa_by_region` filled in |

```python
import pyportaldalingua as pdl

pdl.phonetics("palavra")              # 'pɐ.lˈa.vɾɐ'

lm = pdl.phonetics_detail("palavra")
for region, ipa in lm.ipa_by_region.items():
    print(f"{region:30} {ipa}")
```

## Regions

The dictionary transcribes these accents (see `pyportaldalingua.REGIONS`):
Luanda, Lisboa (padrão / não padrão), Maputo (padrão / não padrão), Rio de
Janeiro (padrão / não padrão), São Paulo (padrão / não padrão), and Díli. The
**Lisboa (padrão)** value is surfaced as the `Lemma.ipa` headline.

## What's captured

- `word` — the plain lemma headword (syllable dots stripped);
- `ipa` — standard IPA, verbatim, with stress (`ˈ`), length (`ː`) and
  syllable-dot (`.`) marks intact;
- `syllabification` — dot-separated (`"a.ca.sa.la.do"`), from the search row's
  `·` breaks; `Lemma.syllables` splits it into a list;
- `grammatical_class` — the portal's label (`adjetivo`, `nome`, `verbo`, …);
- `ipa_by_region` — every accent's transcription (detail fetch only).

## Caveats

- Matching is exact and case-insensitive against the lemma headword. The portal
  may index several related/inflected forms under one search; `lemmas()` returns
  them all, `phonetics()` keeps the exact-headword hit.
- The phonetic dictionary is a *Recurso em teste* (research resource, Ashby et
  al. 2012); transcriptions are rule-generated per accent. Treat them as a
  high-quality reference, not a hand-curated gold standard.
- Coverage is the dictionary's lemma set, not the full vocabulary; some words in
  the word-lists have no phonetic entry.
