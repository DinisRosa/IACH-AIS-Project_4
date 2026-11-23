"""Leitura de diagnóstico de uma viagem reservada (REV-050): só dados sintéticos inventados nos testes."""
import json

import numpy as np
import pandas as pd
import pytest

from ais.phase1.reserved import load_reserved_diagnostic, read_log

AUTH = {"id": "d1", "conjuntos_autorizados": ["test"], "finalidade": "diagnostico",
        "viagens_autorizadas": ["E1"], "colunas_autorizadas": ["id", "point_id", "t", "x", "y"],
        "max_leituras": 1, "validation_autorizado": False}


@pytest.fixture()
def world(tmp_path):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"id": ["E1"] * 5 + ["E2"] * 4, "point_id": range(9),
                       "t": pd.date_range("2021-01-01", periods=9, freq="10s"),
                       "x": rng.normal(size=9), "y": rng.normal(size=9), "target": [0, 1] * 4 + [0]})
    df.to_parquet(tmp_path / "clean_test.parquet")
    pd.DataFrame({"id": ["E1", "E2", "T1"], "split": ["test", "test", "train"]}).to_csv(tmp_path / "m.csv", index=False)
    (tmp_path / "auth.json").write_text(json.dumps(AUTH))
    return tmp_path


def go(w, trip="E1", cols=("id", "point_id", "x", "y"), split="test", name="clean_test.parquet"):
    return load_reserved_diagnostic(split, w / name, w / "m.csv", w / "auth.json", w / "log.jsonl", trip, cols)


def test_reads_only_the_authorized_trip_and_columns_and_logs_it(world):
    out = go(world)
    assert list(out.columns) == ["id", "point_id", "x", "y"] and set(out["id"]) == {"E1"} and len(out) == 5
    ev = read_log(world / "log.jsonl")
    assert [e["event"] for e in ev] == ["diagnostic_read"] and ev[0]["trip"] == "E1"
    assert not any(e["event"] == "open" for e in ev)  # não conta como abertura de seleção


def test_second_read_is_refused(world):
    go(world)
    with pytest.raises(PermissionError, match="esgotadas"):
        go(world)
    assert len(read_log(world / "log.jsonl")) == 1


@pytest.mark.parametrize("kwargs,match", [
    ({"trip": "E2"}, "não consta da autorização"),
    ({"cols": ("id", "target")}, "Colunas não autorizadas"),
    ({"split": "validation"}, "validation"),
])
def test_refusals_leave_no_log(world, kwargs, match):
    with pytest.raises(PermissionError, match=match):
        go(world, **kwargs)
    assert read_log(world / "log.jsonl") == []


def test_wrong_purpose_or_validation_flag_or_file_is_refused(world):
    for patch, match in (({"finalidade": "selecao"}, "não é de diagnóstico"),
                         ({"validation_autorizado": True}, "validation"),
                         ({"conjuntos_autorizados": ["validation"]}, "Sem autorização")):
        (world / "auth.json").write_text(json.dumps({**AUTH, **patch}))
        with pytest.raises(PermissionError, match=match):
            go(world)
    (world / "auth.json").write_text(json.dumps(AUTH))
    (world / "clean_train.parquet").write_bytes(b"x")
    with pytest.raises(PermissionError, match="não corresponde"):
        go(world, name="clean_train.parquet")
    assert read_log(world / "log.jsonl") == []
