"""Pós-processamento da referência sobre as previsões já guardadas do `validation` (Marco 5, REV-057).

Protocolo: `configs/postproc_protocol.json` (declarado e commitado antes de medir). NÃO abre o parquet do
`validation` e NÃO volta a correr a CNN: lê `results/final_validation/predictions_validation.csv`, gerado na
medição final (REV-053), filtra `p_fishing` com a janela gaussiana de 13 pontos, aplica o limiar 0,65 e
compara com `target` antes e depois. Uma só execução, registada em `results/access_log.jsonl`.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.postproc_validation
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

from ais.cli.select_windows_on_test import segment_report
from ais.phase1.inference import tables_for
from ais.phase1.postprocessing import gaussian_kernel, smooth_probabilities
from ais.phase1.reserved import log_access, read_log, sha256_of

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = Path("configs/postproc_protocol.json")
OUT = Path("results/postproc_validation")
REQUIRED = ["id", "point_id", "t", "target", "p_fishing", "predicted"]
SOURCE = "results/final_validation/predictions_validation.csv"
THRESHOLD = 0.65  # limiar congelado da referência; o protocolo não o pode mudar
EVENTS = ("postproc_start", "postproc_done")


def load_protocol(root: Path) -> dict:
    proto = json.loads((root / PROTOCOL).read_text(encoding="utf-8"))
    f = proto["filtro"]
    size, sigma = int(f["tamanho_pontos"]), float(Fraction(f["sigma_pontos"]))
    if (proto.get("execucoes") != 1 or size != 13 or abs(sigma - 13 / 6) > 1e-12
            or float(f["limiar_depois_do_filtro"]) != THRESHOLD or proto["fonte"]["ficheiro"] != SOURCE):
        raise ValueError("O protocolo não corresponde ao decidido (13 pontos, sigma 13/6, limiar 0,65, "
                         "previsões da medição final, uma execução).")
    return proto


def check_preconditions(root: Path, proto: dict, log_path: Path) -> None:
    """Falha antes de ler qualquer linha se algo não estiver conforme o protocolo."""
    rel = str(PROTOCOL)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=root, capture_output=True)
    changed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=root)
    if tracked.returncode != 0 or changed.returncode != 0:
        raise PermissionError("O protocolo tem de estar commitado e sem alterações antes de medir.")
    if any(e.get("event") in EVENTS for e in read_log(log_path)) or (root / OUT).exists():
        raise PermissionError("O pós-processamento já foi executado; o protocolo só permite uma execução.")
    src = root / proto["fonte"]["ficheiro"]
    if sha256_of(src) != proto["fonte"]["sha256"]:
        raise ValueError("O ficheiro de previsões não é o da medição final (hash diferente).")


def order_points(df: pd.DataFrame) -> pd.DataFrame:
    """Viagens pela ordem de aparição; dentro de cada viagem, por t e depois point_id."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas em falta: {missing}")
    if not df["point_id"].is_unique:
        raise ValueError("point_id repetido")
    out = df.copy()
    out["_trip"] = pd.Categorical(out["id"], categories=pd.unique(out["id"]), ordered=True)
    out["_t"] = pd.to_datetime(out["t"])
    out = out.sort_values(["_trip", "_t", "point_id"], kind="mergesort")
    return out.drop(columns=["_trip", "_t"]).reset_index(drop=True)


def apply_filter(df: pd.DataFrame, threshold: float, kernel: np.ndarray) -> pd.DataFrame:
    """Acrescenta p_fishing_filtrada e predicted_filtrado; não altera as colunas originais."""
    out = df.copy()
    out["p_fishing_filtrada"] = smooth_probabilities(out["p_fishing"].to_numpy(), out["id"].to_numpy(), kernel)
    out["predicted_filtrado"] = (out["p_fishing_filtrada"] >= threshold).astype(int)
    return out


