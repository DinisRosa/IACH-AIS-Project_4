"""Macros e figuras da medição final no `validation` para a proposta (Secção 9, REV-053).

Parte de `results/final_validation/final_validation.json` e de `predictions_validation.csv`, que
`final_validation` já gerou numa única abertura do `validation`. NÃO abre o parquet do `validation`, nem o
do `test`; os números do `test` do modelo medido vêm dos ficheiros de seleção já existentes.

Confirma por hash e pelo `access_log` que o `validation` foi aberto uma só vez, ao abrigo da autorização da
medição final, e que a escolha do modelo foi gravada antes dessa abertura. Escreve:
  - latex/generated/resultados_validacao.tex : macros \\resVa... (nomes sem dígitos);
  - latex/figures/validacao_*.png            : figuras geradas dos mesmos números.

Execução (a partir da raiz do projeto, depois de `final_validation`):
    iach-ais-venv-4/bin/python -m ais.cli.build_validation_results

Com `--worst-trip-figure-only` (REV-074) volta a gerar só a linha temporal da viagem de menor exatidão, sem
reescrever macros nem outras figuras (exige a autorização `validation_report_figure_baseline` e regista a leitura).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ais.cli.build_final_results import INK, INK2, NAV, PESCA, load_json, pct, plt, pt, save, thousands, trip_summary
from ais.cli.build_window_results import point_macros, segment_macros
from ais.cli.freeze_baseline import verify_frozen
from ais.phase1.reserved import log_access, read_log, sha256_of
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[3]
FV = ROOT / "results" / "final_validation"
GEN = ROOT / "latex" / "generated"
AUTH_ID = "validation_final_2026-11-24"
FIG_AUTH = "configs/authorizations/validation_report_figure_baseline.json"
PREFIX = {"baseline": "Bs", "J0": "JZ", "J50": "JC"}
NOME = {"baseline": "a referência (viagem completa)", "J0": "J0 (janelas sem sobreposição)",
        "J50": "J50 (janelas com 50\\,\\% de sobreposição)"}
TEST_SEG = {"baseline": ("results/baseline_frozen/test_segment_results.json", "metricas_por_segmento"),
            "J0": ("results/windows_j0/selection_test.json", "metricas_por_segmento"),
            "J50": ("results/windows_j50/selection_test.json", "metricas_por_segmento")}
CMAP = ListedColormap([NAV, PESCA])


def collect() -> dict:
    R = load_json(FV / "final_validation.json")
    choice = load_json(FV / "model_choice.json")
    log = read_log(ROOT / "results" / "access_log.jsonl")
    opens = [e for e in log if e.get("split") == "validation" and e.get("event") == "open"]
    i_choice = next(i for i, e in enumerate(log) if e.get("event") == "model_chosen")
    i_open = next(i for i, e in enumerate(log) if e.get("split") == "validation" and e.get("event") == "open")
    checks = {
        "validation_aberto_uma_so_vez": len(opens) == 1,
        "aberto_ao_abrigo_da_autorizacao_da_medicao_final": opens[0].get("authorization") == AUTH_ID,
        "escolha_gravada_antes_da_abertura": i_choice < i_open,
        "modelo_medido_e_o_escolhido": R["modelo"] == choice["escolhido"],
        "so_o_modelo_escolhido_foi_aberto": sum(1 for e in log if e.get("event") == "final_measurement_done") == 1,
        "checkpoint_congelado_confere": all(
            verify_frozen(ROOT / d, label=l)["checkpoint_confere"] for d, l in (
                ("results/baseline_frozen", "baseline"), ("results/windows_j0_frozen", "j0"),
                ("results/windows_j50_frozen", "j50"))),
        "protocolo_igual_ao_declarado": R["hashes"]["protocolo"] == choice["hash_do_protocolo"],
    }
    assert all(checks.values()), f"Proveniência incoerente: {checks}"
    rel, key = TEST_SEG[R["modelo"]]
    R["segmentos_test"] = load_json(ROOT / rel)[key]
    R["verificacoes"] = checks
    return R


def latex_macros(R: dict) -> str:
    m = R["modelo"]
    g = R["validation"]["global"]
    M = {"Modelo": NOME[m], "Epoca": str(R["epoca"]), "Limiar": pt(R["limiar"], 2),
         "Pontos": thousands(R["n_pontos"]), "Viagens": str(R["n_viagens"]),
         "PercPesca": pct(g["por_classe"]["pesca"]["n_real"] / g["n_points"])}
    for r in R["ranking_no_test"]:
        P = PREFIX[r["modelo"]]
        M[f"FMedio{P}"] = pt(r["f1_medio_por_ponto_no_test"], 3)
        M[f"AccTeste{P}"] = pct(r["exatidao_no_test"])
    M.update(point_macros("Va", R["validation"], "Valid"))
    M.update(point_macros("Va", R["test_do_mesmo_modelo"], "Teste"))
    M.update(segment_macros("Va", R["segmentos_validation"]))
    M.update(segment_macros("VaT", R["segmentos_test"]))
    rv = trip_summary(R["validation"]["por_viagem"])
    M.update({"ViagMin": pct(rv["accuracy_minima"]), "ViagMed": pct(rv["accuracy_mediana"]),
              "ViagMax": pct(rv["accuracy_maxima"]), "PiorViagem": "\\texttt{" + rv["pior_viagem"] + "}",
              "NViagNaoSuperam": str(len(rv["viagens_que_nao_superam_a_classe_maioritaria"]))})
    lines = [f"% Gerado por ais.cli.build_validation_results em {R['criado_utc']} (medição final, commit {R['git_commit'][:9]}).",
             "% NÃO EDITAR À MÃO: volta a gerar-se a partir de results/final_validation/final_validation.json.",
             "% Prefixos: Va = validation (e Va...Teste = test do mesmo modelo); VaT = segmentos do test."]
    lines += [f"\\newcommand{{\\res{'Va' + k}}}{{{v}}}" if not k.startswith(("Va",)) else f"\\newcommand{{\\res{k}}}{{{v}}}"
              for k, v in M.items()]
    return "\n".join(lines) + "\n"


def fig_summary(R: dict) -> str:
    """Matriz de confusão e exatidão por viagem no validation, lado a lado."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.9, 2.5), gridspec_kw={"width_ratios": [1, 2.3]})
    cm = np.array(R["validation"]["matriz_confusao_linhas_real_colunas_previsto"])
    rows = cm / cm.sum(axis=1, keepdims=True)
    a1.imshow(rows, cmap="Blues", vmin=0, vmax=1)
    a1.grid(False)
    for i in range(2):
        for j in range(2):
            a1.text(j, i, f"{100 * rows[i, j]:.1f} %", ha="center", va="center", fontsize=7,
                    color=INK if rows[i, j] < 0.6 else "white")
    a1.set_xticks([0, 1], ["nav.", "pesca"], fontsize=7)
    a1.set_yticks([0, 1], ["nav.", "pesca"], fontsize=7)
    a1.set(xlabel="Previsto", ylabel="Real")
    a1.set_title("Matriz de confusão", fontsize=8)
    pv = R["validation"]["por_viagem"]
    items = sorted(pv.items(), key=lambda kv: kv[1]["accuracy"])
    x = np.arange(len(items))
    a2.bar(x, [100 * m["accuracy"] for _, m in items], color=NAV, width=0.7, label="modelo")
    a2.scatter(x, [100 * m["accuracy_maioritaria"] for _, m in items], color=INK, s=12, zorder=3,
               label="prever sempre a classe maioritária da viagem")
    a2.set_xticks(x, [i for i, _ in items], rotation=60, ha="right", fontsize=5.5)
    a2.set(ylabel="Exatidão (%)", ylim=(0, 102), xlim=(-0.7, len(items) - 0.3))
    a2.set_title("Exatidão por viagem (por ordem crescente)", fontsize=8)
    fig.tight_layout(w_pad=1.0)
    return save(fig, "validacao_resumo.png")


