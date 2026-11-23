"""Testes sintéticos de scripts/count_anomalies_train.py (dados inventados, sem ler data/)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "count_anomalies_train", ROOT / "scripts" / "count_anomalies_train.py"
)
cat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cat)


def frame(rows):
    """rows: (id, speed_mps, signed_turn_deg). Primeiro ponto de cada viagem com NaN."""
    return pd.DataFrame(rows, columns=["id", "speed_calc_mps", "signed_turn_calc_deg"])


def test_salto_conta_acima_do_limiar_em_nos():
    # 30 nós = 15.4322 m/s. Um passo a 20 m/s (38.9 nós) é salto; a 10 m/s não é.
    data = frame([
        ("A", np.nan, np.nan),
        ("A", 20.0, 0.0),
        ("A", 10.0, 0.0),
    ])
    out = cat.count_per_trip(data, threshold_kn=30.0).set_index("id")
    assert out.loc["A", "saltos"] == 1
    assert out.loc["A", "pares_velocidade"] == 2


def test_inversao_acima_de_170_graus_em_valor_absoluto():
    data = frame([
        ("A", np.nan, np.nan),
        ("A", 1.0, 175.0),    # inversão positiva
        ("A", 1.0, -175.0),   # inversão negativa
        ("A", 1.0, 169.0),    # não é inversão
    ])
    out = cat.count_per_trip(data, threshold_kn=30.0).set_index("id")
    assert out.loc["A", "inversoes"] == 2
    assert out.loc["A", "pares_rumo"] == 3


def test_nan_nao_conta():
    data = frame([("A", np.nan, np.nan), ("A", np.nan, np.nan)])
    out = cat.count_per_trip(data, threshold_kn=30.0).set_index("id")
    assert out.loc["A", "saltos"] == 0
    assert out.loc["A", "inversoes"] == 0
    assert out.loc["A", "pares_velocidade"] == 0


def test_contagem_separada_por_viagem():
    data = frame([
        ("A", np.nan, np.nan), ("A", 50.0, 0.0),
        ("B", np.nan, np.nan), ("B", 1.0, 180.0),
    ])
    out = cat.count_per_trip(data, threshold_kn=30.0).set_index("id")
    assert out.loc["A", "saltos"] == 1 and out.loc["B", "saltos"] == 0
    assert out.loc["A", "inversoes"] == 0 and out.loc["B", "inversoes"] == 1


def test_resumo_media_e_mediana():
    per_trip = pd.DataFrame({
        "id": ["A", "B", "C"],
        "pares_velocidade": [10, 10, 10],
        "pares_rumo": [10, 10, 10],
        "saltos": [0, 0, 3],
        "inversoes": [1, 2, 9],
    })
    stats = cat.summary(per_trip, threshold_kn=30.0)
    assert stats["inversoes_por_viagem"]["media"] == pytest.approx(4.0)
    assert stats["inversoes_por_viagem"]["mediana"] == pytest.approx(2.0)
    assert stats["saltos_por_viagem"]["viagens_com_pelo_menos_1"] == 1
