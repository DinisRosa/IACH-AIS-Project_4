"""Testes sintéticos do pós-processamento no validation (REV-057).

Só dados criados aqui (tmp_path); nunca se toca em results/ nem data/ do projeto real.
O protocolo real é apenas copiado como modelo de estrutura.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ais.cli import postproc_validation as pv
from ais.phase1.postprocessing import gaussian_kernel
from ais.phase1.reserved import read_log, sha256_of

REAL_PROTOCOL = Path(__file__).resolve().parents[1] / "configs" / "postproc_protocol.json"
KERNEL = gaussian_kernel(13, 13 / 6)


def _t(i: int) -> str:
    return (pd.Timestamp("2020-01-01") + pd.Timedelta(minutes=i)).isoformat()


def _df(rows) -> pd.DataFrame:
    """rows: (id, point_id, t_index, target, p_fishing)."""
    df = pd.DataFrame(rows, columns=["id", "point_id", "ti", "target", "p_fishing"])
    df["t"] = df["ti"].map(_t)
    df["predicted"] = (df["p_fishing"] >= 0.65).astype(int)
    return df.drop(columns="ti")


# ---------------------------------------------------------------- order_points
def test_order_points_sorts_by_t_keeps_trip_appearance_order():
    df = _df([("B", 1, 2, 0, 0.1), ("A", 2, 1, 0, 0.1), ("B", 3, 0, 0, 0.1), ("A", 4, 0, 0, 0.1)])
    out = pv.order_points(df)
    assert out["id"].tolist() == ["B", "B", "A", "A"]  # B apareceu primeiro
    assert out["point_id"].tolist() == [3, 1, 4, 2]


def test_order_points_ties_broken_by_point_id():
    df = _df([("A", 9, 0, 0, 0.1), ("A", 5, 0, 0, 0.1), ("A", 7, 0, 0, 0.1)])
    assert pv.order_points(df)["point_id"].tolist() == [5, 7, 9]


def test_order_points_rejects_duplicate_point_id():
    df = _df([("A", 1, 0, 0, 0.1), ("B", 1, 0, 0, 0.1)])
    with pytest.raises(ValueError, match="point_id repetido"):
        pv.order_points(df)


def test_order_points_rejects_missing_columns():
    df = _df([("A", 1, 0, 0, 0.1)]).drop(columns=["target"])
    with pytest.raises(ValueError, match="Colunas em falta"):
        pv.order_points(df)


# ---------------------------------------------------------------- apply_filter
def test_apply_filter_keeps_original_columns():
    df = _df([("A", i, i, 0, 0.9 if i == 3 else 0.1) for i in range(20)])
    out = pv.apply_filter(df, 0.65, KERNEL)
    assert np.array_equal(out["p_fishing"], df["p_fishing"])
    assert np.array_equal(out["predicted"], df["predicted"])
    assert {"p_fishing_filtrada", "predicted_filtrado"} <= set(out.columns)


def test_apply_filter_trip_shorter_than_kernel():
    df = _df([("A", i, i, 0, 0.1) for i in range(10)])
    assert len(pv.apply_filter(df, 0.65, KERNEL)) == 10


def test_apply_filter_removes_isolated_fishing_point():
    p = [0.0] * 30 + [1.0] + [0.0] * 30
    df = _df([("A", i, i, 0, v) for i, v in enumerate(p)])
    out = pv.apply_filter(df, 0.65, KERNEL)
    assert df["predicted"].sum() == 1
    assert out["predicted_filtrado"].sum() == 0


def test_apply_filter_does_not_mix_trips():
    rows = [("A", i, i, 0, 0.0) for i in range(20)] + [("B", 100 + i, i, 1, 1.0) for i in range(20)]
    out = pv.apply_filter(_df(rows), 0.65, KERNEL)
    assert np.allclose(out.loc[out["id"] == "A", "p_fishing_filtrada"], 0.0)
    assert np.allclose(out.loc[out["id"] == "B", "p_fishing_filtrada"], 1.0)


# -------------------------------------------------------------- change_summary
def test_change_summary_hand_counted():
    # before, after, target
    cases = [
        (0, 1, 1),  # nav->pesca, corrigido
        (0, 1, 0),  # nav->pesca, estragado
        (1, 0, 0),  # pesca->nav, corrigido
        (1, 0, 1),  # pesca->nav, estragado
        (1, 0, 0),  # pesca->nav, corrigido
        (1, 1, 1),  # igual
        (0, 0, 1),  # igual
        (0, 0, 0),  # igual
    ]
    df = pd.DataFrame(cases, columns=["predicted", "predicted_filtrado", "target"])
    assert pv.change_summary(df) == {
        "n_pontos": 8, "n_mudam": 5, "navegacao_para_pesca": 2, "pesca_para_navegacao": 3,
        "corrigidos": 3, "estragados": 2,
    }


# --------------------------------------------------------------------- measure
def test_measure_hand_computed_accuracy_and_segments():
    target = [0, 0, 1, 1, 0, 0]
    before = [0, 1, 0, 1, 1, 0]  # 3/6 certos; 2 segmentos de pesca previstos
    after = [0, 0, 1, 1, 0, 0]   # 6/6 certos; 1 segmento
    df = pd.DataFrame({"id": "A", "point_id": range(6), "t": [_t(i) for i in range(6)],
                       "target": target, "predicted": before, "predicted_filtrado": after,
                       "label": target})
    res = pv.measure(df)
    assert res["antes"]["ponto"]["global"]["accuracy"] == pytest.approx(0.5)
    assert res["depois"]["ponto"]["global"]["accuracy"] == pytest.approx(1.0)
    assert res["antes"]["segmento"]["pesca"]["n_pred_segments"] == 2
    assert res["depois"]["segmento"]["pesca"]["n_pred_segments"] == 1
    assert res["antes"]["segmento"]["pesca"]["n_ref_segments"] == 1
    assert res["mudancas"]["n_mudam"] == 3


# ------------------------------------------------------------------ run / repo
def _synthetic_csv(path: Path, n: int = 40) -> None:
    rng = np.random.default_rng(0)
    rows = []
    for trip, base in (("V1", 0), ("V2", 1000)):
        for i in range(n):
            fishing = 1 if 10 <= i < 25 else 0
            p = float(np.clip(fishing * 0.8 + 0.1 + rng.normal(0, 0.25), 0, 1))
            rows.append((trip, base + i, i, fishing, p))
    df = _df(rows)
    df["label"] = df["target"]
    df = df.sample(frac=1, random_state=1)  # linhas baralhadas: order_points tem de as pôr em ordem
    path.parent.mkdir(parents=True, exist_ok=True)
    df[["id", "point_id", "t", "target", "p_fishing", "predicted", "label"]].to_csv(path, index=False)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _make_repo(root: Path, *, commit: bool = True, size: int | None = None, bad_predicted: bool = False,
               wrong_hash: bool = False) -> Path:
    csv = root / "results" / "final_validation" / "predictions_validation.csv"
    _synthetic_csv(csv)
    if bad_predicted:
        df = pd.read_csv(csv)
        df.loc[0, "predicted"] = 1 - df.loc[0, "predicted"]
        df.to_csv(csv, index=False)
    proto = json.loads(REAL_PROTOCOL.read_text(encoding="utf-8"))
    proto["fonte"]["sha256"] = "0" * 64 if wrong_hash else sha256_of(csv)
    if size is not None:
        proto["filtro"]["tamanho_pontos"] = size
    p = root / "configs" / "postproc_protocol.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(proto, indent=2), encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    if commit:
        _git(root, "add", "configs/postproc_protocol.json")
        _git(root, "commit", "-q", "-m", "protocolo")
    return root


def test_run_end_to_end_and_single_execution(tmp_path):
    _make_repo(tmp_path)
    res = pv.run(root=tmp_path)
    out = tmp_path / "results" / "postproc_validation"
    assert (out / "predictions_validation_postproc.csv").exists()
    saved = json.loads((out / "postproc_validation.json").read_text(encoding="utf-8"))
    assert saved["n_viagens"] == 2 and res["n_viagens"] == 2
    assert saved["mudancas"]["n_pontos"] == 80
    assert len(saved["filtro"]["pesos"]) == 13
    events = [e["event"] for e in read_log(tmp_path / "results" / "access_log.jsonl")]
    assert events == ["postproc_start", "postproc_done"]
    out_df = pd.read_csv(out / "predictions_validation_postproc.csv")
    src = pd.read_csv(tmp_path / "results" / "final_validation" / "predictions_validation.csv")
    first = src["id"].drop_duplicates().tolist()  # o CSV está baralhado: conta a ordem de aparição
    assert out_df["id"].tolist() == [v for v in first for _ in range(40)]
    with pytest.raises(PermissionError, match="já foi executado"):
        pv.run(root=tmp_path)


# --------------------------------------------------------------------- recusas
def test_refuses_wrong_hash(tmp_path):
    _make_repo(tmp_path, wrong_hash=True)
    with pytest.raises(ValueError, match="hash"):
        pv.run(root=tmp_path)
    assert not (tmp_path / "results" / "postproc_validation").exists()


def test_refuses_uncommitted_protocol(tmp_path):
    _make_repo(tmp_path, commit=False)
    with pytest.raises(PermissionError, match="commitado"):
        pv.run(root=tmp_path)


def test_refuses_protocol_modified_after_commit(tmp_path):
    _make_repo(tmp_path)
    p = tmp_path / "configs" / "postproc_protocol.json"
    p.write_text(p.read_text(encoding="utf-8") + "\n ", encoding="utf-8")
    with pytest.raises(PermissionError, match="commitado"):
        pv.run(root=tmp_path)


def test_refuses_filter_size_11(tmp_path):
    _make_repo(tmp_path, size=11)
    with pytest.raises(ValueError, match="protocolo"):
        pv.run(root=tmp_path)


def test_refuses_predicted_inconsistent_with_threshold(tmp_path):
    _make_repo(tmp_path, bad_predicted=True)
    with pytest.raises(ValueError, match="limiar"):
        pv.run(root=tmp_path)


def test_failure_mid_run_does_not_burn_single_execution(tmp_path):
    # Uma falha técnica depois de ler o CSV não regista nada nem grava resultados.
    _make_repo(tmp_path, bad_predicted=True)
    with pytest.raises(ValueError):
        pv.run(root=tmp_path)
    assert read_log(tmp_path / "results" / "access_log.jsonl") == []
    assert not (tmp_path / "results" / "postproc_validation").exists()


def test_refuses_changed_threshold_or_source(tmp_path):
    for key, val in (("limiar", 0.55), ("fonte", "results/outro.csv")):
        root = tmp_path / key
        root.mkdir()
        _make_repo(root)
        p = root / "configs" / "postproc_protocol.json"
        proto = json.loads(p.read_text(encoding="utf-8"))
        if key == "limiar":
            proto["filtro"]["limiar_depois_do_filtro"] = val
        else:
            proto["fonte"]["ficheiro"] = val
        p.write_text(json.dumps(proto), encoding="utf-8")
        _git(root, "commit", "-qam", "muda")
        with pytest.raises(ValueError, match="protocolo"):
            pv.run(root=root)


def test_any_previous_postproc_event_blocks_even_with_new_id(tmp_path):
    _make_repo(tmp_path)
    pv.run(root=tmp_path)
    p = tmp_path / "configs" / "postproc_protocol.json"
    proto = json.loads(p.read_text(encoding="utf-8"))
    proto["id"] = "outro_id"
    p.write_text(json.dumps(proto), encoding="utf-8")
    _git(tmp_path, "commit", "-qam", "novo id")
    with pytest.raises(PermissionError):
        pv.run(root=tmp_path)
