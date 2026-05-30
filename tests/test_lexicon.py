"""Offline tests for lexicon.py — VOP search and lemma entry parsing."""
import pytest

from pyportaldalingua.lexicon import parse_vop_search, parse_lemma_entry


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def vop_contain_html(request):
    import os
    path = os.path.join(os.path.dirname(__file__), "fixtures", "vop_search_contain_casa.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def vop_start_html(request):
    import os
    path = os.path.join(os.path.dirname(__file__), "fixtures", "vop_search_start_casa.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def lemma_casa_html(request):
    import os
    path = os.path.join(os.path.dirname(__file__), "fixtures", "lemma_casa.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def lemma_acasalar_html(request):
    import os
    path = os.path.join(os.path.dirname(__file__), "fixtures", "lemma_acasalar.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ VOP search

class TestParseVopSearch:
    def test_returns_results(self, vop_contain_html):
        results = parse_vop_search(vop_contain_html)
        assert len(results) > 10

    def test_word_and_id_populated(self, vop_contain_html):
        results = parse_vop_search(vop_contain_html)
        for r in results:
            assert r.word
            assert r.lemma_id and r.lemma_id.isdigit()

    def test_acasalado_present(self, vop_contain_html):
        results = parse_vop_search(vop_contain_html)
        words = [r.word for r in results]
        assert "acasalado" in words

    def test_grammatical_class_populated(self, vop_contain_html):
        results = parse_vop_search(vop_contain_html)
        classes = {r.grammatical_class for r in results if r.grammatical_class}
        assert classes, "expected at least one grammatical class"

    def test_start_search_results_begin_with_query(self, vop_start_html):
        results = parse_vop_search(vop_start_html)
        assert results
        for r in results:
            assert r.word.lower().startswith("cas"), (
                f"start-search result {r.word!r} does not start with 'cas'")

    def test_casa_id_known(self, vop_start_html):
        results = parse_vop_search(vop_start_html)
        ids = {r.lemma_id for r in results if r.word.lower() == "casa"}
        assert "67444" in ids


# ------------------------------------------------------------------ lemma entry

class TestParseLemmaEntry:
    def test_noun_word_and_class(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        assert entry is not None
        assert entry.word == "casa"
        assert entry.grammatical_class == "nome feminino"

    def test_noun_syllabification(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        assert entry.syllabification == "ca.sa"
        assert entry.syllables == ["ca", "sa"]

    def test_noun_inflection(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        assert "singular" in entry.inflection
        assert entry.inflection["singular"] == "casa"
        assert "plural" in entry.inflection
        assert entry.inflection["plural"] == "casas"

    def test_noun_related_forms(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        assert "diminutivo" in entry.related
        dim_words = [w for w, _ in entry.related["diminutivo"]]
        assert "casinha" in dim_words

    def test_noun_paradigm(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        assert entry.paradigm == "casa"

    def test_verb_word_and_class(self, lemma_acasalar_html):
        entry = parse_lemma_entry(lemma_acasalar_html)
        assert entry is not None
        assert entry.word == "acasalar"
        assert entry.grammatical_class == "verbo"

    def test_verb_paradigm(self, lemma_acasalar_html):
        entry = parse_lemma_entry(lemma_acasalar_html)
        assert entry.paradigm == "amar"

    def test_verb_related_pp(self, lemma_acasalar_html):
        entry = parse_lemma_entry(lemma_acasalar_html)
        # "adjetivo PP" link to acasalado
        pp_words = []
        for label, links in entry.related.items():
            if "PP" in label or "pp" in label.lower():
                pp_words.extend(w for w, _ in links)
        assert "acasalado" in pp_words

    def test_to_dict_roundtrip(self, lemma_casa_html):
        entry = parse_lemma_entry(lemma_casa_html)
        d = entry.to_dict()
        assert d["word"] == "casa"
        assert "inflection" in d
        assert "related" in d
