"""Testes sintéticos de ais.cli.count_shared_vessels (sem dados reais)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from ais.cli.count_shared_vessels import build_summary, count_shared_vessels, vessel_of


def _manifest(rows: list[tuple[str, str]]) -> pd.DataFrame:
    """Constrói um manifesto sintético a partir de pares (id, split)."""
    return pd.DataFrame(rows, columns=["id", "split"])


# Manifesto inventado com contagens conhecidas à mão.
# Navio 100: viagens em train, validation e test.
# Navio 200: só validation.
# Navio 300: só test.
# Navio 400: train e test.
# Navio 500-1 (ids com hífen duplo): validation e test.
# Navio 500-2: só train.
SYNTHETIC_ROWS = [
    ("100-1", "train"),
    ("400-1", "train"),
    ("500-2-1", "train"),
    ("100-2", "validation"),
    ("200-1", "validation"),
    ("200-2", "validation"),
    ("500-1-8", "validation"),
    ("100-3", "test"),
    ("300-1", "test"),
    ("400-2", "test"),
    ("500-1-7", "test"),
]


@pytest.mark.parametrize(
    ("trip_id", "expected"),
    [
        ("211477000-2", "211477000"),
        ("500-1-7", "500-1"),
        ("a-b-c-9", "a-b-c"),
        ("123", "123"),
        ("  42-3 ", "42"),
    ],
)
def test_vessel_of_splits_at_last_hyphen(trip_id: str, expected: str) -> None:
    assert vessel_of(trip_id) == expected


def test_counts_on_synthetic_manifest() -> None:
    result = count_shared_vessels(_manifest(SYNTHETIC_ROWS))

    val = result["conjuntos"]["validation"]
    # Validação: 4 viagens, navios {100, 200, 500-1}; só 100-2 tem navio no treino.
    assert val["viagens"] == 4
    assert val["navios_distintos"] == 3
    assert val["viagens_com_navio_no_treino"] == 1
    assert val["fracao_viagens_com_navio_no_treino"] == pytest.approx(0.25)

    test = result["conjuntos"]["test"]
    # Teste: 4 viagens, navios {100, 300, 400, 500-1}; 100-3 e 400-2 têm navio no treino.
    assert test["viagens"] == 4
    assert test["navios_distintos"] == 4
    assert test["viagens_com_navio_no_treino"] == 2
    assert test["fracao_viagens_com_navio_no_treino"] == pytest.approx(0.5)

    pair = result["validation_vs_test"]
    # Navios partilhados entre validação e teste: {100, 500-1}.
    assert pair["navios_partilhados"] == 2
    # Validação: 100-2 e 500-1-8 têm navio no teste.
    assert pair["viagens_validation_com_navio_no_test"] == 2
    assert pair["fracao_viagens_validation_com_navio_no_test"] == pytest.approx(0.5)
    # Teste: 100-3 e 500-1-7 têm navio na validação.
    assert pair["viagens_test_com_navio_na_validation"] == 2
    assert pair["fracao_viagens_test_com_navio_na_validation"] == pytest.approx(0.5)


def test_vessel_only_in_test_is_not_counted_as_shared_with_train() -> None:
    rows = [("1-1", "train"), ("2-1", "validation"), ("3-1", "test")]
    result = count_shared_vessels(_manifest(rows))
    assert result["conjuntos"]["test"]["viagens_com_navio_no_treino"] == 0
    assert result["conjuntos"]["test"]["fracao_viagens_com_navio_no_treino"] == 0.0
    assert result["validation_vs_test"]["navios_partilhados"] == 0


def test_empty_test_set_gives_none_fractions() -> None:
    rows = [("1-1", "train"), ("2-1", "validation"), ("2-2", "validation")]
    result = count_shared_vessels(_manifest(rows))

    test = result["conjuntos"]["test"]
    assert test["viagens"] == 0
    assert test["navios_distintos"] == 0
    assert test["fracao_viagens_com_navio_no_treino"] is None

    pair = result["validation_vs_test"]
    assert pair["fracao_viagens_test_com_navio_na_validation"] is None
    # Validação não vazia sem navios no teste: fração 0.0, não None.
    assert pair["fracao_viagens_validation_com_navio_no_test"] == 0.0


def test_empty_validation_set_gives_none_fractions() -> None:
    rows = [("1-1", "train"), ("1-2", "test")]
    result = count_shared_vessels(_manifest(rows))
    val = result["conjuntos"]["validation"]
    assert val["viagens"] == 0
    assert val["fracao_viagens_com_navio_no_treino"] is None
    assert result["validation_vs_test"]["fracao_viagens_validation_com_navio_no_test"] is None


def test_missing_columns_raise() -> None:
    with pytest.raises(ValueError, match="colunas obrigatórias"):
        count_shared_vessels(pd.DataFrame({"id": ["1-1"]}))


def test_build_summary_records_provenance(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.csv"
    _manifest(SYNTHETIC_ROWS).to_csv(manifest_path, index=False)

    summary = build_summary(manifest_path)

    prov = summary["proveniencia"]
    assert prov["manifesto"] == str(manifest_path)
    assert prov["manifesto_sha256"] == hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    assert prov["data_utc"].endswith("+00:00")
    assert summary["conjuntos"]["validation"]["viagens"] == 4
