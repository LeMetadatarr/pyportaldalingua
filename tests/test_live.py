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
    assert len(lm.ipa_by_region) >= 5
    assert "Lisboa (padrão)" in lm.ipa_by_region


def test_live_scrape_letter_ao():
    changes = pdl.scrape_letter("a", "pt_PT")
    assert changes
    assert all(c.old and c.new for c in changes)
    assert all(c.variant == "pt_PT" for c in changes)
