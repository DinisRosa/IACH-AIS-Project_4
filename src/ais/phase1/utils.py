"""Utilitários de reprodutibilidade e seleção de dispositivo (fase 1).

A reprodutibilidade aqui registada refere-se ao mesmo ambiente (mesma versão de
Python/PyTorch/NumPy e mesmo hardware). Não se promete identidade numérica entre
máquinas diferentes.
"""

from __future__ import annotations

import platform
import random

import numpy as np
import torch


def set_reproducibility(seed: int, deterministic: bool = True) -> dict:
    """Fixa seeds de random, NumPy e PyTorch e devolve metadados da execução.

    deterministic=True pede algoritmos deterministas ao PyTorch com warn_only=True:
    se uma operação não tiver versão determinista, o PyTorch avisa em vez de falhar.
    """
    seed = int(seed)
    if not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed deve estar entre 0 e 2**32 - 1")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(bool(deterministic), warn_only=True)

    return {
        "seed": seed,
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "numpy_version": np.__version__,
        "deterministic": bool(deterministic),
        "deterministic_warn_only": True,
        "num_threads": torch.get_num_threads(),
    }


def select_device(requested: str = "cpu") -> torch.device:
    """Escolhe o dispositivo de treino: 'cpu', 'cuda' ou 'auto'.

    'cpu' é o valor por omissão. 'cuda' sem GPU disponível levanta RuntimeError
    (não há recurso silencioso para CPU). 'auto' usa CUDA apenas se estiver disponível.
    """
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA pedido mas indisponível neste ambiente")
        return torch.device("cuda")
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    raise ValueError(f"Dispositivo desconhecido: {requested!r} (use 'cpu', 'cuda' ou 'auto')")
