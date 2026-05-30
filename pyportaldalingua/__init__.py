"""pyportaldalingua — typed Python client for the Portal da Língua Portuguesa.

The **Portal da Língua Portuguesa** (``portaldalinguaportuguesa.org``) is an
ILTEC repository of Portuguese language resources. This client covers:

- the **Dicionário Fonético** — per-lemma **IPA / AFI** transcription in several
  regional accents (Lisboa, Luanda, Rio de Janeiro, São Paulo, Maputo, Díli);
- the **Acordo Ortográfico de 1990** change lists (pt_PT / pt_BR), plus the
  bundled word-lists in ``data/``;
- the **Vocabulário Ortográfico do Português (VOP)** — fuzzy/partial headword
  search (exact, prefix, suffix, substring) and per-lemma lexicon entries with
  inflection tables and related-form links;
- the **Dicionário de Estrangeirismos** — foreign-origin words with source
  language, domain, adaptation, and equivalent;
- the **Dicionário de Gentílicos e Topónimos** — place-names mapped to their
  Portuguese demonyms.

Quick start::

    import pyportaldalingua as pdl

    # IPA / AFI for a Portuguese word (Lisboa padrão)
    pdl.phonetics("acasalado")            # 'ɐ.kɐ.zɐ.lˈa.du'

    # the full lemma in every transcribed region
    lm = pdl.phonetics_detail("acasalado")
    print(lm.ipa_by_region["Rio de Janeiro (padrão)"])

    # fuzzy / partial headword resolution (VOP vocabulary)
    for r in pdl.vop_search("casament"):
        print(r.word, r.grammatical_class, r.lemma_id)

    # VOP lexicon entry (inflection, related forms)
    entry = pdl.lemma_entry("67444")  # casa
    print(entry.inflection)           # {'singular': 'casa', 'plural': 'casas'}

    # Dicionário de Estrangeirismos
    for e in pdl.loanword_search("jazz"):
        print(e.word, e.source_language)

    # Dicionário de Gentílicos e Topónimos
    for g in pdl.toponym_search("lisboa"):
        print(g.toponym, [d.demonym for d in g.demonyms])

    # Acordo Ortográfico spelling changes
    for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
        print(ch.old, "->", ch.new)

Build Hugging-Face-shaped corpora with :mod:`pyportaldalingua.dataset` (configs
``ipa`` and ``acordo``).
"""
from pyportaldalingua.models import AOChange, Lemma, REGIONS
from pyportaldalingua.transport import Transport
from pyportaldalingua.phonetics import (
    lemmas,
    parse_detail,
    parse_search,
    phonetics,
    phonetics_detail,
)
from pyportaldalingua.orthography import (
    load_changes_csv,
    load_wordlists,
    parse_changes,
    scrape_letter,
    scrape_variant,
    wordlist_names,
)
from pyportaldalingua.lexicon import (
    VopResult,
    LemmaEntry,
    parse_vop_search,
    parse_lemma_entry,
    vop_search,
    lemma_entry,
)
from pyportaldalingua.loanwords import (
    LoanwordEntry,
    parse_loanwords,
    loanword_search,
)
from pyportaldalingua.toponyms import (
    GentilicoEntry,
    ToponymResult,
    parse_toponyms,
    group_by_toponym,
    toponym_search,
)
from pyportaldalingua.client import PortalDaLingua
from pyportaldalingua.ids import id_from_url, lemma_id, lemma_to_extra
from pyportaldalingua.version import __version__

__all__ = [
    # models
    "Lemma",
    "AOChange",
    "REGIONS",
    "VopResult",
    "LemmaEntry",
    "LoanwordEntry",
    "GentilicoEntry",
    "ToponymResult",
    # transport
    "Transport",
    # client
    "PortalDaLingua",
    # phonetics
    "phonetics",
    "phonetics_detail",
    "lemmas",
    "parse_search",
    "parse_detail",
    # orthography
    "scrape_letter",
    "scrape_variant",
    "parse_changes",
    "load_changes_csv",
    "load_wordlists",
    "wordlist_names",
    # lexicon / VOP
    "vop_search",
    "lemma_entry",
    "parse_vop_search",
    "parse_lemma_entry",
    # loanwords
    "loanword_search",
    "parse_loanwords",
    # toponyms
    "toponym_search",
    "parse_toponyms",
    "group_by_toponym",
    # ids
    "lemma_id",
    "id_from_url",
    "lemma_to_extra",
    "__version__",
]
