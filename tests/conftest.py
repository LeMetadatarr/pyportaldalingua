import os

import pytest

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live: hits the live Portal da Língua Portuguesa (network required)")


def _read(name: str) -> str:
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture
def ao_list_html() -> str:
    """Acordo Ortográfico list page for letter 'a', pt_PT (pe)."""
    return _read("ao_list_a_pe.html")


@pytest.fixture
def fonetica_search_html() -> str:
    """Dicionário Fonético search-list page for 'casa'."""
    return _read("fonetica_search_casa.html")


@pytest.fixture
def fonetica_detail_html() -> str:
    """Dicionário Fonético detail page for the lemma 'acasalado'."""
    return _read("fonetica_details_acasalado.html")
