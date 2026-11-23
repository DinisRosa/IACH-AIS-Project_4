"""Política de acesso: load_training_data só aceita treino coerente com o manifesto."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ais.phase1.data import (FEATURE_COLS, apply_scaler, build_full_sequences, fit_scaler,
                         load_training_data, validate_training_data)

REAL_TRAIN = Path(__file__).resolve().parents[1] / "data" / "123_fishing_trajs_clean_train.parquet"
REAL_MANIFEST = Path(__file__).resolve().parents[1] / "manifests" / "split_manifest_seed42.csv"


def _manifest(tmp_path, mapping):
    p = tmp_path / "manifest.csv"
    pd.DataFrame({"id": list(mapping), "split": list(mapping.values())}).to_csv(p, index=False)
    return p


def _df(ids, split=None):
    rows = []
    for tid in ids:
        for i in range(3):
            rows.append({"point_id": len(rows) + 1, "id": tid, "t": pd.Timestamp("2020-01-01") + pd.Timedelta(minutes=i),
                         "speed_calc_mps": np.nan if i == 0 else 1.0, "signed_turn_calc_deg": np.nan if i < 2 else 1.0,
                         "time_gap_calc_s": np.nan if i == 0 else 60.0, "distanceToShore": 5.0, "target": 0})
    df = pd.DataFrame(rows)
    if split is not None:
        df["split"] = split
    return df


@pytest.mark.parametrize("name", ["x_clean_validation.parquet", "x_clean_test.parquet", "Validation_train.parquet"])
def test_rejects_validation_and_test_names_without_opening(tmp_path, name):
    man = _manifest(tmp_path, {"a": "train"})
    with pytest.raises(ValueError, match="Política de acesso"):  # não FileNotFoundError
        load_training_data(tmp_path / "inexistente" / name, man)


def test_rejects_non_train_name(tmp_path):
    with pytest.raises(ValueError, match="Política de acesso"):
        load_training_data(tmp_path / "dados.parquet", _manifest(tmp_path, {"a": "train"}))


def test_rejects_ids_not_train_in_manifest(tmp_path):
    f = tmp_path / "syn_train.parquet"
    _df(["a", "b"]).to_parquet(f)
    with pytest.raises(ValueError, match="não constam como train"):
        load_training_data(f, _manifest(tmp_path, {"a": "train", "b": "validation"}))
    with pytest.raises(ValueError, match="não constam como train"):  # id ausente do manifesto
        load_training_data(f, _manifest(tmp_path, {"a": "train"}))


def test_rejects_split_column_not_train(tmp_path):
    f = tmp_path / "syn_train.parquet"
    df = _df(["a"], split="train"); df.loc[0, "split"] = "test"
    df.to_parquet(f)
    with pytest.raises(ValueError, match="split"):
        load_training_data(f, _manifest(tmp_path, {"a": "train"}))


def test_accepts_synthetic_train(tmp_path):
    f = tmp_path / "syn_train.parquet"
    _df(["a", "b"], split="train").to_parquet(f)
    out = load_training_data(f, _manifest(tmp_path, {"a": "train", "b": "train", "c": "test"}))
    assert len(out) == 6 and set(out["id"]) == {"a", "b"}


@pytest.mark.skipif(not (REAL_TRAIN.exists() and REAL_MANIFEST.exists()), reason="treino real ausente")
def test_real_train_three_ids_pipeline():
    """Lê só 3 viagens do TREINO real (filtro por id) e corre o pipeline."""
    import pyarrow.parquet as pq

    man = pd.read_csv(REAL_MANIFEST)
    train_ids = set(man.loc[man["split"] == "train", "id"])
    present = pq.read_table(REAL_TRAIN, columns=["id"]).column("id").unique().to_pylist()
    chosen = [i for i in man.loc[man["split"] == "train", "id"] if i in set(present)][:3]
    assert len(chosen) == 3 and set(chosen) <= train_ids
    df = pq.read_table(REAL_TRAIN, filters=[("id", "in", chosen)]).to_pandas()

    rep = validate_training_data(df, FEATURE_COLS)
    seqs = build_full_sequences(df, FEATURE_COLS)
    sc = fit_scaler(seqs)
    out = [apply_scaler(s, sc) for s in seqs]
    assert len(out) == 3
    for s in out:
        n = len(s["point_ids"])
        assert s["X"].shape == (7, n) and s["y"].shape == (1, n)
        assert not np.isnan(s["X"]).any()
        m = s["X"][4:]
        assert m[0, 0] == 1 and m[2, 0] == 1 and m[1, :2].tolist() == [1, 1]
        assert m[0, 1:].sum() == 0 and m[2, 1:].sum() == 0 and m[1, 2:].sum() == 0
    mem_mb = df.memory_usage(deep=True).sum() / 1e6
    print(f"[treino real] ids={chosen} pontos={rep['n_rows']} memória df≈{mem_mb:.2f} MB")
