"""Inferência por ponto da CNN de viagem completa e tabelas de métricas (REV-038).

Uma probabilidade por ponto original (sigmoide aplicada UMA só vez, aqui) e a classe prevista.
Recebe sequências já normalizadas; não decide que conjunto é permitido (isso é política de acesso,
em `reserved.py` e no ponto de entrada).
"""
from __future__ import annotations

import pandas as pd
import torch

from .data import build_sequence_loader
from .metrics import CLASS_NAMES, class_metrics


@torch.no_grad()
def predict(model, seqs, labels, device, threshold) -> pd.DataFrame:
    """Uma probabilidade por ponto (sigmoid aplicada uma só vez, aqui) e a classe prevista."""
    model.eval()
    rows = []
    for X, y, m in build_sequence_loader(seqs, shuffle=False, seed=0):
        p = torch.sigmoid(model(X.to(device)))[0, 0].cpu().numpy()
        rows.append(pd.DataFrame({"id": m["id"], "point_id": m["point_ids"], "t": m["t"],
                                  "target": y[0, 0].numpy().astype(int), "p_fishing": p}))
    pred = pd.concat(rows, ignore_index=True)
    pred["predicted"] = (pred["p_fishing"] >= threshold).astype(int)
    pred = pred.merge(labels, on="point_id", how="left")
    assert pred["point_id"].is_unique and pred["label"].notna().all()
    return pred


def tables_for(pred: pd.DataFrame) -> dict:
    tgt, prd = pred["target"].to_numpy(), pred["predicted"].to_numpy()
    return {
        "global": class_metrics(tgt, prd),
        "por_viagem": {i: class_metrics(g["target"].to_numpy(), g["predicted"].to_numpy())
                       for i, g in pred.groupby("id", sort=False)},
        "rotulo_original_vs_previsto": (
            pred.groupby(["label", "predicted"]).size().unstack(fill_value=0)
            .rename(columns=CLASS_NAMES).reset_index().to_dict(orient="records")),
        "matriz_confusao_linhas_real_colunas_previsto": [
            [int(((tgt == r) & (prd == c)).sum()) for c in (0, 1)] for r in (0, 1)],
    }
