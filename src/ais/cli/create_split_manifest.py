"""Cria o manifesto de divisão por ID completo (docs/00 §6, AGENTS.md §3).

Lê apenas a coluna `id` do CSV. Não lê, não conta e não analisa outras colunas
nem valores de rótulo. Atribui cada ID único a train, validation ou test com
uma seed e proporções fixas, e grava um CSV id → split.

Regra de arredondamento: validação e teste arredondados ao inteiro mais
próximo; treino recebe o resto.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.create_split_manifest
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

SEED = 42
PROPORTIONS = {"train": 0.70, "validation": 0.15, "test": 0.15}

DATA_PATH = Path("data/123_fishing_trajs.csv")
MANIFEST_PATH = Path("manifests/split_manifest_seed42.csv")


def read_ids_and_row_counts(path: Path) -> tuple[dict[str, int], int]:
    """Devolve {id: número de linhas} e o total de linhas de dados, lendo só a coluna id."""
    counts: dict[str, int] = {}
    total_rows = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if "id" not in header:
            raise ValueError("O ficheiro não tem a coluna 'id'.")
        id_index = header.index("id")
        for row in reader:
            total_rows += 1
            trip_id = row[id_index].strip()
            if not trip_id:
                raise ValueError(f"ID ausente na linha de dados {total_rows}.")
            counts[trip_id] = counts.get(trip_id, 0) + 1
    return counts, total_rows


def assign_splits(unique_ids: list[str]) -> dict[str, str]:
    """Atribui IDs únicos a conjuntos com a seed e as proporções fixas."""
    ordered = sorted(unique_ids)
    rng = random.Random(SEED)
    rng.shuffle(ordered)

    n_total = len(ordered)
    n_validation = round(n_total * PROPORTIONS["validation"])
    n_test = round(n_total * PROPORTIONS["test"])
    n_train = n_total - n_validation - n_test

    assignment: dict[str, str] = {}
    for trip_id in ordered[:n_train]:
        assignment[trip_id] = "train"
    for trip_id in ordered[n_train : n_train + n_validation]:
        assignment[trip_id] = "validation"
    for trip_id in ordered[n_train + n_validation :]:
        assignment[trip_id] = "test"
    return assignment


def validate(assignment: dict[str, str], counts: dict[str, int], total_rows: int) -> dict[str, int]:
    """Confirma atribuição única, cobertura de todos os IDs e conservação de linhas."""
    if set(assignment) != set(counts):
        raise AssertionError("Algum ID não ficou atribuído ou há IDs extra.")
    rows_per_split = {name: 0 for name in PROPORTIONS}
    ids_per_split = {name: 0 for name in PROPORTIONS}
    for trip_id, split in assignment.items():
        rows_per_split[split] += counts[trip_id]
        ids_per_split[split] += 1
    if sum(rows_per_split.values()) != total_rows:
        raise AssertionError("A soma das linhas por conjunto não é igual ao total.")
    return {
        **{f"ids_{k}": v for k, v in ids_per_split.items()},
        **{f"rows_{k}": v for k, v in rows_per_split.items()},
    }


def write_manifest(assignment: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "split"])
        for trip_id in sorted(assignment):
            writer.writerow([trip_id, assignment[trip_id]])


def main() -> int:
    if not DATA_PATH.exists():
        print(f"Ficheiro não encontrado: {DATA_PATH}", file=sys.stderr)
        return 1
    counts, total_rows = read_ids_and_row_counts(DATA_PATH)
    assignment = assign_splits(list(counts))
    summary = validate(assignment, counts, total_rows)
    write_manifest(assignment, MANIFEST_PATH)
    print(f"seed={SEED} proporções={PROPORTIONS}")
    print(f"IDs únicos={len(counts)} linhas={total_rows}")
    for key, value in summary.items():
        print(f"{key}={value}")
    print(f"manifesto={MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
