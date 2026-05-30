# Provenance

## Source

All data comes from the **Portal da Língua Portuguesa**
(`http://www.portaldalinguaportuguesa.org/`), an ILTEC language-resource
repository. The client reads its public `index.php?action=…` pages:

- `action=fonetica&act=list&region=lbx&search=<word>` — the **Dicionário
  Fonético** search list (lemma, grammatical class, standard IPA, detail link);
- `action=fonetica&act=details&id=<N>` — the lemma's IPA in every transcribed
  regional accent;
- `action=novoacordo&act=list&letter=<a-z>&version=<pe|pb>` — the **Acordo
  Ortográfico de 1990** spelling-change lists (`pe` = European / `pt_PT`,
  `pb` = Brazilian / `pt_BR`).

No private endpoint and no API key — the same pages the portal serves to any
visitor.

## Bundled data (`data/`)

The repo ships pre-built corpora captured from the portal, so the offline and
dataset paths need no network:

| File | Content |
|---|---|
| `acordo_ortografico_pt_PT.csv` | AO90 changes, European Portuguese |
| `acordo_ortografico_pt_BR.csv` | AO90 changes, Brazilian Portuguese |
| `wordlist-ao-latest.txt.xz` | vocabulary in post-AO90 orthography |
| `wordlist-preao-latest.txt.xz` | vocabulary in pre-AO90 orthography |
| `wordlist-big-latest.txt.xz` | combined large word-list |
| `proverbios.txt` | Portuguese proverbs |
| `estrangeirismos.pdf` | loanwords reference |

The CSVs reproduce what `scrape_variant` fetches live; the word-lists are
latin-1 text.

## Citation

The Dicionário Fonético is a research resource. If you use its transcriptions,
cite the portal's own request:

> Ashby, S. et al. (2012). *A Rule Based Pronunciation Generator and Regional
> Accent Databank for Portuguese.* Proceedings of Interspeech 2012.

Transcriptions are rule-generated per regional accent (Luanda, Lisboa, Maputo,
Rio de Janeiro, São Paulo, Díli — padrão and não-padrão).

## Coverage and limits

- `phonetics()` returns only the IPA the dictionary actually transcribes; its
  lemma set is smaller than the full word-lists, so some words have no entry.
- Matching is on the exact lemma headword (case-insensitive); `lemmas()` exposes
  the related/inflected forms the portal indexes under a search.
- IPA strings are kept verbatim, including stress (`ˈ`), length (`ː`) and
  syllable-dot (`.`) marks.

## Reproducing

The offline fixtures in `tests/fixtures/` are verbatim captures of live pages
(`fonetica_search_casa.html`, `fonetica_details_acasalado.html`,
`ao_list_a_pe.html`), used to exercise the parsers without network access.
Refresh them by re-fetching the corresponding endpoints above.

## Politeness

The portal is shared, unauthenticated infrastructure. The client sets a
descriptive `User-Agent`, reuses one session per `Transport`, and sleeps a
configurable `delay` between requests. Keep bulk crawls modest and prefer
running them as a homelab job.
