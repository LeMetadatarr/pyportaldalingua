import json

import pytest

from pyportaldalingua import dataset
from pyportaldalingua.orthography import load_changes_csv
from pyportaldalingua.phonetics import parse_detail, parse_search


def test_ipa_row_from_lemma(fonetica_search_html):
    lm = parse_search(fonetica_search_html)[0]
    row = dataset.ipa_row(lm)
    assert row["word"] == "acasalado"
    assert row["ipa"] == "ɐ.kɐ.zɐ.lˈa.du"
    assert row["syllables"] == ["a", "ca", "sa", "la", "do"]
    assert row["source"] == "portaldalinguaportuguesa.org"


def test_ipa_row_none_without_ipa():
    from pyportaldalingua.models import Lemma
    assert dataset.ipa_row(Lemma(word="x")) is None


def test_acordo_row():
    ch = load_changes_csv("pt_BR")[0]
    row = dataset.acordo_row(ch)
    assert set(row) == {"old", "new", "variant", "note", "source"}
    assert row["variant"] == "pt_BR"


def test_export_jsonl_ipa(tmp_path, fonetica_detail_html):
    lm = parse_detail(fonetica_detail_html)
    path = tmp_path / "ipa.jsonl"
    n = dataset.export_jsonl([lm], str(path), "ipa")
    assert n == 1
    row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert row["word"] == "acasalado"
    assert row["ipa"]


def test_export_all_both_configs(tmp_path, fonetica_search_html):
    lemmas = parse_search(fonetica_search_html)
    changes = load_changes_csv("pt_PT")[:10]
    counts = dataset.export_all(lemmas, changes, str(tmp_path))
    assert set(counts) == {"ipa", "acordo"}
    assert counts["acordo"] == 10
    assert counts["ipa"] > 0
    assert (tmp_path / "ipa.jsonl").exists()
    assert (tmp_path / "acordo.jsonl").exists()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["configs"] == counts


def test_export_jsonl_rejects_unknown_config(tmp_path):
    with pytest.raises(ValueError):
        dataset.export_jsonl([], str(tmp_path / "x"), "bogus")
