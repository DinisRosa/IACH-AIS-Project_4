"""Testes sintéticos do janelamento (Marco 4): índice, cobertura, lotes com máscara,
equivalência com a janela isolada, perda mascarada, reconstrução por média e configuração."""
import json

import numpy as np
import pandas as pd
import pytest
import torch

from ais.phase1.model import build_cnn
from ais.phase1.windows import (
    WindowSet, calculate_stride, load_window_config, masked_bce, predict_window_probabilities,
    predict_window_table, reconstructed_loss_per_point, train_window_epoch,
    validate_window_coverage, window_starts,
)


def make_seqs(lengths, seed=0, channels=7):
    rng = np.random.default_rng(seed)
    seqs, pid = [], 0
    for tid, n in lengths.items():
        seqs.append({
            "id": tid, "point_ids": np.arange(pid, pid + n, dtype=np.int64),
            "t": np.arange(n).astype("datetime64[s]"),
            "X": rng.normal(size=(channels, n)).astype(np.float32),
            "y": rng.integers(0, 2, size=(1, n)).astype(np.float32)})
        pid += n
    return seqs


def test_stride_and_invalid_overlaps():
    assert calculate_stride(64, 0.0) == 64
    assert calculate_stride(64, 0.5) == 32
    assert calculate_stride(64, 0.75) == 16
    for bad in (1.0, -0.1, 0.3333):
        with pytest.raises(ValueError):
            calculate_stride(64, bad)
    with pytest.raises(ValueError):
        calculate_stride(0, 0.0)


@pytest.mark.parametrize("n,stride,expected", [
    (1, 64, [0]), (63, 64, [0]), (64, 64, [0]), (65, 64, [0, 64]), (128, 64, [0, 64]),
    (130, 64, [0, 64, 128]), (64, 32, [0]), (65, 32, [0, 32]), (96, 32, [0, 32]),
    (97, 32, [0, 32, 64]), (100, 32, [0, 32, 64]),
])
def test_window_starts(n, stride, expected):
    assert window_starts(n, 64, stride) == expected


def test_window_starts_rejects_gaps_in_coverage():
    with pytest.raises(ValueError):
        window_starts(100, 64, 65)
    with pytest.raises(ValueError):
        window_starts(0, 64, 64)


@pytest.mark.parametrize("overlap", [0.0, 0.5])
def test_coverage_tail_and_no_crossing(overlap):
    lengths = {"a": 10, "b": 64, "c": 65, "d": 200, "e": 1}
    ws = WindowSet(make_seqs(lengths), 64, overlap)
    rep = validate_window_coverage(ws)
    assert rep["min_coverage"] >= 1
    assert ws.n_points == sum(lengths.values())
    if overlap == 0.0:
        assert rep["max_coverage"] == 1
        # a, b: 1 janela; c: 2 (64 + 1); d: 4 (64+64+64+8); e: 1
        assert len(ws) == 1 + 1 + 2 + 4 + 1
    # a viagem curta dá uma única janela com o seu comprimento real (sem enchimento falso)
    first = np.flatnonzero(ws.win_seq == 0)
    assert list(ws.win_len[first]) == [10]
    table = ws.window_table()
    assert table.groupby("window_id")["id"].nunique().eq(1).all()
    assert table["point_id"].nunique() == ws.n_points


def test_tail_window_is_short_in_j0():
    ws = WindowSet(make_seqs({"d": 200}), 64, 0.0)
    assert list(ws.win_len) == [64, 64, 64, 8]


def test_overlap_50_covers_points_twice_inside():
    ws = WindowSet(make_seqs({"d": 192}), 64, 0.5)
    cnt = ws.coverage()
    # início e fim com 1 janela, miolo com 2
    assert cnt[0] == 1 and cnt[31] == 1 and cnt[32] == 2 and cnt[100] == 2 and cnt.max() == 2


def test_batch_padding_and_mask():
    ws = WindowSet(make_seqs({"a": 10, "b": 64}), 64, 0.0)
    X, Y, M = ws.get_batch([0, 1])
    assert X.shape == (2, 7, 64) and Y.shape == (2, 1, 64) and M.shape == (2, 1, 64)
    assert M[0].sum() == 10 and M[1].sum() == 64
    assert torch.all(X[0, :, 10:] == 0) and torch.all(Y[0, :, 10:] == 0)


