"""Seleção da época e do limiar no conjunto `test` (REV-038). Uma só ronda, protocolo declarado.

Papéis (REV-036): `test` seleciona; o `validation` NUNCA é aberto por este programa.
Só corre com um ficheiro de autorização (`configs/authorizations/test_selection.json`) e um
protocolo declarado antes (`configs/selection_protocol.json`); regista a abertura em
`results/access_log.jsonl` e recusa uma segunda ronda.

Avalia os checkpoints `epoch_*.pt` da execução de treino, escolhe a época pela menor perda por ponto
no `test`, escolhe o limiar pelo F1 médio e grava `selection_test.json` e
`predictions_test_selected.csv` na pasta da execução. NÃO calcula métricas por segmento.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.select_on_test [results/phase1_select]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

from ais.phase1.artifacts import load_checkpoint
from ais.phase1.data import (
    apply_scaler, build_full_sequences, build_sequence_loader, validate_training_data,
)
from ais.phase1.inference import predict, tables_for
from ais.phase1.reserved import load_reserved_data, log_access, sha256_of
from ais.phase1.selection import THRESHOLD_GRID, choose_epoch, choose_threshold
from ais.phase1.training import build_loss, evaluate_training_subset

ROOT = Path(__file__).resolve().parents[3]
BOUNDARY_EPOCH = 291  # protocolo: >= 291 => possivelmente não convergiu


def run_selection(run_dir, data_path, manifest_path, auth_path, protocol_path, log_path,
                  device="cpu") -> dict:
    run_dir = Path(run_dir)
    device = torch.device(device)
    ckpt_paths = sorted((run_dir / "checkpoints").glob("epoch_*.pt"))
    if not ckpt_paths:
        raise FileNotFoundError(f"Sem checkpoints em {run_dir / 'checkpoints'}.")
    # O scaler vem do treino (guardado em cada checkpoint); lê-se ANTES de abrir o test.
    _, first = load_checkpoint(ckpt_paths[0], device)
    scaler = first["scaler"]
    protocol = json.loads(Path(protocol_path).read_text(encoding="utf-8"))

    df = load_reserved_data("test", data_path, manifest_path, auth_path, protocol_path, log_path)
    report = validate_training_data(df)
    labels = df[["point_id", "label"]]
    seqs = [apply_scaler(s, scaler) for s in build_full_sequences(df)]
    loader = build_sequence_loader(seqs, shuffle=False, seed=0)
    loss_fn = build_loss()

    curve, models_info = {}, {}
    for path in ckpt_paths:
        model, ck = load_checkpoint(path, device)
        if ck["scaler"] != scaler:
            raise ValueError(f"Scaler diferente no checkpoint {path.name}.")
        ev = evaluate_training_subset(model, loader, loss_fn, device, 0.5)
        c = ev["counts"]
        curve[int(ck["epoch"])] = float(ev["mean_loss_per_point"])
        models_info[int(ck["epoch"])] = {
            "ficheiro": path.name, "loss_por_ponto": float(ev["mean_loss_per_point"]),
            "accuracy_limiar_0_5": (c["TP"] + c["TN"]) / ev["n_points"]}

    epoch = choose_epoch(curve)
    best_path = run_dir / "checkpoints" / models_info[epoch]["ficheiro"]
    model, _ = load_checkpoint(best_path, device)
    pred = predict(model, seqs, labels, device, 0.5)
    threshold, grid_rows = choose_threshold(pred["p_fishing"].to_numpy(), pred["target"].to_numpy())
    pred["predicted"] = (pred["p_fishing"] >= threshold).astype(int)
    pred.to_csv(run_dir / "predictions_test_selected.csv", index=False)
    tables = tables_for(pred)

    result = {
        "protocolo": protocol["id"], "autorizacao": Path(auth_path).name,
        "conjunto": "test", "n_pontos_test": report["n_rows"], "n_viagens_test": report["n_ids"],
        "epoca_escolhida": epoch, "limiar_escolhido": threshold,
        "possivelmente_nao_convergiu": bool(epoch >= BOUNDARY_EPOCH),
        "n_candidatos": len(curve), "grelha_de_limiares": grid_rows,
        "curva_de_perda_por_epoca": {str(k): v for k, v in sorted(curve.items())},
        "candidatos": {str(k): v for k, v in sorted(models_info.items())},
        "metricas_no_test_com_limiar_escolhido": tables,
        "hashes": {"checkpoint_escolhido": sha256_of(best_path),
                   "ficheiro_test": sha256_of(data_path), "manifesto": sha256_of(manifest_path)},
        "aviso": "Seleção no conjunto test: estas métricas são otimistas por terem servido a escolher. "
                 "Sem métricas por segmento. O conjunto validation não foi aberto.",
    }
    (run_dir / "selection_test.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    log_access(log_path, {"event": "selection_done", "split": "test", "epoch": epoch,
                          "threshold": threshold, "protocol": protocol["id"]})
    return result


def main(run: str | None = None) -> None:
    run_dir = Path(run) if run else ROOT / "results" / "phase1_select"
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    res = run_selection(
        run_dir, ROOT / "data" / "123_fishing_trajs_clean_test.parquet",
        ROOT / "manifests" / "split_manifest_seed42.csv",
        ROOT / "configs" / "authorizations" / "test_selection.json",
        ROOT / "configs" / "selection_protocol.json", ROOT / "results" / "access_log.jsonl")
    g = res["metricas_no_test_com_limiar_escolhido"]["global"]
    print(f"época escolhida {res['epoca_escolhida']} de {res['n_candidatos']}; limiar "
          f"{res['limiar_escolhido']}; accuracy no test {g['accuracy']:.4f}; "
          f"possivelmente não convergiu: {res['possivelmente_nao_convergiu']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
