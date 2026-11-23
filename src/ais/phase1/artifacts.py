"""Guardar e carregar checkpoints da fase 1 (só tipos simples: tensores, números, texto).

O checkpoint guarda o necessário para reproduzir as previsões: pesos, configuração do modelo,
ordem dos canais, normalizador, época e métricas de monitorização. Carregar apenas
checkpoints confiáveis (gerados por este projeto).
"""
from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

import torch

from .model import build_cnn


def save_checkpoint(path, model, optimizer, config: dict, scaler: dict, epoch: int,
                    metrics: dict, input_channels: list[str]) -> Path:
    """Grava pesos, estado do otimizador, configuração, scaler, época, métricas e versões."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "optimizer_state": optimizer.state_dict() if optimizer is not None else None,
        "model_config": dict(model.model_config),
        "n_channels": int(model.n_channels),
        "input_channels": list(input_channels),
        "scaler": scaler,
        "config": config,
        "epoch": int(epoch),
        "metrics": metrics,
        "versions": {"python": platform.python_version(), "torch": str(torch.__version__)},
    }, path)
    return path


def load_checkpoint(path, device="cpu") -> tuple[torch.nn.Module, dict]:
    """Reconstrói o modelo (em modo de avaliação) e devolve-o com os metadados do checkpoint."""
    ckpt: dict[str, Any] = torch.load(Path(path), map_location=device, weights_only=True)
    model = build_cnn(ckpt["model_config"], n_channels=ckpt["n_channels"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt
