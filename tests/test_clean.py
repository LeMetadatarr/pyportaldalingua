from pyportaldalingua._clean import clean, clean_or_none, normalize, strip_tags, syllabify


def test_strip_tags_unescapes():
    assert strip_tags("<b>a&middot;b</b>") == "a·b"


def test_normalize_collapses_whitespace():
    assert normalize("  a\n\t b  ") == "a b"


def test_clean():
    assert clean("<td> <p> acto </p>") == "acto"


def test_clean_or_none_empty():
    assert clean_or_none("<td></td>") is None


def test_syllabify_maps_middots():
    cell = "<a href='x'>a<b>&middot;</b>ca<b>&middot;</b><u><b>sa</b></u></a>"
    assert syllabify(cell) == "a.ca.sa"


def test_syllabify_none_without_breaks():
    assert syllabify("<a>casa</a>") is None
