"""Testes sintéticos do filtro gaussiano do pós-processamento (REV-056)."""
import numpy as np
import pytest

from ais.phase1.postprocessing import SIGMA, WINDOW_SIZE, gaussian_kernel, smooth_probabilities, smooth_trip


def test_kernel_shape_and_sum():
    w = gaussian_kernel()
    assert len(w) == WINDOW_SIZE == 13
    assert SIGMA == pytest.approx(13 / 6)
    assert w.sum() == pytest.approx(1.0)
    assert np.argmax(w) == 6
    assert np.allclose(w, w[::-1])
    assert np.all(np.diff(w[:7]) > 0)


@pytest.mark.parametrize("size", [0, 2, 12, -3])
def test_kernel_rejects_even_or_nonpositive(size):
    with pytest.raises(ValueError):
        gaussian_kernel(size)


def test_size_one_is_identity():
    p = np.array([0.1, 0.9, 0.2, 0.7])
    assert np.allclose(smooth_trip(p, gaussian_kernel(1)), p)


def test_isolated_point_flips_both_ways():
    nav = np.full(41, 0.02)
    nav[20] = 0.98  # um ponto de pesca isolado no meio de navegação
    assert smooth_trip(nav, gaussian_kernel())[20] < 0.65
    fish = np.full(41, 0.98)
    fish[20] = 0.02  # um ponto de navegação isolado no meio de pesca
    assert smooth_trip(fish, gaussian_kernel())[20] > 0.65


def test_long_block_is_kept():
    p = np.r_[np.full(30, 0.02), np.full(30, 0.98), np.full(30, 0.02)]
    s = smooth_trip(p, gaussian_kernel())
    assert np.all(s[35:55] > 0.65) and np.all(s[:25] < 0.65) and np.all(s[65:] < 0.65)


def test_constant_stays_constant_including_edges():
    p = np.full(5, 0.4)  # viagem mais curta que a janela
    s = smooth_trip(p, gaussian_kernel())
    assert s.shape == (5,) and np.allclose(s, 0.4)


def test_matches_manual_truncated_weighted_mean():
    rng = np.random.default_rng(0)
    p = rng.random(20)
    w = gaussian_kernel()
    s = smooth_trip(p, w)
    for i in (0, 3, 10, 19):
        idx = [j for j in range(i - 6, i + 7) if 0 <= j < 20]
        ww = np.array([w[j - i + 6] for j in idx])
        assert s[i] == pytest.approx(np.dot(ww, p[idx]) / ww.sum())


def test_rejects_even_kernel():
    with pytest.raises(ValueError):
        smooth_trip(np.zeros(5), np.ones(4) / 4)


def test_does_not_cross_trips():
    p = np.r_[np.full(20, 0.0), np.full(20, 1.0)]
    ids = np.array(["a"] * 20 + ["b"] * 20)
    s = smooth_probabilities(p, ids)
    assert np.allclose(s[:20], 0.0) and np.allclose(s[20:], 1.0)


def test_rejects_non_contiguous_trips_and_nan():
    with pytest.raises(ValueError):
        smooth_probabilities(np.zeros(3), np.array(["a", "b", "a"]))
    with pytest.raises(ValueError):
        smooth_trip(np.array([0.1, np.nan]), gaussian_kernel())


def test_error_runs_and_summary():
    import pandas as pd
    from ais.phase1.postprocessing import error_runs, summarize_runs
    df = pd.DataFrame({"id": ["a"] * 8 + ["b"] * 4,
                       "target":    [0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
                       "predicted": [0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0]})
    r = error_runs(df)
    assert r["comprimento"].tolist() == [1, 2, 2, 1, 2]
    assert r["classe_prevista"].tolist() == [1, 0, 1, 0, 0]
    s = summarize_runs(r["comprimento"])
    assert s["n_blocos"] == 5 and s["n_pontos"] == 8 and s["media"] == pytest.approx(1.6)
    assert s["distribuicao"][0]["n_blocos"] == 2 and s["distribuicao"][1]["n_pontos"] == 6


def test_error_run_does_not_cross_trips():
    import pandas as pd
    from ais.phase1.postprocessing import error_runs
    df = pd.DataFrame({"id": ["a", "a", "b", "b"], "target": [0, 0, 0, 0], "predicted": [0, 1, 1, 0]})
    assert error_runs(df)["comprimento"].tolist() == [1, 1]


def test_max_removable_island_grows_with_window():
    from ais.phase1.postprocessing import max_removable_island
    a = [max_removable_island(w, 0.65, 1) for w in (13, 51, 101)]
    assert a[0] >= 1 and a[0] < a[1] < a[2]
    assert max_removable_island(1, 0.65, 1) == 0


def test_eval_postproc_test_on_synthetic():
    import pandas as pd
    from ais.cli.eval_postproc_test import evaluate
    # Segmento de pesca de 600 pontos (os reais têm >= 584): as fronteiras recuam ~20 pontos de cada lado.
    n = 950
    p = np.r_[np.full(150, 0.02), np.full(600, 0.98), np.full(200, 0.02)]
    p[60] = 0.9          # pesca isolada
    p[440:460] = 0.1     # 20 pontos de navegação no meio de pesca
    tgt = np.r_[np.zeros(150), np.ones(600), np.zeros(200)].astype(int)
    df = pd.DataFrame({"id": "a", "point_id": range(n), "t": pd.date_range("2021-01-01", periods=n, freq="min").astype(str),
                       "target": tgt, "p_fishing": p, "label": tgt})
    df["predicted"] = (df["p_fishing"] >= 0.65).astype(int)
    r = evaluate(df, sizes=(13, 301))
    rows = {row["janela"]: row for row in r["resumo"]}
    assert rows[None]["erros"] == 21
    assert rows[301]["seg_pesca_previstos"] == 1 and rows[13]["seg_pesca_previstos"] == 2
    assert rows[301]["erros"] < 60  # remove o buraco, mas as fronteiras recuam


def test_large_window_erodes_short_real_segment():
    # Risco conhecido: com 301 pontos, um segmento real de navegação de 30 pontos no meio de pesca desaparece.
    p = np.r_[np.full(300, 0.98), np.full(30, 0.02), np.full(300, 0.98)]
    s = smooth_trip(p, gaussian_kernel(301, 301 / 6))
    assert np.all(s[300:330] >= 0.65)