def change_summary(df: pd.DataFrame) -> dict:
    """Pontos que mudam de classe com o filtro, por sentido, e se a mudança corrige ou estraga."""
    before, after, tgt = (df[c].to_numpy() for c in ("predicted", "predicted_filtrado", "target"))
    ch = before != after
    return {
        "n_pontos": int(len(df)),
        "n_mudam": int(ch.sum()),
        "navegacao_para_pesca": int((ch & (after == 1)).sum()),
        "pesca_para_navegacao": int((ch & (after == 0)).sum()),
        "corrigidos": int((ch & (after == tgt)).sum()),
        "estragados": int((ch & (before == tgt)).sum()),
    }


def measure(df: pd.DataFrame) -> dict:
    """Tabelas por ponto e por segmento, antes e depois do filtro."""
    after = df.drop(columns=["predicted"]).rename(columns={"predicted_filtrado": "predicted"})
    if "label" not in df.columns:  # tables_for usa a etiqueta original, se existir
        df = df.assign(label=df["target"])
        after = after.assign(label=after["target"])
    return {"antes": {"ponto": tables_for(df), "segmento": segment_report(df)},
            "depois": {"ponto": tables_for(after), "segmento": segment_report(after)},
            "mudancas": change_summary(df)}


def _git_commit(root: Path) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    return r.stdout.strip()


def run(root: Path = ROOT) -> dict:
    root = Path(root)
    log_path = root / "results" / "access_log.jsonl"
    proto = load_protocol(root)
    check_preconditions(root, proto, log_path)
    threshold = THRESHOLD
    kernel = gaussian_kernel(int(proto["filtro"]["tamanho_pontos"]), float(Fraction(proto["filtro"]["sigma_pontos"])))

    # Tudo é calculado em memória antes de registar ou gravar: uma falha técnica a meio não mostra
    # resultados nem gasta a execução única. Só no fim se regista e grava.
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    df = order_points(pd.read_csv(root / proto["fonte"]["ficheiro"]))
    if not np.array_equal((df["p_fishing"] >= threshold).astype(int), df["predicted"]):
        raise ValueError("As previsões guardadas não correspondem ao limiar do protocolo.")
    df = apply_filter(df, threshold, kernel)
    res = measure(df)

    log_access(log_path, {"event": "postproc_start", "split": "validation", "protocol": proto["id"],
                          "file": proto["fonte"]["ficheiro"], "file_sha256": proto["fonte"]["sha256"],
                          "calculo_iniciado_utc": started})
    out = root / OUT
    out.mkdir(parents=True, exist_ok=False)
    df.rename(columns={"predicted": "predicted_antes", "predicted_filtrado": "predicted_depois",
                       "p_fishing_filtrada": "p_fishing_depois"}).to_csv(
        out / "predictions_validation_postproc.csv", index=False)
    result = {
        "protocolo": proto["id"], "hash_do_protocolo": sha256_of(root / PROTOCOL),
        "fonte": proto["fonte"]["ficheiro"], "fonte_sha256": proto["fonte"]["sha256"],
        "filtro": {"tamanho_pontos": int(len(kernel)), "sigma_pontos": float(Fraction(proto["filtro"]["sigma_pontos"])),
                   "pesos": kernel.tolist(), "limiar": threshold},
        "n_viagens": int(df["id"].nunique()), **res,
        "git_commit": _git_commit(root),
        "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aviso": "Uma só aplicação, com o filtro fixado antes. Sem nova passagem pela CNN nem leitura do parquet "
                 "do validation; as anotações são usadas pela segunda vez, só para medir.",
    }
    (out / "postproc_validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str),
                                                 encoding="utf-8")
    log_access(log_path, {"event": "postproc_done", "split": "validation", "protocol": proto["id"]})
    return result


def main() -> None:
    r = run()
    a, d = r["antes"]["ponto"]["global"], r["depois"]["ponto"]["global"]
    sa, sd = r["antes"]["segmento"]["pesca"], r["depois"]["segmento"]["pesca"]
    print(f"exatidão {a['accuracy']:.4f} -> {d['accuracy']:.4f}; segmentos de pesca previstos "
          f"{sa['n_pred_segments']} -> {sd['n_pred_segments']} (reais {sa['n_ref_segments']}); "
          f"mudanças: {r['mudancas']}")


if __name__ == "__main__":
    sys.exit(main())
