"""Perda, otimizador, passo de treino e avaliação de diagnóstico (fase 1).

Convenções:
- Cada passo de treino usa UMA sequência completa (batch_size=1), X [1, C, N] e
  y [1, 1, N]. A perda de um passo é BCEWithLogitsLoss com reduction='mean', ou
  seja, a média por ponto dessa sequência. Assim, viagens longas e curtas pesam
  igual POR PASSO, não por ponto. A média por ponto é calculada à parte, ponderada
  pelo número de pontos de cada sequência.
- Sem pesos de classe e sem reamostragem.
- O modelo devolve logits; a Sigmoid só é aplicada na avaliação, uma vez.
- `evaluate_training_subset` identifica o resultado como 'train_or_internal_monitor'.
  Não é validação nem teste e não serve para seleção formal.
"""

from __future__ import annotations

import time
from typing import Any, Iterable, Mapping

import numpy as np
import torch
from torch import nn

# PLACEHOLDER NÃO VALIDADO: a taxa de aprendizagem 1e-3 é apenas um valor inicial
# por omissão. Não foi escolhida nem validada com dados; deve ser definida na config.
DEFAULT_OPTIMIZER_CONFIG: dict[str, Any] = {"lr": 1e-3}


def build_loss(loss_config: Mapping[str, Any] | None = None) -> nn.Module:
    """BCEWithLogitsLoss sem pesos de classe e sem reamostragem (reduction='mean')."""
    if loss_config:
        raise ValueError(
            "build_loss não aceita parâmetros: a perda é BCEWithLogitsLoss sem pesos "
            "de classe nem reamostragem"
        )
    return nn.BCEWithLogitsLoss(reduction="mean")


def build_optimizer(model: nn.Module, optimizer_config: Mapping[str, Any] | None = None) -> torch.optim.Optimizer:
    """Adam com a taxa de aprendizagem indicada na config (por omissão 1e-3, placeholder)."""
    config = dict(DEFAULT_OPTIMIZER_CONFIG)
    if optimizer_config:
        unknown = set(optimizer_config) - set(DEFAULT_OPTIMIZER_CONFIG)
        if unknown:
            raise ValueError(f"Chaves de optimizer_config desconhecidas: {sorted(unknown)}")
        config.update(optimizer_config)

    lr = float(config["lr"])
    if not lr > 0:
        raise ValueError("lr deve ser positivo")
    return torch.optim.Adam(model.parameters(), lr=lr)


def _prepare_batch(batch: Any, device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    """Valida (X, y, meta) de uma sequência completa e envia X e y para o dispositivo."""
    X, y = batch[0], batch[1]
    if X.dim() != 3 or X.shape[0] != 1:
        raise ValueError(f"X deve ter forma [1, C, N], recebido {tuple(X.shape)}")
    if y.shape != (1, 1, X.shape[2]):
        raise ValueError(f"y deve ter forma [1, 1, N={X.shape[2]}], recebido {tuple(y.shape)}")
    return X.to(device=device, dtype=torch.float32), y.to(device=device, dtype=torch.float32)


def train_one_epoch(
    model: nn.Module,
    loader: Iterable,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device,
) -> dict:
    """Uma passagem pelo loader, um passo de Adam por sequência.

    A perda registada em cada passo é calculada ANTES do passo de otimização
    (é a perda com os pesos desse momento).
    """
    model.train()
    n_steps = 0
    n_points = 0
    sum_step_loss = 0.0
    sum_point_loss = 0.0

    start = time.perf_counter()
    for batch in loader:
        X, y = _prepare_batch(batch, device)
        n = X.shape[2]

        optimizer.zero_grad()
        logits = model(X)
        loss = loss_fn(logits, y)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"Perda não finita no passo {n_steps}: {loss.item()}")
        loss.backward()
        optimizer.step()

        value = float(loss.item())
        n_steps += 1
        n_points += n
        sum_step_loss += value
        sum_point_loss += value * n

    seconds = time.perf_counter() - start
    if n_steps == 0:
        raise ValueError("O loader não devolveu nenhuma sequência")

    return {
        "mean_loss_per_step": sum_step_loss / n_steps,
        "mean_loss_per_point": sum_point_loss / n_points,
        "n_steps": n_steps,
        "n_points": n_points,
        "seconds": seconds,
    }


def _sigmoid(z: np.ndarray) -> np.ndarray:
    """Sigmoid em NumPy com recorte para evitar overflow. Usada só na avaliação."""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500.0, 500.0)))


def _ratio(numerator: int, denominator: int) -> tuple[float, bool]:
    """Divisão com denominador zero devolvendo 0.0 e flag explícita."""
    if denominator == 0:
        return 0.0, True
    return numerator / denominator, False