def fig_worst_trip(R: dict) -> tuple[str, str]:
    """A viagem de menor exatidão: classe real e da baseline, ponto a ponto (só previsões já geradas)."""
    pv = R["validation"]["por_viagem"]
    trip = min(pv, key=lambda i: (pv[i]["accuracy"], i))
    p = pd.read_csv(FV / "predictions_validation.csv", usecols=["id", "t", "target", "predicted"])
    p = p[p["id"] == trip].sort_values("t")
    fig, axes = plt.subplots(2, 1, figsize=(6.9, 1.3), sharex=True)
    for ax, lab, arr in zip(axes, ("real", "baseline"), (p["target"].to_numpy(), p["predicted"].to_numpy())):
        ax.imshow(arr[None, :], aspect="auto", cmap=CMAP, vmin=0, vmax=1, interpolation="nearest")
        ax.set_yticks([0], [lab], fontsize=7)
        ax.grid(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0)
    axes[-1].set_xlabel(f"Pontos da viagem {trip} (azul: navegação; laranja: pesca)", fontsize=7)
    fig.tight_layout(h_pad=0.2)
    return save(fig, "validacao_pior_viagem.png"), trip


def worst_trip_figure() -> tuple[str, str]:
    """Só a linha temporal da Figura 7, a partir das previsões guardadas da medição final."""
    auth = load_json(ROOT / FIG_AUTH)
    if auth.get("conjuntos_autorizados") != ["validation"] or auth.get("finalidade") != "figuras_relatorio" \
            or auth.get("validation_autorizado") is not True:
        raise PermissionError("Autorização inválida para a figura da validação.")
    R = load_json(FV / "final_validation.json")
    source = FV / "predictions_validation.csv"
    log_access(ROOT / "results" / "access_log.jsonl",
               {"event": "report_figures", "split": "validation", "authorization": auth["id"],
                "file_sha256": sha256_of(source)})
    return fig_worst_trip(R)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--worst-trip-figure-only", action="store_true", help="só a linha temporal da Figura 7")
    if parser.parse_args(argv).worst_trip_figure_only:
        path, trip = worst_trip_figure()
        print(f"escrita {path} (viagem {trip})")
        return
    R = collect()
    figs = [fig_summary(R)]
    f2, trip = fig_worst_trip(R)
    figs.append(f2)
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "resultados_validacao.tex").write_text(latex_macros(R), encoding="utf-8")
    out = {k: v for k, v in R.items()}
    out["figuras"], out["macros_latex"] = figs, "latex/generated/resultados_validacao.tex"
    out["viagem_da_figura"] = {"id": trip, "regra": "a viagem de validation com menor exatidão"}
    (FV / "build_info.json").write_text(json.dumps({
        "verificacoes": R["verificacoes"], "figuras": figs, "macros_latex": out["macros_latex"],
        "viagem_da_figura": out["viagem_da_figura"], "hash_final_validation_json": sha256_of(FV / "final_validation.json")},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"escrito latex/generated/resultados_validacao.tex, {len(figs)} figuras e {FV / 'build_info.json'}")


if __name__ == "__main__":
    main()
