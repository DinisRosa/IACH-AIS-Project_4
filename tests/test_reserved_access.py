"""Acesso reservado e seleção no `test` (REV-038). Só dados sintéticos inventados nos testes."""
import json

import numpy as np
import pandas as pd
import pytest
import torch

from ais.cli.select_on_test import run_selection
from ais.phase1.artifacts import load_checkpoint
from ais.phase1.data import (
    INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences, fit_scaler,
)
from ais.phase1.model import build_cnn
from ais.phase1.reserved import check_access, load_reserved_data, log_access, read_log
from ais.phase1.selection import THRESHOLD_GRID, choose_epoch, choose_threshold, macro_f1
from ais.phase1.training import train_model

CFG = {"stage": "development", "seed": 1, "train_path": "x_clean_train.parquet",
       "split_manifest_path": "m.csv", "output_dir": "r", "internal_monitor_fraction": 0.0,
       "lr": 1e-2, "max_epochs": 3, "patience": 3, "min_delta": 0.0, "threshold": 0.5,
       "time_budget_seconds": 600, "device": "cpu", "checkpoint_every_epoch": True}
AUTH = {"id": "a1", "conjuntos_autorizados": ["test"], "finalidade": "selecao",
        "max_rondas": 1, "validation_autorizado": False}
PROTO = {"id": "p1", "conjunto": "test", "declarado_antes_de_abrir_o_test": True}


def make_df(ids, seed):
    """Viagens sintéticas no formato das bases limpas (ordenadas por id e t, NaN esperados)."""
    rng = np.random.default_rng(seed)
    parts, pid = [], 0
    for tid in ids:
        n = int(rng.integers(25, 40))
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


@pytest.fixture()
def world(tmp_path):
    train_ids, test_ids = ["T1", "T2", "T3", "T4"], ["E1", "E2"]
    manifest = pd.DataFrame({"id": train_ids + test_ids + ["V1"],
                             "split": ["train"] * 4 + ["test"] * 2 + ["validation"]})
    manifest.to_csv(tmp_path / "m.csv", index=False)
    train_df, test_df = make_df(train_ids, 1), make_df(test_ids, 2)
    test_df.to_parquet(tmp_path / "clean_test.parquet")
    seqs = build_full_sequences(train_df)
    scaler = fit_scaler(seqs)
    seqs = [apply_scaler(s, scaler) for s in seqs]
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    run = tmp_path / "run"
    train_model(model, seqs, [], CFG, torch.device("cpu"), scaler, INPUT_CHANNELS,
                checkpoint_path=run / "checkpoint_best.pt", log=lambda *_: None)
    (tmp_path / "auth.json").write_text(json.dumps(AUTH))
    (tmp_path / "proto.json").write_text(json.dumps(PROTO))
    return {"dir": tmp_path, "run": run, "log": tmp_path / "log.jsonl"}


def go(w):
    d = w["dir"]
    return run_selection(w["run"], d / "clean_test.parquet", d / "m.csv", d / "auth.json",
                         d / "proto.json", w["log"])


# ---------------- critérios (funções puras) ----------------
def test_choose_epoch_min_loss_and_tie_goes_to_earliest():
    assert choose_epoch({1: 0.5, 2: 0.3, 3: 0.3, 4: 0.9}) == 2
    with pytest.raises(ValueError):
        choose_epoch({1: float("nan")})
    with pytest.raises(ValueError):
        choose_epoch({})


def test_choose_threshold_known_case_and_grid():
    assert THRESHOLD_GRID[0] == 0.05 and THRESHOLD_GRID[-1] == 0.95 and len(THRESHOLD_GRID) == 19
    target = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    prob = np.array([0.1, 0.2, 0.3, 0.45, 0.55, 0.6, 0.8, 0.9])
    th, rows = choose_threshold(prob, target)
    assert th == 0.5 and len(rows) == 19  # separação perfeita entre 0,45 e 0,55: empate => mais perto de 0,5
    # classe sem exemplos e sem previsões: F1 indefinido (None), nunca 0
    assert macro_f1(np.array([1, 1]), np.array([1, 1])) is None


