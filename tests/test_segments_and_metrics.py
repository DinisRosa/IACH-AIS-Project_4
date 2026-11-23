"""Testes sintéticos da extração de segmentos e das métricas por segmento.

Notação: N = navegação (0), P = pesca (1); pontos de 1 em 1 s. Todos os valores
esperados foram calculados à mão.
"""

import pandas as pd
import pytest

from ais.phase1.segments import (
    compute_segment_metrics,
    extract_segments,
    match_segments,
)

BASE = pd.Timestamp("2024-01-01 00:00:00")


def make_trip(trip_id, real, pred=None, step_s=1):
    """Cria os pontos de uma viagem a partir de strings de N/P."""
    pred = real if pred is None else pred
    assert len(real) == len(pred)
    code = {"N": 0, "P": 1}
    return pd.DataFrame({
        "id": trip_id,
        "point_id": range(len(real)),
        "t": [BASE + pd.Timedelta(seconds=step_s * i) for i in range(len(real))],
        "target": [code[c] for c in real],
        "predicted": [code[c] for c in pred],
    })


def seg_tuples(seg):
    return list(zip(seg["id"], seg["cls"], seg["start_pos"], seg["end_pos"],
                    seg["n_points"], seg["start_s"], seg["end_s"], seg["duration_s"]))


def test_single_class_one_segment():
    seg = extract_segments(make_trip("a", "NNNN"), "target")
    assert seg["segment_id"].tolist() == [0]
    # último segmento: end_s = tempo do último ponto (3 s)
    assert seg_tuples(seg) == [("a", 0, 0, 3, 4, 0.0, 3.0, 3.0)]


def test_alternations():
    seg = extract_segments(make_trip("a", "NNPPPN"), "target")
    assert seg_tuples(seg) == [
        ("a", 0, 0, 1, 2, 0.0, 2.0, 2.0),
        ("a", 1, 2, 4, 3, 2.0, 5.0, 3.0),
        ("a", 0, 5, 5, 1, 5.0, 5.0, 0.0),  # último com 1 ponto: duração 0
    ]
    assert seg["segment_id"].tolist() == [0, 1, 2]


def test_one_point_trip():
    seg = extract_segments(make_trip("a", "P"), "target")
    assert seg_tuples(seg) == [("a", 1, 0, 0, 1, 0.0, 0.0, 0.0)]


def test_two_independent_ids():
    pts = pd.concat([make_trip("a", "NNPP"), make_trip("b", "PPN")], ignore_index=True)
    seg = extract_segments(pts, "target")
    assert seg["segment_id"].tolist() == [0, 1, 2, 3]
    assert seg_tuples(seg) == [
        ("a", 0, 0, 1, 2, 0.0, 2.0, 2.0),
        ("a", 1, 2, 3, 2, 2.0, 3.0, 1.0),
        ("b", 1, 0, 1, 2, 0.0, 2.0, 2.0),   # b não herda nada de a
        ("b", 0, 2, 2, 1, 2.0, 2.0, 0.0),
    ]


def test_string_time_and_class_continuity_across_ids():
    pts = make_trip("a", "NN")
    pts["t"] = pts["t"].astype(str)
    pts = pd.concat([pts, make_trip("b", "NN")], ignore_index=True)
    seg = extract_segments(pts, "target")
    assert len(seg) == 2  # mesma classe em ids diferentes não se funde


@pytest.mark.parametrize("bad", ["decreasing_time", "interleaved_ids", "bad_class",
                                 "nan_class", "nan_time", "missing_col"])
def test_invalid_inputs(bad):
    pts = make_trip("a", "NNPP")
    if bad == "decreasing_time":
        pts.loc[2, "t"] = BASE - pd.Timedelta(seconds=5)
    elif bad == "interleaved_ids":
        pts = pd.concat([make_trip("a", "NN"), make_trip("b", "NN"),
                         make_trip("a", "NN")], ignore_index=True)
    elif bad == "bad_class":
        pts.loc[1, "predicted"] = 2
    elif bad == "nan_class":
        pts["predicted"] = pts["predicted"].astype(float)
        pts.loc[1, "predicted"] = float("nan")
    elif bad == "nan_time":
        pts.loc[1, "t"] = pd.NaT
    elif bad == "missing_col":
        pts = pts.drop(columns=["predicted"])
    with pytest.raises(ValueError):
        extract_segments(pts, "predicted")


def test_equal_times_allowed():
    pts = make_trip("a", "NP")
    pts["t"] = BASE  # não decrescente (iguais) é aceite
    seg = extract_segments(pts, "target")
    assert seg["duration_s"].tolist() == [0.0, 0.0]


