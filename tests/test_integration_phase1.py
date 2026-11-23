"""Teste de integração sintético: dados -> sequências -> scaler -> loader -> CNN -> passo de treino.

Só dados inventados e minúsculos. Não abre data/. Não é treino real: serve para
confirmar que as peças da fase 1 encaixam e que o scaler não vê a monitorização interna.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from phase1.checks import run_training_smoke_test
from phase1.data import (
    FEATURE_COLS,
    N_INPUT_CHANNELS,
    apply_scaler,
    build_full_sequences,
    build_sequence_loader,
    create_internal_training_split,
    fit_scaler,
    validate_training_data,
)
from phase1.model import build_cnn
from phase1.training import build_loss, build_optimizer, evaluate_training_subset, train_one_epoch


def _synthetic_df(lengths, seed=0):
    """Viagens sintéticas ordenadas por id, t, point_id, com NaN só nos pontos iniciais."""
    rng = np.random.default_rng(seed)
    frames, pid = [], 0
    for k, n in enumerate(lengths):
        df = pd.DataFrame({
            "id": f"S{k:02d}-1",
            "point_id": np.arange(pid, pid + n),
            "t": pd.date_range("2020-01-01", periods=n, freq="60s"),
            "speed_calc_mps": rng.normal(3, 1, n),
            "signed_turn_calc_deg": rng.normal(0, 20, n),
            "time_gap_calc_s": rng.normal(60, 5, n),
            "distanceToShore": rng.normal(5000, 500, n),
            "target": (rng.random(n) > 0.5).astype(int),
        })
        df.loc[0, ["speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s"]] = np.nan
        if n > 1:
            df.loc[1, "signed_turn_calc_deg"] = np.nan
        frames.append(df)
        pid += n
    return pd.concat(frames, ignore_index=True)


def _prepared(lengths, seed=0):
    df = _synthetic_df(lengths, seed)
    validate_training_data(df, FEATURE_COLS)
    return build_full_sequences(df, FEATURE_COLS)


def test_pipeline_end_to_end_one_epoch():
    seqs = _prepared([30, 17, 50, 9])
    scaler = fit_scaler(seqs)
    seqs = [apply_scaler(s, scaler) for s in seqs]
    loader = build_sequence_loader(seqs, shuffle=True, seed=1)

    torch.manual_seed(0)
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    loss_fn, device = build_loss(), torch.device("cpu")
    opt = build_optimizer(model, {"lr": 1e-2})

    # Uma probabilidade por ponto original, para cada comprimento.
    model.eval()
    for X, y, meta in loader:
        with torch.no_grad():
            assert model(X).shape == (1, 1, len(meta["point_ids"]))
    run_training_smoke_test(model, next(iter(loader)), loss_fn, device)

    stats = train_one_epoch(model, loader, opt, loss_fn, device)
    assert stats["n_steps"] == 4
    assert stats["n_points"] == 30 + 17 + 50 + 9
    assert np.isfinite(stats["mean_loss_per_point"])
    ev = evaluate_training_subset(model, loader, loss_fn, device)
    assert ev["n_points"] == 106
    assert ev["result_kind"] == "train_or_internal_monitor"


def test_scaler_does_not_see_internal_monitor():
    """Ajustado só com o treino interno: alterar a monitorização não muda o scaler."""
    seqs = _prepared([30, 17, 50, 9, 22, 41])
    train_s, mon_s, _ = create_internal_training_split(seqs, fraction=0.34, seed=42)
    sc_a = fit_scaler(train_s)
    for s in mon_s:  # valores extremos na monitorização
        s["features_raw"] = s["features_raw"] * 1000.0
    sc_b = fit_scaler(train_s)
    assert sc_a == sc_b
    assert fit_scaler(train_s + mon_s) != sc_a  # e o scaler global seria diferente
