"""Macros da primeira versão do filtro (ais.cli.build_postproc_results), só com dados sintéticos."""
import re

from ais.cli.build_postproc_results import first_version_macros


def _trips(*accuracies: float) -> dict:
    return {str(i): {"n_points": 10, "accuracy": a, "n_errors": 1, "accuracy_maioritaria": 0.5}
            for i, a in enumerate(accuracies)}


def test_first_version_macros_take_each_value_from_the_summary():
    R = {"criado_utc": "2000-01-01T00:00:00+00:00", "git_commit": "abcdef0123", "filtro": {"tamanho_pontos": 13},
         "antes": {"ponto": {"por_viagem": _trips(0.5, 0.5, 0.5, 0.5)}},
         "depois": {"ponto": {"por_viagem": _trips(0.6, 0.7, 0.4, 0.5), "global": {"accuracy": 0.9454}},
                    "segmento": {"pesca": {"n_pred_segments": 1255, "f1": 0.0659}}}}
    values = dict(re.findall(r"\\newcommand\{\\res(\w+)\}\{(.*)\}", first_version_macros(R)))
    assert values == {"PpViJanela": "13", "PpViDepoisAcc": "94,5\\,\\%", "PpViSegPescaNPred": "1\\,255",
                      "PpViSegPescaF": "0,066", "PpViViagMelhoram": "2", "PpViViagPioram": "1"}
