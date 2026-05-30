"""Offline tests for loanwords.py — Dicionário de Estrangeirismos parsing."""
import os
import pytest

from pyportaldalingua.loanwords import parse_loanwords


@pytest.fixture
def loanwords_jazz_html():
    path = os.path.join(os.path.dirname(__file__), "fixtures", "loanwords_search_jazz.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestParseLoanwords:
    def test_returns_results(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        assert len(results) >= 2

    def test_jazz_present(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        words = [r.word for r in results]
        assert "jazz" in words

    def test_source_language_populated(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        for r in results:
            assert r.source_language, f"expected source_language for {r.word!r}"

    def test_jazz_source_is_english(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        jazz_entries = [r for r in results if r.word == "jazz"]
        assert jazz_entries
        assert all("inglês" in (r.source_language or "") for r in jazz_entries)

    def test_lemma_id_populated(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        for r in results:
            assert r.lemma_id and r.lemma_id.isdigit(), (
                f"expected numeric lemma_id for {r.word!r}, got {r.lemma_id!r}")

    def test_acid_jazz_domain(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        acid = [r for r in results if r.word == "acid-jazz"]
        assert acid
        assert acid[0].domain == "música"

    def test_to_dict_roundtrip(self, loanwords_jazz_html):
        results = parse_loanwords(loanwords_jazz_html)
        for r in results:
            d = r.to_dict()
            assert d["word"] == r.word
