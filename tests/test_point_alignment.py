"""Alinhamento ponto a ponto: point_ids, t, X e y mantêm correspondência 1:1."""
import numpy as np
import pandas as pd

from ais.phase1.data import (FEATURE_COLS, apply_scaler, build_full_sequences, build_sequence_loader,
                         fit_scaler)


def make_encoded_df(lengths):
    """Cada valor codifica o seu point_id: feature_k = point_id*10 + k; target = point_id % 2.

    Linhas das viagens baralhadas (ids intercalados) para provar que não há mistura.
    """
    rows, pid = [], 0
    t0 = pd.Timestamp("2021-05-01")
    for tid, n in lengths.items():
        for i in range(n):
            pid += 1
            rows.append({"point_id": pid, "id": tid, "t": t0 + pd.Timedelta(seconds=pid),
                         "speed_calc_mps": pid * 10.0 + 0, "signed_turn_calc_deg": pid * 10.0 + 1,
                         "time_gap_calc_s": pid * 10.0 + 2, "distanceToShore": pid * 10.0 + 3,
                         "target": pid % 2})
    df = pd.DataFrame(rows)
    return df.sample(frac=1.0, random_state=0).reset_index(drop=True)


def test_alignment_after_build_and_apply():
    lengths = {"a": 6, "b": 2, "c": 9, "d": 1}
    df = make_encoded_df(lengths)
    seqs = build_full_sequences(df, FEATURE_COLS)
    assert sorted(s["id"] for s in seqs) == ["a", "b", "c", "d"]
    sc = fit_scaler(seqs)
    ids_of_point = dict(zip(df["point_id"], df["id"]))
    t_of_point = dict(zip(df["point_id"], df["t"]))
    for s in seqs:
        assert len(s["point_ids"]) == lengths[s["id"]]
        out = apply_scaler(s, sc)
        mean = np.array(sc["mean"])
        std = np.array(sc["std"])
        for i, p in enumerate(out["point_ids"]):
            assert ids_of_point[p] == out["id"]  # nenhuma viagem recebe pontos de outra
            assert out["t"][i] == t_of_point[p]
            assert out["y"][0, i] == p % 2
            for k in range(4):  # X normalizado desfaz-se para o valor que codifica p
                raw = out["X"][k, i] * std[k] + mean[k]
                assert raw == np.float32(p * 10.0 + k) or abs(raw - (p * 10.0 + k)) < 1e-2 * max(1, std[k])


def test_alignment_through_loader():
    df = make_encoded_df({"a": 4, "b": 3, "c": 5})
    seqs = build_full_sequences(df, FEATURE_COLS)
    sc = fit_scaler(seqs)
    out = [apply_scaler(s, sc) for s in seqs]
    ids_of_point = dict(zip(df["point_id"], df["id"]))
    y_of_point = dict(zip(df["point_id"], df["target"]))
    seen = 0
    for x, y, meta in build_sequence_loader(out, shuffle=True, seed=3):
        pids = list(meta["point_ids"])
        assert x.shape[2] == y.shape[2] == len(pids) == len(meta["t"])
        for i, p in enumerate(pids):
            assert ids_of_point[p] == meta["id"]
            assert y[0, 0, i].item() == y_of_point[p]
        seen += len(pids)
    assert seen == len(df)
