"""Confirma o número de viagens (IDs únicos) do ficheiro de dados.

Lê apenas a coluna `id` e conta linhas e IDs distintos. Não lê outras colunas.
Compara com o manifesto de divisão, para garantir que todos os IDs estão nele.

Uso (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python scripts/verify_trip_count.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

DATA_PATH = Path("data/123_fishing_trajs.csv")
MANIFEST_PATH = Path("manifests/split_manifest_seed42.csv")
EXPECTED_TRIPS = 123


def count_ids(path: Path) -> tuple[set[str], int]:
    ids: set[str] = set()
    rows = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        index = header.index("id")
        for row in reader:
            rows += 1
            ids.add(row[index].strip())
    return ids, rows


def main() -> int:
    if not DATA_PATH.exists() or not MANIFEST_PATH.exists():
        print("Ficheiro de dados ou manifesto não encontrado.", file=sys.stderr)
        return 1

    data_ids, data_rows = count_ids(DATA_PATH)
    manifest_ids, _ = count_ids(MANIFEST_PATH)

    print(f"Linhas de dados: {data_rows}")
    print(f"IDs únicos no ficheiro: {len(data_ids)}")
    print(f"IDs no manifesto: {len(manifest_ids)}")
    print(f"IDs do ficheiro fora do manifesto: {len(data_ids - manifest_ids)}")
    print(f"IDs do manifesto fora do ficheiro: {len(manifest_ids - data_ids)}")

    ok = len(data_ids) == EXPECTED_TRIPS and data_ids == manifest_ids
    print("RESULTADO:", "OK (123 viagens, manifesto coincide)" if ok else "DIFERENTE do esperado")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
