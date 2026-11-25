"""Macros da análise dos blocos de erro (ais.cli.build_window_analysis_macros), só com dados sintéticos."""
import re

import pytest

from ais.cli.build_window_analysis_macros import check_logged, latex_macros


def _summary(split: str, nav_min: int, fish_min: int) -> dict:
    return {
        "split": split, "fonte_sha256": "abc", "criado_utc": "2000-01-01T00:00:00+00:00",
        "todos": {"n_blocos": 10, "n_pontos": 2000, "media": 14.75, "mediana": 5.0, "p90": 37.4, "maximo": 1286},
        "navegacao_prevista_no_meio_de_pesca": {"n_blocos": 7, "n_pontos": 1500},
        "pesca_prevista_no_meio_de_navegacao": {"n_blocos": 3, "n_pontos": 500},
        "segmentos_reais_navegacao": {"minimo": nav_min},
        "segmentos_reais_pesca": {"minimo": fish_min},
        "janelas_candidatas": [{"janela": 21, "remove_pesca_isolada_ate": 6, "remove_navegacao_isolada_ate": 2,
                                "perc_buracos_cobertos": 0.904, "perc_pontos_de_erro_cobertos": 0.5901}],
    }


def _values(tex: str) -> dict:
    return dict(re.findall(r"\\newcommand\{\\res(\w+)\}\{(.*)\}", tex))


def test_macros_take_each_value_from_its_source():
    v = _values(latex_macros(_summary("test", 127, 633), _summary("train", 102, 1584), 21))
    assert v["BuTesteBlocos"] == "10"
    assert v["BuTesteErros"] == "2\\,000"
    assert v["BuTesteNoventa"] == "37"
    assert v["BuTesteNavPercPontos"] == "75\\,\\%"
    assert (v["BuTesteRealNavMin"], v["BuTreinoRealNavMin"]) == ("127", "102")
    assert (v["BuTesteRealPescaMin"], v["BuTreinoRealPescaMin"]) == ("633", "1\\,584")
    assert (v["BuRemovePesca"], v["BuRemoveNav"]) == ("6", "2")
    assert (v["BuTesteBlocosCobertos"], v["BuTestePontosCobertos"]) == ("90\\,\\%", "59\\,\\%")


def test_macro_names_have_no_digits():
    v = _values(latex_macros(_summary("test", 1, 1), _summary("train", 1, 1), 21))
    assert v and all(name.isalpha() for name in v)


def test_unknown_window_size_is_rejected():
    with pytest.raises(ValueError):
        latex_macros(_summary("test", 1, 1), _summary("train", 1, 1), 999)


def test_requires_a_logged_read_of_the_same_file():
    t = _summary("test", 1, 1)
    check_logged(t, [{"event": "postproc_window_analysis", "file_sha256": "abc"}])
    with pytest.raises(PermissionError):
        check_logged(t, [{"event": "postproc_window_analysis", "file_sha256": "outro"}])
    with pytest.raises(ValueError):
        check_logged(_summary("train", 1, 1), [])