def test_masked_batch_equals_isolated_windows():
    """A previsão de uma janela curta empilhada com enchimento é igual à da janela sozinha."""
    torch.manual_seed(0)
    model = build_cnn().eval()
    ws = WindowSet(make_seqs({"a": 10, "b": 64, "c": 37, "d": 5}, seed=3), 64, 0.0)
    with torch.no_grad():
        X, _, M = ws.get_batch(list(range(len(ws))))
        batched = model(X, mask=M)
        for w in range(len(ws)):
            n = int(ws.win_len[w])
            alone = model(X[w:w + 1, :, :n])
            torch.testing.assert_close(batched[w:w + 1, :, :n], alone, atol=1e-5, rtol=1e-5)


def test_mask_none_is_baseline_behaviour():
    torch.manual_seed(0)
    model = build_cnn().eval()
    x = torch.randn(1, 7, 50)
    with torch.no_grad():
        torch.testing.assert_close(model(x), model(x, mask=torch.ones(1, 1, 50)))


def test_loss_ignores_masked_positions_and_rejects_empty():
    logits = torch.randn(2, 1, 6)
    y = torch.randint(0, 2, (2, 1, 6)).float()
    mask = torch.tensor([[[1, 1, 1, 0, 0, 0]], [[1, 1, 1, 1, 1, 1]]], dtype=torch.float32)
    base = masked_bce(logits, y, mask)
    changed = logits.clone()
    changed[0, 0, 3:] = 1e3
    y2 = y.clone()
    y2[0, 0, 3:] = 1 - y2[0, 0, 3:]
    assert torch.isclose(base, masked_bce(changed, y2, mask))
    manual = torch.nn.functional.binary_cross_entropy_with_logits(
        torch.cat([logits[0, 0, :3], logits[1, 0]]), torch.cat([y[0, 0, :3], y[1, 0]]))
    assert torch.isclose(base, manual)
    with pytest.raises(ValueError):
        masked_bce(logits, y, torch.zeros_like(mask))


def test_reconstruction_j0_matches_concatenated_windows():
    torch.manual_seed(1)
    model = build_cnn().eval()
    seqs = make_seqs({"a": 150, "b": 20}, seed=5)
    ws = WindowSet(seqs, 64, 0.0)
    prob, cnt = predict_window_probabilities(model, ws, "cpu", batch_size=3)
    assert (cnt == 1).all() and prob.shape == (170,)
    expected = []
    with torch.no_grad():
        for w in range(len(ws)):
            s, n = int(ws.win_start[w]), int(ws.win_len[w])
            x = torch.from_numpy(ws.X[:, s:s + n])[None]
            expected.append(torch.sigmoid(model(x).double())[0, 0].numpy())
    np.testing.assert_allclose(prob, np.concatenate(expected), atol=1e-6)


def test_reconstruction_is_mean_of_probabilities_with_overlap():
    torch.manual_seed(2)
    model = build_cnn().eval()
    ws = WindowSet(make_seqs({"a": 128}, seed=7), 64, 0.5)  # janelas 0, 32, 64
    assert list(ws.win_start) == [0, 32, 64] and list(ws.win_len) == [64, 64, 64]
    prob, cnt = predict_window_probabilities(model, ws, "cpu")
    assert list(cnt[:32]) == [1] * 32 and list(cnt[32:96]) == [2] * 64 and list(cnt[96:]) == [1] * 32
    with torch.no_grad():
        outs = {}
        for w in range(3):
            s = int(ws.win_start[w])
            x = torch.from_numpy(ws.X[:, s:s + 64])[None]
            outs[w] = torch.sigmoid(model(x).double())[0, 0].numpy()
    np.testing.assert_allclose(prob[:32], outs[0][:32], atol=1e-6)
    np.testing.assert_allclose(prob[32:64], (outs[0][32:] + outs[1][:32]) / 2, atol=1e-6)
    np.testing.assert_allclose(prob[64:96], (outs[1][32:] + outs[2][:32]) / 2, atol=1e-6)
    np.testing.assert_allclose(prob[96:], outs[2][32:], atol=1e-6)


def test_table_preserves_order_ids_times_and_targets():
    torch.manual_seed(3)
    model = build_cnn().eval()
    seqs = make_seqs({"a": 90, "b": 40}, seed=9)
    ws = WindowSet(seqs, 64, 0.5)
    labels = pd.DataFrame({"point_id": ws.point_ids, "label": [f"l{p}" for p in ws.point_ids]})
    tab = predict_window_table(model, ws, labels, "cpu", 0.65)
    assert len(tab) == 130 and tab["point_id"].is_unique
    assert (tab["point_id"].to_numpy() == np.concatenate([s["point_ids"] for s in seqs])).all()
    assert (tab["t"].to_numpy() == np.concatenate([s["t"] for s in seqs])).all()
    assert (tab["id"].to_numpy() == np.array(["a"] * 90 + ["b"] * 40)).all()
    assert (tab["target"].to_numpy() == np.concatenate([s["y"][0] for s in seqs])).all()
    assert (tab["label"].to_numpy() == np.array([f"l{p}" for p in tab["point_id"]])).all()
    assert (tab["predicted"] == (tab["p_fishing"] >= 0.65).astype(int)).all()
    assert tab["n_windows"].min() >= 1