@torch.no_grad()
def evaluate_training_subset(
    model: nn.Module,
    loader: Iterable,
    loss_fn: nn.Module,
    device: torch.device,
    threshold: float = 0.5,
) -> dict:
    """Perda e métricas diagnósticas simples sobre um subconjunto de TREINO/monitor interno.

    Não é validação nem teste. Serve apenas para diagnóstico de ajuste.
    As métricas são calculadas em NumPy sobre todos os pontos de todas as sequências.
    Quando uma divisão tem denominador zero, o valor é 0.0 e a flag fica True.
    """
    model.eval()
    tp = fp = fn = tn = 0
    n_steps = 0
    n_points = 0
    sum_step_loss = 0.0
    sum_point_loss = 0.0

    for batch in loader:
        X, y = _prepare_batch(batch, device)
        n = X.shape[2]

        logits = model(X)
        loss = loss_fn(logits, y)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"Perda não finita na avaliação: {loss.item()}")
        value = float(loss.item())
        n_steps += 1
        n_points += n
        sum_step_loss += value
        sum_point_loss += value * n

        z = logits.detach().cpu().numpy().astype(np.float64).reshape(-1)
        y_np = y.detach().cpu().numpy().astype(np.float64).reshape(-1)
        if not np.isin(y_np, (0.0, 1.0)).all():
            raise ValueError("Os alvos y devem ser binários (0 ou 1)")
        target = y_np > 0.5

        probs = _sigmoid(z)  # única aplicação da Sigmoid
        pred = probs >= threshold

        tp += int(np.sum(pred & target))
        fp += int(np.sum(pred & ~target))
        fn += int(np.sum(~pred & target))
        tn += int(np.sum(~pred & ~target))

    if n_steps == 0:
        raise ValueError("O loader não devolveu nenhuma sequência")

    precision, precision_zero = _ratio(tp, tp + fp)
    sensitivity, sensitivity_zero = _ratio(tp, tp + fn)
    f1, f1_zero = _ratio(2 * tp, 2 * tp + fp + fn)
    iou, iou_zero = _ratio(tp, tp + fp + fn)

    return {
        "result_kind": "train_or_internal_monitor",
        "threshold": float(threshold),
        "mean_loss_per_step": sum_step_loss / n_steps,
        "mean_loss_per_point": sum_point_loss / n_points,
        "n_steps": n_steps,
        "n_points": n_points,
        "counts": {"TP": tp, "FP": fp, "FN": fn, "TN": tn},
        "metrics": {
            "precision": precision,
            "sensitivity": sensitivity,
            "f1": f1,
            "iou": iou,
        },
        "zero_division_flags": {
            "precision": precision_zero,
            "sensitivity": sensitivity_zero,
            "f1": f1_zero,
            "iou": iou_zero,
        },
    }


def train_model(model, train_seqs, monitor_seqs, config: dict, device, scaler: dict,
                input_channels: list[str], checkpoint_path=None, log=print) -> dict:
    """Treina com paragem antecipada na perda por ponto da monitorização interna.

    Só treino oficial: `train_seqs` e `monitor_seqs` vêm da partição interna do treino.
    Para quando: (a) a perda de monitorização não melhora (por mais de `min_delta`) durante
    `patience` épocas; (b) se atinge `max_epochs`; (c) o tempo decorrido ultrapassa
    `time_budget_seconds` (verificado no fim de cada época). Guarda o melhor checkpoint (em
    memória e, se indicado, em disco) e restaura-o no modelo no fim.
    Devolve histórico, época do melhor modelo, motivo da paragem e tempos.
    """
    import copy

    from .artifacts import save_checkpoint
    from .data import build_sequence_loader

    loss_fn = build_loss()
    optimizer = build_optimizer(model, {"lr": config["lr"]})
    monitor_loader = build_sequence_loader(monitor_seqs, shuffle=False, seed=0)

    history, best_loss, best_epoch, best_state, stale = [], float("inf"), 0, None, 0
    stop_reason = "max_epochs"
    t0 = time.perf_counter()
    for epoch in range(1, config["max_epochs"] + 1):
        loader = build_sequence_loader(train_seqs, shuffle=True, seed=config["seed"] + epoch)
        tr = train_one_epoch(model, loader, optimizer, loss_fn, device)
        mon = evaluate_training_subset(model, monitor_loader, loss_fn, device, config["threshold"])
        elapsed = time.perf_counter() - t0
        improved = mon["mean_loss_per_point"] < best_loss - config["min_delta"]
        if improved:
            best_loss, best_epoch, stale = mon["mean_loss_per_point"], epoch, 0
            best_state = copy.deepcopy(model.state_dict())
            if checkpoint_path is not None:
                save_checkpoint(checkpoint_path, model, optimizer, config, scaler, epoch,
                                {"monitor_loss_per_point": best_loss, "monitor": mon["metrics"]},
                                input_channels)
        else:
            stale += 1
        history.append({
            "epoch": epoch, "train_loss_per_point": tr["mean_loss_per_point"],
            "train_loss_per_step": tr["mean_loss_per_step"], "train_seconds": tr["seconds"],
            "monitor_loss_per_point": mon["mean_loss_per_point"],
            "monitor_precision": mon["metrics"]["precision"],
            "monitor_sensitivity": mon["metrics"]["sensitivity"],
            "monitor_f1": mon["metrics"]["f1"], "monitor_iou": mon["metrics"]["iou"],
            "improved": improved, "elapsed_seconds": elapsed})
        log(f"época {epoch:3d} | treino {tr['mean_loss_per_point']:.4f} | monitor "
            f"{mon['mean_loss_per_point']:.4f} | F1 monitor {mon['metrics']['f1']:.3f} | "
            f"{'melhor' if improved else f'sem melhoria {stale}/{config['patience']}'} | {elapsed:6.1f}s")
        if stale >= config["patience"]:
            stop_reason = "paragem_antecipada"
            break
        if elapsed > config["time_budget_seconds"]:
            stop_reason = "orcamento_de_tempo"
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    return {"history": history, "best_epoch": best_epoch, "best_monitor_loss_per_point": best_loss,
            "stop_reason": stop_reason, "epochs_run": len(history),
            "total_seconds": time.perf_counter() - t0}
