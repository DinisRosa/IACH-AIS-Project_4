"""Verificação de unidades e convenções, apenas com o conjunto de treino.

Objetivo (docs/01 §2 e §9): confirmar hipóteses sobre unidades antes de
recalcular variáveis. Não usa validação nem teste: as linhas desses conjuntos são
descartadas logo a seguir a lerem o `id`, e nenhum valor delas é guardado.

Hipóteses testadas:
- x/y estão em metros (distância plana entre pontos consecutivos ≈ distância
  geodésica calculada a partir de longitude/latitude).
- distance_gap está em metros (≈ haversine entre pontos consecutivos).
- time_gap está em segundos (≈ diferença de t em segundos).
- euc_speed está em nós (≈ distance_gap/time_gap × 1,94384449).
- bearing está em graus e segue a convenção de azimute a partir do norte.
- signed_turn está em graus e tem o sinal coerente com a variação de bearing.

Limitação: distanceToShore não tem referência interna, por isso só é descrito
em distribuição e marcado como não confirmado.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.check_units_train
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SEED = 42
DATA_PATH = Path("data/123_fishing_trajs.csv")
MANIFEST_PATH = Path("manifests/split_manifest_seed42.csv")
OUTPUT_DIR = Path("results/units_check_train")
EARTH_RADIUS_M = 6_371_008.8
KNOTS_PER_MPS = 1.9438444924406
PLOT_SAMPLE = 20_000

# Colunas usadas. `label` não é necessária para verificar unidades.
COLUMNS = [
    "id", "t", "longitude", "latitude", "x", "y",
    "signed_turn", "bearing", "time_gap", "distance_gap", "euc_speed", "distanceToShore",
]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_train_ids(manifest: Path) -> set[str]:
    table = pd.read_csv(manifest, dtype={"id": str, "split": str})
    return set(table.loc[table["split"] == "train", "id"])


def load_train_rows(data: Path, train_ids: set[str]) -> pd.DataFrame:
    """Lê o CSV por blocos e mantém apenas linhas cujo id pertence ao treino."""
    kept = []
    total = 0
    for chunk in pd.read_csv(
        data, usecols=COLUMNS, dtype={"id": str}, chunksize=200_000
    ):
        total += len(chunk)
        mask = chunk["id"].isin(train_ids)
        kept.append(chunk.loc[mask])
    frame = pd.concat(kept, ignore_index=True)
    frame["t"] = pd.to_datetime(frame["t"], format="%Y-%m-%d %H:%M:%S")
    return frame.sort_values(["id", "t"], kind="stable").reset_index(drop=True), total


def haversine_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def initial_bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0


def wrap_180(angle):
    return (angle + 180.0) % 360.0 - 180.0


def describe(values: np.ndarray) -> dict:
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"n": 0}
    return {
        "n": int(values.size),
        "median": float(np.median(values)),
        "p05": float(np.percentile(values, 5)),
        "p95": float(np.percentile(values, 95)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def build_consecutive(frame: pd.DataFrame) -> pd.DataFrame:
    """Pares consecutivos dentro do mesmo id. Nunca atravessa viagens."""
    same = frame["id"].eq(frame["id"].shift(1))
    prev = frame.shift(1)
    pairs = pd.DataFrame(
        {
            "id": frame["id"],
            "dt_s": (frame["t"] - prev["t"]).dt.total_seconds(),
            "hav_m": haversine_m(
                prev["latitude"], prev["longitude"], frame["latitude"], frame["longitude"]
            ),
            "xy_m": np.hypot(frame["x"] - prev["x"], frame["y"] - prev["y"]),
            "bearing_calc_deg": initial_bearing_deg(
                prev["latitude"], prev["longitude"], frame["latitude"], frame["longitude"]
            ),
            "bearing": frame["bearing"],
            "signed_turn": frame["signed_turn"],
            "time_gap": frame["time_gap"],
            "distance_gap": frame["distance_gap"],
            "euc_speed": frame["euc_speed"],
            "distanceToShore": frame["distanceToShore"],
            "longitude": frame["longitude"],
            "latitude": frame["latitude"],
            "x": frame["x"],
            "y": frame["y"],
        }
    )
    return pairs.loc[same].reset_index(drop=True)


def main() -> int:
    if not DATA_PATH.exists() or not MANIFEST_PATH.exists():
        print("Ficheiro de dados ou manifesto não encontrado.", file=sys.stderr)
        return 1

    train_ids = load_train_ids(MANIFEST_PATH)
    frame, total_rows = load_train_rows(DATA_PATH, train_ids)
    pairs = build_consecutive(frame)
    pairs = pairs.loc[pairs["dt_s"] > 0].copy()

    # Razões de escala (1,0 = hipótese confirmada).
    pairs["ratio_xy_vs_hav"] = pairs["xy_m"] / pairs["hav_m"]
    pairs["ratio_dist_vs_hav"] = pairs["distance_gap"] / pairs["hav_m"]
    pairs["ratio_dist_vs_xy"] = pairs["distance_gap"] / pairs["xy_m"]
    pairs["ratio_time_vs_dt"] = pairs["time_gap"] / pairs["dt_s"]
    speed_mps = pairs["distance_gap"] / pairs["time_gap"]
    pairs["ratio_euc_speed_vs_mps"] = pairs["euc_speed"] / speed_mps
    pairs["bearing_diff_deg"] = wrap_180(pairs["bearing"] - pairs["bearing_calc_deg"])
    pairs["turn_from_bearing_deg"] = wrap_180(pairs["bearing"].diff())
    same_trip = pairs["id"].eq(pairs["id"].shift(1))
    pairs.loc[~same_trip, "turn_from_bearing_deg"] = np.nan

    summary = {
        "meta": {
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seed": SEED,
            "script": "src/ais/cli/check_units_train.py",
            "data_file": str(DATA_PATH),
            "data_sha256": sha256_of(DATA_PATH),
            "manifest_file": str(MANIFEST_PATH),
            "manifest_sha256": sha256_of(MANIFEST_PATH),
            "train_ids": len(train_ids),
            "rows_in_file": int(total_rows),
            "rows_train_kept": int(len(frame)),
            "consecutive_pairs_used": int(len(pairs)),
            "note": "Só linhas de treino foram guardadas. Validação e teste foram descartados ao ler o id.",
        },
        "hypothesis_tests": {
            "xy_distance_over_haversine": describe(pairs["ratio_xy_vs_hav"].to_numpy()),
            "distance_gap_over_haversine": describe(pairs["ratio_dist_vs_hav"].to_numpy()),
            "distance_gap_over_xy": describe(pairs["ratio_dist_vs_xy"].to_numpy()),
            "time_gap_over_dt_seconds": describe(pairs["ratio_time_vs_dt"].to_numpy()),
            "euc_speed_over_mps": describe(pairs["ratio_euc_speed_vs_mps"].to_numpy()),
            "bearing_minus_calculated_deg_abs": describe(np.abs(pairs["bearing_diff_deg"].to_numpy())),
            "turn_from_bearing_vs_signed_turn_deg_abs": describe(
                np.abs(
                    wrap_180(
                        pairs["turn_from_bearing_deg"].to_numpy()
                        - pairs["signed_turn"].to_numpy()
                    )
                )
            ),
            "distanceToShore": describe(pairs["distanceToShore"].to_numpy()),
        },
        "unit_fit": {
            "euc_speed_mps_factor_candidates": {
                "m_per_s": 1.0,
                "knots": KNOTS_PER_MPS,
                "km_per_h": 3.6,
            },
            "fraction_closest_to": {},
        },
    }

    # Qual o fator (m/s, nós ou km/h) fica mais próximo da razão observada?
    ratios = pairs["ratio_euc_speed_vs_mps"].to_numpy()
    ratios = ratios[np.isfinite(ratios)]
    candidates = np.array([1.0, KNOTS_PER_MPS, 3.6])
    names = ["m_per_s", "knots", "km_per_h"]
    nearest = np.argmin(np.abs(np.log(ratios[:, None]) - np.log(candidates)[None, :]), axis=1)
    for index, name in enumerate(names):
        summary["unit_fit"]["fraction_closest_to"][name] = float(np.mean(nearest == index))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)
    sample_idx = rng.choice(len(pairs), size=min(PLOT_SAMPLE, len(pairs)), replace=False)
    sample = pairs.iloc[sample_idx]

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / name, dpi=110)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(np.log10(pairs["ratio_xy_vs_hav"].dropna()), bins=120)
    ax.axvline(0, color="red", label="razão 1 (metros)")
    ax.set_xlabel("log10(dist. em x,y / haversine)")
    ax.set_ylabel("pares consecutivos")
    ax.legend()
    save(fig, "01_xy_vs_haversine_log_ratio.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(np.log10(pairs["ratio_dist_vs_hav"].dropna()), bins=120)
    ax.axvline(0, color="red", label="razão 1 (metros)")
    ax.set_xlabel("log10(distance_gap / haversine)")
    ax.set_ylabel("pares consecutivos")
    ax.legend()
    save(fig, "02_distance_gap_vs_haversine_log_ratio.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(np.log10(pairs["ratio_euc_speed_vs_mps"].dropna()), bins=120)
    for value, label, color in [(1.0, "m/s", "red"), (KNOTS_PER_MPS, "nós", "green"), (3.6, "km/h", "orange")]:
        ax.axvline(math.log10(value), color=color, label=label)
    ax.set_xlabel("log10(euc_speed / (distance_gap/time_gap))")
    ax.set_ylabel("pares consecutivos")
    ax.legend()
    save(fig, "03_euc_speed_unit_log_ratio.png")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(sample["dt_s"], sample["time_gap"], s=2, alpha=0.3)
    lim = float(np.nanpercentile(sample["dt_s"], 99))
    ax.plot([0, lim], [0, lim], color="red", label="igualdade")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("diferença de t (s)")
    ax.set_ylabel("time_gap (original)")
    ax.legend()
    save(fig, "04_time_gap_vs_dt.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].scatter(sample["longitude"], sample["x"], s=2, alpha=0.3)
    axes[0].set_xlabel("longitude")
    axes[0].set_ylabel("x")
    axes[1].scatter(sample["latitude"], sample["y"], s=2, alpha=0.3)
    axes[1].set_xlabel("latitude")
    axes[1].set_ylabel("y")
    save(fig, "05_lonlat_vs_xy_scatter.png")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(sample["bearing_calc_deg"], sample["bearing"], s=2, alpha=0.3)
    ax.plot([0, 360], [0, 360], color="red", label="igualdade")
    ax.set_xlabel("azimute calculado a partir de lat/lon (graus)")
    ax.set_ylabel("bearing original (graus)")
    ax.legend()
    save(fig, "06_bearing_calc_vs_original.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    turn_ok = sample.dropna(subset=["turn_from_bearing_deg", "signed_turn"])
    ax.scatter(turn_ok["turn_from_bearing_deg"], turn_ok["signed_turn"], s=2, alpha=0.3)
    ax.set_xlabel("variação de bearing entre pontos (graus)")
    ax.set_ylabel("signed_turn original")
    save(fig, "07_signed_turn_vs_bearing_change.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(pairs["distanceToShore"].dropna(), bins=120)
    ax.set_xlabel("distanceToShore (unidade não confirmada)")
    ax.set_ylabel("pontos de treino")
    save(fig, "08_distance_to_shore_distribution.png")

    summary_path = OUTPUT_DIR / "summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nGráficos e sumário em: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
