"""Treino da CNN 1D de referência (viagem completa) só com o TREINO oficial (REV-032).

Fluxo: carrega o treino (política de acesso), valida a base inteira, constrói as sequências,
separa a monitorização interna por ID (antes de ajustar o scaler), ajusta o scaler só com o treino
interno, treina com paragem antecipada e orçamento de tempo, restaura o melhor modelo e grava
histórico, checkpoint, previsões da monitorização, tabelas e manifesto. NÃO abre validação nem teste.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.run_phase1_training configs/phase1_run1.json
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[3]

from ais.phase1.artifacts import load_checkpoint  # noqa: E402
from ais.phase1.config import load_phase1_config  # noqa: E402
from ais.phase1.data import (  # noqa: E402
    FEATURE_COLS, INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences,
    build_sequence_loader, create_internal_training_split, fit_scaler, load_training_data,
    save_scaler, validate_training_data,
)
from ais.phase1.metrics import CLASS_NAMES, class_metrics  # noqa: E402
from ais.phase1.model import build_cnn, count_parameters, receptive_field  # noqa: E402
from ais.phase1.training import train_model  # noqa: E402
from ais.phase1.utils import select_device, set_reproducibility  # noqa: E402


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


def main(cfg_path: str) -> None:
    cfg = load_phase1_config(cfg_path)
    out = ROOT / cfg["output_dir"]
    out.mkdir(parents=True, exist_ok=True)
    meta = set_reproducibility(cfg["seed"], deterministic=True)
    device = select_device(cfg["device"])
    t_start = time.perf_counter()

    df = load_training_data(ROOT / cfg["train_path"], ROOT / cfg["split_manifest_path"])
    report = validate_training_data(df, FEATURE_COLS)
    print(f"treino carregado e validado: {report['n_ids']} viagens, {report['n_rows']} pontos "
          f"(ordenação e NaN esperados verificados na base inteira)", flush=True)
    labels = df[["point_id", "label"]]
    seqs = build_full_sequences(df, FEATURE_COLS)

    train_s, mon_s, split = create_internal_training_split(
        seqs, cfg["internal_monitor_fraction"], cfg["seed"])
    pd.Series(split, name="split_interno").rename_axis("id").to_csv(out / "internal_split.csv")
    scaler = fit_scaler(train_s)  # só treino interno: sem vazamento da monitorização
    save_scaler(scaler, out / "scaler.json")
    train_s = [apply_scaler(s, scaler) for s in train_s]
    mon_s = [apply_scaler(s, scaler) for s in mon_s]
    n_tr, n_mon = sum(s["y"].shape[1] for s in train_s), sum(s["y"].shape[1] for s in mon_s)
    print(f"partição interna: {len(train_s)} viagens de ajuste ({n_tr} pontos) e "
          f"{len(mon_s)} de monitorização ({n_mon} pontos); scaler ajustado só com o ajuste", flush=True)

    torch.manual_seed(cfg["seed"])
    model = build_cnn(n_channels=N_INPUT_CHANNELS).to(device)
    print(f"modelo: {count_parameters(model)} parâmetros, campo recetivo {receptive_field()} pontos; "
          f"lr={cfg['lr']}, máx. {cfg['max_epochs']} épocas, paciência {cfg['patience']}, "
          f"orçamento {cfg['time_budget_seconds']:.0f}s", flush=True)

    res = train_model(model, train_s, mon_s, cfg, device, scaler, INPUT_CHANNELS,
                      checkpoint_path=out / "checkpoint_best.pt", log=lambda m: print(m, flush=True))
    pd.DataFrame(res["history"]).to_csv(out / "training_history.csv", index=False)
    print(f"treino terminado: {res['stop_reason']} após {res['epochs_run']} épocas em "
          f"{res['total_seconds']:.1f}s; melhor época {res['best_epoch']} "
          f"(perda de monitorização {res['best_monitor_loss_per_point']:.4f})", flush=True)

    # Previsões com o melhor checkpoint recarregado do disco (prova que o checkpoint serve).
    best, ck = load_checkpoint(out / "checkpoint_best.pt", device)
    assert ck["epoch"] == res["best_epoch"]
    pred_mon = predict(best, mon_s, labels, device, cfg["threshold"])
    pred_tr = predict(best, train_s, labels, device, cfg["threshold"])
    pred_mon.to_csv(out / "predictions_monitor.csv", index=False)
    tables = {"monitor_interna": tables_for(pred_mon), "ajuste": tables_for(pred_tr)}
    (out / "tables.json").write_text(json.dumps(tables, indent=2, ensure_ascii=False))
    (out / "run_manifest.json").write_text(json.dumps({
        "script": "src/ais/cli/run_phase1_training.py", "config_path": str(cfg_path), "config": cfg,
        "n_train_trips": len(train_s), "n_monitor_trips": len(mon_s),
        "train_ids": [s["id"] for s in train_s], "monitor_ids": [s["id"] for s in mon_s],
        "n_train_points": n_tr, "n_monitor_points": n_mon, "n_parameters": count_parameters(model),
        "input_channels": INPUT_CHANNELS, "scaler": scaler, "train_result": {
            k: v for k, v in res.items() if k != "history"},
        "total_script_seconds": time.perf_counter() - t_start, "reproducibility": meta,
        "python": platform.python_version(), "torch": str(torch.__version__),
        "aviso": "Só treino oficial. 'monitor_interna' são viagens do treino reservadas por ID; "
                 "não é validação oficial. Validação e teste não foram abertos."}, indent=2,
        ensure_ascii=False, default=str))
    g, m = tables["ajuste"]["global"], tables["monitor_interna"]["global"]
    print(f"accuracy: ajuste {g['accuracy']:.4f} | monitorização {m['accuracy']:.4f} "
          f"(maioritária {m['accuracy_maioritaria']:.4f})", flush=True)
    print(f"artefactos em {out}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "configs" / "phase1_run1.json"))
