"""Medição final no `validation` (Marcos 6 e 7): só dados sintéticos inventados nos testes.

Monta um projeto-miniatura numa pasta temporária (base `validation` sintética, três modelos congelados e
os resultados do `test` de cada um) e corre o programa de ponta a ponta, sem tocar em nenhum dado real.
"""
import json

import numpy as np
import pandas as pd
import pytest
import torch

from ais.cli.final_validation import choose_model, run_final_validation
from ais.phase1.artifacts import save_checkpoint
from ais.phase1.data import INPUT_CHANNELS, N_INPUT_CHANNELS, build_full_sequences, fit_scaler
from ais.phase1.model import build_cnn
from ais.phase1.reserved import read_log, sha256_of

AUTH = {"id": "vf1", "conjuntos_autorizados": ["validation"], "finalidade": "medicao_final",
        "max_rondas": 1, "validation_autorizado": True}
PROTO = {"id": "pf1", "conjunto": "validation", "declarado_antes_de_abrir_o_test": True}


def tables(acc, f1_nav, f1_fish):
    return {"global": {"accuracy": acc, "por_classe": {"navegação": {"f1": f1_nav}, "pesca": {"f1": f1_fish}}}}


def make_df(ids, seed):
    rng = np.random.default_rng(seed)
    parts, pid = [], 0
    for tid in ids:
        n = int(rng.integers(30, 50))
        speed = rng.normal(5, 2, n)
        d = pd.DataFrame({
            "id": tid, "point_id": np.arange(pid, pid + n),
            "t": pd.Timestamp("2021-01-01") + pd.to_timedelta(np.arange(n) * 10, unit="s"),
            "speed_calc_mps": speed, "signed_turn_calc_deg": rng.normal(0, 10, n),
            "time_gap_calc_s": np.full(n, 10.0), "distanceToShore": rng.normal(1000, 100, n),
            "target": (speed > 5).astype("int8")})
        d["label"] = np.where(d["target"] == 1, "02-fishing", "01-sailing")
        d.loc[d.index[0], ["speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s"]] = np.nan
        d.loc[d.index[1], "signed_turn_calc_deg"] = np.nan
        parts.append(d)
        pid += n
    return pd.concat(parts, ignore_index=True)


def make_project(tmp, test_tables, auth=AUTH):
    """`test_tables`: {modelo: tabelas do test}. Devolve a raiz do projeto-miniatura."""
    (tmp / "data").mkdir()
    (tmp / "manifests").mkdir()
    (tmp / "configs" / "authorizations").mkdir(parents=True)
    pd.DataFrame({"id": ["T1", "T2", "V1", "V2"], "split": ["train", "train", "validation", "validation"]}
                 ).to_csv(tmp / "manifests" / "split_manifest_seed42.csv", index=False)
    make_df(["V1", "V2"], 2).to_parquet(tmp / "data" / "123_fishing_trajs_clean_validation.parquet")
    scaler = fit_scaler(build_full_sequences(make_df(["T1", "T2"], 1)))
    (tmp / "configs" / "authorizations" / "validation_final.json").write_text(json.dumps(auth))
    (tmp / "configs" / "selection_protocol_validation.json").write_text(json.dumps(PROTO))
    spec = {"baseline": ("baseline_frozen", "baseline", {}, 162, 0.65),
            "J0": ("windows_j0_frozen", "j0", {"window_length": 16, "overlap": 0.0}, 8, 0.6),
            "J50": ("windows_j50_frozen", "j50", {"window_length": 16, "overlap": 0.5}, 4, 0.75)}
    for k, (name, (d, label, cfg, ep, th)) in enumerate(spec.items()):
        torch.manual_seed(k)
        save_checkpoint(tmp / "results" / d / "checkpoint_frozen.pt", build_cnn(n_channels=N_INPUT_CHANNELS), None,
                        cfg, scaler, ep, {}, INPUT_CHANNELS)
        (tmp / "results" / d / f"{label}_frozen.json").write_text(json.dumps({
            "epoca": ep, "limiar": th, "checkpoint": "checkpoint_frozen.pt",
            "checkpoint_sha256": sha256_of(tmp / "results" / d / "checkpoint_frozen.pt")}))
    (tmp / "results" / "baseline_frozen" / "test_segment_results.json").write_text(
        json.dumps({"metricas_no_test": test_tables["baseline"]}))
    for name, d in (("J0", "windows_j0"), ("J50", "windows_j50")):
        (tmp / "results" / d).mkdir(parents=True, exist_ok=True)
        (tmp / "results" / d / "selection_test.json").write_text(
            json.dumps({"metricas_no_test_com_limiar_escolhido": test_tables[name]}))
    return tmp


