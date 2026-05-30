# Reverse-Engineering the Portal da Língua Portuguesa — AFI/IPA Endpoint

The **Dicionário Fonético** on `portaldalinguaportuguesa.org` exposes
Portuguese IPA (AFI) transcriptions through a two-step internal PHP
interface that is **not documented as an API** anywhere on the site. The
endpoints were recovered by inspecting live browser traffic and confirmed
against verbatim page captures in `tests/fixtures/`. This document records
exactly what was found.

---

## Why this is reverse engineering

The portal presents a conventional HTML form to users: a search box on the
Dicionário Fonético page that accepts a word, submits it via a GET form, and
renders a results table. There is no public API specification, no OpenAPI
document, no versioned endpoint, and no developer documentation.

The internal `index.php?action=fonetica&act=…` parameter surface that powers
that form is what `pyportaldalingua` uses. It was identified by inspecting the
`form` element's `action` and `method` attributes in the page HTML and the
`href` links inside each search result row.

```html
<!-- from the detail page's right-sidebar search form -->
<input type=hidden name=action value=fonetica>
<input type=hidden name=act value=list>
<input type=hidden name=region value='lbx'>
<input name=search size=25>
```

The critical second hop — the per-lemma detail link — uses a numeric `id`
parameter that appears inside each result row's anchor href:

```html
<a href='>?action=fonetica&act=details&id=103134'>ɐ.kɐ.zɐ.lˈa.du</a>
```

That `id` is opaque to any caller and cannot be known without first performing
the search. There is no public index of IDs, no REST resource to enumerate
them, and no documentation that they exist.

---

## Base URL and entry point

All requests go to one PHP file:

```
http://www.portaldalinguaportuguesa.org/index.php
```

The `action` query parameter selects the resource; `act` selects the sub-view.

---

## Endpoint 1 — Headword search (ID resolution)

```
GET http://www.portaldalinguaportuguesa.org/index.php
    ?action=fonetica
    &act=list
    &region=lbx
    &search=<headword>
```

### Parameters

| Parameter | Required | Value |
|-----------|----------|-------|
| `action`  | yes      | `fonetica` — selects the Dicionário Fonético resource |
| `act`     | yes      | `list` — requests the search-result list view |
| `region`  | yes      | `lbx` — Lisboa; used as the rendering locale (affects which accent is highlighted in the list) |
| `search`  | yes      | the query word, URL-encoded; the portal matches against headwords and indexed inflected forms |

### Response

An HTML page (UTF-8, `Content-Type: text/html; charset=UTF-8`) containing a
table with one row per matching lemma. The relevant columns are:

- **Palavra** (`<td title='Palavra'>`) — the lemma headword, rendered with
  `·` (U+00B7 middle dot) syllable-break markers and the stressed syllable
  wrapped in `<u><b>…</b></u>`. The plain word is obtained by stripping dots
  and markup.
- **Classe Gramatical** (`<td>`) — the grammatical class label, e.g.
  `adjetivo`, `nome`, `verbo`.
- **Fonética** (`<td title='Fonética'>`) — an anchor whose `href` encodes the
  detail `id` (`act=details&id=<N>`) and whose link text is the standard
  Lisboa padrão IPA. The anchor is malformed (the `href` value opens with `'>`
  rather than a proper delimiter), so the IPA text must be extracted by
  splitting on `</a>` and then on the last `>`.

The numeric `id` extracted from the `href` is the only stable key to the
lemma's detail page.

### Code reference

`pyportaldalingua.phonetics.lemmas()` and `parse_search()` in
`pyportaldalingua/phonetics.py`.

---

## Endpoint 2 — AFI/IPA detail page (all regional accents)

```
GET http://www.portaldalinguaportuguesa.org/index.php
    ?action=fonetica
    &act=details
    &id=<numeric-id>
    &region=lbx
```

### Parameters

| Parameter | Required | Value |
|-----------|----------|-------|
| `action`  | yes      | `fonetica` |
| `act`     | yes      | `details` — requests the per-lemma detail view |
| `id`      | yes      | numeric identifier from the search list row; opaque, site-internal |
| `region`  | no       | `lbx` — Lisboa; the site uses it for UI context; the full regional table is always rendered regardless |

### Response

An HTML page (UTF-8) containing:

1. A heading:
   ```html
   <h2>Palavra: <a href='?action=lemma&id=103134' style='font-size: 16px;'>acasalado</a> (adjetivo)</h2>
   ```
   The anchor text is the headword; the parenthetical is the grammatical class.

2. A `<table>` immediately following the heading with one `<tr>` per
   transcribed region. Each row: `<td>region label</td><td>IPA string</td>`.
   No table header row; no `id` or `class` attributes on the table itself.

### The 10 transcribed regional accents

The table delivers (in page order):

