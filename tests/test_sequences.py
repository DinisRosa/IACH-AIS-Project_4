"""Testes sintéticos de sequências, scaler, validação, separação interna e loader."""
import math

import numpy as np
import pandas as pd
import pytest
import torch

from phase1.data import (
    FEATURE_COLS, INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences,
    build_sequence_loader, create_internal_training_split, fit_scaler, load_scaler,
    save_scaler, validate_training_data,
)


def make_df(lengths):
    """Viagens sintéticas ordenadas (id, t, point_id); NaN só nos 2 primeiros pontos."""
    rows, pid = [], 0
    t0 = pd.Timestamp("2020-01-01")
    for tid, n in lengths.items():
        for i in range(n):
            pid += 1
            rows.append({
                "point_id": pid, "id": tid, "t": t0 + pd.Timedelta(minutes=i),
                "speed_calc_mps": np.nan if i == 0 else 1.0 + i,
                "signed_turn_calc_deg": np.nan if i < 2 else 10.0 * i,
                "time_gap_calc_s": np.nan if i == 0 else 60.0,
                "distanceToShore": 100.0 + pid,
                "target": i % 2,
            })
    return pd.DataFrame(rows)


def test_constants():
    assert N_INPUT_CHANNELS == 7 and len(INPUT_CHANNELS) == 7
    assert INPUT_CHANNELS[:4] == FEATURE_COLS


def test_shapes_and_different_lengths():
    df = make_df({"a": 5, "b": 3, "c": 8})
    seqs = build_full_sequences(df, FEATURE_COLS)
    assert [s["features_raw"].shape for s in seqs] == [(4, 5), (4, 3), (4, 8)]
    sc = fit_scaler(seqs)
    out = [apply_scaler(s, sc) for s in seqs]
    for s, n in zip(out, (5, 3, 8)):
        assert s["X"].shape == (7, n) and s["X"].dtype == np.float32
        assert s["y"].shape == (1, n) and s["y"].dtype == np.float32
    batch = next(iter(build_sequence_loader(out, shuffle=False, seed=0)))
    x, y, meta = batch
    assert x.shape == (1, 7, 5) and y.shape == (1, 1, 5)
    assert list(meta["point_ids"]) == [1, 2, 3, 4, 5]


def test_masks_first_two_points_including_short_ids():
    df = make_df({"a": 5, "one": 1, "two": 2})
    seqs = build_full_sequences(df, FEATURE_COLS)
    sc = fit_scaler(seqs)
    by = {s["id"]: apply_scaler(s, sc)["X"] for s in seqs}
    # canais 4,5,6 = máscaras speed, turn, gap
    assert by["a"][4].tolist() == [1, 0, 0, 0, 0]
    assert by["a"][5].tolist() == [1, 1, 0, 0, 0]
    assert by["a"][6].tolist() == [1, 0, 0, 0, 0]
    assert by["one"][4:].tolist() == [[1], [1], [1]]
    assert by["two"][4].tolist() == [1, 0]
    assert by["two"][5].tolist() == [1, 1]
    assert by["two"][6].tolist() == [1, 0]
    assert not np.isnan(by["a"]).any()


def test_missing_is_zero_after_normalizing_not_minus_mean_over_std():
    seq = {"id": "a", "point_ids": np.array([1, 2, 3]), "t": np.arange(3),
           "features_raw": np.array([[np.nan, 2, 4], [np.nan, np.nan, 5],
                                     [np.nan, 60, 60], [1, 2, 3]], dtype=np.float32),
           "y": np.zeros((1, 3), dtype=np.float32)}
    sc = fit_scaler([seq])
    assert sc["mean"][0] != 0  # se fosse preenchido antes, daria -mean/std != 0
    X = apply_scaler(seq, sc)["X"]
    assert X[0, 0] == 0.0 and X[1, 0] == 0.0 and X[1, 1] == 0.0 and X[2, 0] == 0.0
    # observado: (2-3)/1 e (4-3)/1
    assert X[0, 1:].tolist() == pytest.approx([-1.0, 1.0])


def test_scaler_ignores_nan_and_matches_manual():
    # speed observado: 2,4,6 -> média 4, var populacional 8/3
    a = {"features_raw": np.array([[np.nan, 2, 4], [np.nan, np.nan, 1], [np.nan, 10, 10], [1, 2, 3]],
                                  dtype=np.float32)}
    b = {"features_raw": np.array([[np.nan, 6], [np.nan, 3], [np.nan, 30], [5, 6]], dtype=np.float32)}
    sc = fit_scaler([a, b])
    assert sc["n_observed"] == [3, 2, 3, 5]
    assert sc["mean"][0] == pytest.approx(4.0)
    assert sc["std"][0] == pytest.approx(math.sqrt(8 / 3))
    assert sc["mean"][1] == pytest.approx(2.0) and sc["std"][1] == pytest.approx(1.0)  # 1 e 3
    assert sc["mean"][3] == pytest.approx(3.4)
    vals = np.array([1, 2, 3, 5, 6.0])
    assert sc["std"][3] == pytest.approx(vals.std(ddof=0))
    # independente da ordem
    sc2 = fit_scaler([b, a])
    assert sc2["mean"] == pytest.approx(sc["mean"]) and sc2["std"] == pytest.approx(sc["std"])


