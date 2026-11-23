"""Métricas por segmento (pesca e navegação) a partir de previsões por ponto.

Finalidade: medir, sobre previsões brutas, a qualidade da segmentação
(precisão/sensibilidade/F1 de segmentos, IoU temporal, erros de fronteira,
fragmentação). Não faz pós-processamento nem altera previsões.

Comando:
    iach-ais-venv-4/bin/python -m ais.cli.segment_metrics CAMINHO_PREVISOES.csv \
        [--iou 0.5] [--out saida.json] [--por-viagem]

O CSV tem de ter as colunas id, t, target e predicted, ordenado por id e t.
ATENÇÃO: só deve receber previsões de conjuntos autorizados (treino ou
sintéticos). Nunca passar previsões de validação/teste sem autorização
explícita do utilizador.
"""

from __future__ import annotations

import argparse
import json

import pandas as pd

from ais.phase1.segments import compute_segment_metrics


def _to_python(obj):
    """Converte escalares numpy em tipos nativos para o JSON."""
    if hasattr(obj, "item"):
        return obj.item()
    return str(obj)


def _jsonable(metrics: dict, with_per_trip: bool) -> dict:
    """Converte o dicionário de métricas em estrutura serializável em JSON."""
    out = dict(metrics)
    per_trip = out.pop("por_viagem")
    if with_per_trip:
        records = per_trip.astype(object).where(per_trip.notna(), None)
        out["por_viagem"] = records.to_dict(orient="records")
    return out


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("predictions_csv")
    parser.add_argument("--iou", type=float, default=0.5, help="limiar de IoU")
    parser.add_argument("--out", default=None, help="JSON de saída (inclui por_viagem)")
    parser.add_argument("--por-viagem", action="store_true",
                        help="inclui a tabela por viagem no que é impresso")
    args = parser.parse_args(argv)

    points = pd.read_csv(args.predictions_csv, usecols=["id", "t", "target", "predicted"])
    results = {"origem": args.predictions_csv, "n_pontos": len(points)}
    for name, cls in (("pesca", 1), ("navegacao", 0)):
        results[name] = compute_segment_metrics(
            points, class_col="predicted", cls=cls, iou_threshold=args.iou)

    shown = {k: (_jsonable(v, args.por_viagem) if isinstance(v, dict) else v)
             for k, v in results.items()}
    print(json.dumps(shown, indent=2, ensure_ascii=False, default=_to_python))
    if args.out:
        full = {k: (_jsonable(v, True) if isinstance(v, dict) else v)
                for k, v in results.items()}
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(full, fh, indent=2, ensure_ascii=False, default=_to_python)


if __name__ == "__main__":
    main()