# ---------------- política de acesso ----------------
def test_selection_runs_once_logs_and_second_round_is_refused(world):
    res = go(world)
    assert 1 <= res["epoca_escolhida"] <= 3 and res["limiar_escolhido"] in THRESHOLD_GRID
    assert res["n_candidatos"] == 3 and res["n_viagens_test"] == 2
    events = [e["event"] for e in read_log(world["log"])]
    assert events == ["open", "selection_done"]
    assert (world["run"] / "selection_test.json").is_file()
    assert (world["run"] / "predictions_test_selected.csv").is_file()
    with pytest.raises(PermissionError, match="esgotadas"):
        go(world)
    assert [e["event"] for e in read_log(world["log"])] == ["open", "selection_done"]  # nada novo


def test_validation_is_refused_without_authorization(tmp_path):
    with pytest.raises(PermissionError, match="Sem autorização"):
        check_access("validation", AUTH, {**PROTO, "conjunto": "validation"}, tmp_path / "l.jsonl")
    with pytest.raises(PermissionError, match="não é um conjunto reservado"):
        check_access("train", AUTH, PROTO, tmp_path / "l.jsonl")


def test_purpose_and_protocol_must_match(tmp_path):
    with pytest.raises(PermissionError, match="Finalidade"):
        check_access("test", {**AUTH, "finalidade": "medicao_final"}, PROTO, tmp_path / "l.jsonl")
    with pytest.raises(PermissionError, match="Protocolo"):
        check_access("test", AUTH, {**PROTO, "declarado_antes_de_abrir_o_test": False}, tmp_path / "l.jsonl")
    with pytest.raises(PermissionError, match="Protocolo"):
        check_access("test", AUTH, {**PROTO, "conjunto": "validation"}, tmp_path / "l.jsonl")


def test_validation_needs_own_authorization_frozen_run_and_opens_only_once(tmp_path):
    auth = {**AUTH, "conjuntos_autorizados": ["validation"], "finalidade": "medicao_final",
            "validation_autorizado": True}
    proto = {**PROTO, "conjunto": "validation"}
    log, frozen = tmp_path / "l.jsonl", tmp_path / "frozen.json"
    with pytest.raises(PermissionError, match="congelada"):
        check_access("validation", auth, proto, log, frozen)  # sem execução congelada
    frozen.write_text("{}")
    check_access("validation", auth, proto, log, frozen)  # agora passa
    log_access(log, {"event": "open", "split": "validation", "authorization": "outra"})
    with pytest.raises(PermissionError, match="uma vez"):
        check_access("validation", auth, proto, log, frozen)
    with pytest.raises(PermissionError, match="própria"):
        check_access("validation", {**auth, "validation_autorizado": False}, proto, tmp_path / "x.jsonl", frozen)


def test_wrong_file_or_wrong_ids_are_refused(world):
    d = world["dir"]
    pd.read_parquet(d / "clean_test.parquet").to_parquet(d / "x_clean_train.parquet")
    with pytest.raises(PermissionError, match="não corresponde"):
        load_reserved_data("test", d / "x_clean_train.parquet", d / "m.csv", d / "auth.json",
                           d / "proto.json", world["log"])
    assert read_log(world["log"]) == []  # recusado antes de registar/ler
    bad = pd.read_parquet(d / "clean_test.parquet").assign(id="T1")
    bad.to_parquet(d / "other_clean_test.parquet")
    with pytest.raises(ValueError, match="não constam como 'test'"):
        load_reserved_data("test", d / "other_clean_test.parquet", d / "m.csv", d / "auth.json",
                           d / "proto.json", world["log"])


def test_selected_checkpoint_matches_the_chosen_epoch(world):
    res = go(world)
    _, ck = load_checkpoint(world["run"] / "checkpoints" / res["candidatos"][str(res["epoca_escolhida"])]["ficheiro"])
    assert ck["epoch"] == res["epoca_escolhida"]


def test_freeze_baseline_records_hashes_and_detects_tampering(world):
    from ais.cli.freeze_baseline import freeze_baseline, verify_frozen
    res = go(world)
    out = world["dir"] / "frozen"
    m = freeze_baseline(world["run"], out, world["log"])
    assert m["epoca"] == res["epoca_escolhida"] and m["limiar"] == res["limiar_escolhido"]
    assert m["validation_aberto_ate_agora"] is False
    assert verify_frozen(out)["checkpoint_confere"] is True
    with open(out / "checkpoint_frozen.pt", "ab") as f:
        f.write(b"x")
    assert verify_frozen(out)["checkpoint_confere"] is False
