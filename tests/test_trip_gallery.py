"""Galeria de viagens (ais.cli.build_trip_gallery), só com dados sintéticos numa raiz temporária."""
import json

import numpy as np
import pandas as pd
import pytest

from ais.cli import build_trip_gallery as G
from ais.cli.postproc_validation import THRESHOLD, apply_filter
from ais.phase1.postprocessing import gaussian_kernel
from ais.phase1.reserved import read_log, sha256_of


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(obj, pd.DataFrame):
        obj.to_csv(path, index=False)
    else:
        path.write_text(json.dumps(obj), encoding="utf-8")


def _points(prefix: str, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frames = []
    for n, trip in ((700, f"{prefix}-1"), (450, f"{prefix}-2")):
        target = (np.arange(n) // 150) % 2
        p = np.clip(target + rng.normal(0, 0.45, n), 0, 1)
        frames.append(pd.DataFrame({"id": trip, "t": pd.date_range("2000-01-01", periods=n, freq="10s").astype(str),
                                    "target": target, "p_fishing": p}))
    df = pd.concat(frames, ignore_index=True)
    df.insert(1, "point_id", [f"{prefix}{k}" for k in range(len(df))])
    df["predicted"] = (df["p_fishing"] >= THRESHOLD).astype(int)
    return df


def _saved(values, row):
    tables = {i: {"accuracy": v["accuracy"]} for i, v in values[row].items()}
    segments = [{"id": i, "n_pred": v["n_pred"], "n_ref": v["n_ref"]} for i, v in values[row].items()]
    return tables, segments


@pytest.fixture
def root(tmp_path):
    test, val = _points("T", 1), _points("V", 2)
    for split, spec in G.SETS.items():
        _write(tmp_path / spec["auth"], {"id": f"auth_{split}", "conjuntos_autorizados": [split],
                                         "finalidade": "galeria_viagens",
                                         "validation_autorizado": split == "validation"})
    _write(tmp_path / G.MANIFEST, pd.DataFrame({"id": ["T-1", "T-2", "V-1", "V-2"],
                                                "split": ["test", "test", "validation", "validation"]}))
    src = G.SETS["test"]["sources"]
    _write(tmp_path / src[G.BASE], test)
    j0, j50 = test.assign(predicted=1 - test["predicted"]), test.assign(predicted=test["target"])
    _write(tmp_path / src["J0"], j0.sample(frac=1, random_state=3))  # a ordem do ficheiro não pode importar
    _write(tmp_path / src["J50"], j50)

    kernel = gaussian_kernel(G.SIZE, G.SIZE / 6)
    filtered = apply_filter(test, THRESHOLD, kernel)["predicted_filtrado"]
    frame = pd.DataFrame({"id": test["id"], "t": test["t"], G.REAL: test["target"], G.BASE: test["predicted"],
                          "J0": j0["predicted"], "J50": j50["predicted"], G.PP: filtered})
    values = G.trip_values(frame, G.SETS["test"]["rows"])
    block = {}
    for row in (G.BASE, "J0", "J50"):
        tables, segments = _saved(values, row)
        block[row] = {"test": {"por_viagem": tables}, "segmentos_test": {"pesca": {"por_viagem": segments}}}
    windows, evaluation = G.SETS["test"]["checks"]
    _write(tmp_path / windows, {"baseline": block[G.BASE], "variantes": {n: block[n] for n in ("J0", "J50")}})
    _write(tmp_path / evaluation, {
        "fonte_sha256": sha256_of(tmp_path / src[G.BASE]),
        "exatidao_por_viagem": {"301": {i: v["accuracy"] for i, v in values[G.PP].items()}},
        "resumo": [{"janela": None}, {"janela": 301,
                                      "seg_pesca_previstos": sum(v["n_pred"] for v in values[G.PP].values())}]})

    after = apply_filter(val, THRESHOLD, kernel)
    saved_val = val.drop(columns=["predicted"]).assign(predicted_antes=val["predicted"],
                                                       predicted_depois=after["predicted_filtrado"])
    _write(tmp_path / G.SETS["validation"]["sources"][G.BASE], saved_val)
    frame = pd.DataFrame({"id": val["id"], "t": val["t"], G.REAL: val["target"], G.BASE: val["predicted"],
                          G.PP: after["predicted_filtrado"]})
    values = G.trip_values(frame, G.SETS["validation"]["rows"])
    result = {}
    for row, k in ((G.BASE, "antes"), (G.PP, "depois")):
        tables, segments = _saved(values, row)
        result[k] = {"ponto": {"por_viagem": tables}, "segmento": {"pesca": {"por_viagem": segments}}}
    _write(tmp_path / G.SETS["validation"]["checks"][0], result)
    return tmp_path


def test_build_writes_one_image_per_trip_page_and_provenance(root):
    info = G.build(root)
    assert sorted(info["imagens_sha256"]) == ["viagens/teste/T-1.png", "viagens/teste/T-2.png",
                                              "viagens/validacao/V-1.png", "viagens/validacao/V-2.png"]
    page = (root / "viagens" / "README.md").read_text(encoding="utf-8")
    test_part, val_part = page.split("## Teste")[1].split("## Validação")
    assert "| J0 |" in test_part and "| J50 |" in test_part and f"| {G.PP} |" in test_part
    assert "| J0 |" not in val_part and "| J50 |" not in val_part
    assert "![Viagem V-2" in val_part and "(validacao/V-2.png)" in val_part
    assert [e["split"] for e in read_log(root / "results" / "access_log.jsonl")] == ["test", "validation"]


def test_mismatch_with_saved_results_writes_nothing(root):
    path = root / G.SETS["validation"]["checks"][0]
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved["depois"]["ponto"]["por_viagem"]["V-1"]["accuracy"] += 0.01
    _write(path, saved)
    with pytest.raises(ValueError, match="não coincidem"):
        G.build(root)
    assert not (root / "viagens").exists()


def test_missing_authorization_stops_before_reading(root):
    path = root / G.SETS["validation"]["auth"]
    auth = json.loads(path.read_text(encoding="utf-8"))
    _write(path, {**auth, "validation_autorizado": False})
    with pytest.raises(PermissionError):
        G.build(root)
    assert not (root / "results" / "access_log.jsonl").exists() and not (root / "viagens").exists()


def test_variant_with_other_points_is_refused(root):
    path = root / G.SETS["test"]["sources"]["J50"]
    pd.read_csv(path).iloc[:-1].to_csv(path, index=False)
    with pytest.raises(ValueError, match="mesmos"):
        G.build(root)


def test_trips_outside_the_manifest_split_are_refused(root):
    _write(root / G.MANIFEST, pd.DataFrame({"id": ["T-1", "V-1", "V-2"], "split": ["test", "validation", "validation"]}))
    with pytest.raises(ValueError, match="manifesto"):
        G.build(root)
