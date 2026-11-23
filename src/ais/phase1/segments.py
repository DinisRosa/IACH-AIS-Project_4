"""Extração de segmentos e métricas por segmento sobre previsões por ponto.

Esta é uma FERRAMENTA DE MEDIÇÃO sobre previsões brutas. Não é
pós-processamento: não suaviza, não remove segmentos curtos e não altera
nenhuma previsão.

Convenções fixadas
------------------
* Segmento: bloco máximo de pontos consecutivos da mesma classe dentro da
  mesma viagem (cada ``id`` é uma viagem completa, sem quebras).
* Tempos em segundos desde o primeiro ponto da própria viagem.
* Intervalo meio-aberto ``[start_s, end_s)``. ``end_s`` é o tempo do 1.º ponto
  do segmento seguinte da mesma viagem; no último segmento da viagem é o tempo
  do seu último ponto. Caso-limite: um segmento que seja o último da viagem e
  tenha um só ponto fica com duração 0.
* "Referência" = segmentos extraídos de ``target``; "previsto" = segmentos
  extraídos da coluna de classe prevista.
* IoU temporal = |interseção| / |união| em segundos. Se a união for 0 (dois
  segmentos de duração 0), IoU = 1.0 se ``start_s`` coincide, senão 0.0.
* Emparelhamento um-para-um, guloso por IoU decrescente, dentro da mesma
  viagem e da mesma classe, só com IoU >= limiar.
* Agregação global = soma das contagens de todas as viagens (micro).
  Divisões por zero devolvem ``None``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEGMENT_COLUMNS = [
    "segment_id", "id", "cls", "start_pos", "end_pos", "n_points",
    "start_s", "end_s", "duration_s",
]


def _validate_points(
    points: pd.DataFrame, class_col: str, id_col: str, time_col: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Valida a tabela de pontos e devolve (ids, classes int8, segundos).

    Os segundos são contados desde o primeiro ponto de cada viagem. Levanta
    ValueError se faltarem colunas, houver NaN/NaT, classes fora de {0, 1},
    ids não contíguos ou tempo decrescente dentro de uma viagem.
    """
    for col in (id_col, time_col, class_col):
        if col not in points.columns:
            raise ValueError(f"Coluna em falta: '{col}'.")
    if points[[id_col, time_col, class_col]].isna().any().any():
        raise ValueError("Valores em falta (NaN/NaT) em id, tempo ou classe.")

    cls = points[class_col].to_numpy()
    if not np.isin(cls, [0, 1]).all():
        raise ValueError(f"A coluna '{class_col}' só pode conter 0 ou 1.")
    cls = cls.astype(np.int8)

    ids = points[id_col].to_numpy()
    n = len(ids)
    if n == 0:
        return ids, cls, np.zeros(0)

    t = pd.to_datetime(points[time_col])
    if t.isna().any():
        raise ValueError(f"A coluna '{time_col}' tem valores não convertíveis.")
    t = t.reset_index(drop=True)
    t0 = t.groupby(ids).transform("first")
    secs = (t - t0).dt.total_seconds().to_numpy()

    new_trip = np.ones(n, dtype=bool)
    new_trip[1:] = ids[1:] != ids[:-1]
    if new_trip.sum() != len(pd.unique(ids)):
        raise ValueError("Cada id tem de formar um bloco contíguo (ordenar por id e t).")
    if (np.diff(secs)[~new_trip[1:]] < 0).any():
        raise ValueError("O tempo tem de ser não decrescente dentro de cada id.")
    return ids, cls, secs