REAL = "NNNNNNNPPPPPPPPPPPPNNNNNPPPPPPNNNN"
PRED = "NNNNNNNPPPPPPPNPPPPNNNNNNNPPPPNNNN"


def test_known_example_segments_and_matching():
    pts = make_trip("a", REAL, PRED)
    ref = extract_segments(pts, "target")
    pred = extract_segments(pts, "predicted")
    # Pesca real: [7,19) e [24,30); pesca prevista: [7,14), [15,19), [26,30)
    assert seg_tuples(ref[ref.cls == 1]) == [
        ("a", 1, 7, 18, 12, 7.0, 19.0, 12.0),
        ("a", 1, 24, 29, 6, 24.0, 30.0, 6.0),
    ]
    assert pred[pred.cls == 1][["start_s", "end_s"]].values.tolist() == [
        [7.0, 14.0], [15.0, 19.0], [26.0, 30.0]]
    pairs, unm_pred, unm_ref = match_segments(pred, ref, cls=1, iou_threshold=0.5)
    # IoU: [7,14)/[7,19) = 7/12; [15,19)/[7,19) = 4/12; [26,30)/[24,30) = 4/6
    assert pairs["iou"].tolist() == pytest.approx([7 / 12, 4 / 6])
    assert pairs["erro_inicio_s"].tolist() == [0.0, 2.0]
    assert pairs["erro_fim_s"].tolist() == [-5.0, 0.0]
    assert unm_pred[["start_s", "end_s"]].values.tolist() == [[15.0, 19.0]]
    assert len(unm_ref) == 0


def test_known_example_metrics_fishing():
    m = compute_segment_metrics(make_trip("a", REAL, PRED), cls=1)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (2, 3, 2)
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["sensitivity"] == pytest.approx(1.0)
    assert m["f1"] == pytest.approx(4 / 5)
    assert m["fragmentation_ratio"] == pytest.approx(1.5)
    assert m["mean_iou_matched"] == pytest.approx((7 / 12 + 2 / 3) / 2)  # 0.625
    assert m["mean_abs_start_error_s"] == pytest.approx(1.0)
    assert m["median_abs_start_error_s"] == pytest.approx(1.0)
    assert m["mean_abs_end_error_s"] == pytest.approx(2.5)
    assert m["median_abs_end_error_s"] == pytest.approx(2.5)
    assert m["convencoes"]["iou_threshold"] == 0.5
    assert m["convencoes"]["unidade_tempo"] == "segundos"
    row = m["por_viagem"].iloc[0]
    assert (row["id"], row["n_ref"], row["n_pred"], row["n_matched"]) == ("a", 2, 3, 2)
    assert row["fragmentation_ratio"] == pytest.approx(1.5)


def test_known_example_metrics_navigation():
    # N real: [0,7), [19,24), [30,33]; N previsto: [0,7), [14,15), [19,26), [30,33]
    # IoU: 1, 5/7, 1; [14,15) sem par
    m = compute_segment_metrics(make_trip("a", REAL, PRED), cls=0)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (3, 4, 3)
    assert m["precision"] == pytest.approx(3 / 4)
    assert m["sensitivity"] == pytest.approx(1.0)
    assert m["f1"] == pytest.approx(6 / 7)
    assert m["mean_iou_matched"] == pytest.approx((1 + 5 / 7 + 1) / 3)
    assert m["mean_abs_end_error_s"] == pytest.approx(2 / 3)  # erros 0, 2, 0


def test_tie_prefers_smaller_reference_start():
    # Um previsto [0,10) sobrepõe duas referências [0,4) e [6,10): IoU 0.4 em ambas
    pts = make_trip("a", "PPPPNNPPPPNN", "PPPPPPPPPPNN")
    m = compute_segment_metrics(pts, cls=1, iou_threshold=0.4)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (2, 1, 1)
    pairs, _, unm_ref = match_segments(
        extract_segments(pts, "predicted"), extract_segments(pts, "target"), 1, 0.4)
    assert pairs["ref_segment_id"].tolist() == [0]
    assert unm_ref["start_s"].tolist() == [6.0]


def test_tie_prefers_smaller_predicted_start():
    # Uma referência [0,10) e dois previstos [0,4) e [6,10): IoU 0.4 em ambos
    pts = make_trip("a", "PPPPPPPPPPNN", "PPPPNNPPPPNN")
    pairs, unm_pred, _ = match_segments(
        extract_segments(pts, "predicted"), extract_segments(pts, "target"), 1, 0.4)
    assert pairs["start_s_pred"].tolist() == [0.0]
    assert unm_pred["start_s"].tolist() == [6.0]


