"""Testes sintéticos do pós-processamento no validation (REV-057 e REV-059).

Só dados criados aqui (tmp_path); nunca se toca em results/ nem data/ do projeto real.
Os protocolos reais (v1 e v2) são apenas copiados como modelo de estrutura.

Cada versão tem o seu protocolo, o seu tamanho de janela e a sua pasta de saída:
  - posproc_validation_v1: configs/postproc_protocol.json, 13 pontos, results/postproc_validation;
  - posproc_validation_v2: configs/postproc_protocol_v2.json, 301 pontos, results/postproc_validation_v2.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ais.cli import postproc_validation as pv
from ais.phase1.postprocessing import gaussian_kernel
from ais.phase1.reserved import log_access, read_log, sha256_of

REAL_PROTOCOL = Path(__file__).resolve().parents[1] / "configs" / "postproc_protocol.json"
REAL_PROTOCOL_V2 = Path(__file__).resolve().parents[1] / "configs" / "postproc_protocol_v2.json"
KERNEL = gaussian_kernel(13, 13 / 6)
KERNEL_V2 = gaussian_kernel(301, 301 / 6)
V1 = "posproc_validation_v1"
V2 = "posproc_validation_v2"


def _t(i: int) -> str:
    return (pd.Timestamp("2020-01-01") + pd.Timedelta(minutes=i)).isoformat()


def _df(rows) -> pd.DataFrame:
    """rows: (id, point_id, t_index, target, p_fishing)."""
    df = pd.DataFrame(rows, columns=["id", "point_id", "ti", "target", "p_fishing"])
    df["t"] = df["ti"].map(_t)
    df["predicted"] = (df["p_fishing"] >= 0.65).astype(int)
    return df.drop(columns="ti")


# ---------------------------------------------------------------- order_points
def test_order_points_sorts_by_t_keeps_trip_appearance_order():
    df = _df([("B", 1, 2, 0, 0.1), ("A", 2, 1, 0, 0.1), ("B", 3, 0, 0, 0.1), ("A", 4, 0, 0, 0.1)])
    out = pv.order_points(df)
    assert out["id"].tolist() == ["B", "B", "A", "A"]  # B apareceu primeiro
    assert out["point_id"].tolist() == [3, 1, 4, 2]


def test_order_points_ties_broken_by_point_id():
    df = _df([("A", 9, 0, 0, 0.1), ("A", 5, 0, 0, 0.1), ("A", 7, 0, 0, 0.1)])
    assert pv.order_points(df)["point_id"].tolist() == [5, 7, 9]


def test_order_points_rejects_duplicate_point_id():
    df = _df([("A", 1, 0, 0, 0.1), ("B", 1, 0, 0, 0.1)])
    with pytest.raises(ValueError, match="point_id repetido"):
        pv.order_points(df)


def test_order_points_rejects_missing_columns():
    df = _df([("A", 1, 0, 0, 0.1)]).drop(columns=["target"])
    with pytest.raises(ValueError, match="Colunas em falta"):
        pv.order_points(df)


# ---------------------------------------------------------------- apply_filter
def test_apply_filter_keeps_original_columns():
    df = _df([("A", i, i, 0, 0.9 if i == 3 else 0.1) for i in range(20)])
    out = pv.apply_filter(df, 0.65, KERNEL)
    assert np.array_equal(out["p_fishing"], df["p_fishing"])
    assert np.array_equal(out["predicted"], df["predicted"])
    assert {"p_fishing_filtrada", "predicted_filtrado"} <= set(out.columns)


def test_apply_filter_trip_shorter_than_kernel():
    df = _df([("A", i, i, 0, 0.1) for i in range(10)])
    assert len(pv.apply_filter(df, 0.65, KERNEL)) == 10


def test_apply_filter_removes_isolated_fishing_point():
    p = [0.0] * 30 + [1.0] + [0.0] * 30
    df = _df([("A", i, i, 0, v) for i, v in enumerate(p)])
    out = pv.apply_filter(df, 0.65, KERNEL)
    assert df["predicted"].sum() == 1
    assert out["predicted_filtrado"].sum() == 0


def test_apply_filter_v2_kernel_smooths_short_block():
    # Com a janela de 301 pontos, um bloco de 60 pontos de pesca não chega para passar o limiar.
    p = [0.0] * 180 + [1.0] * 60 + [0.0] * 180
    df = _df([("A", i, i, 0, v) for i, v in enumerate(p)])
    out = pv.apply_filter(df, 0.65, KERNEL_V2)
    assert df["predicted"].sum() == 60
    assert out["predicted_filtrado"].sum() == 0


def test_apply_filter_does_not_mix_trips():
    rows = [("A", i, i, 0, 0.0) for i in range(20)] + [("B", 100 + i, i, 1, 1.0) for i in range(20)]
    out = pv.apply_filter(_df(rows), 0.65, KERNEL)
    assert np.allclose(out.loc[out["id"] == "A", "p_fishing_filtrada"], 0.0)
    assert np.allclose(out.loc[out["id"] == "B", "p_fishing_filtrada"], 1.0)


# -------------------------------------------------------------- change_summary
def test_change_summary_hand_counted():
    # before, after, target
    cases = [
        (0, 1, 1),  # nav->pesca, corrigido
        (0, 1, 0),  # nav->pesca, estragado
        (1, 0, 0),  # pesca->nav, corrigido
        (1, 0, 1),  # pesca->nav, estragado
        (1, 0, 0),  # pesca->nav, corrigido
        (1, 1, 1),  # igual
        (0, 0, 1),  # igual
        (0, 0, 0),  # igual
    ]
    df = pd.DataFrame(cases, columns=["predicted", "predicted_filtrado", "target"])
    assert pv.change_summary(df) == {
        "n_pontos": 8, "n_mudam": 5, "navegacao_para_pesca": 2, "pesca_para_navegacao": 3,
        "corrigidos": 3, "estragados": 2,
    }


# --------------------------------------------------------------------- measure
def test_measure_hand_computed_accuracy_and_segments():
    target = [0, 0, 1, 1, 0, 0]
    before = [0, 1, 0, 1, 1, 0]  # 3/6 certos; 2 segmentos de pesca previstos
    after = [0, 0, 1, 1, 0, 0]   # 6/6 certos; 1 segmento
    df = pd.DataFrame({"id": "A", "point_id": range(6), "t": [_t(i) for i in range(6)],
                       "target": target, "predicted": before, "predicted_filtrado": after,
                       "label": target})
    res = pv.measure(df)
    assert res["antes"]["ponto"]["global"]["accuracy"] == pytest.approx(0.5)
    assert res["depois"]["ponto"]["global"]["accuracy"] == pytest.approx(1.0)
    assert res["antes"]["segmento"]["pesca"]["n_pred_segments"] == 2
    assert res["depois"]["segmento"]["pesca"]["n_pred_segments"] == 1
    assert res["antes"]["segmento"]["pesca"]["n_ref_segments"] == 1
    assert res["mudancas"]["n_mudam"] == 3


# ------------------------------------------------------------------ run / repo
def _synthetic_csv(path: Path, n: int = 40) -> None:
    """Duas viagens de n pontos cada, com um bloco de pesca a meio; linhas baralhadas."""
    rng = np.random.default_rng(0)
    rows = []
    for trip, base in (("V1", 0), ("V2", 1000)):
        for i in range(n):
            fishing = 1 if n // 4 <= i < n // 2 else 0
            p = float(np.clip(fishing * 0.8 + 0.1 + rng.normal(0, 0.25), 0, 1))
            rows.append((trip, base + i, i, fishing, p))
    df = _df(rows)
    df["label"] = df["target"]
    df = df.sample(frac=1, random_state=1)  # linhas baralhadas: order_points tem de as pôr em ordem
    path.parent.mkdir(parents=True, exist_ok=True)
    df[["id", "point_id", "t", "target", "p_fishing", "predicted", "label"]].to_csv(path, index=False)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _make_repo(root: Path, *, version: str = V1, commit: bool = True, size: int | None = None,
               sigma: str | None = None, proto_id: str | None = None, bad_predicted: bool = False,
               wrong_hash: bool = False, n_points: int | None = None) -> Path:
    """Repositório sintético com o protocolo da versão no caminho certo e o hash do CSV criado aqui."""
    spec = pv.PROTOCOLS[version]
    n = n_points if n_points is not None else (40 if version == V1 else 420)
    csv = root / pv.SOURCE
    _synthetic_csv(csv, n)
    if bad_predicted:
        df = pd.read_csv(csv)
        df.loc[0, "predicted"] = 1 - df.loc[0, "predicted"]
        df.to_csv(csv, index=False)
    model = REAL_PROTOCOL if version == V1 else REAL_PROTOCOL_V2
    proto = json.loads(model.read_text(encoding="utf-8"))
    proto["id"] = proto_id or version
    proto["execucoes"] = 1
    proto["fonte"]["ficheiro"] = pv.SOURCE
    proto["fonte"]["sha256"] = "0" * 64 if wrong_hash else sha256_of(csv)
    proto["filtro"]["tamanho_pontos"] = spec["size"] if size is None else size
    proto["filtro"]["sigma_pontos"] = sigma or f"{proto['filtro']['tamanho_pontos']}/6"
    proto["filtro"]["limiar_depois_do_filtro"] = pv.THRESHOLD
    p = root / spec["path"]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(proto, indent=2), encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    if commit:
        _git(root, "add", spec["path"])
        _git(root, "commit", "-q", "-m", f"protocolo {version}")
    return root


# ------------------------------------------------------- load / preconditions
def test_load_protocol_reads_each_version_from_its_own_path(tmp_path):
    _make_repo(tmp_path, version=V1)
    _make_repo(tmp_path, version=V2)
    p1 = pv.load_protocol(tmp_path, V1)
    p2 = pv.load_protocol(tmp_path, V2)
    assert p1["id"] == V1 and int(p1["filtro"]["tamanho_pontos"]) == 13
    assert p2["id"] == V2 and int(p2["filtro"]["tamanho_pontos"]) == 301
    assert (tmp_path / "configs" / "postproc_protocol.json").exists()
    assert (tmp_path / "configs" / "postproc_protocol_v2.json").exists()


def test_check_preconditions_new_signature(tmp_path):
    _make_repo(tmp_path, version=V1)
    log = tmp_path / "results" / "access_log.jsonl"
    proto = pv.load_protocol(tmp_path, V1)
    pv.check_preconditions(tmp_path, V1, proto, log)  # não levanta
    (tmp_path / "results" / "postproc_validation").mkdir(parents=True)
    with pytest.raises(PermissionError, match="já foi executado"):
        pv.check_preconditions(tmp_path, V1, proto, log)


# ---------------------------------------------------------------- ponta a ponta
def test_run_v1_end_to_end_and_single_execution(tmp_path):
    _make_repo(tmp_path, version=V1)
    res = pv.run(root=tmp_path, version=V1)
    out = tmp_path / "results" / "postproc_validation"
    assert (out / "predictions_validation_postproc.csv").exists()
    saved = json.loads((out / "postproc_validation.json").read_text(encoding="utf-8"))
    assert saved["versao"] == V1 and saved["protocolo"] == V1
    assert saved["n_viagens"] == 2 and res["n_viagens"] == 2
    assert saved["mudancas"]["n_pontos"] == 80
    assert len(saved["filtro"]["pesos"]) == 13
    events = read_log(tmp_path / "results" / "access_log.jsonl")
    assert [e["event"] for e in events] == ["postproc_start", "postproc_done"]
    assert {e["protocol"] for e in events} == {V1}
    out_df = pd.read_csv(out / "predictions_validation_postproc.csv")
    src = pd.read_csv(tmp_path / pv.SOURCE)
    first = src["id"].drop_duplicates().tolist()  # o CSV está baralhado: conta a ordem de aparição
    assert out_df["id"].tolist() == [v for v in first for _ in range(40)]
    with pytest.raises(PermissionError, match="já foi executado"):
        pv.run(root=tmp_path, version=V1)


def test_run_v2_end_to_end(tmp_path):
    _make_repo(tmp_path, version=V2)
    res = pv.run(root=tmp_path, version=V2)
    out = tmp_path / "results" / "postproc_validation_v2"
    assert (out / "predictions_validation_postproc.csv").exists()
    saved = json.loads((out / "postproc_validation.json").read_text(encoding="utf-8"))
    assert saved["versao"] == V2 and saved["protocolo"] == V2
    assert saved["filtro"]["tamanho_pontos"] == 301
    assert len(saved["filtro"]["pesos"]) == 301
    assert saved["filtro"]["sigma_pontos"] == pytest.approx(301 / 6)
    assert saved["mudancas"]["n_pontos"] == 840 and res["n_viagens"] == 2
    assert not (tmp_path / "results" / "postproc_validation").exists()
    events = read_log(tmp_path / "results" / "access_log.jsonl")
    assert [e["event"] for e in events] == ["postproc_start", "postproc_done"]
    assert {e["protocol"] for e in events} == {V2}
    out_df = pd.read_csv(out / "predictions_validation_postproc.csv")
    src = pd.read_csv(tmp_path / pv.SOURCE)
    first = src["id"].drop_duplicates().tolist()
    assert out_df["id"].tolist() == [v for v in first for _ in range(420)]


def test_v1_run_does_not_block_v2(tmp_path):
    # As duas versões partilham o mesmo CSV de previsões: com o mesmo n o segundo _make_repo recria um
    # ficheiro idêntico e o hash do protocolo v1 continua válido.
    _make_repo(tmp_path, version=V1, n_points=420)
    _make_repo(tmp_path, version=V2)  # os dois protocolos ficam commitados
    r1 = pv.run(root=tmp_path, version=V1)
    r2 = pv.run(root=tmp_path, version=V2)
    assert r1["versao"] == V1 and len(r1["filtro"]["pesos"]) == 13
    assert r2["versao"] == V2 and len(r2["filtro"]["pesos"]) == 301
    assert (tmp_path / "results" / "postproc_validation").is_dir()
    assert (tmp_path / "results" / "postproc_validation_v2").is_dir()
    protos = [e["protocol"] for e in read_log(tmp_path / "results" / "access_log.jsonl")]
    assert protos == [V1, V1, V2, V2]


def test_run_defaults_to_v2_and_second_run_refused(tmp_path):
    _make_repo(tmp_path, version=V2)
    res = pv.run(root=tmp_path)  # por omissão é a v2
    assert res["versao"] == V2
    assert (tmp_path / "results" / "postproc_validation_v2").is_dir()
    with pytest.raises(PermissionError, match="já foi executado"):
        pv.run(root=tmp_path, version=V2)


# --------------------------------------------------------------------- recusas
def test_refuses_wrong_hash(tmp_path):
    _make_repo(tmp_path, version=V1, wrong_hash=True)
    with pytest.raises(ValueError, match="hash"):
        pv.run(root=tmp_path, version=V1)
    assert not (tmp_path / "results" / "postproc_validation").exists()


def test_refuses_uncommitted_protocol(tmp_path):
    _make_repo(tmp_path, version=V1, commit=False)
    with pytest.raises(PermissionError, match="commitado"):
        pv.run(root=tmp_path, version=V1)


def test_refuses_protocol_modified_after_commit(tmp_path):
    _make_repo(tmp_path, version=V1)
    p = tmp_path / "configs" / "postproc_protocol.json"
    p.write_text(p.read_text(encoding="utf-8") + "\n ", encoding="utf-8")
    with pytest.raises(PermissionError, match="commitado"):
        pv.run(root=tmp_path, version=V1)


def test_refuses_filter_size_11(tmp_path):
    _make_repo(tmp_path, version=V1, size=11)
    with pytest.raises(ValueError, match="protocolo"):
        pv.run(root=tmp_path, version=V1)


def test_refuses_predicted_inconsistent_with_threshold(tmp_path):
    _make_repo(tmp_path, version=V1, bad_predicted=True)
    with pytest.raises(ValueError, match="limiar"):
        pv.run(root=tmp_path, version=V1)


def test_failure_mid_run_does_not_burn_single_execution(tmp_path):
    # Uma falha técnica depois de ler o CSV não regista nada nem grava resultados.
    _make_repo(tmp_path, version=V1, bad_predicted=True)
    with pytest.raises(ValueError):
        pv.run(root=tmp_path, version=V1)
    assert read_log(tmp_path / "results" / "access_log.jsonl") == []
    assert not (tmp_path / "results" / "postproc_validation").exists()


def test_refuses_changed_threshold_or_source(tmp_path):
    for key, val in (("limiar", 0.55), ("fonte", "results/outro.csv")):
        root = tmp_path / key
        root.mkdir()
        _make_repo(root, version=V1)
        p = root / "configs" / "postproc_protocol.json"
        proto = json.loads(p.read_text(encoding="utf-8"))
        if key == "limiar":
            proto["filtro"]["limiar_depois_do_filtro"] = val
        else:
            proto["fonte"]["ficheiro"] = val
        p.write_text(json.dumps(proto), encoding="utf-8")
        _git(root, "commit", "-qam", "muda")
        with pytest.raises(ValueError, match="protocolo"):
            pv.run(root=root, version=V1)


def test_previous_event_blocks_even_without_output_dir(tmp_path):
    # Apagar a pasta de saída não devolve a execução única: o evento no registo continua a bloquear.
    _make_repo(tmp_path, version=V1)
    pv.run(root=tmp_path, version=V1)
    shutil.rmtree(tmp_path / "results" / "postproc_validation")
    with pytest.raises(PermissionError, match="já foi executado"):
        pv.run(root=tmp_path, version=V1)


# ------------------------------------------------------------- recusas da v2
def test_refuses_v2_protocol_with_size_13(tmp_path):
    _make_repo(tmp_path, version=V2, size=13)
    with pytest.raises(ValueError, match="protocolo"):
        pv.run(root=tmp_path, version=V2)
    assert not (tmp_path / "results" / "postproc_validation_v2").exists()


def test_refuses_v2_protocol_with_wrong_sigma(tmp_path):
    _make_repo(tmp_path, version=V2, sigma="301/4")
    with pytest.raises(ValueError, match="protocolo"):
        pv.run(root=tmp_path, version=V2)
    assert not (tmp_path / "results" / "postproc_validation_v2").exists()


def test_refuses_v2_protocol_with_other_id(tmp_path):
    _make_repo(tmp_path, version=V2, proto_id=V1)
    with pytest.raises(ValueError, match="protocolo"):
        pv.run(root=tmp_path, version=V2)


def test_unknown_version_raises_value_error(tmp_path):
    _make_repo(tmp_path, version=V2)
    with pytest.raises(ValueError, match="desconhecida"):
        pv.run(root=tmp_path, version="posproc_validation_v3")
    assert read_log(tmp_path / "results" / "access_log.jsonl") == []
    assert not (tmp_path / "results" / "postproc_validation_v2").exists()


def test_refuses_unknown_protocol_event_in_log(tmp_path):
    _make_repo(tmp_path, version=V2)
    log = tmp_path / "results" / "access_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    log_access(log, {"event": "postproc_start", "split": "validation", "protocol": "posproc_validation_v9"})
    with pytest.raises(PermissionError, match="fora da lista"):
        pv.run(root=tmp_path, version=V2)
    assert not (tmp_path / "results" / "postproc_validation_v2").exists()



@pytest.fixture(autouse=True)
def _synthetic_source_hash(monkeypatch):
    # Os CSV sintéticos têm outro hash: o hash fixado no código só vale para o projeto real.
    monkeypatch.setattr(pv, "SOURCE_SHA256", None)


def test_pinned_source_hash_is_enforced(tmp_path, monkeypatch):
    _make_repo(tmp_path, version=V2)
    monkeypatch.setattr(pv, "SOURCE_SHA256", "f" * 64)
    with pytest.raises(ValueError, match="medição final"):
        pv.run(root=tmp_path, version=V2)


def test_refuses_uncommitted_code(tmp_path):
    _make_repo(tmp_path, version=V2)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(PermissionError, match="commitados"):
        pv.run(root=tmp_path, version=V2)


def test_write_failure_does_not_burn_execution(tmp_path, monkeypatch):
    _make_repo(tmp_path, version=V2)
    def boom(*a, **k):
        raise OSError("disco cheio")
    monkeypatch.setattr(pv, "_write_outputs", boom)
    with pytest.raises(OSError):
        pv.run(root=tmp_path, version=V2)
    assert read_log(tmp_path / "results" / "access_log.jsonl") == []
    assert not (tmp_path / "results" / "postproc_validation_v2").exists()
    assert not (tmp_path / "results" / "postproc_validation_v2.tmp").exists()
    monkeypatch.undo()
    monkeypatch.setattr(pv, "SOURCE_SHA256", None)
    assert pv.run(root=tmp_path, version=V2)["versao"] == V2
