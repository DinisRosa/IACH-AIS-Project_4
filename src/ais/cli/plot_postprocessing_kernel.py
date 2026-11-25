"""Figura da janela do pós-processamento para a proposta (Secção 10, REV-056).

Só usa os pesos do filtro (configuração) e um exemplo SINTÉTICO; não lê nenhum dado do projeto.
Escreve latex/figures/posproc_janela.png.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.plot_postprocessing_kernel
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ais.cli.build_final_results import INK, NAV, PESCA, plt, save
from ais.phase1.postprocessing import SIGMA, WINDOW_SIZE, gaussian_kernel, smooth_trip

ROOT = Path(__file__).resolve().parents[3]
THRESHOLD = 0.65  # limiar congelado da referência (results/baseline_frozen)


def synthetic_example() -> np.ndarray:
    """Probabilidades sintéticas: navegação, um ponto isolado de pesca, pesca com uma falha curta, navegação."""
    rng = np.random.default_rng(42)
    p = np.r_[np.full(30, 0.05), np.full(40, 0.95), np.full(30, 0.05)]
    p[12] = 0.9          # pesca isolada no meio de navegação
    p[48:50] = 0.1       # dois pontos de navegação no meio de pesca
    p[85] = 0.8          # outro ponto isolado
    return np.clip(p + rng.normal(0, 0.03, len(p)), 0, 1)


def main() -> None:
    w = gaussian_kernel()
    h = WINDOW_SIZE // 2
    p = synthetic_example()
    s = smooth_trip(p, w)
    x = np.arange(len(p))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 2.8), gridspec_kw={"width_ratios": [1, 2.2]})
    a1.bar(np.arange(-h, h + 1), w, color=INK, width=0.7)
    a1.set_xticks(np.arange(-h, h + 1, 2))
    a1.set_xlabel("posição em relação ao ponto (pontos)")
    a1.set_ylabel("peso")
    a1.set_title(f"Janela gaussiana: {WINDOW_SIZE} pontos, σ = {SIGMA:.2f}", fontsize=9)

    a2.plot(x, p, ".", color="0.55", ms=4, label="probabilidade da CNN")
    a2.plot(x, s, "-", color=INK, lw=1.4, label="depois do filtro")
    a2.axhline(THRESHOLD, color="0.3", ls="--", lw=0.8, label=f"limiar {THRESHOLD:.2f}")
    for xi, pi, si in zip(x, p, s):
        if (pi >= THRESHOLD) != (si >= THRESHOLD):
            a2.plot(xi, si, "o", mfc="none", mec=PESCA if si >= THRESHOLD else NAV, ms=7)
    a2.set_xlabel("ponto da viagem (exemplo sintético)")
    a2.set_ylabel("P(pesca)")
    a2.set_ylim(-0.05, 1.05)
    a2.set_title("Efeito: os pontos isolados passam à classe dos vizinhos (círculos)", fontsize=9)
    a2.legend(fontsize=7, loc="center right", frameon=False)
    fig.tight_layout()
    save(fig, "posproc_janela.png")


if __name__ == "__main__":
    main()
