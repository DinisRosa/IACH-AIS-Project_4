"""Pós-processamento temporal (Marco 5, REV-056): filtro gaussiano sobre as probabilidades previstas.

O filtro anda ponto a ponto ao longo de cada viagem e substitui a probabilidade de pesca de cada ponto pela
média pesada das probabilidades dos vizinhos, com pesos em forma de sino (gaussiana) centrados no ponto.
Depois aplica-se o limiar congelado do modelo. Não atravessa viagens e não inventa pontos: nas pontas da
viagem usa só os vizinhos que existem e reajusta os pesos para somarem 1.

Valores declarados antes de qualquer medição (configuração, não estatística aprendida): janela de 13
pontos (o campo recetivo da CNN de referência) e sigma = 13 / 6.
"""
from __future__ import annotations

import numpy as np

WINDOW_SIZE = 13
SIGMA = WINDOW_SIZE / 6


def gaussian_kernel(size: int = WINDOW_SIZE, sigma: float = SIGMA) -> np.ndarray:
    """Pesos gaussianos de uma janela ímpar (posições -h..+h), normalizados para somarem 1."""
    if size < 1 or size % 2 == 0:
        raise ValueError("o tamanho da janela tem de ser um inteiro ímpar positivo")
    if sigma <= 0:
        raise ValueError("sigma tem de ser positivo")
    h = size // 2
    k = np.arange(-h, h + 1, dtype=float)
    w = np.exp(-(k**2) / (2 * sigma**2))
    return w / w.sum()


def smooth_trip(p: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Filtra as probabilidades de UMA viagem (pela ordem temporal), com reajuste dos pesos nas pontas."""
    p = np.asarray(p, dtype=float)
    if p.ndim != 1:
        raise ValueError("p tem de ser um vetor")
    if not np.all(np.isfinite(p)):
        raise ValueError("p tem valores não finitos")
    kernel = np.asarray(kernel, dtype=float)
    if kernel.ndim != 1 or len(kernel) % 2 == 0:
        raise ValueError("a janela tem de ter um número ímpar de posições")
    h = len(kernel) // 2
    n = len(p)
    out = np.empty(n)
    for i in range(n):  # explícito: funciona também em viagens mais curtas do que a janela
        lo, hi = max(0, i - h), min(n, i + h + 1)
        w = kernel[lo - i + h: hi - i + h]
        out[i] = np.dot(w, p[lo:hi]) / w.sum()
    return out


def smooth_probabilities(p: np.ndarray, trip_ids: np.ndarray, kernel: np.ndarray | None = None) -> np.ndarray:
    """Filtra viagem a viagem. Os pontos de cada viagem têm de estar contíguos e por ordem temporal."""
    kernel = gaussian_kernel() if kernel is None else kernel
    p = np.asarray(p, dtype=float)
    ids = np.asarray(trip_ids)
    if len(p) != len(ids):
        raise ValueError("p e trip_ids têm comprimentos diferentes")
    out = np.empty_like(p)
    if len(p) == 0:
        return out
    starts = np.r_[0, np.flatnonzero(ids[1:] != ids[:-1]) + 1]
    ends = np.r_[starts[1:], len(p)]
    if len(set(ids[starts].tolist())) != len(starts):
        raise ValueError("os pontos de cada viagem têm de estar contíguos")
    for s, e in zip(starts, ends):
        out[s:e] = smooth_trip(p[s:e], kernel)
    return out
