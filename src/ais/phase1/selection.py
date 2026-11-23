"""Critérios de seleção declarados em `configs/selection_protocol.json` (REV-038).

Funções puras, testáveis com dados sintéticos. Não leem ficheiros nem decidem acessos.
  - época: menor perda por ponto (empate: a menor época);
  - limiar: grelha 0,05 a 0,95 (passo 0,05), maximiza a média dos F1 de navegação e pesca
    (empate: o mais próximo de 0,5; novo empate: o menor).
"""
from __future__ import annotations

import numpy as np

from .metrics import class_metrics

THRESHOLD_GRID = [round(0.05 * k, 2) for k in range(1, 20)]  # 0,05 ... 0,95


def choose_epoch(losses: dict[int, float]) -> int:
    """Época com menor perda por ponto; empate: a menor época. Valores não finitos são recusados."""
    if not losses:
        raise ValueError("Sem épocas candidatas.")
    if not all(np.isfinite(v) for v in losses.values()):
        raise ValueError("Perda não finita num candidato.")
    return min(losses, key=lambda e: (losses[e], e))


def macro_f1(target: np.ndarray, predicted: np.ndarray) -> float | None:
    """Média dos F1 das duas classes; None se algum F1 não estiver definido."""
    m = class_metrics(target, predicted)["por_classe"]
    f = [m["navegação"]["f1"], m["pesca"]["f1"]]
    return None if any(x is None for x in f) else float(np.mean(f))


def choose_threshold(prob: np.ndarray, target: np.ndarray, grid=THRESHOLD_GRID) -> tuple[float, list[dict]]:
    """Limiar da grelha que maximiza o F1 médio; devolve também a tabela completa da grelha."""
    prob, target = np.asarray(prob), np.asarray(target)
    rows = []
    for th in grid:
        rows.append({"threshold": float(th), "macro_f1": macro_f1(target, (prob >= th).astype(int))})
    valid = [r for r in rows if r["macro_f1"] is not None]
    if not valid:
        raise ValueError("F1 indefinido em todos os limiares.")
    best = max(valid, key=lambda r: (round(r["macro_f1"], 12), -abs(r["threshold"] - 0.5), -r["threshold"]))
    return best["threshold"], rows
