"""Live smoke test — hits the real Portal da Língua Portuguesa.

Run explicitly with ``pytest -m live``; skipped by default selections that
exclude the ``live`` marker.
"""
import pytest

import pyportaldalingua as pdl

pytestmark = pytest.mark.live


def test_live_phonetics():
    ipa = pdl.phonetics("palavra")
    assert ipa, "expected an IPA transcription for 'palavra'"
    assert "<" not in ipa and "action=" not in ipa


def test_live_phonetics_detail_regions():
    lm = pdl.phonetics_detail("palavra")
    assert lm is not None
    assert lm.word == "palavra"
    # the portal transcribes 10 regions per lemma (see models.REGIONS);
    # Díli is the last row in the table and must be included.
    assert len(lm.ipa_by_region) == 10
    assert "Lisboa (padrão)" in lm.ipa_by_region
    assert "Díli" in lm.ipa_by_region


def test_live_scrape_letter_ao():
    changes = pdl.scrape_letter("a", "pt_PT")
    assert changes
    assert all(c.old and c.new for c in changes)
    assert all(c.variant == "pt_PT" for c in changes)


def test_live_vop_search_contain():
    results = pdl.vop_search("casament")
    assert results
    words = [r.word for r in results]
    assert any("casament" in w for w in words)


def test_live_vop_search_exact():
    results = pdl.vop_search("casa", mode="exact")
    assert results
    assert any(r.word == "casa" for r in results)


def test_live_vop_search_start():
    results = pdl.vop_search("casa", mode="start")
    assert results
    for r in results:
        assert r.word.lower().startswith("cas")


def test_live_lemma_entry_noun():
    entry = pdl.lemma_entry("67444")  # casa
    assert entry is not None
    assert entry.word == "casa"
    assert entry.inflection.get("singular") == "casa"
    assert entry.inflection.get("plural") == "casas"


def test_live_lemma_entry_verb():
    entry = pdl.lemma_entry("53815")  # acasalar
    assert entry is not None
    assert entry.word == "acasalar"
    assert entry.grammatical_class == "verbo"
    assert entry.paradigm is not None


def test_live_loanword_search():
    results = pdl.loanword_search("jazz")
    assert results
    words = [r.word for r in results]
    assert "jazz" in words
    assert all(r.source_language for r in results)


def test_live_toponym_search():
    results = pdl.toponym_search("porto")
    assert results
    toponyms = [g.toponym for g in results]
    assert any("Porto" in t for t in toponyms)
    all_demonyms = [d.demonym for g in results for d in g.demonyms]
    assert "portuense" in all_demonyms