| Row label | Example IPA for *acasalado* |
|-----------|------------------------------|
| `Luanda` | `a.kɐ.zɐ.lˈa.dʊ` |
| `Lisboa (não padrão)` | `ɐ.kɐ.zɐ.lˈa.du` |
| `Lisboa (padrão)` | `ɐ.kɐ.zɐ.lˈa.du` |
| `Maputo (não padrão)` | `a.kɐ.zɐ.lˈa.dːʊ` |
| `Maputo (padrão)` | `ɐ.kɐ.zɐ.lˈa.du` |
| `Rio de Janeiro (não padrão)` | `a.ka.za.lˈa.dʊ` |
| `Rio de Janeiro (padrão)` | `a.ka.za.lˈa.dʊ` |
| `São Paulo (não padrão)` | `a.ka.za.lˈa.dʊ` |
| `São Paulo (padrão)` | `a.ka.za.lˈa.dʊ` |
| `Díli` | `ə.kə.zə.lˈa.dʊ` |

The `Lisboa (padrão)` row is highlighted in the page (`font-weight: bold;
background-color: #ffffaa`) and is the value `pyportaldalingua` surfaces as
`Lemma.ipa`.

IPA strings are returned verbatim from the page, preserving primary stress
(`ˈ`), length (`ː`), and syllable dot (`.`) marks as served by the portal.

### Code reference

`pyportaldalingua.phonetics.phonetics_detail()` and `parse_detail()` in
`pyportaldalingua/phonetics.py`. The canonical `Lemma.url` property in
`pyportaldalingua/models.py` reconstructs the full detail URL from a known
`detail_id`.

---

## The two-hop flow

```
phonetics_detail("acasalado")
│
├─ GET index.php?action=fonetica&act=list&region=lbx&search=acasalado
│   └─ parse_search() → [Lemma(word="acasalado", ipa="ɐ.kɐ.zɐ.lˈa.du", detail_id="103134"), …]
│
└─ GET index.php?action=fonetica&act=details&id=103134&region=lbx
    └─ parse_detail() → Lemma(ipa_by_region={"Lisboa (padrão)": "ɐ.kɐ.zɐ.lˈa.du", …})
```

`phonetics()` performs only the first hop and returns the Lisboa padrão IPA
from the search row directly (one request). `phonetics_detail()` performs both
hops (two requests) to fill `ipa_by_region`.

---

## Encoding

The portal's HTML pages declare `charset=UTF-8` and are served as UTF-8.
Bundled word-list files in `data/*.txt.xz` are latin-1 encoded (a property
of the source archive format, not the live HTTP interface).

---

## Caveats

- **Exact headword match only.** `phonetics()` and `phonetics_detail()` perform
  a case-insensitive exact match against the lemma headword. The search may
  return related or inflected forms under the same query; only the row whose
  `word` equals the query (case-folded) is used. `lemmas()` exposes all rows.
- **Numeric IDs are opaque and site-internal.** There is no public list of IDs.
  All callers must resolve via the search endpoint first.
- **Malformed anchor.** The search list's phonetics link is syntactically
  malformed (`href='>?action=…`). The IPA text is extracted by splitting on
  `</a>` and `>`, not by a standard attribute parser. See `_row_to_lemma()` in
  `phonetics.py`.
- **Research status.** The Dicionário Fonético is labelled *Recurso em teste*
  on the site. Transcriptions are rule-generated (Ashby et al., 2012); coverage
  is the dictionary's lemma set, which is smaller than the full word-lists.

---

---

## Endpoint 3 — VOP vocabulary search (fuzzy / partial headword resolution)

```
GET http://www.portaldalinguaportuguesa.org/simplesearch.php
    ?sel=<mode>
    &action=simplesearch
    &base=form
    &query=<word>
```

This endpoint backs the **Vocabulário Ortográfico do Português (VOP)** search
form on the portal's main navigation.

### Parameters

| Parameter | Required | Value |
|-----------|----------|-------|
| `sel`     | yes      | `exact` / `contain` / `start` / `end` |
| `action`  | yes      | `simplesearch` |
| `base`    | yes      | `form` |
| `query`   | yes      | the query word or prefix |

`sel=contain` is the portal's substring/fuzzy mode and is what
`pyportaldalingua.vop_search()` defaults to.

### Response

An HTML page with `<h1>Resultados da pesquisa</h1>` and a result count, then a
`<table>` with one `<tr>` per matching lemma. Each row carries:

- a `<td label="…">` attribute whose value is a normalised key for the headword;
- a `<span style="color: …">` containing the **grammatical class**;
- a `<td>` with an optional inflected-form note (when the hit is an inflected
  form indexed under a different headword);
- an `<a href="?action=lemma&lemma=<id>">` anchor with the **headword** and the
  numeric **lemma id**.

Results are returned in alphabetical order of the `label` attribute.

### Code reference

`pyportaldalingua.lexicon.parse_vop_search()` and `vop_search()` in
`pyportaldalingua/lexicon.py`.

---

## Endpoint 4 — VOP lemma entry (inflection, conjugation, related forms)

```
GET http://www.portaldalinguaportuguesa.org/index.php
    ?action=lemma
    &lemma=<numeric-id>
```

