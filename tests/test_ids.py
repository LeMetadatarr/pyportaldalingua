from pyportaldalingua.ids import id_from_url, lemma_id, lemma_to_extra
from pyportaldalingua.models import Lemma


def test_lemma_id_is_word():
    assert lemma_id(" casa ") == "casa"


def test_id_from_url():
    url = ("http://www.portaldalinguaportuguesa.org/index.php"
           "?action=fonetica&region=lbx&act=details&id=32032")
    assert id_from_url(url) == "32032"


def test_id_from_url_none():
    assert id_from_url("http://example.com/foo") is None


def test_lemma_to_extra_namespaced():
    lm = Lemma(word="acasalado", ipa="ɐ.kɐ.zɐ.lˈa.du",
               syllabification="a.ca.sa.la.do", grammatical_class="adjetivo",
               detail_id="32032")
    extra = lemma_to_extra(lm)
    assert extra["portaldalingua_word"] == "acasalado"
    assert extra["portaldalingua_id"] == "32032"
    assert extra["portaldalingua_ipa"] == "ɐ.kɐ.zɐ.lˈa.du"
    assert extra["portaldalingua_syllables"] == "a.ca.sa.la.do"
    assert extra["portaldalingua_class"] == "adjetivo"
    assert "act=details" in extra["portaldalingua_url"]
    assert all(k.startswith("portaldalingua_") for k in extra)


def test_lemma_to_extra_minimal():
    extra = lemma_to_extra(Lemma(word="casa"))
    assert extra == {"portaldalingua_word": "casa"}
