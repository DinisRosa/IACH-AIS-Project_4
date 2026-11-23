"""Smoke test de treino sobre uma CÓPIA do modelo (fase 1).

Verifica, com um único lote sintético ou de treino, que o modelo faz forward com a
forma esperada, que a perda é finita, que todos os parâmetros recebem gradientes
não nulos e finitos e que um passo de Adam altera os pesos. O modelo original não é
alterado: todo o trabalho é feito numa cópia (copy.deepcopy).
"""

from __future__ import annotations

import copy
from typing import Any

import torch
from torch import nn

from .training import build_optimizer


def run_training_smoke_test(
    model: nn.Module,
    train_batch: Any,
    loss_fn: nn.Module,
    device: torch.device,
) -> dict:
    """Executa o smoke test e devolve um relatório com booleanos e valores medidos.

    train_batch: (X [1, C, N], y [1, 1, N], ...). Deve ser dados sintéticos ou de treino.
    Levanta AssertionError se alguma verificação falhar e ValueError se a entrada
    não tiver a forma esperada.
    """
    if not isinstance(train_batch, (tuple, list)) or len(train_batch) < 2:
        raise ValueError("train_batch deve ser (X, y, ...)")

    X = train_batch[0].to(device=device, dtype=torch.float32)
    y = train_batch[1].to(device=device, dtype=torch.float32)
    if X.dim() != 3 or X.shape[0] != 1:
        raise ValueError(f"X deve ter forma [1, C, N], recebido {tuple(X.shape)}")
    if y.shape != (1, 1, X.shape[2]):
        raise ValueError(f"y deve ter forma [1, 1, N], recebido {tuple(y.shape)}")
    B, _, N = X.shape

    original_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    work = copy.deepcopy(model).to(device)
    work.train()
    params = list(work.named_parameters())

    report: dict[str, Any] = {
        "input_shape": list(X.shape),
    }

    # Forward: a forma é verificada antes da perda, para que a falha seja clara
    logits = work(X)
    report["output_shape"] = list(logits.shape)
    report["forward_shape_ok"] = tuple(logits.shape) == (B, 1, N)
    if not report["forward_shape_ok"]:
        raise AssertionError(
            f"Saída com forma {tuple(logits.shape)}, esperado {(B, 1, N)}. Relatório: {report}"
        )
    loss = loss_fn(logits, y)
    report["loss_value"] = float(loss.item())
    report["loss_finite"] = bool(torch.isfinite(loss).item())

    # Gradientes
    work.zero_grad(set_to_none=True)
    loss.backward()
    missing = [name for name, p in params if p.grad is None]
    nonfinite = [name for name, p in params if p.grad is not None and not torch.isfinite(p.grad).all()]
    zero = [name for name, p in params if p.grad is None or float(p.grad.abs().max().item()) == 0.0]
    max_abs_grad = max(
        (float(p.grad.abs().max().item()) for _, p in params if p.grad is not None),
        default=0.0,
    )
    report["n_parameter_tensors"] = len(params)
    report["grads_missing"] = missing
    report["grads_nonfinite"] = nonfinite
    report["grads_zero"] = zero
    report["max_abs_grad"] = max_abs_grad
    report["grads_all_present_and_finite"] = not missing and not nonfinite
    report["grads_all_nonzero"] = not zero

    # Um passo de Adam deve alterar todos os tensores (todos têm gradiente não nulo)
    before = {name: p.detach().clone() for name, p in params}
    optimizer = build_optimizer(work)
    optimizer.step()
    changes = {name: float((p.detach() - before[name]).abs().max().item()) for name, p in params}
    changed = [name for name, delta in changes.items() if delta > 0.0]
    report["optimizer_step_changed_all_tensors"] = len(changed) == len(params)
    report["max_abs_weight_change"] = max(changes.values(), default=0.0)

    # O original não pode ter sido alterado
    current_state = model.state_dict()
    report["original_unchanged"] = all(
        torch.equal(current_state[k].detach(), v) for k, v in original_state.items()
    )

    checks = [
        "forward_shape_ok",
        "loss_finite",
        "grads_all_present_and_finite",
        "grads_all_nonzero",
        "optimizer_step_changed_all_tensors",
        "original_unchanged",
    ]
    failed = [name for name in checks if not report[name]]
    report["all_checks_passed"] = not failed
    if failed:
        raise AssertionError(f"Smoke test de treino falhou: {failed}. Relatório: {report}")
    return report
