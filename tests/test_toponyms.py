"""Offline tests for toponyms.py — Dicionário de Gentílicos e Topónimos parsing."""
import os
import pytest

from pyportaldalingua.toponyms import parse_toponyms, group_by_toponym


@pytest.fixture
def toponyms_lisboa_html():
    path = os.path.join(os.path.dirname(__file__), "fixtures", "toponyms_search_lisboa.html")
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestParseToponyms:
    def test_returns_entries(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        assert len(entries) >= 6

    def test_toponym_populated(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        for e in entries:
            assert e.toponym

    def test_lisboa_place_type(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        lisboa_entries = [e for e in entries if "Lisboa" in e.toponym]
        assert lisboa_entries
        types = {e.place_type for e in lisboa_entries if e.place_type}
        assert "cidade" in types

    def test_demonyms_populated(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        demonyms = {e.demonym for e in entries}
        assert "lisboano" in demonyms
        assert "lisboeta" in demonyms

    def test_grammatical_class_populated(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        classes = {e.grammatical_class for e in entries if e.grammatical_class}
        assert "adjetivo" in classes
        assert "nome" in classes

    def test_lemma_id_populated(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        for e in entries:
            assert e.lemma_id and e.lemma_id.isdigit(), (
                f"expected numeric lemma_id for demonym {e.demonym!r}")

    def test_part_of_populated(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        parts = {e.part_of for e in entries if e.part_of}
        assert parts

    def test_to_dict_roundtrip(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        for e in entries:
            d = e.to_dict()
            assert d["toponym"]


class TestGroupByToponym:
    def test_grouped_count(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        grouped = group_by_toponym(entries)
        # Lisboa appears once as a group
        names = [g.toponym for g in grouped]
        assert "Lisboa" in names

    def test_grouped_demonyms(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        grouped = group_by_toponym(entries)
        lisboa = next(g for g in grouped if g.toponym == "Lisboa")
        dem_words = [d.demonym for d in lisboa.demonyms]
        assert "lisboano" in dem_words
        assert "lisboeta" in dem_words

    def test_to_dict_roundtrip(self, toponyms_lisboa_html):
        entries = parse_toponyms(toponyms_lisboa_html)
        grouped = group_by_toponym(entries)
        for g in grouped:
            d = g.to_dict()
            assert d["toponym"]
            assert "demonyms" in d
