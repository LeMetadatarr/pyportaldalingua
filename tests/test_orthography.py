import itertools

import pytest

from pyportaldalingua import orthography
from pyportaldalingua.orthography import (
    load_changes_csv,
    load_wordlists,
    parse_changes,
    wordlist_names,
)


def test_parse_changes_from_fixture(ao_list_html):
    changes = parse_changes(ao_list_html, "pt_PT")
    assert len(changes) > 100
    first = changes[0]
    assert first.old == "ab-reacção"
    assert first.new == "ab-reação"
    assert first.variant == "pt_PT"


def test_parse_changes_no_markup(ao_list_html):
    for ch in parse_changes(ao_list_html, "pt_PT"):
        assert "<" not in ch.old and "<" not in ch.new
        assert ch.old and ch.new


def test_load_changes_csv_both_variants():
    pt = load_changes_csv("pt_PT")
    br = load_changes_csv("pt_BR")
    assert len(pt) > 1000
    assert len(br) > 1000
    assert all(c.variant == "pt_PT" for c in pt)
    assert all(c.variant == "pt_BR" for c in br)
    assert pt[0].old and pt[0].new


def test_load_wordlists_stream():
    words = list(itertools.islice(load_wordlists("ao"), 5))
    assert len(words) == 5
    assert all(isinstance(w, str) and w for w in words)


def test_load_wordlists_variants_exist():
    names = wordlist_names()
    assert set(names) == {"ao", "preao", "big"}
    for key in names:
        first = next(load_wordlists(key))
        assert isinstance(first, str) and first


def test_load_wordlists_rejects_unknown():
    with pytest.raises(ValueError):
        next(load_wordlists("bogus"))


def test_scrape_letter_rejects_bad_variant():
    with pytest.raises(ValueError):
        orthography._version("pt_XX")
