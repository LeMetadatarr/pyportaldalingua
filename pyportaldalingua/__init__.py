"""pyportaldalingua — typed Python client for the Portal da Língua Portuguesa.

The **Portal da Língua Portuguesa** (``portaldalinguaportuguesa.org``) is an
ILTEC repository of Portuguese language resources. This client reads two of them
into typed dataclasses:

- the **Dicionário Fonético** — per-lemma **IPA / AFI** transcription in several
  regional accents (Lisboa, Luanda, Rio de Janeiro, São Paulo, Maputo, Díli):
  the Portuguese IPA pronunciation source;
- the **Acordo Ortográfico de 1990** change lists (pt_PT / pt_BR), plus the
  bundled word-lists shipped in ``data/``.

Quick start::

    import pyportaldalingua as pdl

    # IPA / AFI for a Portuguese word (Lisboa padrão)
    pdl.phonetics("acasalado")            # 'ɐ.kɐ.zɐ.lˈa.du'

    # the full lemma in every transcribed region
    lm = pdl.phonetics_detail("acasalado")
    print(lm.ipa_by_region["Rio de Janeiro (padrão)"])
    print(lm.syllabification, lm.grammatical_class)

    # Acordo Ortográfico spelling changes
    for ch in pdl.scrape_letter("a", "pt_PT")[:3]:
        print(ch.old, "->", ch.new)

    # the bundled corpora (offline)
    pt = pdl.load_changes_csv("pt_PT")
    words = list(pdl.load_wordlists("ao"))

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
from pyportaldalingua.client import PortalDaLingua
from pyportaldalingua.ids import id_from_url, lemma_id, lemma_to_extra
from pyportaldalingua.version import __version__

__all__ = [
    "Lemma",
    "AOChange",
    "REGIONS",
    "Transport",
    "PortalDaLingua",
    "phonetics",
    "phonetics_detail",
    "lemmas",
    "parse_search",
    "parse_detail",
    "scrape_letter",
    "scrape_variant",
    "parse_changes",
    "load_changes_csv",
    "load_wordlists",
    "wordlist_names",
    "lemma_id",
    "id_from_url",
    "lemma_to_extra",
    "__version__",
]
