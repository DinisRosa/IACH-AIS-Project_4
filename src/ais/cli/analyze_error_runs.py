"""Comprimento dos "buracos" nas previsões da referência, para escolher a janela do pós-processamento (REV-058).

Um buraco é um bloco máximo de pontos consecutivos mal classificados (com a mesma classe prevista) dentro de
uma viagem. Usa só previsões JÁ GUARDADAS da referência congelada (época 162, limiar 0,65); não volta a correr
a CNN nem abre parquets. Também calcula, com dados ideais sintéticos, o maior buraco isolado que cada
janela gaussiana candidata (sigma = tamanho/6, limiar 0,65) consegue remover.

  --split test  : results/baseline_frozen/predictions_test_baseline.csv; exige a autorização
                  configs/authorizations/test_postproc_window.json e regista a leitura no access_log.
  --split train : results/baseline_frozen/predictions_train_frozen.csv (sem restrições).
NUNCA aceita o validation.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.analyze_error_runs --split test
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ais.cli.postproc_validation import order_points
from ais.phase1.postprocessing import error_runs, max_removable_island, summarize_runs
from ais.phase1.reserved import log_access, sha256_of
from ais.phase1.segments import extract_segments

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {"test": "results/baseline_frozen/predictions_test_baseline.csv",
           "train": "results/baseline_frozen/predictions_train_frozen.csv"}
AUTH = "configs/authorizations/test_postproc_window.json"
CANDIDATES = (13, 25, 51, 75, 101, 151, 201, 301, 401)
THRESHOLD = 0.65


def removable_table() -> list[dict]:
    return [{"janela": w, "remove_pesca_isolada_ate": max_removable_island(w, THRESHOLD, 1),
             "remove_navegacao_isolada_ate": max_removable_island(w, THRESHOLD, 0)} for w in CANDIDATES]


def analyze(df: pd.DataFrame) -> dict:
    df = order_points(df)
    runs = error_runs(df)
    out = {"n_pontos": int(len(df)), "n_viagens": int(df["id"].nunique()), "n_erros": int((df["target"] != df["predicted"]).sum()),
           "todos": summarize_runs(runs["comprimento"])}
    for cls, name in ((1, "pesca_prevista_no_meio_de_navegacao"), (0, "navegacao_prevista_no_meio_de_pesca")):
        out[name] = summarize_runs(runs.loc[runs["classe_prevista"] == cls, "comprimento"])
    real = extract_segments(df, "target", "id", "t")
    for cls, name in ((1, "segmentos_reais_pesca"), (0, "segmentos_reais_navegacao")):
        out[name] = summarize_runs(real.loc[real["cls"] == cls, "n_points"])
        out[name]["minimo"] = int(real.loc[real["cls"] == cls, "n_points"].min()) if (real["cls"] == cls).any() else None
    out["por_viagem"] = (runs.groupby("id")["comprimento"].agg(["count", "sum", "mean", "max"])
                         .rename(columns={"count": "n_blocos", "sum": "n_pontos", "mean": "media", "max": "maximo"})
                         .sort_values("n_pontos", ascending=False).reset_index().to_dict(orient="records"))
    return out, runs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=sorted(SOURCES), required=True)
    split = ap.parse_args().split
    src = ROOT / SOURCES[split]
    if split == "test":
        auth = json.loads((ROOT / AUTH).read_text(encoding="utf-8"))
        if "test" not in auth["conjuntos_autorizados"] or auth.get("validation_autorizado"):
            raise PermissionError("Autorização inválida para esta análise.")
        log_access(ROOT / "results" / "access_log.jsonl",
                   {"event": "postproc_window_analysis", "split": "test", "authorization": auth["id"],
                    "file": SOURCES[split], "file_sha256": sha256_of(src)})
    res, runs = analyze(pd.read_csv(src, usecols=["id", "point_id", "t", "target", "p_fishing", "predicted"]))
    table = removable_table()
    for row in table:  # buracos ISOLADOS que a janela removeria, por comprimento (aproximação: fundo ideal 0/1)
        ok = (((runs["classe_prevista"] == 1) & (runs["comprimento"] <= row["remove_pesca_isolada_ate"]))
              | ((runs["classe_prevista"] == 0) & (runs["comprimento"] <= row["remove_navegacao_isolada_ate"])))
        row["perc_buracos_cobertos"] = float(ok.mean()) if len(runs) else None
        row["perc_pontos_de_erro_cobertos"] = float(runs.loc[ok, "comprimento"].sum() / runs["comprimento"].sum()) if len(runs) else None
    res.update({"split": split, "fonte": SOURCES[split], "fonte_sha256": sha256_of(src),
                "janelas_candidatas": table,
                "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    out = ROOT / "results" / "postproc_window_analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{split}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    runs.to_csv(out / f"buracos_{split}.csv", index=False)
    t = res["todos"]
    print(f"{split}: {t['n_blocos']} buracos, {t['n_pontos']} pontos; média {t['media']:.1f}, mediana {t['mediana']:.0f}, "
          f"p75 {t['p75']:.0f}, p90 {t['p90']:.0f}, p95 {t['p95']:.0f}, máximo {t['maximo']}")


if __name__ == "__main__":
    main()
