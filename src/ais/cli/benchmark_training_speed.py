"""Medição da velocidade de treino da CNN 1D em CPU, com poucas viagens de TREINO (REV-032).

Mede o tempo por época, por passo e por ponto com 1 viagem, 2 viagens e a maior viagem do
treino, e projeta (por nº de pontos) o custo de treinar com mais viagens. É uma MEDIÇÃO DE
CUSTO: não avalia a qualidade do modelo. Só lê o parquet de treino; não abre validação/teste.
As projeções assumem custo proporcional ao nº de pontos: são estimativas, não medições.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.benchmark_training_speed
Saídas em results/benchmark_speed/ (não versionadas): benchmark.json, benchmark.csv.
"""
from __future__ import annotations

import json
import platform
import resource
import statistics as st
import time
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import torch

ROOT = Path(__file__).resolve().parents[3]

from ais.phase1.data import (  # noqa: E402
    FEATURE_COLS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences,
    build_sequence_loader, fit_scaler, validate_training_data,
)
from ais.phase1.model import build_cnn  # noqa: E402
from ais.phase1.training import (  # noqa: E402
    build_loss, build_optimizer, evaluate_training_subset, train_one_epoch,
)
from ais.phase1.utils import select_device, set_reproducibility  # noqa: E402

TRAIN = ROOT / "data" / "123_fishing_trajs_clean_train.parquet"
MANIFEST = ROOT / "manifests" / "split_manifest_seed42.csv"
OUT = ROOT / "results" / "benchmark_speed"
CONFIG = {"seed": 42, "lr": 1e-3, "warmup_epochs": 2, "measured_epochs": 20, "repeats": 3}
SCENARIOS = {"13 viagens (média)": 13, "74 viagens (85 % de 87)": 74, "87 viagens (treino todo)": 87}


def train_trip_sizes() -> pd.Series:
    """Nº de pontos por viagem do treino (só lê a coluna id) e confirma que são todas train."""
    ids = pq.read_table(TRAIN, columns=["id"]).column("id").to_pandas().astype(str)
    split_of = dict(zip(*pd.read_csv(MANIFEST)[["id", "split"]].astype(str).values.T))
    sizes = ids.value_counts()
    assert all(split_of[i] == "train" for i in sizes.index), "id fora do treino"
    return sizes


def first_train_ids(n: int, sizes: pd.Series) -> list[str]:
    man = pd.read_csv(MANIFEST)
    return [i for i in man.loc[man["split"] == "train", "id"].astype(str) if i in sizes.index][:n]


def prepare(ids: list[str]):
    df = pq.read_table(TRAIN, filters=[("id", "in", ids)]).to_pandas()
    df = df.sort_values(["id", "t", "point_id"], kind="stable").reset_index(drop=True)
    validate_training_data(df, FEATURE_COLS)
    seqs = build_full_sequences(df, FEATURE_COLS)
    scaler = fit_scaler(seqs)
    return [apply_scaler(s, scaler) for s in seqs], int(len(df))


def bench(name: str, ids: list[str], device) -> dict:
    seqs, n_points = prepare(ids)
    runs = []
    for r in range(CONFIG["repeats"]):
        torch.manual_seed(CONFIG["seed"])
        model = build_cnn(n_channels=N_INPUT_CHANNELS).to(device)
        loss_fn, opt = build_loss(), build_optimizer(model, {"lr": CONFIG["lr"]})
        t_all = time.perf_counter()
        ep_times = []
        for ep in range(CONFIG["warmup_epochs"] + CONFIG["measured_epochs"]):
            loader = build_sequence_loader(seqs, shuffle=True, seed=CONFIG["seed"] + ep)
            s = train_one_epoch(model, loader, opt, loss_fn, device)
            if ep >= CONFIG["warmup_epochs"]:
                ep_times.append(s["seconds"])
        wall = time.perf_counter() - t_all
        ev_times = []
        for _ in range(5):
            t = time.perf_counter()
            evaluate_training_subset(model, build_sequence_loader(seqs, False, 0), loss_fn, device)
            ev_times.append(time.perf_counter() - t)
        runs.append({"epoch_median_s": st.median(ep_times), "epoch_min_s": min(ep_times),
                     "epoch_max_s": max(ep_times), "wall_s_with_warmup": wall,
                     "eval_pass_median_s": st.median(ev_times)})
    med = st.median(x["epoch_median_s"] for x in runs)
    ev = st.median(x["eval_pass_median_s"] for x in runs)
    return {"config": name, "ids": ids, "n_trips": len(ids), "n_points": n_points,
            "steps_per_epoch": len(ids), "epoch_median_s": med,
            "epoch_spread_s": [min(x["epoch_min_s"] for x in runs), max(x["epoch_max_s"] for x in runs)],
            "ms_per_step": 1000 * med / len(ids), "us_per_point_train": 1e6 * med / n_points,
            "points_per_s_train": n_points / med, "eval_pass_median_s": ev,
            "us_per_point_eval": 1e6 * ev / n_points, "repeats": runs}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = set_reproducibility(CONFIG["seed"], deterministic=True)
    device = select_device("cpu")
    sizes = train_trip_sizes()
    total_points, n_trips = int(sizes.sum()), int(len(sizes))
    mean_pts = total_points / n_trips
    configs = [("1 viagem", first_train_ids(1, sizes)), ("2 viagens", first_train_ids(2, sizes)),
               ("maior viagem do treino", [sizes.idxmax()])]
    results = [bench(n, ids, device) for n, ids in configs]

    proj = []
    for r in results:
        for sc, k in SCENARIOS.items():
            pts = k * mean_pts if k != n_trips else total_points
            proj.append({"base": r["config"], "cenario": sc, "pontos_estimados": pts,
                         "epoca_treino_s": pts * r["us_per_point_train"] / 1e6,
                         "epoca_avaliacao_s": pts * r["us_per_point_eval"] / 1e6,
                         "100_epocas_min": 100 * pts * r["us_per_point_train"] / 1e6 / 60})
    out = {"config": CONFIG, "n_train_trips": n_trips, "n_train_points": total_points,
           "mean_points_per_trip": mean_pts, "largest_trip_points": int(sizes.max()),
           "results": results, "projections_by_points": proj,
           "num_threads": torch.get_num_threads(), "reproducibility": meta,
           "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
           "python": platform.python_version(), "torch": torch.__version__,
           "aviso": "Projeções por nº de pontos (custo proporcional): estimativas, não medições."}
    (OUT / "benchmark.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    pd.DataFrame([{k: v for k, v in r.items() if k not in ("ids", "repeats")} for r in results]
                 ).to_csv(OUT / "benchmark.csv", index=False)
    print(f"treino: {n_trips} viagens, {total_points} pontos, média {mean_pts:.0f} pts/viagem; "
          f"threads={out['num_threads']}; pico RSS={out['peak_rss_mb']:.0f} MB")


if __name__ == "__main__":
    main()
