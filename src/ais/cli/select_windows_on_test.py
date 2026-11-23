"""Seleção de J0 e J50 no conjunto `test` e medição por segmento (Marco 4, REV-046). UMA só abertura.

Papéis (REV-036): `test` seleciona; o `validation` NUNCA é aberto por este programa.
Só corre com `configs/authorizations/test_selection_windows.json` e o protocolo declarado antes
(`configs/selection_protocol_windows.json`); a abertura fica em `results/access_log.jsonl` e uma segunda
abertura é recusada (`ais.phase1.reserved`).

Numa só abertura:
  1. para J0 e J50: avalia as 300 épocas (perda por ponto depois da reconstrução), escolhe a época
     (menor perda) e o limiar (F1 médio, grelha 0,05 a 0,95) e grava `selection_test.json`;
  2. mede por ponto e por SEGMENTO (IoU 0,5, sem suavizar) a baseline congelada (época 162, limiar 0,65,
     NÃO reselecionada), J0 e J50;
  3. congela J0 e J50 (`results/windows_j0_frozen`, `results/windows_j50_frozen`).

Pré-condições verificadas ANTES de abrir o test: os dois treinos terminaram (`status = completo`,
300 checkpoints), o normalizador é o da baseline e a baseline congelada confere por hash.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.select_windows_on_test
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ais.cli.freeze_baseline import freeze_baseline, verify_frozen
from ais.cli.segment_metrics import _jsonable, _to_python
from ais.phase1.artifacts import load_checkpoint
from ais.phase1.data import apply_scaler, build_full_sequences, validate_training_data
from ais.phase1.inference import predict, tables_for
from ais.phase1.reserved import load_reserved_data, log_access, sha256_of
from ais.phase1.segments import compute_segment_metrics
from ais.phase1.selection import choose_epoch, choose_threshold
from ais.phase1.windows import (
    WindowSet, predict_window_probabilities, predict_window_table, reconstructed_loss_per_point,
    validate_window_coverage,
)

ROOT = Path(__file__).resolve().parents[3]
BOUNDARY_EPOCH = 291
VARIANTS = {"J0": "windows_j0", "J50": "windows_j50"}
IOU = 0.5


def segment_report(pred: pd.DataFrame) -> dict:
    """Métricas por segmento (pesca e navegação) sobre previsões brutas, sem suavizar."""
    out = {}
    for name, cls in (("pesca", 1), ("navegacao", 0)):
        out[name] = _jsonable(compute_segment_metrics(pred, class_col="predicted", cls=cls,
                                                      iou_threshold=IOU), True)
    return json.loads(json.dumps(out, default=_to_python))


def preconditions(root: Path) -> dict:
    """Verifica, SEM abrir o test, que os treinos terminaram e a baseline congelada confere."""
    info = {}
    frozen = root / "results" / "baseline_frozen"
    if not verify_frozen(frozen)["checkpoint_confere"]:
        raise ValueError("A baseline congelada não confere com o seu manifesto (hash).")
    _, base_ck = load_checkpoint(frozen / "checkpoint_frozen.pt")
    for variant, d in VARIANTS.items():
        run = root / "results" / d
        man = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))
        if man["status"] != "completo":
            raise ValueError(f"{variant}: treino não terminou (status={man['status']}); sem seleção.")
        n_ck = len(list((run / "checkpoints").glob("epoch_*.pt")))
        if n_ck != man["config"]["max_epochs"]:
            raise ValueError(f"{variant}: {n_ck} checkpoints, esperados {man['config']['max_epochs']}.")
        if man["scaler"] != base_ck["scaler"]:
            raise ValueError(f"{variant}: normalizador diferente do da baseline.")
        info[variant] = man
    return info


def run_selection(root: Path = ROOT, device: str = "cpu") -> dict:
    root = Path(root)
    dev = torch.device(device)
    manifests = preconditions(root)
    frozen_dir = root / "results" / "baseline_frozen"
    frozen_meta = json.loads((frozen_dir / "baseline_frozen.json").read_text(encoding="utf-8"))
    base_model, base_ck = load_checkpoint(frozen_dir / "checkpoint_frozen.pt", dev)
    scaler = base_ck["scaler"]

    data_path = root / "data" / "123_fishing_trajs_clean_test.parquet"
    manifest_path = root / "manifests" / "split_manifest_seed42.csv"
    auth = root / "configs" / "authorizations" / "test_selection_windows.json"
    proto_path = root / "configs" / "selection_protocol_windows.json"
    log_path = root / "results" / "access_log.jsonl"
    protocol = json.loads(proto_path.read_text(encoding="utf-8"))

    # ---- ÚNICA abertura do test (registada ANTES da leitura) ----
    df = load_reserved_data("test", data_path, manifest_path, auth, proto_path, log_path)
    report = validate_training_data(df)
    labels = df[["point_id", "label"]]
    seqs = [apply_scaler(s, scaler) for s in build_full_sequences(df)]
    hashes_common = {"ficheiro_test": sha256_of(data_path), "manifesto": sha256_of(manifest_path)}

    results = {}
    for variant, d in VARIANTS.items():
        run = root / "results" / d
        cfg = manifests[variant]["config"]
        ws = WindowSet(seqs, cfg["window_length"], cfg["overlap"])
        cov = validate_window_coverage(ws)
        target = ws.y[0]
        curve, cand = {}, {}
        for path in sorted((run / "checkpoints").glob("epoch_*.pt")):
            model, ck = load_checkpoint(path, dev)
            if ck["scaler"] != scaler:
                raise ValueError(f"Scaler diferente em {path.name}.")
            prob, _ = predict_window_probabilities(model, ws, dev)
            ep = int(ck["epoch"])
            curve[ep] = reconstructed_loss_per_point(prob, target)
            cand[ep] = {"ficheiro": path.name, "loss_por_ponto": curve[ep],
                        "accuracy_limiar_0_5": float(((prob >= 0.5).astype(int) == target).mean())}
        epoch = choose_epoch(curve)
        best_path = run / "checkpoints" / cand[epoch]["ficheiro"]
        model, _ = load_checkpoint(best_path, dev)
        pred = predict_window_table(model, ws, labels, dev, 0.5)
        threshold, grid_rows = choose_threshold(pred["p_fishing"].to_numpy(), pred["target"].to_numpy())
        pred["predicted"] = (pred["p_fishing"] >= threshold).astype(int)
        pred.to_csv(run / "predictions_test_selected.csv", index=False)
        res = {
            "variante": variant, "protocolo": protocol["id"], "autorizacao": auth.name,
            "conjunto": "test", "n_pontos_test": report["n_rows"], "n_viagens_test": report["n_ids"],
            "janelas_no_test": cov, "epoca_escolhida": epoch, "limiar_escolhido": threshold,
            "possivelmente_nao_convergiu": bool(epoch >= BOUNDARY_EPOCH),
            "n_candidatos": len(curve), "grelha_de_limiares": grid_rows,
            "curva_de_perda_por_epoca": {str(k): v for k, v in sorted(curve.items())},
            "candidatos": {str(k): v for k, v in sorted(cand.items())},
            "metricas_no_test_com_limiar_escolhido": tables_for(pred),
            "metricas_por_segmento": segment_report(pred),
            "hashes": {"checkpoint_escolhido": sha256_of(best_path), **hashes_common},
            "aviso": "Seleção no conjunto test: estas métricas são otimistas por terem servido a escolher. "
                     "O conjunto validation não foi aberto."}
        (run / "selection_test.json").write_text(json.dumps(res, indent=2, ensure_ascii=False),
                                                 encoding="utf-8")
        results[variant] = res

    # ---- baseline congelada: medida, nunca reselecionada ----
    base_pred = predict(base_model, seqs, labels, dev, frozen_meta["limiar"])
    base_pred.to_csv(frozen_dir / "predictions_test_baseline.csv", index=False)
    old = root / "results" / "phase1_select" / "predictions_test_selected.csv"
    same_as_before = None
    if old.is_file():
        prev = pd.read_csv(old, usecols=["point_id", "p_fishing"]).set_index("point_id")["p_fishing"]
        cur = base_pred.set_index("point_id")["p_fishing"].reindex(prev.index)
        same_as_before = bool(np.allclose(prev.to_numpy(), cur.to_numpy(), atol=1e-6))
    base_res = {
        "variante": "baseline", "protocolo": protocol["id"], "autorizacao": auth.name,
        "epoca": frozen_meta["epoca"], "limiar": frozen_meta["limiar"],
        "previsoes_iguais_as_da_selecao_anterior": same_as_before,
        "metricas_no_test": tables_for(base_pred), "metricas_por_segmento": segment_report(base_pred),
        "aviso": "Baseline congelada medida por segmento no test, sem reselecionar."}
    (frozen_dir / "test_segment_results.json").write_text(
        json.dumps(base_res, indent=2, ensure_ascii=False), encoding="utf-8")
    results["baseline"] = base_res

    log_access(log_path, {"event": "selection_done", "split": "test", "protocol": protocol["id"],
                          "J0_epoch": results["J0"]["epoca_escolhida"],
                          "J50_epoch": results["J50"]["epoca_escolhida"]})
    for variant, d in VARIANTS.items():
        freeze_baseline(root / "results" / d, root / "results" / f"{d}_frozen", log_path,
                        label=variant.lower())
    return results


def main() -> None:
    res = run_selection()
    for v in ("J0", "J50"):
        r = res[v]
        g = r["metricas_no_test_com_limiar_escolhido"]["global"]
        print(f"{v}: época {r['epoca_escolhida']} de {r['n_candidatos']}, limiar {r['limiar_escolhido']}, "
              f"accuracy no test {g['accuracy']:.4f}, possivelmente não convergiu: "
              f"{r['possivelmente_nao_convergiu']}")
    b = res["baseline"]
    print(f"baseline (congelada): época {b['epoca']}, limiar {b['limiar']}, previsões iguais às da "
          f"seleção anterior: {b['previsoes_iguais_as_da_selecao_anterior']}")


if __name__ == "__main__":
    sys.exit(main())
