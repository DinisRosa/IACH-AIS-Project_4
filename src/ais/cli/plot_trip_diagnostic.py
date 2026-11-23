"""Gráfico de diagnóstico de UMA viagem: classe real e classe prevista pela referência, J0 e J50 (REV-049).

Só lê as previsões por ponto que a abertura autorizada do `test` já produziu
(`results/baseline_frozen/predictions_test_baseline.csv` e
`results/windows_j{0,50}/predictions_test_selected.csv`). NÃO abre o parquet do `test` nem o `validation`.
Mostra, por ponto: a classe real, a prevista por cada modelo e a probabilidade de pesca (com o limiar de
cada modelo); em J0 marca as fronteiras das janelas de 64 pontos. A exatidão de cada modelo nesta viagem
é calculada aqui. É um diagnóstico: não serve para escolher nada.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.plot_trip_diagnostic 219001624-2
Saída: results/diagnostic_trip/<id>_classes.png (não versionada).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from ais.cli.build_final_results import GREY, INK, INK2, NAV, PESCA, plt

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "baseline": ROOT / "results" / "baseline_frozen" / "predictions_test_baseline.csv",
    "J0": ROOT / "results" / "windows_j0" / "predictions_test_selected.csv",
    "J50": ROOT / "results" / "windows_j50" / "predictions_test_selected.csv",
}
COLORS = {"baseline": GREY, "J0": "#2a9d8f", "J50": "#7b5ea7"}
CMAP = ListedColormap([NAV, PESCA])


def load_trip(trip: str) -> dict[str, pd.DataFrame]:
    out = {}
    for name, path in SOURCES.items():
        df = pd.read_csv(path, usecols=lambda c: c in {"id", "point_id", "t", "target", "p_fishing", "predicted"})
        df = df[df["id"] == trip].sort_values("t", kind="stable").reset_index(drop=True)
        if df.empty:
            raise SystemExit(f"Viagem {trip!r} não existe nas previsões de {name}.")
        out[name] = df
    n = {len(d) for d in out.values()}
    ids = {tuple(d["point_id"]) for d in out.values()}
    assert len(n) == 1 and len(ids) == 1, "Os três modelos devem ter os mesmos pontos, pela mesma ordem."
    return out


def plot(trip: str, out_dir: Path | None = None) -> tuple[Path, dict]:
    data = load_trip(trip)
    base = data["baseline"]
    target = base["target"].to_numpy()
    acc = {k: float((d["predicted"].to_numpy() == target).mean()) for k, d in data.items()}
    n = len(base)
    x = np.arange(n)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 5.2), gridspec_kw={"height_ratios": [1.5, 1.6]}, sharex=True)
    rows = [("real", target)] + [(f"{k} ({100 * acc[k]:.1f} % certo)", d["predicted"].to_numpy()) for k, d in data.items()]
    for i, (_, arr) in enumerate(rows):
        ax1.imshow(arr[None, :], extent=(-0.5, n - 0.5, -i - 0.9, -i - 0.1), aspect="auto", cmap=CMAP,
                   vmin=0, vmax=1, interpolation="nearest")
    ax1.set_ylim(-len(rows) + 0.0, 0.0)
    ax1.set_yticks([-i - 0.5 for i in range(len(rows))], [r[0] for r in rows], fontsize=8)
    ax1.grid(False)
    ax1.set_title(f"Viagem {trip}: classe por ponto (azul: navegação; laranja: pesca)", fontsize=9)

    for name, d in data.items():
        ax2.plot(x, d["p_fishing"].to_numpy(), color=COLORS[name], lw=1.0, label=f"{name}")
    for b in range(0, n, 64):
        ax2.axvline(b, color=COLORS["J0"], lw=0.4, alpha=0.35)
    ax2.plot(x, target, color=INK, lw=0.8, ls=":", label="real (0 / 1)")
    ax2.set(ylabel="Probabilidade de pesca", xlabel="Ponto da viagem (as linhas finas marcam as janelas de 64 pontos de J0)",
            ylim=(-0.03, 1.03), xlim=(-0.5, n - 0.5))
    ax2.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.15))
    fig.tight_layout()
    out_dir = out_dir or ROOT / "results" / "diagnostic_trip"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{trip}_classes.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path, {"n_points": n, "accuracy": acc, "pontos_de_pesca_reais": int(target.sum())}


if __name__ == "__main__":
    p, info = plot(sys.argv[1])
    print(p, info)
