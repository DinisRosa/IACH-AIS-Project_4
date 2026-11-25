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
