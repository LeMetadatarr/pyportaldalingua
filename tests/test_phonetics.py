from pyportaldalingua.phonetics import parse_detail, parse_search


def test_parse_search_extracts_lemma(fonetica_search_html):
    lemmas = parse_search(fonetica_search_html)
    assert lemmas
    first = lemmas[0]
    assert first.word == "acasalado"
    assert first.ipa == "ɐ.kɐ.zɐ.lˈa.du"
    assert first.syllabification == "a.ca.sa.la.do"
    assert first.grammatical_class == "adjetivo"
    assert first.detail_id == "32032"


def test_parse_search_ipa_has_no_markup(fonetica_search_html):
    # the portal serves a malformed anchor; the IPA must not leak href text
    for lm in parse_search(fonetica_search_html):
        assert lm.ipa is None or "action=" not in lm.ipa
        assert lm.ipa is None or "<" not in lm.ipa


def test_parse_search_word_has_no_syllable_dots(fonetica_search_html):
    for lm in parse_search(fonetica_search_html):
        assert "·" not in lm.word
        assert " " not in lm.word


def test_lemma_url_built_from_detail_id(fonetica_search_html):
    first = parse_search(fonetica_search_html)[0]
    assert first.url is not None
    assert "act=details" in first.url
    assert "id=32032" in first.url


def test_parse_detail_all_regions(fonetica_detail_html):
    lm = parse_detail(fonetica_detail_html)
    assert lm is not None
    assert lm.word == "acasalado"
    assert lm.grammatical_class == "adjetivo"
    assert len(lm.ipa_by_region) == 9
    assert lm.ipa_by_region["Lisboa (padrão)"] == "ɐ.kɐ.zɐ.lˈa.du"
    assert lm.ipa_by_region["Rio de Janeiro (padrão)"] == "a.ka.za.lˈa.dʊ"
    # standard accent is surfaced as the headline ipa
    assert lm.ipa == lm.ipa_by_region["Lisboa (padrão)"]


def test_syllables_accessor(fonetica_search_html):
    first = parse_search(fonetica_search_html)[0]
    assert first.syllables == ["a", "ca", "sa", "la", "do"]