def extract_segments(
    points: pd.DataFrame, class_col: str, id_col: str = "id", time_col: str = "t"
) -> pd.DataFrame:
    """Extrai os segmentos (blocos máximos da mesma classe) de cada viagem.

    Devolve colunas: segment_id (inteiro único crescente, global), id, cls,
    start_pos, end_pos (posições inclusivas dentro da viagem), n_points,
    start_s, end_s, duration_s (ver convenções no módulo).
    """
    ids, cls, secs = _validate_points(points, class_col, id_col, time_col)
    n = len(ids)
    if n == 0:
        return pd.DataFrame({c: [] for c in SEGMENT_COLUMNS})

    idx = np.arange(n)
    new_trip = np.ones(n, dtype=bool)
    new_trip[1:] = ids[1:] != ids[:-1]
    pos = idx - np.maximum.accumulate(np.where(new_trip, idx, 0))

    is_start = new_trip.copy()
    is_start[1:] |= cls[1:] != cls[:-1]
    starts = np.flatnonzero(is_start)
    ends = np.append(starts[1:] - 1, n - 1)

    seg_ids = ids[starts]
    start_s = secs[starts]
    end_s = secs[ends].copy()  # último segmento da viagem: tempo do último ponto
    same_next = np.zeros(len(starts), dtype=bool)
    same_next[:-1] = seg_ids[1:] == seg_ids[:-1]
    end_s[same_next] = start_s[1:][same_next[:-1]]

    return pd.DataFrame({
        "segment_id": np.arange(len(starts)),
        "id": seg_ids,
        "cls": cls[starts].astype(int),
        "start_pos": pos[starts],
        "end_pos": pos[ends],
        "n_points": ends - starts + 1,
        "start_s": start_s,
        "end_s": end_s,
        "duration_s": end_s - start_s,
    })


def temporal_iou(
    start_a: np.ndarray, end_a: np.ndarray, start_b: np.ndarray, end_b: np.ndarray
) -> np.ndarray:
    """IoU temporal vetorizado entre intervalos [start, end) emparelhados.

    Se a união for 0 (duas durações nulas), devolve 1.0 quando os inícios
    coincidem e 0.0 caso contrário.
    """
    inter = np.maximum(0.0, np.minimum(end_a, end_b) - np.maximum(start_a, start_b))
    union = (end_a - start_a) + (end_b - start_b) - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        iou = np.where(union > 0, inter / np.where(union > 0, union, 1.0), 0.0)
    return np.where(union > 0, iou, (start_a == start_b).astype(float))