def test_pred_overlapping_two_refs_matches_best_only():
    # Previsto [0,10) vs refs [0,6) (IoU 0.6) e [7,10) (IoU 0.3)
    pts = make_trip("a", "PPPPPPNPPPNN", "PPPPPPPPPPNN")
    m = compute_segment_metrics(pts, cls=1)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (2, 1, 1)
    assert m["mean_iou_matched"] == pytest.approx(0.6)
    assert m["sensitivity"] == pytest.approx(0.5)
    assert m["precision"] == pytest.approx(1.0)


def test_iou_below_threshold_no_pair():
    # Ref [0,10), previsto [0,4): IoU 0.4 < 0.5
    pts = make_trip("a", "PPPPPPPPPPNN", "PPPPNNNNNNNN")
    m = compute_segment_metrics(pts, cls=1)
    assert m["n_matched"] == 0
    assert m["precision"] == 0.0 and m["sensitivity"] == 0.0 and m["f1"] == 0.0
    assert m["mean_iou_matched"] is None
    assert m["median_abs_start_error_s"] is None
    assert m["mean_abs_end_error_s"] is None


def test_trip_without_fishing_in_reference():
    pts = pd.concat([make_trip("a", "NNNN", "NNNN"),
                     make_trip("b", "NNNN", "NPPN")], ignore_index=True)
    m = compute_segment_metrics(pts, cls=1)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (0, 1, 0)
    assert m["sensitivity"] is None
    assert m["fragmentation_ratio"] is None
    assert m["f1"] == 0.0 and m["precision"] == 0.0
    pv = m["por_viagem"].set_index("id")
    assert pv.loc["a", "fragmentation_ratio"] is None
    assert pv.loc["b", "fragmentation_ratio"] is None
    assert (pv.loc["b", "n_pred"], pv.loc["a", "n_pred"]) == (1, 0)


def test_no_fishing_anywhere_all_none():
    m = compute_segment_metrics(make_trip("a", "NNNN"), cls=1)
    assert m["n_pred_segments"] == 0 and m["n_ref_segments"] == 0
    for key in ("precision", "sensitivity", "f1", "fragmentation_ratio"):
        assert m[key] is None


def test_micro_aggregation_over_trips():
    # a: ref 1 seg, pred 1 seg igual (par); b: ref 1 seg, pred 2 segs (só 1 par)
    a = make_trip("a", "NPPPPPN", "NPPPPPN")
    b = make_trip("b", "NPPPPPPN", "NPPPNPPN")
    m = compute_segment_metrics(pd.concat([a, b], ignore_index=True), cls=1)
    # b: ref [1,7); previstos [1,4) IoU 3/6=0.5 (par), [5,7) IoU 2/6 (sem par)
    assert (m["n_ref_segments"], m["n_pred_segments"], m["n_matched"]) == (2, 3, 2)
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(4 / 5)
    assert m["fragmentation_ratio"] == pytest.approx(1.5)
    pv = m["por_viagem"].set_index("id")
    assert pv.loc["a", "fragmentation_ratio"] == pytest.approx(1.0)
    assert pv.loc["b", "fragmentation_ratio"] == pytest.approx(2.0)


def test_zero_duration_segments():
    # Viagem de 1 ponto de pesca, igual na referência e no previsto: IoU 1
    m = compute_segment_metrics(make_trip("a", "P"), cls=1)
    assert m["n_matched"] == 1 and m["mean_iou_matched"] == 1.0
    # Último ponto isolado: ref P em [5,5], previsto N → sem par
    pts = make_trip("a", "NNNNNP", "NNNNNN")
    assert compute_segment_metrics(pts, cls=1)["n_matched"] == 0
    # Previsto de duração 0 contra referência com duração: IoU 0
    pts = make_trip("a", "NPPPPP", "NNNNNP")
    assert compute_segment_metrics(pts, cls=1)["n_matched"] == 0
    # Duração 0 em ambos mas inícios diferentes: IoU 0 (via match_segments)
    ref = pd.DataFrame({"segment_id": [0], "id": ["a"], "cls": [1],
                        "start_s": [3.0], "end_s": [3.0]})
    pred = ref.assign(start_s=4.0, end_s=4.0)
    pairs, up, ur = match_segments(pred, ref, 1, 0.5)
    assert len(pairs) == 0 and len(up) == 1 and len(ur) == 1


def test_invalid_threshold():
    with pytest.raises(ValueError):
        compute_segment_metrics(make_trip("a", "NP"), cls=1, iou_threshold=0.0)
