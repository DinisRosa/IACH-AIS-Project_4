"""Configuração de execução da fase 1 (desenvolvimento): leitura e validação de um JSON.

Rejeita qualquer configuração que não seja de desenvolvimento com o ficheiro de TREINO.
Uma flag aqui nunca concede acesso a validação ou teste (AGENTS.md §3).
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED = {
    "stage": str, "seed": int, "train_path": str, "split_manifest_path": str, "output_dir": str,
    "internal_monitor_fraction": float, "lr": float, "max_epochs": int, "patience": int,
    "min_delta": float, "threshold": float, "time_budget_seconds": float, "device": str,
}


def load_phase1_config(path) -> dict:
    """Lê o JSON e valida chaves, tipos, valores e a política de acesso (só treino)."""
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = sorted(set(REQUIRED) - set(cfg))
    unknown = sorted(set(cfg) - set(REQUIRED))
    if missing or unknown:
        raise ValueError(f"Configuração inválida; em falta: {missing}; desconhecidas: {unknown}")
    for k, t in REQUIRED.items():
        v = cfg[k]
        if isinstance(v, bool) or not (isinstance(v, t) or (t is float and isinstance(v, int))):
            raise ValueError(f"Tipo inválido em '{k}': esperado {t.__name__}, recebido {type(v).__name__}")
    if cfg["stage"] != "development":
        raise ValueError("Só stage='development' é permitido (validação/teste exigem autorização externa).")
    name = Path(cfg["train_path"]).name.lower()
    if "validation" in name or "test" in name or "train" not in name:
        raise ValueError("Política de acesso: train_path tem de ser o ficheiro de treino.")
    if not 0.0 < cfg["internal_monitor_fraction"] < 1.0:
        raise ValueError("internal_monitor_fraction tem de estar em (0,1).")
    if not (cfg["lr"] > 0 and cfg["max_epochs"] >= 1 and cfg["patience"] >= 1
            and cfg["time_budget_seconds"] > 0 and 0.0 < cfg["threshold"] < 1.0 and cfg["min_delta"] >= 0):
        raise ValueError("Valores fora do intervalo (lr, épocas, paciência, orçamento, limiar, min_delta).")
    if cfg["device"] not in ("cpu", "auto", "cuda"):
        raise ValueError("device tem de ser cpu, auto ou cuda.")
    return cfg