def match_segments(
    pred_segments: pd.DataFrame,
    ref_segments: pd.DataFrame,
    cls: int,
    iou_threshold: float = 0.5,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Emparelhamento um-para-um, guloso por IoU decrescente.

    Só se emparelham segmentos da mesma viagem e da classe ``cls``, com
    IoU >= ``iou_threshold`` (que tem de estar em (0, 1]). Empates: menor
    start_s da referência, depois menor start_s do previsto.

    Devolve (pares, previstos_sem_correspondencia, referencias_sem_correspondencia).
    Os pares têm id, pred_segment_id, ref_segment_id, iou, os limites de cada
    um, erro_inicio_s = start_s_prev - start_s_ref e erro_fim_s = end_s_prev -
    end_s_ref (ambos com sinal).
    """
    if not 0 < iou_threshold <= 1:
        raise ValueError("iou_threshold tem de estar em (0, 1].")
    pred = pred_segments[pred_segments["cls"] == cls]
    ref = ref_segments[ref_segments["cls"] == cls]

    cand = pred[["segment_id", "id", "start_s", "end_s"]].merge(
        ref[["segment_id", "id", "start_s", "end_s"]],
        on="id", suffixes=("_pred", "_ref"),
    ).rename(columns={"segment_id_pred": "pred_segment_id",
                      "segment_id_ref": "ref_segment_id"})
    cand["iou"] = temporal_iou(
        cand["start_s_pred"].to_numpy(), cand["end_s_pred"].to_numpy(),
        cand["start_s_ref"].to_numpy(), cand["end_s_ref"].to_numpy(),
    )
    cand = cand[cand["iou"] >= iou_threshold].sort_values(
        ["iou", "start_s_ref", "start_s_pred"],
        ascending=[False, True, True], kind="mergesort",
    )

    used_pred: set = set()
    used_ref: set = set()
    keep = []
    for row, (p, r) in enumerate(zip(cand["pred_segment_id"], cand["ref_segment_id"])):
        if p in used_pred or r in used_ref:
            continue
        used_pred.add(p)
        used_ref.add(r)
        keep.append(row)

    pairs = cand.iloc[keep].sort_values("ref_segment_id").reset_index(drop=True)
    pairs["erro_inicio_s"] = pairs["start_s_pred"] - pairs["start_s_ref"]
    pairs["erro_fim_s"] = pairs["end_s_pred"] - pairs["end_s_ref"]
    pairs = pairs[[
        "id", "pred_segment_id", "ref_segment_id", "iou",
        "start_s_pred", "end_s_pred", "start_s_ref", "end_s_ref",
        "erro_inicio_s", "erro_fim_s",
    ]]
    unmatched_pred = pred[~pred["segment_id"].isin(used_pred)].reset_index(drop=True)
    unmatched_ref = ref[~ref["segment_id"].isin(used_ref)].reset_index(drop=True)
    return pairs, unmatched_pred, unmatched_ref


def _ratio(num: float, den: float):
    """Divisão que devolve None quando o denominador é 0."""
    return None if den == 0 else float(num) / float(den)


def compute_segment_metrics(
    points: pd.DataFrame,
    class_col: str = "predicted",
    cls: int = 1,
    iou_threshold: float = 0.5,
    id_col: str = "id",
    time_col: str = "t",
    target_col: str = "target",
) -> dict:
    """Métricas por segmento para a classe ``cls`` (1 pesca, 0 navegação).

    Devolve um dicionário com contagens globais (soma sobre todas as viagens),
    precision = n_matched/n_pred, sensitivity = n_matched/n_ref,
    f1 = 2*n_matched/(n_pred+n_ref), mean_iou_matched, mediana e média do
    erro absoluto de início e de fim (segundos) entre pares,
    fragmentation_ratio = n_pred/n_ref, a tabela ``por_viagem`` (DataFrame com
    id, n_ref, n_pred, n_matched, fragmentation_ratio) e ``convencoes``.
    Divisões por zero e estatísticas sem pares dão None.
    """
    ref_seg = extract_segments(points, target_col, id_col, time_col)
    pred_seg = extract_segments(points, class_col, id_col, time_col)
    pairs, _, _ = match_segments(pred_seg, ref_seg, cls, iou_threshold)

    trips = pd.Index(pd.unique(points[id_col]), name="id")
    count = lambda df: df[df["cls"] == cls].groupby("id").size().reindex(trips, fill_value=0)
    per_trip = pd.DataFrame({
        "n_ref": count(ref_seg),
        "n_pred": count(pred_seg),
        "n_matched": pairs.groupby("id").size().reindex(trips, fill_value=0),
    }).reset_index()
    per_trip["fragmentation_ratio"] = pd.Series(
        [_ratio(p, r) for p, r in zip(per_trip["n_pred"], per_trip["n_ref"])],
        dtype=object,
    )

    n_ref, n_pred = int(per_trip["n_ref"].sum()), int(per_trip["n_pred"].sum())
    n_matched = len(pairs)
    abs_start = pairs["erro_inicio_s"].abs()
    abs_end = pairs["erro_fim_s"].abs()
    has_pairs = n_matched > 0

    return {
        "cls": int(cls),
        "n_trips": len(trips),
        "n_ref_segments": n_ref,
        "n_pred_segments": n_pred,
        "n_matched": n_matched,
        "precision": _ratio(n_matched, n_pred),
        "sensitivity": _ratio(n_matched, n_ref),
        "f1": _ratio(2 * n_matched, n_pred + n_ref),
        "mean_iou_matched": float(pairs["iou"].mean()) if has_pairs else None,
        "median_abs_start_error_s": float(abs_start.median()) if has_pairs else None,
        "mean_abs_start_error_s": float(abs_start.mean()) if has_pairs else None,
        "median_abs_end_error_s": float(abs_end.median()) if has_pairs else None,
        "mean_abs_end_error_s": float(abs_end.mean()) if has_pairs else None,
        "fragmentation_ratio": _ratio(n_pred, n_ref),
        "por_viagem": per_trip,
        "convencoes": {
            "iou_threshold": float(iou_threshold),
            "unidade_tempo": "segundos",
            "intervalo": "meio-aberto [start_s, end_s); end_s = início do segmento "
                         "seguinte, ou último ponto no último segmento da viagem",
            "agregacao": "micro (soma das contagens de todas as viagens)",
            "divisao_por_zero": "None",
        },
    }
