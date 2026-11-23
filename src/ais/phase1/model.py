"""CNN 1D de referência (viagem completa) para segmentação por ponto de viagens AIS.

Contrato:
- Entrada X [B, C, N] float32, com C canais de características (por omissão 7).
  Cada passo de treino usa uma sequência completa (batch_size=1); não há padding
  nesta fase, por isso não há máscaras.
- Saída LOGITS [B, 1, N]. O modelo NÃO aplica Sigmoid: a BCEWithLogitsLoss recebe
  logits e a probabilidade é calculada fora do modelo, uma única vez.
- Sem pooling, stride, dilatação, normalização de lote ou dropout: N é preservado
  para qualquer N >= 1.

Arquitetura por omissão (Conv1D, padding = k // 2 para manter N):
    Conv1D(C -> 32, k=5) ReLU -> Conv1D(32 -> 64, k=5) ReLU
    -> Conv1D(64 -> 32, k=5) ReLU -> Conv1D(32 -> 1, k=1)
Campo recetivo = 1 + sum(k_i - 1) = 13 pontos (ver `receptive_field`).
"""

from __future__ import annotations

from typing import Any, Mapping

import torch
from torch import nn

DEFAULT_MODEL_CONFIG: dict[str, Any] = {
    "hidden_channels": (32, 64, 32),
    "kernel_sizes": (5, 5, 5),
    "output_kernel_size": 1,
}

_ALLOWED_KEYS = frozenset(DEFAULT_MODEL_CONFIG)


def _resolve_config(model_config: Mapping[str, Any] | None) -> dict[str, Any]:
    """Junta a configuração recebida à por omissão e valida-a.

    Kernels ímpares são obrigatórios para que padding = k // 2 preserve N.
    """
    config = dict(DEFAULT_MODEL_CONFIG)
    if model_config:
        unknown = set(model_config) - _ALLOWED_KEYS
        if unknown:
            raise ValueError(f"Chaves de model_config desconhecidas: {sorted(unknown)}")
        config.update(model_config)

    hidden = tuple(int(c) for c in config["hidden_channels"])
    kernels = tuple(int(k) for k in config["kernel_sizes"])
    out_kernel = int(config["output_kernel_size"])

    if len(hidden) != len(kernels):
        raise ValueError("hidden_channels e kernel_sizes devem ter o mesmo comprimento")
    if any(c <= 0 for c in hidden):
        raise ValueError("hidden_channels deve conter inteiros positivos")
    for k in (*kernels, out_kernel):
        if k <= 0 or k % 2 == 0:
            raise ValueError(f"Kernel {k} inválido: são necessários kernels ímpares e positivos")

    return {
        "hidden_channels": hidden,
        "kernel_sizes": kernels,
        "output_kernel_size": out_kernel,
    }


def receptive_field(model_config: Mapping[str, Any] | None = None) -> int:
    """Campo recetivo, em pontos, de uma saída da rede (stride 1, dilatação 1).

    Fórmula: 1 + soma(k_i - 1) sobre todas as convoluções. Com a arquitetura por
    omissão (três kernels 5 e uma convolução 1x1) dá 1 + 3 * 4 + 0 = 13.
    """
    config = _resolve_config(model_config)
    rf = 1
    for k in (*config["kernel_sizes"], config["output_kernel_size"]):
        rf += k - 1
    return rf


class FullTripCNN(nn.Module):
    """CNN 1D que produz um logit por ponto original de uma viagem completa."""

    def __init__(self, model_config: Mapping[str, Any] | None = None, n_channels: int = 7):
        super().__init__()
        if int(n_channels) <= 0:
            raise ValueError("n_channels deve ser positivo")
        self.n_channels = int(n_channels)
        self.model_config = _resolve_config(model_config)

        layers: list[nn.Module] = []
        in_channels = self.n_channels
        for out_channels, kernel in zip(
            self.model_config["hidden_channels"], self.model_config["kernel_sizes"]
        ):
            layers.append(nn.Conv1d(in_channels, out_channels, kernel, padding=kernel // 2))
            layers.append(nn.ReLU())
            in_channels = out_channels

        out_kernel = self.model_config["output_kernel_size"]
        layers.append(nn.Conv1d(in_channels, 1, out_kernel, padding=out_kernel // 2))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """x [B, C, N] -> logits [B, 1, N]. Sem Sigmoid.

        `mask` [B, 1, N] (1 = ponto real, 0 = enchimento) é opcional e serve só para empilhar
        janelas de comprimentos diferentes num lote (Marco 4). Se existir, as posições de
        enchimento voltam a zero depois de cada ReLU; assim cada janela recebe, nas bordas, o
        mesmo zero que o padding das convoluções lhe daria se fosse processada sozinha, e a
        saída nas posições reais não depende do enchimento. Sem máscara (baseline) nada muda.
        """
        if x.dim() != 3:
            raise ValueError(f"Entrada deve ter forma [B, C, N], recebido {tuple(x.shape)}")
        if x.shape[1] != self.n_channels:
            raise ValueError(
                f"Esperados {self.n_channels} canais, recebidos {x.shape[1]}"
            )
        if mask is None:
            return self.net(x)
        if mask.shape != (x.shape[0], 1, x.shape[2]):
            raise ValueError(f"mask deve ter forma [B, 1, N], recebido {tuple(mask.shape)}")
        x = x * mask  # o enchimento da entrada também fica a zero, qualquer que seja o seu valor
        for layer in self.net:
            x = layer(x)
            if isinstance(layer, nn.ReLU):
                x = x * mask
        return x


def build_cnn(model_config: Mapping[str, Any] | None = None, n_channels: int = 7) -> nn.Module:
    """Constrói a CNN de viagem completa (`FullTripCNN`)."""
    return FullTripCNN(model_config=model_config, n_channels=n_channels)


def count_parameters(model: nn.Module) -> int:
    """Número total de parâmetros treináveis e não treináveis do modelo."""
    return sum(p.numel() for p in model.parameters())
