"""Ensaio curto da CNN 1D: ajuste em 3 viagens de TREINO e avaliação em outras 3 (REV-027, REV-028).

O QUE É: treina a CNN durante poucas épocas SÓ em 3 viagens do treino oficial e prevê (a)
essas mesmas 3 viagens ("ajuste", sobreajuste) e (b) outras 3 viagens do treino oficial
que a rede e o scaler nunca viram ("fora_da_amostra"). Não abre validação nem teste.
A segunda avaliação é uma monitorização interna dentro do treino, por ID completo, e
não substitui a validação oficial. Com 3 viagens é só uma ilustração, sem valor estatístico.

O scaler é ajustado só com as 3 viagens de ajuste e depois aplicado às outras 3.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python scripts/diagnostic_fit_3_trips.py
Saídas em results/diagnostic_3trips/ (não versionadas): predictions.csv, tables.json,
training_history.csv, run_manifest.json.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phase1.data import (  # noqa: E402
    FEATURE_COLS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences,
    build_sequence_loader, fit_scaler, validate_training_data,
)
from phase1.model import build_cnn, count_parameters  # noqa: E402
from phase1.training import build_loss, build_optimizer, train_one_epoch  # noqa: E402
from phase1.utils import select_device, set_reproducibility  # noqa: E402

TRAIN = ROOT / "data" / "123_fishing_trajs_clean_train.parquet"
MANIFEST = ROOT / "manifests" / "split_manifest_seed42.csv"
OUT = ROOT / "results" / "diagnostic_3trips"

# Configuração declarada deste ensaio (valores escolhidos aqui, não validados).
CONFIG = {"seed": 42, "n_fit_trips": 3, "n_eval_trips": 3, "epochs": 200, "lr": 1e-3,
          "threshold": 0.5}
CLASS_NAMES = {0: "navegação", 1: "pesca"}


def choose_ids(n: int) -> list[str]:
    """As n primeiras viagens do manifesto marcadas train e presentes no parquet de treino."""
    man = pd.read_csv(MANIFEST)
    present = set(pq.read_table(TRAIN, columns=["id"]).column("id").unique().to_pylist())
    return [i for i in man.loc[man["split"] == "train", "id"].astype(str) if i in present][:n]


def class_metrics(target: np.ndarray, pred: np.ndarray) -> dict:
    """Contagens e métricas globais e por classe (positivo = a própria classe)."""
    out = {"n_points": int(target.size), "n_correct": int((target == pred).sum()),
           "n_errors": int((target != pred).sum())}
    out["accuracy"] = out["n_correct"] / out["n_points"]
    per = {}
    for c, name in CLASS_NAMES.items():
        tp = int(((target == c) & (pred == c)).sum())
        fp = int(((target != c) & (pred == c)).sum())
        fn = int(((target == c) & (pred != c)).sum())
        tn = int(((target != c) & (pred != c)).sum())
        d = lambda a, b: (a / b) if b else None  # noqa: E731  (None = divisão por zero)
        per[name] = {"n_real": tp + fn, "n_predicted": tp + fp, "acertos": tp, "erros": fn,
                     "recall_acerto_da_classe": d(tp, tp + fn), "precisao": d(tp, tp + fp),
                     "f1": d(2 * tp, 2 * tp + fp + fn), "iou": d(tp, tp + fp + fn),
                     "tp": tp, "fp": fp, "fn": fn, "tn": tn}
    out["por_classe"] = per
    out["accuracy_maioritaria"] = float(max((target == 0).mean(), (target == 1).mean()))
    return out


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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = set_reproducibility(CONFIG["seed"], deterministic=True)
    device = select_device("cpu")
    n_fit, n_eval = CONFIG["n_fit_trips"], CONFIG["n_eval_trips"]

    ids = choose_ids(n_fit + n_eval)
    fit_ids, eval_ids = ids[:n_fit], ids[n_fit:]
    assert not set(fit_ids) & set(eval_ids)
    assert TRAIN.name == "123_fishing_trajs_clean_train.parquet"  # só treino
    df = pq.read_table(TRAIN, filters=[("id", "in", ids)]).to_pandas()
    split_of = dict(zip(*pd.read_csv(MANIFEST)[["id", "split"]].astype(str).values.T))
    assert all(split_of[i] == "train" for i in df["id"].unique()), "id fora do treino"
    df = df.sort_values(["id", "t", "point_id"], kind="stable").reset_index(drop=True)
    validate_training_data(df, FEATURE_COLS)
    labels = df[["point_id", "label"]]

    seqs = build_full_sequences(df, FEATURE_COLS)
    fit_seqs = [s for s in seqs if s["id"] in fit_ids]
    eval_seqs = [s for s in seqs if s["id"] in eval_ids]
    assert len(fit_seqs) == n_fit and len(eval_seqs) == n_eval
    scaler = fit_scaler(fit_seqs)  # só as viagens de ajuste: sem vazamento para as de avaliação
    fit_seqs = [apply_scaler(s, scaler) for s in fit_seqs]
    eval_seqs = [apply_scaler(s, scaler) for s in eval_seqs]

    torch.manual_seed(CONFIG["seed"])
    model = build_cnn(n_channels=N_INPUT_CHANNELS).to(device)
    loss_fn, opt = build_loss(), build_optimizer(model, {"lr": CONFIG["lr"]})

    history, t0 = [], time.perf_counter()
    for ep in range(1, CONFIG["epochs"] + 1):
        loader = build_sequence_loader(fit_seqs, shuffle=True, seed=CONFIG["seed"] + ep)
        history.append({"epoch": ep, **train_one_epoch(model, loader, opt, loss_fn, device)})
    train_seconds = time.perf_counter() - t0
    pd.DataFrame(history).to_csv(OUT / "training_history.csv", index=False)

    pred_fit = predict(model, fit_seqs, labels, device, CONFIG["threshold"]).assign(conjunto="ajuste")
    pred_eval = predict(model, eval_seqs, labels, device, CONFIG["threshold"]).assign(
        conjunto="fora_da_amostra")
    pd.concat([pred_fit, pred_eval], ignore_index=True).to_csv(OUT / "predictions.csv", index=False)

    (OUT / "tables.json").write_text(json.dumps(
        {"ajuste": tables_for(pred_fit), "fora_da_amostra": tables_for(pred_eval)},
        indent=2, ensure_ascii=False))
    (OUT / "run_manifest.json").write_text(json.dumps({
        "script": "scripts/diagnostic_fit_3_trips.py", "config": CONFIG,
        "ids_ajuste": fit_ids, "ids_fora_da_amostra": eval_ids,
        "n_points_ajuste": int(len(pred_fit)), "n_points_fora_da_amostra": int(len(pred_eval)),
        "n_parameters": count_parameters(model), "scaler_ajustado_so_com": "ids_ajuste",
        "scaler": scaler, "reproducibility": meta, "train_seconds": train_seconds,
        "python": platform.python_version(), "torch": torch.__version__,
        "first_epoch_loss_per_point": history[0]["mean_loss_per_point"],
        "final_epoch_loss_per_point": history[-1]["mean_loss_per_point"],
        "aviso": "As 6 viagens são do treino oficial. 'fora_da_amostra' não foi vista pela rede "
                 "nem pelo scaler, mas não é validação oficial e 3 viagens não têm valor estatístico.",
    }, indent=2, ensure_ascii=False, default=str))
    print(f"ajuste={fit_ids} ({len(pred_fit)} pts)  fora_da_amostra={eval_ids} ({len(pred_eval)} pts)")
    print(f"treino={train_seconds:.1f}s  perda/ponto: época 1={history[0]['mean_loss_per_point']:.4f} "
          f"época {CONFIG['epochs']}={history[-1]['mean_loss_per_point']:.4f}")


if __name__ == "__main__":
    main()
