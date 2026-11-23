"""Conta saltos e inversões de rumo por viagem, só no conjunto de TREINO.

- Salto: par de pontos consecutivos da mesma viagem com velocidade implícita acima
  de THRESHOLD_KN (speed_calc_mps convertida para nós).
- Inversão de rumo: par com |signed_turn_calc_deg| acima de TURN_DEG (170 graus).

Só lê data/123_fishing_trajs_clean_train.parquet. Não lê validação nem teste (REV-016).
Não altera dados. Os resultados são só diagnóstico, sem remoção de nada (REV-012).

Saídas (em results/anomalies_train/, ignoradas pelo git):
- per_trip.csv              : uma linha por viagem.
- summary.json              : totais, médias, medianas, mínimos, máximos e desvios.
- jumps_per_trip.png        : histograma de saltos por viagem.
- inversions_per_trip.png   : histograma de inversões de rumo por viagem.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.count_anomalies_train
    iach-ais-venv-4/bin/python -m ais.cli.count_anomalies_train --threshold-kn 30
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

KNOTS_PER_MPS = 1.94384
TURN_DEG = 170.0
DEFAULT_THRESHOLD_KN = 30.0
INPUT_PATH = Path("data/123_fishing_trajs_clean_train.parquet")
OUT_DIR = Path("results/anomalies_train")


def count_per_trip(frame: pd.DataFrame, threshold_kn: float, turn_deg: float = TURN_DEG) -> pd.DataFrame:
    """Devolve uma linha por viagem com pares válidos, saltos e inversões."""
    speed_kn = frame["speed_calc_mps"] * KNOTS_PER_MPS
    jump = speed_kn > threshold_kn
    reversal = frame["signed_turn_calc_deg"].abs() > turn_deg
    valid_speed = speed_kn.notna()
    valid_turn = frame["signed_turn_calc_deg"].notna()
    work = pd.DataFrame({
        "id": frame["id"],
        "pares_velocidade": valid_speed,
        "pares_rumo": valid_turn,
        "saltos": jump & valid_speed,
        "inversoes": reversal & valid_turn,
    })
    grouped = work.groupby("id", sort=True).agg(
        pares_velocidade=("pares_velocidade", "sum"),
        pares_rumo=("pares_rumo", "sum"),
        saltos=("saltos", "sum"),
        inversoes=("inversoes", "sum"),
    )
    grouped["pontos"] = frame.groupby("id").size()
    grouped["pct_saltos"] = 100.0 * grouped["saltos"] / grouped["pares_velocidade"]
    grouped["pct_inversoes"] = 100.0 * grouped["inversoes"] / grouped["pares_rumo"]
    grouped = grouped.reset_index()
    grouped.insert(1, "pontos_total", grouped.pop("pontos"))
    return grouped


def describe(series: pd.Series) -> dict:
    return {
        "total": int(series.sum()),
        "media": float(series.mean()),
        "mediana": float(series.median()),
        "minimo": int(series.min()),
        "maximo": int(series.max()),
        "desvio_padrao": float(series.std(ddof=1)),
        "viagens_com_pelo_menos_1": int((series > 0).sum()),
    }


def summary(per_trip: pd.DataFrame, threshold_kn: float) -> dict:
    total_vel = int(per_trip["pares_velocidade"].sum())
    total_rumo = int(per_trip["pares_rumo"].sum())
    jumps = per_trip["saltos"]
    rev = per_trip["inversoes"]
    return {
        "limiar_velocidade_nos": threshold_kn,
        "limiar_inversao_graus": TURN_DEG,
        "viagens": int(len(per_trip)),
        "pares_velocidade": total_vel,
        "pares_rumo": total_rumo,
        "saltos_por_viagem": describe(jumps),
        "inversoes_por_viagem": describe(rev),
        "taxa_saltos_por_mil_pares": 1000.0 * int(jumps.sum()) / total_vel,
        "taxa_inversoes_por_mil_pares": 1000.0 * int(rev.sum()) / total_rumo,
    }


def histogram(values: pd.Series, title: str, xlabel: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    upper = max(int(values.max()), 1)
    bins = np.arange(-0.5, upper + 1.5, 1.0) if upper <= 60 else 40
    ax.hist(values, bins=bins, color="#455A64", edgecolor="white")
    ax.axvline(values.mean(), color="#F57F17", linestyle="--", label=f"média = {values.mean():.1f}")
    ax.axvline(values.median(), color="#1565C0", linestyle=":", label=f"mediana = {values.median():.1f}")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("número de viagens")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Conta saltos e inversões de rumo por viagem (treino).")
    parser.add_argument("--threshold-kn", type=float, default=DEFAULT_THRESHOLD_KN)
    args = parser.parse_args()

    if not INPUT_PATH.exists():
        print(f"Base do treino não encontrada: {INPUT_PATH}", file=sys.stderr)
        return 1

    frame = pd.read_parquet(INPUT_PATH)
    if frame["split"].unique().tolist() != ["train"]:
        print("Erro: a base não contém só o conjunto de treino.", file=sys.stderr)
        return 2

    per_trip = count_per_trip(frame, args.threshold_kn)
    stats = summary(per_trip, args.threshold_kn)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_trip.to_csv(OUT_DIR / "per_trip.csv", index=False, float_format="%.4f")
    with (OUT_DIR / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, ensure_ascii=False, indent=2)
    histogram(per_trip["saltos"], f"Saltos acima de {args.threshold_kn:g} nós por viagem (treino)",
              f"saltos acima de {args.threshold_kn:g} nós", OUT_DIR / "jumps_per_trip.png")
    histogram(per_trip["inversoes"], "Inversões de rumo acima de 170° por viagem (treino)",
              "inversões acima de 170°", OUT_DIR / "inversions_per_trip.png")

    pd.set_option("display.max_rows", 200)
    pd.set_option("display.width", 160)
    print(per_trip.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nResumo do conjunto de treino:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\nSaídas em: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
