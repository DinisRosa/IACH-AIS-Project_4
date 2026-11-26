"""A opção que refaz a figura da validação recusa uma autorização inválida, sem ler nada (só sintéticos)."""
import json

import pytest

from ais.cli import build_validation_results as V


def test_invalid_authorization_stops_before_reading(tmp_path, monkeypatch):
    auth = tmp_path / V.FIG_AUTH
    auth.parent.mkdir(parents=True)
    auth.write_text(json.dumps({"id": "x", "conjuntos_autorizados": ["test"], "finalidade": "figuras_relatorio",
                                "validation_autorizado": False}), encoding="utf-8")
    monkeypatch.setattr(V, "ROOT", tmp_path)
    monkeypatch.setattr(V, "FV", tmp_path / "nao-existe")
    with pytest.raises(PermissionError):
        V.main(["--worst-trip-figure-only"])
    assert not (tmp_path / "results").exists()
