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


# ---- Análise dos "buracos" para escolher a janela (REV-058) ----
BINS = [1, 2, 4, 7, 13, 26, 51, 101, 201, 501, np.inf]


def error_runs(df, id_col: str = "id", target_col: str = "target", pred_col: str = "predicted"):
    """Blocos máximos de pontos consecutivos mal classificados, com a mesma classe prevista, dentro de cada
    viagem. O DataFrame tem de estar ordenado por viagem e tempo. Devolve id, inicio (posição na viagem),
    comprimento (pontos), classe_real_dominante e classe_prevista."""
    import pandas as pd

    rows = []
    for trip, g in df.groupby(id_col, sort=False):
        tgt, prd = g[target_col].to_numpy(), g[pred_col].to_numpy()
        wrong = tgt != prd
        i, n = 0, len(g)
        while i < n:
            if not wrong[i]:
                i += 1
                continue
            j = i
            while j + 1 < n and wrong[j + 1] and prd[j + 1] == prd[i]:
                j += 1
            rows.append({"id": trip, "inicio": i, "comprimento": j - i + 1,
                         "classe_real": int(np.bincount(tgt[i:j + 1], minlength=2).argmax()),
                         "classe_prevista": int(prd[i])})
            i = j + 1
    return pd.DataFrame(rows, columns=["id", "inicio", "comprimento", "classe_real", "classe_prevista"])


def summarize_runs(lengths) -> dict:
    """Média, mediana, quantis (interpolação linear do numpy) e distribuição por classes de comprimento,
    em número de blocos e em número de pontos."""
    x = np.asarray(lengths, dtype=float)
    if x.size == 0:
        return {"n_blocos": 0}
    edges = BINS
    dist = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (x >= lo) & (x < hi)
        dist.append({"de": int(lo), "ate": None if np.isinf(hi) else int(hi - 1), "n_blocos": int(m.sum()),
                     "perc_blocos": float(m.mean()), "n_pontos": int(x[m].sum()),
                     "perc_pontos": float(x[m].sum() / x.sum())})
    return {"n_blocos": int(x.size), "n_pontos": int(x.sum()), "media": float(x.mean()),
            "mediana": float(np.median(x)), **{f"p{q}": float(np.percentile(x, q)) for q in (75, 90, 95, 99)},
            "maximo": int(x.max()), "distribuicao": dist}


def max_removable_island(size: int, threshold: float, island_cls: int, sigma: float | None = None) -> int:
    """Maior bloco isolado (probabilidades ideais 0/1) que a janela gaussiana remove por completo.
    island_cls=1: pesca no meio de navegação; island_cls=0: navegação no meio de pesca."""
    sigma = size / 6 if sigma is None else sigma
    k = gaussian_kernel(size, sigma)
    best = 0
    for L in range(1, size + 1):
        bg = 1.0 - island_cls
        p = np.full(L + 2 * size, bg)
        p[size:size + L] = float(island_cls)
        pred = (smooth_trip(p, k) >= threshold).astype(int)
        if np.all(pred == int(bg)):
            best = L
        else:
            break
    return best