def test_reconstructed_loss_known_values():
    loss = reconstructed_loss_per_point(np.array([0.5, 0.5]), np.array([0, 1]))
    assert loss == pytest.approx(np.log(2))
    # probabilidade totalmente errada: a perda fica limitada pelo recorte de 1e-12
    assert reconstructed_loss_per_point(np.array([0.0, 1.0]), np.array([1, 0])) == pytest.approx(-np.log(1e-12))


def test_train_epoch_runs_with_finite_loss_and_counts_steps():
    torch.manual_seed(0)
    model = build_cnn()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    ws = WindowSet(make_seqs({"a": 200, "b": 70, "c": 9}, seed=1), 64, 0.5)
    r = train_window_epoch(model, ws, opt, 4, seed=1, device=torch.device("cpu"))
    assert np.isfinite(r["mean_loss_per_occurrence"])
    assert r["n_steps"] == -(-len(ws) // 4)
    assert r["n_valid_occurrences"] == int(ws.win_len.sum())
    assert all(torch.isfinite(p).all() for p in model.parameters())


def test_training_changes_weights_and_is_reproducible():
    def run():
        torch.manual_seed(42)
        model = build_cnn()
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        ws = WindowSet(make_seqs({"a": 130, "b": 33}, seed=2), 64, 0.0)
        before = [p.detach().clone() for p in model.parameters()]
        train_window_epoch(model, ws, opt, 2, seed=7, device=torch.device("cpu"))
        return before, [p.detach().clone() for p in model.parameters()]
    b1, a1 = run()
    b2, a2 = run()
    assert any(not torch.equal(x, y) for x, y in zip(b1, a1))
    assert all(torch.equal(x, y) for x, y in zip(a1, a2))


def _cfg(**over):
    cfg = {"stage": "development", "variant": "J0", "seed": 42,
           "train_path": "data/123_fishing_trajs_clean_train.parquet",
           "split_manifest_path": "manifests/split_manifest_seed42.csv",
           "output_dir": "results/windows_j0", "window_length": 64, "overlap": 0.0,
           "batch_size": 32, "lr": 0.001, "max_epochs": 300, "time_budget_seconds": 2700,
           "device": "cpu"}
    cfg.update(over)
    return cfg


def test_config_accepts_valid_and_rejects_reserved(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps(_cfg()))
    assert load_window_config(p)["overlap"] == 0.0
    for bad in (_cfg(train_path="data/123_fishing_trajs_clean_test.parquet"),
                _cfg(train_path="data/123_fishing_trajs_clean_validation.parquet"),
                _cfg(stage="selection"), _cfg(overlap=0.3333), _cfg(batch_size=0)):
        p.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            load_window_config(p)


def test_mask_zeroes_nonzero_input_padding():
    """O valor do enchimento da entrada não pode influenciar as posições reais."""
    torch.manual_seed(0)
    model = build_cnn().eval()
    x = torch.randn(1, 7, 20)
    mask = torch.zeros(1, 1, 20)
    mask[..., :10] = 1
    dirty = x.clone()
    dirty[..., 10:] = 5.0
    with torch.no_grad():
        alone = model(x[:, :, :10])
        torch.testing.assert_close(model(dirty, mask=mask)[:, :, :10], alone, atol=1e-5, rtol=1e-5)


def test_validate_window_coverage_rejects_bad_input():
    ws = WindowSet(make_seqs({"a": 130}), 64, 0.0)
    ws.win_len[0] = 10  # cria pontos sem janela
    with pytest.raises(ValueError, match="sem nenhuma janela"):
        validate_window_coverage(ws)
    ws2 = WindowSet(make_seqs({"b": 20, "a": 130}), 64, 0.0)
    ws2.win_len[0] = 64  # a janela da viagem curta "b" passa a invadir a viagem "a"
    with pytest.raises(ValueError, match="atravessa viagens"):
        validate_window_coverage(ws2)


def test_windowset_rejects_inconsistent_sequences():
    seqs = make_seqs({"a": 30})
    seqs[0]["y"] = seqs[0]["y"][:, :29]
    with pytest.raises(ValueError, match="comprimentos"):
        WindowSet(seqs, 16, 0.0)
    dup = make_seqs({"a": 20, "b": 20})
    dup[1]["id"] = "a"
    with pytest.raises(ValueError, match="mesmo id"):
        WindowSet(dup, 16, 0.0)