### Parameters

| Parameter | Required | Value |
|-----------|----------|-------|
| `action`  | yes      | `lemma` — selects the VOP lemma resource |
| `lemma`   | yes      | numeric id from Endpoint 3, or from links elsewhere on the site |

The portal also accepts `id=<N>` as a synonym for `lemma=<N>` in some contexts,
but `lemma=` is the canonical form used by the search results.

### Response

An HTML page containing:

1. `<h1><word> - <grammatical class></h1>` — the headword and its class.
2. `<p title='Divisão silábica'>` — the syllabification with `·` middots and
   `<u><b>…</b></u>` stress marking (same format as the phonetics endpoint).
3. `<table id=classtable>` — an inflection or conjugation table:
   - **nouns and adjectives**: rows of `<th>label<td>value` (singular/plural,
     masculine/feminine);
   - **verbs**: a full conjugation table with `<th colspan=6>Indicativo` /
     `Conjuntivo / Subjuntivo` / `Imperativo` mood headers and six-column
     tense sub-headers.
4. `<p>Flexiona como : <a href='paradigm.php?paradigm=…'>word</a></p>` — the
   inflectional paradigm class.
5. `<p>` paragraphs with related-form links (`diminutivo`, `aumentativo`,
   `adjetivo PP de`, `forma nominal`, etc.), each an `action=lemma&lemma=<id>`
   anchor.

### Code reference

`pyportaldalingua.lexicon.parse_lemma_entry()` and `lemma_entry()` in
`pyportaldalingua/lexicon.py`.

---

## Endpoint 5 — Dicionário de Estrangeirismos

```
GET http://www.portaldalinguaportuguesa.org/index.php
    ?action=loanwords
    &act=list
    &search=<word>
```

### Response

An HTML table (`id=rollovertable`) with columns:

| Column | Title attribute |
|--------|-----------------|
| Palavra | `<a href='index.php?action=lemma&lemma=<id>'>` |
| Categoria gramatical | `title='Categoria gramatical'` |
| Língua de origem | `title='Língua de origem'` (anchor to a by-language listing) |
| Domínio | `title='Domínio'` |
| Adaptação | `title='Adaptação'` — recommended Portuguese adaptation |
| Equivalente | `title='Equivalente'` — Portuguese synonym |

The search matches by substring. Coverage is the dictionary's indexed headwords;
not all VOP entries have an Estrangeirismos record.

### Code reference

`pyportaldalingua.loanwords.parse_loanwords()` and `loanword_search()` in
`pyportaldalingua/loanwords.py`.

---

## Endpoint 6 — Dicionário de Gentílicos e Topónimos

```
GET http://www.portaldalinguaportuguesa.org/index.php
    ?action=toponyms
    &act=list
    &search=<toponym>
```

### Response

An HTML table (`id=rollovertable`) with columns:

| Column | Note |
|--------|------|
| Topónimo | The place name (empty on continuation rows for the same toponym) |
| Tipo | Place type: `cidade`, `país`, `distrito`, … (also empty on continuation rows) |
| Gentílico | An `<a href='?action=lemma&lemma=<id>'>word</a> - gclass` anchor |
| Parte de | Administrative parent, inner `<i>` text; last italic item is the country/region |

A single toponym with multiple demonym forms (e.g. *Lisboa* → *lisboano*,
*lisboeta*, *lisbonense*, *lisbonino*, *lisbonês*, *lisboês*, *olisiponense*,
*ulissiponense*) appears on multiple rows with the toponym and type fields empty
on all rows except the first.

The `<td>` cells are **not closed** with `</td>` — positional row parsing is
required; attribute-based closing detection is not reliable.

### Code reference

`pyportaldalingua.toponyms.parse_toponyms()`, `group_by_toponym()`, and
`toponym_search()` in `pyportaldalingua/toponyms.py`.

---

## Portal sections not covered

The following `action=` values were found in the site's main navigation but do
not expose a searchable API in any form that could be reliably parametrised:

| action | Description | Status |
|--------|-------------|--------|
| `acordo` / `novoacordo` | Static Acordo Ortográfico overview pages | Covered differently via the AO scraper (`orthography.py`) |
| `vop` | VOP front page | Covered via `simplesearch.php` (Endpoint 3) |
| `estrangeirismos` | Estrangeirismos front page | Covered via `action=loanwords` (Endpoint 5) |
| `gentilicos` | Gentílicos front page | Covered via `action=toponyms` (Endpoint 6) |
| `cruzadas` | Crossword-style look-up | HTML-only, no structured result table found |
| `mestre` | Unknown section | Returns the default portal shell with no content table |
| `lince` | Lince spell-checker resource | No search surface discoverable |

---

## Citation

If you publish work derived from these transcriptions, cite the portal's own
request:

> Ashby, S. et al. (2012). *A Rule Based Pronunciation Generator and Regional
> Accent Databank for Portuguese.* Proceedings of Interspeech 2012.
