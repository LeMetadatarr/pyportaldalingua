# Orthography — Acordo Ortográfico + word-lists

`pyportaldalingua.orthography` covers the **Acordo Ortográfico de 1990** (AO90)
spelling changes and the bundled Portuguese word-lists.

## AO90 changes

The portal lists the changes per letter, per variant, at
`index.php?action=novoacordo&act=list&letter=<a-z>&version=<pe|pb>` — a
`Ortografia Antiga | Ortografia Nova | Notas` table. `pe` is European Portuguese
(`pt_PT`), `pb` is Brazilian (`pt_BR`).

```python
import pyportaldalingua as pdl

# one letter
for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
    print(ch.old, "->", ch.new, ch.note)   # abjecto -> abjeto

# a whole variant, a-z (polite: one session, delay between requests)
all_pt = pdl.scrape_variant("pt_PT")
```

Each row is an `AOChange(old, new, variant, note)`. `variant` is `"pt_PT"` or
`"pt_BR"` (the portal's `pe` / `pb` codes are also accepted).

## Bundled change set (offline)

The repo ships the full pre-scraped change set as CSVs in `data/`:

```python
pt = pdl.load_changes_csv("pt_PT")    # ~3200 AOChange, no network
br = pdl.load_changes_csv("pt_BR")    # ~2000 AOChange
```

These reproduce what `scrape_variant` fetches live — use them for fast, offline
work and reserve the scraper for refreshes.

## Word-lists

Three xz-compressed lists ship in `data/` (latin-1 text), streamed lazily:

| Key | File | Content |
|---|---|---|
| `ao` | `wordlist-ao-latest.txt.xz` | post-AO90 orthography |
| `preao` | `wordlist-preao-latest.txt.xz` | pre-AO90 orthography |
| `big` | `wordlist-big-latest.txt.xz` | combined large list |

```python
for w in pdl.load_wordlists("ao"):
    ...                                # one word per line
pdl.wordlist_names()                   # {'ao': 'wordlist-ao-latest.txt.xz', ...}
```

The `ao` / `preao` pair is a ready-made parallel corpus of the spelling reform
at vocabulary scale; pairing it with `load_changes_csv` gives the lexicalised
changes.

## Other bundled data

`data/` also carries `proverbios.txt` (Portuguese proverbs) and
`estrangeirismos.pdf` (loanwords reference) captured from the portal — see
[PROVENANCE.md](../PROVENANCE.md).
