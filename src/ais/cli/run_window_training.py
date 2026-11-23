"""Treino da CNN 1D de referência sobre JANELAS (Marco 4, REV-046), só com o TREINO oficial.

Mesma rede, mesmo normalizador (confirmado contra o da baseline), mesma seed, mesmo Adam e mesmas 300
épocas da baseline; muda só o janelamento (L, sobreposição) e o lote (janelas por passo). Um checkpoint
por época para a seleção posterior. Sem monitorização interna (como a baseline): as 87 viagens ajustam
a rede. NÃO abre validação nem teste.

Orçamento: se o tempo decorrido ultrapassar `time_budget_seconds` antes das épocas terminarem, o treino
PARA, regista `status = "incompleto"` no manifesto e o programa sai com código 2 (sem seleção).

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.run_window_training configs/windows_j0.json
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

from ais.phase1.artifacts import load_checkpoint, save_checkpoint  # noqa: E402
from ais.phase1.data import (  # noqa: E402
    FEATURE_COLS, INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences, fit_scaler,
    load_training_data, save_scaler, validate_training_data,
)
from ais.phase1.model import build_cnn, count_parameters, receptive_field  # noqa: E402
from ais.phase1.training import build_optimizer  # noqa: E402
from ais.phase1.utils import select_device, set_reproducibility  # noqa: E402
from ais.phase1.windows import (  # noqa: E402
    WindowSet, load_window_config, predict_window_probabilities, reconstructed_loss_per_point,
    train_window_epoch, validate_window_coverage,
)

BASELINE_CHECKPOINT = ROOT / "results" / "baseline_frozen" / "checkpoint_frozen.pt"


def _same_scaler(a: dict, b: dict) -> bool:
    return (list(a["feature_cols"]) == list(b["feature_cols"])
            and np.allclose(a["mean"], b["mean"], rtol=0, atol=1e-9)
            and np.allclose(a["std"], b["std"], rtol=0, atol=1e-9))


def main(cfg_path: str) -> int:
    cfg = load_window_config(cfg_path)
    out = ROOT / cfg["output_dir"]
    (out / "checkpoints").mkdir(parents=True, exist_ok=True)
    meta = set_reproducibility(cfg["seed"], deterministic=True)
    device = select_device(cfg["device"])
    t_script = time.perf_counter()

    df = load_training_data(ROOT / cfg["train_path"], ROOT / cfg["split_manifest_path"])
    report = validate_training_data(df, FEATURE_COLS)
    print(f"treino carregado e validado: {report['n_ids']} viagens, {report['n_rows']} pontos", flush=True)
    seqs = build_full_sequences(df, FEATURE_COLS)
    scaler = fit_scaler(seqs)
    _, base_ck = load_checkpoint(BASELINE_CHECKPOINT, "cpu")
    if not _same_scaler(scaler, base_ck["scaler"]):
        raise ValueError("O normalizador difere do da baseline congelada; a comparação deixava de ser justa.")
    print("normalizador igual ao da baseline congelada", flush=True)
    save_scaler(scaler, out / "scaler.json")
    seqs = [apply_scaler(s, scaler) for s in seqs]

    ws = WindowSet(seqs, cfg["window_length"], cfg["overlap"])
    cov = validate_window_coverage(ws)
    steps_per_epoch = -(-len(ws) // cfg["batch_size"])
    print(f"{cfg['variant']}: L={cfg['window_length']}, sobreposição {cfg['overlap']:.0%} (passo "
          f"{ws.stride}); {cov['n_windows']} janelas ({cov['n_short_windows']} curtas), cobertura "
          f"{cov['min_coverage']}..{cov['max_coverage']}; lote {cfg['batch_size']} => "
          f"{steps_per_epoch} passos por época", flush=True)

    torch.manual_seed(cfg["seed"])
    model = build_cnn(n_channels=N_INPUT_CHANNELS).to(device)
    optimizer = build_optimizer(model, {"lr": cfg["lr"]})
    print(f"modelo: {count_parameters(model)} parâmetros, campo recetivo {receptive_field()} pontos; "
          f"lr={cfg['lr']}, {cfg['max_epochs']} épocas, orçamento {cfg['time_budget_seconds']:.0f}s",
          flush=True)

    target = ws.y[0]
    history, status, t0 = [], "completo", time.perf_counter()
    for epoch in range(1, cfg["max_epochs"] + 1):
        tr = train_window_epoch(model, ws, optimizer, cfg["batch_size"], cfg["seed"] + epoch, device)
        prob, _ = predict_window_probabilities(model, ws, device)
        eval_loss = reconstructed_loss_per_point(prob, target)
        elapsed = time.perf_counter() - t0
        save_checkpoint(out / "checkpoints" / f"epoch_{epoch:03d}.pt", model, None,
                        {k: v for k, v in cfg.items()}, scaler, epoch,
                        {"train_eval_loss_per_point": eval_loss}, INPUT_CHANNELS)
        history.append({"epoch": epoch, "train_loss_per_occurrence": tr["mean_loss_per_occurrence"],
                        "train_eval_loss_per_point": eval_loss, "n_steps": tr["n_steps"],
                        "train_seconds": tr["seconds"], "elapsed_seconds": elapsed})
        pd.DataFrame(history).to_csv(out / "training_history.csv", index=False)
        print(f"época {epoch:3d} | perda treino {tr['mean_loss_per_occurrence']:.4f} | perda por ponto "
              f"(reconstruída) {eval_loss:.4f} | {tr['seconds']:.1f}s | total {elapsed:6.1f}s", flush=True)
        if elapsed > cfg["time_budget_seconds"] and epoch < cfg["max_epochs"]:
            status = "incompleto"
            print(f"ORÇAMENTO DE TEMPO ULTRAPASSADO ({elapsed:.0f}s > {cfg['time_budget_seconds']:.0f}s) "
                  f"na época {epoch} de {cfg['max_epochs']}: treino PARADO, sem seleção.", flush=True)
            break

    total = time.perf_counter() - t0
    (out / "run_manifest.json").write_text(json.dumps({
        "script": "src/ais/cli/run_window_training.py", "config_path": str(cfg_path), "config": cfg,
        "status": status, "epochs_run": len(history), "n_windows": len(ws),
        "steps_per_epoch": steps_per_epoch, "total_steps": steps_per_epoch * len(history),
        "window_coverage": cov, "stride": ws.stride, "n_train_trips": len(seqs),
        "n_train_points": ws.n_points, "n_parameters": count_parameters(model),
        "receptive_field": receptive_field(), "input_channels": INPUT_CHANNELS, "scaler": scaler,
        "scaler_igual_ao_da_baseline": True, "total_training_seconds": total,
        "total_script_seconds": time.perf_counter() - t_script, "reproducibility": meta,
        "python": platform.python_version(), "torch": str(torch.__version__),
        "aviso": "Só treino oficial; teste e validação não foram abertos neste programa."},
        indent=2, ensure_ascii=False, default=str))
    print(f"{status}: {len(history)} épocas em {total:.1f}s; artefactos em {out}", flush=True)
    return 0 if status == "completo" else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