def test_scaler_zero_std_protected_and_json_roundtrip(tmp_path):
    s = {"features_raw": np.array([[np.nan, 5, 5], [np.nan, np.nan, 1], [np.nan, 3, 4], [7, 7, 7]],
                                  dtype=np.float32)}
    sc = fit_scaler([s])
    assert sc["std"][0] == 1.0 and sc["std"][3] == 1.0
    assert "speed_calc_mps" in sc["std_protected"]
    p = tmp_path / "sc.json"
    save_scaler(sc, p)
    assert load_scaler(p) == sc


def test_apply_never_changes_scaler_nor_y():
    df = make_df({"a": 4, "b": 3})
    seqs = build_full_sequences(df)
    sc = fit_scaler(seqs)
    before = repr(sc)
    y_before = [s["y"].copy() for s in seqs]
    for s in seqs:
        out = apply_scaler(s, sc)
        assert "X" not in s  # original intocado (cópia)
    assert repr(sc) == before
    for s, yb in zip(seqs, y_before):
        assert np.array_equal(s["y"], yb)


def test_validate_ok_and_report():
    df = make_df({"a": 4, "b": 3})
    rep = validate_training_data(df, FEATURE_COLS)
    assert rep["n_rows"] == 7 and rep["n_ids"] == 2
    assert rep["n_nan_per_feature"]["signed_turn_calc_deg"] == 4


def test_validate_rejections():
    base = make_df({"a": 4, "b": 3})
    d = base.copy(); d.loc[3, "speed_calc_mps"] = np.nan
    with pytest.raises(ValueError, match="NaN inesperado"):
        validate_training_data(d, FEATURE_COLS)
    d = base.copy(); d.loc[2, "distanceToShore"] = np.nan
    with pytest.raises(ValueError, match="NaN inesperado"):
        validate_training_data(d, FEATURE_COLS)
    d = base.copy(); d.loc[3, "time_gap_calc_s"] = np.inf
    with pytest.raises(ValueError, match="infinit"):
        validate_training_data(d, FEATURE_COLS)
    d = base.copy(); d.loc[1, "target"] = 2
    with pytest.raises(ValueError, match="binário"):
        validate_training_data(d, FEATURE_COLS)
    d = base.copy(); d.loc[2, "t"] = d.loc[0, "t"] - pd.Timedelta(hours=1)
    with pytest.raises(ValueError, match="decrescente"):
        validate_training_data(d, FEATURE_COLS)
    d = base.copy(); d.loc[1, "point_id"] = d.loc[0, "point_id"]
    with pytest.raises(ValueError, match="duplicado"):
        validate_training_data(d, FEATURE_COLS)
    d = base.iloc[[0, 1, 4, 5, 6, 2, 3]].reset_index(drop=True)  # id 'a' partido
    with pytest.raises(ValueError, match="contíguas"):
        validate_training_data(d, FEATURE_COLS)
    with pytest.raises(ValueError, match="em falta"):
        validate_training_data(base.drop(columns=["target"]), FEATURE_COLS)


def _seqs(n):
    return build_full_sequences(make_df({f"id{i}": 2 + i for i in range(n)}))


def test_internal_split_by_whole_id_reproducible():
    seqs = _seqs(10)
    tr, mo, man = create_internal_training_split(seqs, 0.3, seed=1)
    tr2, mo2, man2 = create_internal_training_split(seqs, 0.3, seed=1)
    assert man == man2 and [s["id"] for s in mo] == [s["id"] for s in mo2]
    assert len(mo) == 3 and len(tr) == 7
    assert not {s["id"] for s in tr} & {s["id"] for s in mo}
    assert {s["id"] for s in tr} | {s["id"] for s in mo} == {s["id"] for s in seqs}
    for s in mo:  # sequência completa, não partida
        assert s["features_raw"].shape[1] == len(s["point_ids"])
        assert man[s["id"]] == "monitor_internal"
    assert all(man[s["id"]] == "train_internal" for s in tr)
    _, mo3, _ = create_internal_training_split(seqs, 0.3, seed=2)
    assert [s["id"] for s in mo3] != [s["id"] for s in mo]


def test_internal_split_invalid_and_min_one_each_side():
    seqs = _seqs(4)
    for f in (0, 1, -0.1, 1.5):
        with pytest.raises(ValueError):
            create_internal_training_split(seqs, f, seed=0)
    tr, mo, _ = create_internal_training_split(seqs, 0.01, seed=0)
    assert len(mo) == 1 and len(tr) == 3
    tr, mo, _ = create_internal_training_split(seqs, 0.99, seed=0)
    assert len(tr) == 1 and len(mo) == 3
    with pytest.raises(ValueError):
        create_internal_training_split(seqs[:1], 0.5, seed=0)


def test_loader_requires_X():
    with pytest.raises(ValueError, match="X"):
        build_sequence_loader(_seqs(2), shuffle=False, seed=0)


def test_loader_shuffle_reproducible_and_complete():
    seqs = _seqs(8)
    sc = fit_scaler(seqs)
    out = [apply_scaler(s, sc) for s in seqs]

    def order(seed):
        return [m["id"] for _, _, m in build_sequence_loader(out, shuffle=True, seed=seed)]

    assert order(5) == order(5)
    assert sorted(order(5)) == sorted(s["id"] for s in out)
    assert order(5) != [s["id"] for s in out] or order(6) != [s["id"] for s in out]
    assert [m["id"] for _, _, m in build_sequence_loader(out, shuffle=False, seed=5)] == [s["id"] for s in out]
    x, y, _ = next(iter(build_sequence_loader(out, shuffle=False, seed=0)))
    assert x.dtype == torch.float32 and y.dtype == torch.float32
