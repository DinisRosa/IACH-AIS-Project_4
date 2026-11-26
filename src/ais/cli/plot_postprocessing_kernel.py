"""Figura da janela do pós-processamento para a proposta (Secção 10; REV-056, janela de 301 pontos em REV-059).

Só usa os pesos do filtro (configuração) e um exemplo SINTÉTICO; não lê nenhum dado do projeto.
Escreve latex/figures/posproc_janela.png.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.plot_postprocessing_kernel
"""
from __future__ import annotations

import numpy as np

from ais.cli.build_final_results import INK, NAV, PESCA, plt, save
from ais.phase1.postprocessing import gaussian_kernel, smooth_trip

SIZE = 301           # janela da v2 (protocolo posproc_validation_v2)
SIGMA = SIZE / 6
THRESHOLD = 0.65     # limiar congelado da referência (results/baseline_frozen)


def synthetic_example() -> np.ndarray:
    """Probabilidades sintéticas: navegação, pesca com buracos de 1, 20 e 40 pontos, navegação com uma ilha."""
    rng = np.random.default_rng(42)
    p = np.r_[np.full(400, 0.05), np.full(900, 0.95), np.full(500, 0.05)]
    p[150:210] = 0.9      # 60 pontos de pesca isolados no meio de navegação
    p[550] = 0.1          # 1 ponto de navegação no meio de pesca
    p[800:820] = 0.1      # 20 pontos
    p[1050:1090] = 0.1    # 40 pontos
    return np.clip(p + rng.normal(0, 0.03, len(p)), 0, 1)


def main() -> None:
    w = gaussian_kernel(SIZE, SIGMA)
    h = SIZE // 2
    p = synthetic_example()
    s = smooth_trip(p, w)
    x = np.arange(len(p))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 2.8), gridspec_kw={"width_ratios": [1, 2.2]})
    a1.fill_between(np.arange(-h, h + 1), w, color=INK, alpha=0.85, lw=0)
    a1.set_xlabel("posição em relação ao ponto (pontos)")
    a1.set_ylabel("peso")
    a1.set_title(f"Janela gaussiana: {SIZE} pontos, σ = {SIGMA:.1f}", fontsize=9)

    a2.plot(x, p, ".", color="0.6", ms=2, label="probabilidade da CNN")
    a2.plot(x, s, "-", color=INK, lw=1.4, label="depois do filtro")
    a2.axhline(THRESHOLD, color="0.3", ls="--", lw=0.8, label=f"limiar {THRESHOLD:.2f}")
    before, after = p >= THRESHOLD, s >= THRESHOLD
    for cls, col in ((True, PESCA), (False, NAV)):
        m = (before != after) & (after == cls)
        a2.plot(x[m], s[m], "|", color=col, ms=6)
    a2.set_xlabel("ponto da viagem (exemplo sintético)")
    a2.set_ylabel("P(pesca)")
    a2.set_ylim(-0.05, 1.05)
    a2.set_title("Efeito: os buracos passam à classe dos vizinhos (traços coloridos)", fontsize=9)
    a2.legend(fontsize=7, loc="upper right", frameon=False)  # canto sem dados (acima do limiar, à direita)
    fig.tight_layout()
    save(fig, "posproc_janela.png")


if __name__ == "__main__":
    main()
