"""Testes sintéticos da função de construção de scripts/build_clean_dataset.py.

Os dados são inventados e pequenos, com valores conhecidos à partida. Não leem
data/ nem o manifesto, por isso não tocam em validação nem em teste.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m pytest tests/
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "build_clean_dataset", ROOT / "scripts" / "build_clean_dataset.py"
)
bcd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bcd)


def make_frame(rows: list[tuple]) -> pd.DataFrame:
    """rows: (id, t_segundos, x, y, label). Ordenado por id e t, como no script."""
    frame = pd.DataFrame(rows, columns=["id", "t_s", "x", "y", "label"])
    frame["t"] = pd.Timestamp("2020-01-01") + pd.to_timedelta(frame["t_s"], unit="s")
    frame["point_id"] = np.arange(1, len(frame) + 1)
    frame["distanceToShore"] = 1000.0
    return frame.drop(columns=["t_s"]).sort_values(["id", "t", "point_id"]).reset_index(drop=True)


def run(rows: list[tuple]) -> pd.DataFrame:
    return bcd.build(make_frame(rows), "train")


def test_parado_tem_distancia_zero_e_velocidade_zero():
    out = run([("A", 0, 0, 0, "02-fishing"), ("A", 10, 0, 0, "02-fishing")])
    assert out.loc[1, "distance_gap_calc_m"] == pytest.approx(0.0)
    assert out.loc[1, "speed_calc_mps"] == pytest.approx(0.0)


def test_linha_reta_a_norte_distancia_tempo_velocidade_e_rumo():
    out = run([
        ("A", 0, 0, 0, "02-fishing"),
        ("A", 10, 0, 100, "02-fishing"),
        ("A", 20, 0, 200, "02-fishing"),
    ])
    assert out.loc[1, "distance_gap_calc_m"] == pytest.approx(100.0)
    assert out.loc[1, "time_gap_calc_s"] == pytest.approx(10.0)
    assert out.loc[1, "speed_calc_mps"] == pytest.approx(10.0)
    assert out.loc[1, "bearing_calc_deg"] == pytest.approx(0.0)
    assert out.loc[2, "bearing_calc_deg"] == pytest.approx(0.0)


def test_direcao_leste_tem_rumo_90():
    out = run([("A", 0, 0, 0, "02-fishing"), ("A", 10, 100, 0, "02-fishing")])
    assert out.loc[1, "bearing_calc_deg"] == pytest.approx(90.0)


def test_curva_para_leste_e_positiva_no_sentido_do_relogio():
    # norte (0 graus) e depois leste (90 graus): variação de +90
    out = run([
        ("A", 0, 0, 0, "02-fishing"),
        ("A", 10, 0, 100, "02-fishing"),
        ("A", 20, 100, 100, "02-fishing"),
    ])
    assert out.loc[2, "signed_turn_calc_deg"] == pytest.approx(90.0)


def test_rotacao_pelo_zero_usa_o_caminho_curto():
    # passo 1 com rumo 350; passo 2 com rumo 10: variação +20, não -340
    out = run([
        ("A", 0, 0.0, 0.0, "02-fishing"),
        ("A", 10, -17.36481777, 98.48077530, "02-fishing"),   # rumo 350
        ("A", 20, 0.0, 196.96155060, "02-fishing"),           # rumo 10
    ])
    assert out.loc[2, "signed_turn_calc_deg"] == pytest.approx(20.0, abs=1e-6)


def test_primeiro_ponto_de_cada_viagem_fica_sem_anterior():
    out = run([
        ("A", 0, 0, 0, "02-fishing"), ("A", 10, 0, 100, "02-fishing"),
        ("B", 0, 500, 500, "01-sailing"), ("B", 10, 500, 600, "01-sailing"),
    ])
    assert out["time_gap_calc_s"].isna().sum() == 2
    assert out.loc[out["id"] == "B", "time_gap_calc_s"].isna().sum() == 1


def test_viagens_nao_se_misturam():
    # o primeiro ponto de B não pode usar a posição final de A
    out = run([
        ("A", 0, 0, 0, "02-fishing"), ("A", 10, 0, 1000, "02-fishing"),
        ("B", 0, 5, 5, "01-sailing"),
    ])
    assert out.loc[2, "id"] == "B"
    assert pd.isna(out.loc[2, "distance_gap_calc_m"])


def test_target_pesca_1_navegacao_0():
    out = run([
        ("A", 0, 0, 0, "02-fishing"), ("A", 10, 0, 1, "04-fishing"),
        ("A", 20, 0, 2, "01-sailing"), ("A", 30, 0, 3, "03-sailing"),
        ("A", 40, 0, 4, "05-sailing"),
    ])
    assert out["target"].tolist() == [1, 1, 0, 0, 0]


def test_rotulo_desconhecido_gera_erro():
    with pytest.raises(ValueError):
        run([("A", 0, 0, 0, "99-desconhecido")])


def test_wrap_180_normaliza_para_intervalo():
    angles = pd.Series([190.0, -190.0, 180.0, 0.0, 359.0])
    result = bcd.wrap_180(angles).tolist()
    assert result == pytest.approx([-170.0, 170.0, 180.0, 0.0, -1.0])
