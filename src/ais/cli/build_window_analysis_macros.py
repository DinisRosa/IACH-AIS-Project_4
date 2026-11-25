"""Macros da análise dos blocos de erro, usada para escolher a janela do pós-processamento (REV-065).

Lê só os resumos já guardados por `analyze_error_runs` (`results/postproc_window_analysis/{test,train}.json`)
e o protocolo do pós-processamento (para o tamanho da janela). NÃO lê previsões nem parquets. Confirma, no
`access_log`, que o resumo do `test` veio de uma leitura registada do mesmo ficheiro. Escreve
`latex/generated/resultados_buracos.tex` (macros \\resBu..., sem dígitos nos nomes).

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.build_window_analysis_macros
"""
from __future__ import annotations

import json
from pathlib import Path

from ais.cli.build_final_results import pct, pt, thousands
from ais.phase1.reserved import read_log

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "results" / "postproc_window_analysis"
PROTOCOL = ROOT / "configs" / "postproc_protocol_v2.json"
OUT = ROOT / "latex" / "generated" / "resultados_buracos.tex"
NAV_RUNS = "navegacao_prevista_no_meio_de_pesca"
FISH_RUNS = "pesca_prevista_no_meio_de_navegacao"


def window_row(analysis: dict, size: int) -> dict:
    rows = [r for r in analysis["janelas_candidatas"] if r["janela"] == size]
    if len(rows) != 1:
        raise ValueError(f"A análise não tem exatamente uma linha para a janela de {size} pontos.")
    return rows[0]


def check_logged(test: dict, log: list[dict]) -> None:
    """O resumo do `test` tem de corresponder a uma leitura registada do mesmo ficheiro de origem."""
    if test.get("split") != "test":
        raise ValueError("O resumo indicado não é o do test.")
    if not any(e.get("event") == "postproc_window_analysis" and e.get("file_sha256") == test["fonte_sha256"]
               for e in log):
        raise PermissionError("Não há leitura registada que corresponda ao resumo do test.")


def latex_macros(test: dict, train: dict, size: int) -> str:
    runs, row = test["todos"], window_row(test, size)
    M = {
        "BuTesteBlocos": thousands(runs["n_blocos"]),
        "BuTesteErros": thousands(runs["n_pontos"]),
        "BuTesteMedia": pt(runs["media"], 1),
        "BuTesteMediana": pt(runs["mediana"], 0),
        "BuTesteNoventa": pt(runs["p90"], 0),
        "BuTesteMaximo": thousands(runs["maximo"]),
        "BuTesteNavBlocos": thousands(test[NAV_RUNS]["n_blocos"]),
        "BuTestePescaBlocos": thousands(test[FISH_RUNS]["n_blocos"]),
        "BuTesteNavPercPontos": pct(test[NAV_RUNS]["n_pontos"] / runs["n_pontos"], 0),
        "BuTesteRealNavMin": thousands(test["segmentos_reais_navegacao"]["minimo"]),
        "BuTesteRealPescaMin": thousands(test["segmentos_reais_pesca"]["minimo"]),
        "BuTreinoRealNavMin": thousands(train["segmentos_reais_navegacao"]["minimo"]),
        "BuTreinoRealPescaMin": thousands(train["segmentos_reais_pesca"]["minimo"]),
        "BuRemovePesca": thousands(row["remove_pesca_isolada_ate"]),
        "BuRemoveNav": thousands(row["remove_navegacao_isolada_ate"]),
        "BuTesteBlocosCobertos": pct(row["perc_buracos_cobertos"], 0),
        "BuTestePontosCobertos": pct(row["perc_pontos_de_erro_cobertos"], 0),
    }
    lines = ["% Gerado por ais.cli.build_window_analysis_macros a partir de results/postproc_window_analysis/",
             f"% (análise do test de {test['criado_utc']}, janela de {size} pontos). NÃO EDITAR À MÃO."]
    lines += [f"\\newcommand{{\\res{k}}}{{{v}}}" for k, v in M.items()]
    return "\n".join(lines) + "\n"


def main() -> None:
    test = json.loads((ANALYSIS / "test.json").read_text(encoding="utf-8"))
    train = json.loads((ANALYSIS / "train.json").read_text(encoding="utf-8"))
    check_logged(test, read_log(ROOT / "results" / "access_log.jsonl"))
    size = int(json.loads(PROTOCOL.read_text(encoding="utf-8"))["filtro"]["tamanho_pontos"])
    OUT.write_text(latex_macros(test, train, size), encoding="utf-8")
    print(f"escrito {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
