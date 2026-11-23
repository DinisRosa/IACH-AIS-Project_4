"""Constrói a base de dados limpa a partir das bases geométricas e temporais.

Bases (copiadas tal como estão no CSV original): x, y, t e distanceToShore.
Valores recalculados a partir dessas bases, por viagem (mesmo id):
- time_gap_calc_s       : diferença de t para o ponto anterior, em segundos.
- distance_gap_calc_m   : distância plana (x, y) para o ponto anterior, em metros.
- bearing_calc_deg      : direção do deslocamento de x,y anterior para x,y atual,
                          em graus a partir do eixo y (norte da grelha), [0, 360).
- signed_turn_calc_deg  : variação de bearing_calc_deg para o ponto anterior,
                          normalizada para (-180, 180]. Positivo = aumento de bearing.
- speed_calc_mps        : distance_gap_calc_m / time_gap_calc_s (NaN se time_gap = 0).
- target                : 1 para pesca (02-fishing, 04-fishing), 0 para navegação
                          (01-sailing, 03-sailing, 05-sailing). Qualquer outro rótulo gera erro.

Regras:
- Conjuntos processáveis: train, validation e test (REV-015, autorização explícita do
  utilizador em 2026-11-23). Por defeito processa só train. Cada conjunto gera o seu
  próprio ficheiro e sumário. Cada conjunto é construído só com as suas viagens, a partir
  do manifesto; nunca se misturam conjuntos.
- Nenhuma linha é removida. O primeiro ponto de cada viagem fica com valores ausentes
  (NaN) nas grandezas que dependem do anterior. Remover ou marcar anomalias é uma decisão
  separada, com regra registada.
- Dados ordenados por id, t e point_id.
- point_id = número da linha de dados no CSV original (1 = primeira linha de dados).

Saída: data/123_fishing_trajs_clean_<split>.parquet (formato Parquet).
Sumário de diagnóstico: results/clean_<split>/summary.json.
Usa colunas originais (time_gap, distance_gap, bearing, signed_turn) só para comparação.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python scripts/build_clean_dataset.py --split train
    iach-ais-venv-4/bin/python scripts/build_clean_dataset.py --split validation
    iach-ais-venv-4/bin/python scripts/build_clean_dataset.py --split test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
SPLITS = ("train", "validation", "test")
RAW_PATH = Path("data/123_fishing_trajs.csv")
MANIFEST_PATH = Path("manifests/split_manifest_seed42.csv")

LABEL_TO_TARGET = {
    "02-fishing": 1,
    "04-fishing": 1,
    "01-sailing": 0,
    "03-sailing": 0,
    "05-sailing": 0,
}

RAW_COLUMNS = ["id", "t", "x", "y", "distanceToShore", "label",
               "time_gap", "distance_gap", "bearing", "signed_turn"]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_split_ids(manifest: Path, split: str) -> set[str]:
    table = pd.read_csv(manifest, dtype={"id": str, "split": str})
    return set(table.loc[table["split"] == split, "id"])


def load_raw(path: Path, train_ids: set[str]) -> pd.DataFrame:
    """Lê o CSV por blocos e mantém só linhas do conjunto pedido."""
    kept = []
    row_number = 0
    for chunk in pd.read_csv(path, usecols=RAW_COLUMNS, dtype={"id": str}, chunksize=200_000):
        numbers = np.arange(row_number + 1, row_number + len(chunk) + 1)
        row_number += len(chunk)
        chunk = chunk.assign(point_id=numbers)
        kept.append(chunk.loc[chunk["id"].isin(train_ids)])
    frame = pd.concat(kept, ignore_index=True)
    frame["t"] = pd.to_datetime(frame["t"], format="%Y-%m-%d %H:%M:%S")
    return frame.sort_values(["id", "t", "point_id"], kind="stable").reset_index(drop=True)


def wrap_180(angle: pd.Series) -> pd.Series:
    return (angle + 180.0) % 360.0 - 180.0


def build(frame: pd.DataFrame, split: str) -> pd.DataFrame:
    grouped = frame.groupby("id", sort=False)
    x_prev = grouped["x"].shift(1)
    y_prev = grouped["y"].shift(1)
    t_prev = grouped["t"].shift(1)

    out = pd.DataFrame(
        {
            "point_id": frame["point_id"].astype("int64"),
            "id": frame["id"],
            "split": split,
            "t": frame["t"],
            "x": frame["x"].astype("float64"),
            "y": frame["y"].astype("float64"),
            "distanceToShore": frame["distanceToShore"].astype("float64"),
            "label": frame["label"],
        }
    )

    unknown = sorted(set(frame["label"]) - set(LABEL_TO_TARGET))
    if unknown:
        raise ValueError(f"Rótulos desconhecidos: {unknown}")
    out["target"] = frame["label"].map(LABEL_TO_TARGET).astype("int8")

    dx = frame["x"] - x_prev
    dy = frame["y"] - y_prev
    out["time_gap_calc_s"] = (frame["t"] - t_prev).dt.total_seconds()
    out["distance_gap_calc_m"] = np.hypot(dx, dy)
    out["bearing_calc_deg"] = (np.degrees(np.arctan2(dx, dy)) + 360.0) % 360.0
    bearing_prev = out.groupby("id", sort=False)["bearing_calc_deg"].shift(1)
    out["signed_turn_calc_deg"] = wrap_180(out["bearing_calc_deg"] - bearing_prev)
    with np.errstate(divide="ignore", invalid="ignore"):
        speed = out["distance_gap_calc_m"] / out["time_gap_calc_s"]
    out["speed_calc_mps"] = speed.where(out["time_gap_calc_s"] > 0)
    return out


def diagnostics(out: pd.DataFrame, raw: pd.DataFrame) -> dict:
    """Compara com as colunas originais. Só para relatório; não altera a base."""
    def share(mask: pd.Series) -> float:
        valid = mask.notna()
        return float(mask[valid].mean()) if valid.any() else float("nan")

    dt_diff = (out["time_gap_calc_s"] - raw["time_gap"]).abs()
    dist_diff = (out["distance_gap_calc_m"] - raw["distance_gap"]).abs()
    bear_diff = wrap_180(out["bearing_calc_deg"] - raw["bearing"]).abs()
    turn_diff = wrap_180(out["signed_turn_calc_deg"] - raw["signed_turn"]).abs()
    dup_t = int(out.duplicated(subset=["id", "t"], keep=False).sum())
    first_points = int(out["time_gap_calc_s"].isna().sum())
    zero_dt = int((out["time_gap_calc_s"] == 0).sum())
    return {
        "linhas": int(len(out)),
        "viagens": int(out["id"].nunique()),
        "primeiros_pontos_sem_anterior": first_points,
        "pares_com_time_gap_zero": zero_dt,
        "linhas_com_id_t_repetido": dup_t,
        "target_contagem": {str(k): int(v) for k, v in out["target"].value_counts().sort_index().items()},
        "comparacao_com_colunas_originais": {
            "time_gap_diferente_mais_de_1e-6_s": share(dt_diff > 1e-6),
            "distance_gap_diferente_mais_de_1e-3_m": share(dist_diff > 1e-3),
            "distance_gap_mediana_abs_diff_m": float(np.nanmedian(dist_diff)),
            "bearing_diferente_mais_de_1_grau": share(bear_diff > 1.0),
            "bearing_mediana_abs_diff_graus": float(np.nanmedian(bear_diff)),
            "bearing_percentil95_abs_diff_graus": float(np.nanpercentile(bear_diff, 95)),
            "signed_turn_diferente_mais_de_1_grau": share(turn_diff > 1.0),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Constrói a base limpa de um conjunto (train, validation ou test).")
    parser.add_argument("--split", choices=SPLITS, default="train")
    args = parser.parse_args()
    split = args.split

    if not RAW_PATH.exists() or not MANIFEST_PATH.exists():
        print("Ficheiro de dados ou manifesto não encontrado.", file=sys.stderr)
        return 1

    split_ids = load_split_ids(MANIFEST_PATH, split)
    raw = load_raw(RAW_PATH, split_ids)
    out = build(raw, split)
    summary = diagnostics(out, raw)

    if set(out["id"].unique()) != split_ids:
        print(f"Erro: viagens do manifesto em falta ou extra no conjunto {split}.", file=sys.stderr)
        return 2
    summary["viagens_do_manifesto_encontradas"] = len(split_ids)

    output_path = Path(f"data/123_fishing_trajs_clean_{split}.parquet")
    summary_dir = Path(f"results/clean_{split}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output_path, index=False)

    summary_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "meta": {
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "script": "scripts/build_clean_dataset.py",
            "split": split,
            "raw_file": str(RAW_PATH),
            "raw_sha256": sha256_of(RAW_PATH),
            "manifest_file": str(MANIFEST_PATH),
            "manifest_sha256": sha256_of(MANIFEST_PATH),
            "output_file": str(output_path),
            "output_sha256": sha256_of(output_path),
            "seed": SEED,
        },
        "diagnostics": summary,
    }
    with (summary_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print(json.dumps(report["diagnostics"], ensure_ascii=False, indent=2))
    print(f"\nBase gravada: {output_path}")
    print(f"Sumário: {summary_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
