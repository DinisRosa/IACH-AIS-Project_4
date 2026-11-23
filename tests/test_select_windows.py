"""Seleção de J0 e J50 no `test` (Marco 4): só dados sintéticos inventados nos testes.

Monta um projeto-miniatura numa pasta temporária (base `test` sintética, baseline e duas variantes
com 3 checkpoints cada) e corre o programa de ponta a ponta, sem tocar em nenhum dado real.
"""
import json

import numpy as np
import pandas as pd
import pytest
import torch

from ais.cli.freeze_baseline import verify_frozen
from ais.cli.select_windows_on_test import run_selection
from ais.phase1.artifacts import save_checkpoint
from ais.phase1.data import (
    INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences, fit_scaler,
)
from ais.phase1.model import build_cnn
from ais.phase1.reserved import read_log, sha256_of

AUTH = {"id": "aw1", "conjuntos_autorizados": ["test"], "finalidade": "selecao",
        "max_rondas": 1, "validation_autorizado": False}
PROTO = {"id": "pw1", "conjunto": "test", "declarado_antes_de_abrir_o_test": True}


def make_df(ids, seed):
    rng = np.random.default_rng(seed)
    parts, pid = [], 0
    for tid in ids:
        n = int(rng.integers(30, 50))
        speed = rng.normal(5, 2, n)
        d = pd.DataFrame({
            "id": tid, "point_id": np.arange(pid, pid + n),
            "t": pd.Timestamp("2021-01-01") + pd.to_timedelta(np.arange(n) * 10, unit="s"),
            "speed_calc_mps": speed, "signed_turn_calc_deg": rng.normal(0, 10, n),
            "time_gap_calc_s": np.full(n, 10.0), "distanceToShore": rng.normal(1000, 100, n),
            "target": (speed > 5).astype("int8")})
        d["label"] = np.where(d["target"] == 1, "02-fishing", "01-sailing")
        d.loc[d.index[0], ["speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s"]] = np.nan
        d.loc[d.index[1], "signed_turn_calc_deg"] = np.nan
        parts.append(d)
        pid += n
    return pd.concat(parts, ignore_index=True)


def _save(path, seed, epoch, scaler, cfg):
    torch.manual_seed(seed)
    save_checkpoint(path, build_cnn(n_channels=N_INPUT_CHANNELS), None, cfg, scaler, epoch, {},
                    INPUT_CHANNELS)


@pytest.fixture()
def project(tmp_path):
    train_ids, test_ids = ["T1", "T2", "T3"], ["E1", "E2"]
    (tmp_path / "data").mkdir()
    (tmp_path / "manifests").mkdir()
    (tmp_path / "configs" / "authorizations").mkdir(parents=True)
    pd.DataFrame({"id": train_ids + test_ids + ["V1"], "split": ["train"] * 3 + ["test"] * 2 +
                  ["validation"]}).to_csv(tmp_path / "manifests" / "split_manifest_seed42.csv", index=False)
    make_df(test_ids, 2).to_parquet(tmp_path / "data" / "123_fishing_trajs_clean_test.parquet")
    scaler = fit_scaler(build_full_sequences(make_df(train_ids, 1)))
    (tmp_path / "configs" / "authorizations" / "test_selection_windows.json").write_text(json.dumps(AUTH))
    (tmp_path / "configs" / "selection_protocol_windows.json").write_text(json.dumps(PROTO))

    frozen = tmp_path / "results" / "baseline_frozen"
    _save(frozen / "checkpoint_frozen.pt", 0, 162, scaler, {})
    (frozen / "baseline_frozen.json").write_text(json.dumps({
        "epoca": 162, "limiar": 0.65, "checkpoint": "checkpoint_frozen.pt",
        "checkpoint_sha256": sha256_of(frozen / "checkpoint_frozen.pt")}))
    for d, overlap in (("windows_j0", 0.0), ("windows_j50", 0.5)):
        run = tmp_path / "results" / d
        for e in (1, 2, 3):
            _save(run / "checkpoints" / f"epoch_{e:03d}.pt", e + (10 if overlap else 0), e, scaler, {})
        (run / "run_manifest.json").write_text(json.dumps({
            "status": "completo", "scaler": scaler,
            "config": {"max_epochs": 3, "window_length": 16, "overlap": overlap}}))
    return tmp_path


def test_selection_one_opening_selects_measures_and_freezes(project):
    res = run_selection(project)
    events = [e["event"] for e in read_log(project / "results" / "access_log.jsonl")]
    assert events == ["open", "selection_done"]  # uma só abertura do test
    for v in ("J0", "J50"):
        r = res[v]
        assert 1 <= r["epoca_escolhida"] <= 3 and r["n_candidatos"] == 3 and r["n_viagens_test"] == 2
        assert r["possivelmente_nao_convergiu"] is False
        assert set(r["metricas_por_segmento"]) == {"pesca", "navegacao"}
        d = project / "results" / ("windows_j0" if v == "J0" else "windows_j50")
        assert (d / "selection_test.json").is_file() and (d / "predictions_test_selected.csv").is_file()
        pred = pd.read_csv(d / "predictions_test_selected.csv")
        assert pred["point_id"].is_unique and len(pred) == r["n_pontos_test"]
        frozen = project / "results" / (d.name + "_frozen")
        assert verify_frozen(frozen, label=v.lower())["checkpoint_confere"] is True
    # J0: cada ponto numa só janela; J50: alguns pontos em duas
    p0 = pd.read_csv(project / "results" / "windows_j0" / "predictions_test_selected.csv")
    p50 = pd.read_csv(project / "results" / "windows_j50" / "predictions_test_selected.csv")
    assert p0["n_windows"].max() == 1 and p50["n_windows"].max() == 2
    # a baseline é medida, não reselecionada
    b = res["baseline"]
    assert b["epoca"] == 162 and b["limiar"] == 0.65 and "pesca" in b["metricas_por_segmento"]
    assert (project / "results" / "baseline_frozen" / "test_segment_results.json").is_file()
    assert all(e.get("split") != "validation" for e in read_log(project / "results" / "access_log.jsonl"))


def test_second_opening_is_refused(project):
    run_selection(project)
    with pytest.raises(PermissionError, match="esgotadas"):
        run_selection(project)
    assert [e["event"] for e in read_log(project / "results" / "access_log.jsonl")] == [
        "open", "selection_done"]


def test_incomplete_training_blocks_before_opening_test(project):
    p = project / "results" / "windows_j50" / "run_manifest.json"
    m = json.loads(p.read_text())
    m["status"] = "incompleto"
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="não terminou"):
        run_selection(project)
    assert read_log(project / "results" / "access_log.jsonl") == []  # o test não chegou a abrir


def test_missing_checkpoints_and_scaler_mismatch_block_before_opening(project):
    (project / "results" / "windows_j0" / "checkpoints" / "epoch_003.pt").unlink()
    with pytest.raises(ValueError, match="checkpoints"):
        run_selection(project)
    assert read_log(project / "results" / "access_log.jsonl") == []


def test_tampered_baseline_blocks_before_opening(project):
    (project / "results" / "baseline_frozen" / "checkpoint_frozen.pt").write_bytes(b"x")
    with pytest.raises(ValueError, match="baseline congelada"):
        run_selection(project)
    assert read_log(project / "results" / "access_log.jsonl") == []