BEST = {"baseline": tables(0.95, 0.93, 0.96), "J0": tables(0.93, 0.91, 0.94), "J50": tables(0.94, 0.92, 0.95)}


def test_choice_rule_and_tie_breaks():
    assert choose_model(BEST)[0] == "baseline"
    t = {"baseline": tables(0.9, 0.9, 0.9), "J0": tables(0.9, 0.9, 0.9), "J50": tables(0.9, 0.9, 0.9)}
    assert choose_model(t)[0] == "baseline"  # ordem
    t["J0"] = tables(0.91, 0.9, 0.9)
    assert choose_model(t)[0] == "J0"  # empate no F1: maior exatidão
    t["J50"] = tables(0.5, 0.95, 0.9)
    assert choose_model(t)[0] == "J50"  # F1 médio maior vence a exatidão
    ranking = choose_model(t)[1]
    assert [r["modelo"] for r in ranking][0] == "J50" and len(ranking) == 3


def test_baseline_chosen_runs_once_logs_and_second_run_is_refused(tmp_path):
    root = make_project(tmp_path, BEST)
    res = run_final_validation(root)
    assert res["modelo"] == "baseline" and res["n_viagens"] == 2
    events = [e["event"] for e in read_log(root / "results" / "access_log.jsonl")]
    assert events == ["model_chosen", "open", "final_measurement_done"]
    out = root / "results" / "final_validation"
    assert json.loads((out / "model_choice.json").read_text())["escolhido"] == "baseline"
    pred = pd.read_csv(out / "predictions_validation.csv")
    assert pred["point_id"].is_unique and len(pred) == res["n_pontos"]
    assert set(res["segmentos_validation"]) == {"pesca", "navegacao"} and res["test_do_mesmo_modelo"] == BEST["baseline"]
    with pytest.raises(PermissionError, match="já foi aberto"):
        run_final_validation(root)
    assert [e["event"] for e in read_log(root / "results" / "access_log.jsonl")] == events  # nada de novo


def test_window_model_chosen_uses_windows_and_only_that_model(tmp_path):
    t = dict(BEST)
    t["J50"] = tables(0.97, 0.96, 0.97)
    root = make_project(tmp_path, t)
    res = run_final_validation(root)
    assert res["modelo"] == "J50" and res["epoca"] == 4 and res["limiar"] == 0.75
    pred = pd.read_csv(root / "results" / "final_validation" / "predictions_validation.csv")
    assert pred["n_windows"].max() == 2  # sobreposição de 50 %
    opens = [e for e in read_log(root / "results" / "access_log.jsonl") if e["event"] == "open"]
    assert len(opens) == 1 and opens[0]["split"] == "validation"


def test_tampered_model_blocks_before_anything_is_logged(tmp_path):
    root = make_project(tmp_path, BEST)
    (root / "results" / "windows_j0_frozen" / "checkpoint_frozen.pt").write_bytes(b"x")
    with pytest.raises(ValueError, match="não confere"):
        run_final_validation(root)
    assert read_log(root / "results" / "access_log.jsonl") == []


def test_authorization_without_validation_flag_never_opens(tmp_path):
    root = make_project(tmp_path, BEST, auth={**AUTH, "validation_autorizado": False})
    with pytest.raises(PermissionError, match="autorização própria"):
        run_final_validation(root)
    events = [e["event"] for e in read_log(root / "results" / "access_log.jsonl")]
    assert "open" not in events and "final_measurement_done" not in events
