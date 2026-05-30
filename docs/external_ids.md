# External IDs

`pyportaldalingua.ids` converts a `Lemma` into a flat `str -> str` dict of
namespaced external IDs, suitable for cross-referencing across data sources.
Keys are prefixed with `portaldalingua_`.

A phonetic-dictionary entry has no opaque stable key the way a media record
does — a lexical entry is identified by its **lemma word** (the pt-orthography
headword). The detail-page numeric `id` is carried alongside when known, but the
word is the anchor.

## Functions

```python
import pyportaldalingua as pdl

pdl.lemma_id(" casa ")                # 'casa'  — the canonical anchor

pdl.id_from_url(
  "…?action=fonetica&region=lbx&act=details&id=32032")   # '32032'

lm = pdl.phonetics_detail("acasalado")
pdl.lemma_to_extra(lm)
# {
#   'portaldalingua_word': 'acasalado',
#   'portaldalingua_id': '32032',
#   'portaldalingua_url': '…act=details&id=32032',
#   'portaldalingua_ipa': 'ɐ.kɐ.zɐ.lˈa.du',
#   'portaldalingua_syllables': 'a.ca.sa.la.do',
#   'portaldalingua_class': 'adjetivo',
# }
```

Only keys present on the lemma are written, so a bare `Lemma(word=…)` yields
just `portaldalingua_word`. The shape is compatible with other language clients'
`*_to_extra` helpers (e.g. `pywiktionary.entry_to_extra`), so a pipeline can mix
Portuguese IPA from the portal with Wiktionary IPA under one external-IDs dict.
