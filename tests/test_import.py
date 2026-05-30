def test_public_api():
    import pyportaldalingua as pdl

    for name in (
        "Lemma", "AOChange", "REGIONS", "Transport", "PortalDaLingua",
        "phonetics", "phonetics_detail", "lemmas", "parse_search", "parse_detail",
        "scrape_letter", "scrape_variant", "parse_changes",
        "load_changes_csv", "load_wordlists", "wordlist_names",
        "lemma_id", "id_from_url", "lemma_to_extra", "__version__",
    ):
        assert hasattr(pdl, name), name
        assert name in pdl.__all__


def test_version():
    import pyportaldalingua

    assert pyportaldalingua.__version__ == "0.0.1a1"
