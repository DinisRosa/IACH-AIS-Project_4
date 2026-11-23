"""Conta navios partilhados entre conjuntos, usando apenas os IDs do manifesto de splits.

Lê só `manifests/split_manifest_seed42.csv` (colunas `id` e `split`). Não abre dados
nem resultados de viagens. O navio de um ID é tudo o que vem antes do ÚLTIMO hífen.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.count_shared_vessels

Escreve o sumário em `results/shared_vessels/summary.json` e imprime-o em JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = PROJECT_ROOT / "manifests" / "split_manifest_seed42.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "shared_vessels" / "summary.json"

TRAIN = "train"
VALIDATION = "validation"
TEST = "test"


def vessel_of(trip_id: str) -> str:
    """Devolve o navio de um ID `NAVIO-VIAGEM` (tudo antes do último hífen).

    Um ID sem hífen é tratado como navio por inteiro.
    """
    return str(trip_id).strip().rsplit("-", 1)[0]


def _safe_fraction(part: int, whole: int) -> float | None:
    """Divide `part` por `whole`, devolvendo None quando o denominador é zero."""
    if whole == 0:
        return None
    return part / whole


def _split_stats(trips: pd.DataFrame, other_vessels: set[str]) -> dict:
    """Conta viagens, navios e viagens cujo navio aparece em `other_vessels`."""
    n_trips = len(trips)
    shared_trips = int(trips["vessel"].isin(other_vessels).sum())
    return {
        "viagens": n_trips,
        "navios_distintos": int(trips["vessel"].nunique()),
        "viagens_com_navio_no_treino": shared_trips,
        "fracao_viagens_com_navio_no_treino": _safe_fraction(shared_trips, n_trips),
    }


def count_shared_vessels(manifest_df: pd.DataFrame, provenance: dict | None = None) -> dict:
    """Calcula contagens de navios partilhados entre treino, validação e teste.

    Recebe um DataFrame com as colunas `id` e `split`. Devolve um dicionário com:
    - estatísticas por conjunto (`validation`, `test`) face ao treino;
    - estatísticas da relação `validation` vs `test`;
    - `proveniencia`, o dicionário recebido em `provenance` (vazio se não for dado).
    """
    missing = {"id", "split"} - set(manifest_df.columns)
    if missing:
        raise ValueError(f"Manifesto sem colunas obrigatórias: {sorted(missing)}")

    df = manifest_df[["id", "split"]].copy()
    df["id"] = df["id"].astype(str)
    df["vessel"] = df["id"].map(vessel_of)

    by_split = {name: df[df["split"] == name] for name in (TRAIN, VALIDATION, TEST)}
    train_vessels = set(by_split[TRAIN]["vessel"])
    validation_vessels = set(by_split[VALIDATION]["vessel"])
    test_vessels = set(by_split[TEST]["vessel"])

    validation_trips = by_split[VALIDATION]
    test_trips = by_split[TEST]

    val_in_test = int(validation_trips["vessel"].isin(test_vessels).sum())
    test_in_val = int(test_trips["vessel"].isin(validation_vessels).sum())

    return {
        "conjuntos": {
            VALIDATION: _split_stats(validation_trips, train_vessels),
            TEST: _split_stats(test_trips, train_vessels),
        },
        "validation_vs_test": {
            "navios_partilhados": len(validation_vessels & test_vessels),
            "viagens_validation_com_navio_no_test": val_in_test,
            "fracao_viagens_validation_com_navio_no_test": _safe_fraction(
                val_in_test, len(validation_trips)
            ),
            "viagens_test_com_navio_na_validation": test_in_val,
            "fracao_viagens_test_com_navio_na_validation": _safe_fraction(
                test_in_val, len(test_trips)
            ),
        },
        "proveniencia": dict(provenance) if provenance else {},
    }


def _sha256(path: Path) -> str:
    """Calcula o sha256 de um ficheiro por blocos."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_summary(manifest_path: Path) -> dict:
    """Lê o manifesto (só `id` e `split`) e devolve o sumário com proveniência."""
    manifest_path = Path(manifest_path)
    manifest_df = pd.read_csv(manifest_path, dtype=str, usecols=["id", "split"])
    provenance = {
        "manifesto": str(manifest_path),
        "manifesto_sha256": _sha256(manifest_path),
        "data_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return count_shared_vessels(manifest_df, provenance=provenance)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI: calcula o sumário, grava-o e imprime-o."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    summary = build_summary(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
