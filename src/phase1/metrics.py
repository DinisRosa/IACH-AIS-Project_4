"""Métricas por ponto (global e por classe) a partir de rótulos e previsões binárias.

Divisões por zero devolvem None (não 0), para não esconder casos sem exemplos.
"""
from __future__ import annotations

import numpy as np

CLASS_NAMES = {0: "navegação", 1: "pesca"}


def class_metrics(target: np.ndarray, pred: np.ndarray) -> dict:
    """Contagens e métricas globais e por classe (positivo = a própria classe)."""
    target, pred = np.asarray(target), np.asarray(pred)
    out = {"n_points": int(target.size), "n_correct": int((target == pred).sum()),
           "n_errors": int((target != pred).sum())}
    out["accuracy"] = out["n_correct"] / out["n_points"] if out["n_points"] else None
    per = {}
    for c, name in CLASS_NAMES.items():
        tp = int(((target == c) & (pred == c)).sum())
        fp = int(((target != c) & (pred == c)).sum())
        fn = int(((target == c) & (pred != c)).sum())
        tn = int(((target != c) & (pred != c)).sum())
        d = lambda a, b: (a / b) if b else None  # noqa: E731
        per[name] = {"n_real": tp + fn, "n_predicted": tp + fp, "acertos": tp, "erros": fn,
                     "sensibilidade": d(tp, tp + fn), "precisao": d(tp, tp + fp),
                     "f1": d(2 * tp, 2 * tp + fp + fn), "iou": d(tp, tp + fp + fn),
                     "tp": tp, "fp": fp, "fn": fn, "tn": tn}
    out["por_classe"] = per
    out["accuracy_maioritaria"] = (float(max((target == 0).mean(), (target == 1).mean()))
                                   if out["n_points"] else None)
    return out
