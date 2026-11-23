"""Testes sintéticos: checkpoints, configuração, métricas e ciclo de treino com paragem.

Só dados inventados e minúsculos; não abre data/.
"""
from __future__ import annotations

import json

import numpy as np
import pytest
import torch

from phase1.artifacts import load_checkpoint, save_checkpoint
from phase1.config import load_phase1_config
from phase1.data import INPUT_CHANNELS, N_INPUT_CHANNELS, build_sequence_loader
from phase1.metrics import class_metrics
from phase1.model import build_cnn
from phase1.training import build_optimizer, train_model

GOOD = {"stage": "development", "seed": 42, "train_path": "data/x_clean_train.parquet",
        "split_manifest_path": "manifests/m.csv", "output_dir": "results/r",
        "internal_monitor_fraction": 0.15, "lr": 1e-3, "max_epochs": 100, "patience": 10,
        "min_delta": 0.0, "threshold": 0.5, "time_budget_seconds": 900, "device": "cpu"}


def _seqs(n_trips, seed=0):
    """Viagens sintéticas com X [7,N] e y [1,N]; alvo = canal 0 > 0 (aprendível)."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n_trips):
        n = int(rng.integers(20, 40))
        X = rng.normal(size=(N_INPUT_CHANNELS, n)).astype("float32")
        out.append({"id": f"S{k}", "point_ids": np.arange(n), "t": np.arange(n),
                    "X": X, "y": (X[0] > 0).astype("float32")[None, :]})
    return out


def _cfg(**kw):
    return {**GOOD, **kw}


# ---------------- checkpoint ----------------
def test_checkpoint_roundtrip_preserves_predictions(tmp_path):
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    opt = build_optimizer(model, {"lr": 1e-3})
    scaler = {"mean": [0.0], "std": [1.0], "feature_cols": ["a"]}
    p = save_checkpoint(tmp_path / "c.pt", model, opt, GOOD, scaler, epoch=7,
                        metrics={"m": 1.0}, input_channels=INPUT_CHANNELS)
    x = torch.randn(1, N_INPUT_CHANNELS, 25)
    model.eval()
    with torch.no_grad():
        ref = model(x)
    model2, ck = load_checkpoint(p)
    with torch.no_grad():
        got = model2(x)
    assert torch.allclose(ref, got, atol=1e-6)
    assert ck["epoch"] == 7 and ck["input_channels"] == INPUT_CHANNELS and ck["scaler"] == scaler
    assert not model2.training


# ---------------- configuração ----------------
def test_config_accepts_valid(tmp_path):
    f = tmp_path / "c.json"; f.write_text(json.dumps(GOOD))
    assert load_phase1_config(f)["seed"] == 42


@pytest.mark.parametrize("change", [
    {"stage": "validation"}, {"stage": "test"},
    {"train_path": "data/x_clean_validation.parquet"}, {"train_path": "data/x_clean_test.parquet"},
    {"train_path": "data/outro.parquet"}, {"internal_monitor_fraction": 1.0},
    {"lr": 0.0}, {"patience": 0}, {"device": "tpu"}, {"threshold": 1.5}])
def test_config_rejects_bad_values(tmp_path, change):
    f = tmp_path / "c.json"; f.write_text(json.dumps(_cfg(**change)))
    with pytest.raises(ValueError):
        load_phase1_config(f)


def test_config_rejects_unknown_and_missing_keys(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({**GOOD, "allow_validation": True}))
    with pytest.raises(ValueError, match="desconhecidas"):
        load_phase1_config(f)
    bad = dict(GOOD); bad.pop("lr")
    f.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="em falta"):
        load_phase1_config(f)


# ---------------- métricas ----------------
def test_class_metrics_known_values():
    t = np.array([0, 0, 0, 1, 1, 1, 1, 1])
    p = np.array([0, 0, 1, 1, 1, 1, 0, 1])
    m = class_metrics(t, p)
    assert (m["n_correct"], m["n_errors"]) == (6, 2) and m["accuracy"] == 0.75
    pesca = m["por_classe"]["pesca"]
    assert (pesca["tp"], pesca["fp"], pesca["fn"], pesca["tn"]) == (4, 1, 1, 2)
    assert pesca["sensibilidade"] == pytest.approx(0.8) and pesca["precisao"] == pytest.approx(0.8)
    assert m["accuracy_maioritaria"] == pytest.approx(5 / 8)


def test_class_metrics_division_by_zero_is_none():
    m = class_metrics(np.zeros(4, int), np.zeros(4, int))  # sem pesca real nem prevista
    assert m["por_classe"]["pesca"]["sensibilidade"] is None
    assert m["por_classe"]["pesca"]["precisao"] is None and m["accuracy"] == 1.0


# ---------------- ciclo de treino ----------------
def test_train_model_improves_and_restores_best(tmp_path):
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    tr, mon = _seqs(6, 1), _seqs(3, 2)
    out = train_model(model, tr, mon, _cfg(lr=1e-2, max_epochs=40, patience=40), torch.device("cpu"),
                      {"s": 1}, INPUT_CHANNELS, checkpoint_path=tmp_path / "best.pt", log=lambda *_: None)
    h = out["history"]
    assert h[-1]["monitor_loss_per_point"] < h[0]["monitor_loss_per_point"]
    assert out["stop_reason"] == "max_epochs" and out["epochs_run"] == 40
    best = min(r["monitor_loss_per_point"] for r in h)
    assert out["best_monitor_loss_per_point"] == pytest.approx(best)
    assert h[out["best_epoch"] - 1]["monitor_loss_per_point"] == pytest.approx(best)
    # o modelo devolvido é o melhor e o checkpoint em disco corresponde-lhe
    m2, ck = load_checkpoint(tmp_path / "best.pt")
    assert ck["epoch"] == out["best_epoch"]
    x = torch.randn(1, N_INPUT_CHANNELS, 30)
    model.eval()
    with torch.no_grad():
        assert torch.allclose(model(x), m2(x), atol=1e-6)


def test_train_model_early_stops_when_monitor_does_not_improve():
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    tr = _seqs(4, 1)
    mon = _seqs(3, 2)
    for s in mon:  # alvos aleatórios incompatíveis com o treino: a monitorização não melhora
        s["y"] = np.random.default_rng(5).integers(0, 2, s["y"].shape).astype("float32")
    out = train_model(model, tr, mon, _cfg(lr=1e-2, max_epochs=200, patience=3), torch.device("cpu"),
                      {"s": 1}, INPUT_CHANNELS, log=lambda *_: None)
    assert out["stop_reason"] == "paragem_antecipada" and out["epochs_run"] < 200
    assert out["epochs_run"] == out["best_epoch"] + 3


def test_train_model_respects_time_budget():
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    out = train_model(model, _seqs(4, 1), _seqs(2, 2),
                      _cfg(max_epochs=500, patience=500, time_budget_seconds=1e-9),
                      torch.device("cpu"), {"s": 1}, INPUT_CHANNELS, log=lambda *_: None)
    assert out["stop_reason"] == "orcamento_de_tempo" and out["epochs_run"] == 1


def test_monitor_never_updates_weights():
    """A monitorização usa só avaliação: os pesos não mudam durante a mesma."""
    from phase1.training import build_loss, evaluate_training_subset
    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    before = {k: v.clone() for k, v in model.state_dict().items()}
    evaluate_training_subset(model, build_sequence_loader(_seqs(3, 3), False, 0), build_loss(), torch.device("cpu"))
    assert all(torch.equal(before[k], v) for k, v in model.state_dict().items())
