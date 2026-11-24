"""Ficheiro final de resultados da CNN 1D de referência e ficheiros derivados para a proposta (REV-040).

Parte da BASELINE CONGELADA (`results/baseline_frozen/`, época e limiar escolhidos no conjunto `test`
numa só ronda) e do treino de seleção (`results/phase1_select/`). Não abre o `validation` nem o parquet
do `test`: os números do `test` vêm de `selection_test.json` (já gerado sob a autorização registada).
Só lê o treino, para avaliar a baseline congelada nas 87 viagens de treino.

Confirma por hash que os sumários da preparação, o manifesto, o checkpoint e a seleção coincidem, e que o
`validation` só foi aberto, no máximo uma vez, pela medição final (`results/access_log.jsonl`). Escreve:
  - results/baseline_frozen/final_results.json : todos os números com proveniência (fonte única);
  - latex/generated/resultados.tex             : macros \\res... com os valores formatados;
  - latex/figures/final_*.png                  : figuras geradas a partir dos mesmos números.
O LaTeX só usa estas macros: nenhum número destes resultados é escrito à mão no .tex.

Execução (a partir da raiz do projeto, depois de `select_on_test` e `freeze_baseline`):
    iach-ais-venv-4/bin/python -m ais.cli.build_final_results
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from ais.phase1.artifacts import load_checkpoint  # noqa: E402
from ais.phase1.data import (  # noqa: E402
    INPUT_CHANNELS, N_INPUT_CHANNELS, apply_scaler, build_full_sequences, load_training_data,
    validate_training_data,
)
from ais.phase1.inference import predict, tables_for  # noqa: E402
from ais.phase1.model import build_cnn, receptive_field  # noqa: E402
from ais.phase1.reserved import read_log, sha256_of  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results" / "phase1_select"
FROZEN = ROOT / "results" / "baseline_frozen"
FIG_DIR = ROOT / "latex" / "figures"
GEN_DIR = ROOT / "latex" / "generated"

NAV, PESCA, GREY = "#2a78d6", "#eb6834", "#8a8985"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 8, "axes.titlesize": 9, "axes.titleweight": "bold",
    "axes.titlelocation": "left"})


# ----------------------------------------------------------------------------- utilitários
def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pt(x: float, decimals: int) -> str:
    """Número em notação portuguesa (vírgula decimal), só para apresentação."""
    return f"{x:.{decimals}f}".replace(".", ",")


def thousands(n: int) -> str:
    """Inteiro com espaço fino como separador de milhares (LaTeX)."""
    return f"{n:,}".replace(",", "\\,")


def pct(x: float, decimals: int = 1) -> str:
    return pt(100 * x, decimals) + "\\,\\%"


def git_info() -> dict:
    def run(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "alteracoes_por_commitar": bool(run("status", "--porcelain"))}


def layer_param_counts() -> list[int]:
    """Parâmetros de cada convolução (pesos + enviesamento), lidos do próprio modelo."""
    model = build_cnn(n_channels=N_INPUT_CHANNELS)
    convs = [m for m in model.modules() if isinstance(m, torch.nn.Conv1d)]
    return [sum(p.numel() for p in m.parameters()) for m in convs]


def trip_summary(por_viagem: dict) -> dict:
    accs = pd.Series({i: m["accuracy"] for i, m in por_viagem.items()}).sort_values()
    below = [i for i, m in por_viagem.items() if m["accuracy"] <= m["accuracy_maioritaria"]]
    return {"n": int(len(accs)), "accuracy_minima": float(accs.min()),
            "accuracy_mediana": float(accs.median()), "accuracy_maxima": float(accs.max()),
            "pior_viagem": accs.index[0], "viagens_que_nao_superam_a_classe_maioritaria": below}


def evaluate_frozen_on_train(frz: dict, cfg: dict) -> tuple[dict, pd.DataFrame]:
    """Previsões da baseline congelada nas 87 viagens de TREINO (política de acesso: só treino)."""
    model, ck = load_checkpoint(FROZEN / frz["checkpoint"], "cpu")
    df = load_training_data(ROOT / cfg["train_path"], ROOT / cfg["split_manifest_path"])
    validate_training_data(df)
    seqs = [apply_scaler(s, ck["scaler"]) for s in build_full_sequences(df)]
    pred = predict(model, seqs, df[["point_id", "label"]], torch.device("cpu"), frz["limiar"])
    pred.to_csv(FROZEN / "predictions_train_frozen.csv", index=False)
    return tables_for(pred), pred


# ----------------------------------------------------------------------------- recolha
def collect() -> dict:
    man = load_json(RUN / "run_manifest.json")
    sel = load_json(RUN / "selection_test.json")
    frz = load_json(FROZEN / "baseline_frozen.json")
    hist = pd.read_csv(RUN / "training_history.csv")
    cfg = man["config"]
    assert cfg["stage"] == "development" and "train" in Path(cfg["train_path"]).name
    assert man["n_monitor_trips"] == 0

    clean = {s: load_json(ROOT / "results" / f"clean_{s}" / "summary.json") for s in
             ("train", "validation", "test")}
    train_pq, manifest = ROOT / cfg["train_path"], ROOT / cfg["split_manifest_path"]
    log = read_log(ROOT / "results" / "access_log.jsonl")
    checks = {
        "base_de_treino_coincide_com_o_sumario": sha256_of(train_pq) == clean["train"]["meta"]["output_sha256"],
        "manifesto_coincide_com_os_sumarios": all(
            sha256_of(manifest) == clean[s]["meta"]["manifest_sha256"] for s in clean),
        "checkpoint_congelado_coincide_com_o_manifesto":
            sha256_of(FROZEN / frz["checkpoint"]) == frz["checkpoint_sha256"],
        "checkpoint_congelado_e_o_escolhido_na_selecao":
            frz["checkpoint_sha256"] == sel["hashes"]["checkpoint_escolhido"],
        "selecao_coincide_com_o_manifesto_de_congelacao":
            sha256_of(RUN / "selection_test.json") == frz["selecao"]["sha256"],
        "ficheiro_test_da_selecao_e_o_dos_sumarios":
            sel["hashes"]["ficheiro_test"] == clean["test"]["meta"]["output_sha256"],
        "epoca_e_limiar_congelados_iguais_aos_da_selecao":
            frz["epoca"] == sel["epoca_escolhida"] and frz["limiar"] == sel["limiar_escolhido"],
        # O validation só pode ter sido aberto, no máximo uma vez, pela medição final (REV-053).
        "validation_so_aberto_pela_medicao_final": all(e.get("authorization") == "validation_final_2026-11-24" for e in log if e.get("split") == "validation" and e.get("event") == "open")
            and sum(1 for e in log if e.get("split") == "validation" and e.get("event") == "open") <= 1,
        # Uma abertura ao abrigo da autorização da baseline (REV-046: existe uma segunda abertura, ao
        # abrigo da autorização das janelas, contada em `build_window_results`).
        "test_aberto_so_uma_vez": sum(1 for e in log if e.get("event") == "open" and e.get("split") == "test"
                                      and e.get("authorization") == "test_selection_2026-11-23") == 1,
    }
    assert all(checks.values()), f"Proveniência incoerente: {checks}"

    train_tables, _ = evaluate_frozen_on_train(frz, cfg)
    test_tables = sel["metricas_no_test_com_limiar_escolhido"]
    anomalies = load_json(ROOT / "results" / "anomalies_train" / "summary.json")
    dg = {s: clean[s]["diagnostics"] for s in clean}
    curve = {int(k): v for k, v in sel["curva_de_perda_por_epoca"].items()}
    late = [v for e, v in curve.items() if e >= 100]
    res = man["train_result"]

    return {
        "meta": {
            "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "comando": "iach-ais-venv-4/bin/python -m ais.cli.build_final_results",
            "treino_comando": f"iach-ais-venv-4/bin/python -m ais.cli.run_phase1_training {man['config_path']}",
            "selecao_comando": "iach-ais-venv-4/bin/python -m ais.cli.select_on_test results/phase1_select",
            "git": git_info(), "python": platform.python_version(), "torch": man["torch"],
            "configuracao_do_treino": cfg, "reprodutibilidade": man["reproducibility"],
            "hashes": {"base_de_treino": sha256_of(train_pq), "manifesto": sha256_of(manifest),
                       "checkpoint_congelado": frz["checkpoint_sha256"],
                       "csv_original": clean["train"]["meta"]["raw_sha256"]},
            "verificacoes": checks,
            "protocolo": sel["protocolo"], "autorizacao": sel["autorizacao"],
            "aviso": "Treino nas 87 viagens do treino oficial. Época e limiar foram escolhidos no conjunto "
                     "test (uma ronda): as métricas do test são otimistas por terem servido a escolher. "
                     "O conjunto validation não serviu para escolher nada; a medição final faz-se à parte.",
        },
        "dados": {
            "linhas_total": sum(dg[s]["linhas"] for s in dg), "viagens_total": sum(dg[s]["viagens"] for s in dg),
            "por_conjunto": {s: {"linhas": dg[s]["linhas"], "viagens": dg[s]["viagens"]} for s in dg},
            "treino_pontos_pesca": dg["train"]["target_contagem"]["1"],
            "comparacao_com_originais_treino": dg["train"]["comparacao_com_colunas_originais"],
            "anomalias_treino": anomalies,
        },
        "modelo": {"parametros": man["n_parameters"], "campo_recetivo": receptive_field(),
                   "canais_de_entrada": INPUT_CHANNELS, "parametros_por_camada": layer_param_counts()},
        "treino": {
            "viagens": man["n_train_trips"], "pontos": man["n_train_points"],
            "epocas_executadas": res["epochs_run"], "motivo_de_paragem": res["stop_reason"],
            "segundos_total": res["total_seconds"],
            "segundos_por_epoca": float(hist["train_seconds"].mean()),
        },
        "selecao": {
            "epoca": sel["epoca_escolhida"], "limiar": sel["limiar_escolhido"],
            "n_candidatos": sel["n_candidatos"], "n_viagens_test": sel["n_viagens_test"],
            "n_pontos_test": sel["n_pontos_test"],
            "perda_test_na_epoca_escolhida": curve[sel["epoca_escolhida"]],
            "perda_test_maxima_desde_a_epoca_100": float(max(late)),
            "perda_treino_na_epoca_escolhida": float(
                hist.loc[hist["epoch"] == sel["epoca_escolhida"], "monitor_loss_per_point"].iloc[0]),
            "grelha_de_limiares": sel["grelha_de_limiares"],
        },
        "resultados_treino_baseline": {
            "global": train_tables["global"],
            "matriz_confusao_linhas_real_colunas_previsto": train_tables["matriz_confusao_linhas_real_colunas_previsto"],
            "por_viagem": train_tables["por_viagem"],
        },
        "resultados_test_baseline": {
            "global": test_tables["global"],
            "matriz_confusao_linhas_real_colunas_previsto": test_tables["matriz_confusao_linhas_real_colunas_previsto"],
            "por_viagem": test_tables["por_viagem"],
            "resumo_por_viagem": trip_summary(test_tables["por_viagem"]),
        },
        "_hist": hist, "_curve": curve,
    }


# ----------------------------------------------------------------------------- macros LaTeX
def latex_macros(R: dict) -> str:
    d, m, t, s = R["dados"], R["modelo"], R["treino"], R["selecao"]
    cfg = R["meta"]["configuracao_do_treino"]
    cmp = d["comparacao_com_originais_treino"]
    coincide = 1 - max(cmp["time_gap_diferente_mais_de_1e-6_s"],
                       cmp["distance_gap_diferente_mais_de_1e-3_m"],
                       cmp["signed_turn_diferente_mais_de_1_grau"])
    layers = m["parametros_por_camada"]
    M = {
        "DadosLinhas": thousands(d["linhas_total"]), "DadosViagens": str(d["viagens_total"]),
        "DadosLinhasTreino": thousands(d["por_conjunto"]["train"]["linhas"]),
        "DadosViagensTreino": str(d["por_conjunto"]["train"]["viagens"]),
        "DadosPercPesca": pct(d["treino_pontos_pesca"] / d["por_conjunto"]["train"]["linhas"]),
        "PrepCoincide": pt(100 * coincide, 4) + "\\,\\%",
        "PrepBearingMediana": pt(cmp["bearing_mediana_abs_diff_graus"], 1),
        "ModParametros": thousands(m["parametros"]), "ModCampo": str(m["campo_recetivo"]),
        "ModParamA": thousands(layers[0]), "ModParamB": thousands(layers[1]),
        "ModParamC": thousands(layers[2]), "ModParamD": thousands(layers[3]),
        "TrViagens": str(t["viagens"]), "TrPontos": thousands(t["pontos"]),
        "TrEpocas": str(t["epocas_executadas"]), "TrMaxEpocas": str(cfg["max_epochs"]),
        "TrSegundos": pt(t["segundos_total"] / 60, 0), "TrSegPorEpoca": pt(t["segundos_por_epoca"], 1),
        "TrOrcamentoMin": pt(cfg["time_budget_seconds"] / 60, 0), "TrSemente": str(cfg["seed"]),
        "TrTorch": R["meta"]["torch"].split("+")[0],
        "SelEpoca": str(s["epoca"]), "SelLimiar": pt(s["limiar"], 2), "SelNCand": str(s["n_candidatos"]),
        "SelViagens": str(s["n_viagens_test"]), "SelPontos": thousands(s["n_pontos_test"]),
        "SelPerdaTeste": pt(s["perda_test_na_epoca_escolhida"], 3),
        "SelPerdaTesteMax": pt(s["perda_test_maxima_desde_a_epoca_100"], 3),
        "SelPerdaTreino": pt(s["perda_treino_na_epoca_escolhida"], 3),
        "SelGrelhaMin": pt(s["grelha_de_limiares"][0]["threshold"], 2),
        "SelGrelhaMax": pt(s["grelha_de_limiares"][-1]["threshold"], 2),
    }
    for key, name in (("resultados_treino_baseline", "Treino"), ("resultados_test_baseline", "Teste")):
        r = R[key]
        g = r["global"]
        nav, fish = g["por_classe"]["navegação"], g["por_classe"]["pesca"]
        cm = r["matriz_confusao_linhas_real_colunas_previsto"]
        M.update({
            f"{name}Pontos": thousands(g["n_points"]), f"{name}Erros": thousands(g["n_errors"]),
            f"{name}Acc": pct(g["accuracy"]), f"{name}AccMaj": pct(g["accuracy_maioritaria"]),
            f"{name}PercPesca": pct(fish["n_real"] / g["n_points"]),
            f"{name}NavReal": thousands(nav["n_real"]), f"{name}PescaReal": thousands(fish["n_real"]),
            f"{name}NavPrec": pt(nav["precisao"], 3), f"{name}NavSens": pt(nav["sensibilidade"], 3),
            f"{name}NavF": pt(nav["f1"], 3), f"{name}NavIoU": pt(nav["iou"], 3),
            f"{name}PescaPrec": pt(fish["precisao"], 3), f"{name}PescaSens": pt(fish["sensibilidade"], 3),
            f"{name}PescaF": pt(fish["f1"], 3), f"{name}PescaIoU": pt(fish["iou"], 3),
            f"{name}TN": thousands(cm[0][0]), f"{name}FP": thousands(cm[0][1]),
            f"{name}FN": thousands(cm[1][0]), f"{name}TP": thousands(cm[1][1]),
        })
    rv = R["resultados_test_baseline"]["resumo_por_viagem"]
    M.update({
        "TesteViagMin": pct(rv["accuracy_minima"]), "TesteViagMed": pct(rv["accuracy_mediana"]),
        "TesteViagMax": pct(rv["accuracy_maxima"]),
        "TestePiorViagem": "\\texttt{" + rv["pior_viagem"] + "}",
        "TesteNViagNaoSuperam": str(len(rv["viagens_que_nao_superam_a_classe_maioritaria"])),
    })
    lines = [f"% Gerado por ais.cli.build_final_results em {R['meta']['criado_utc']} "
             f"(commit {R['meta']['git']['commit'][:9]}).",
             "% NÃO EDITAR À MÃO: volta a gerar-se a partir de results/baseline_frozen/final_results.json."]
    lines += [f"\\newcommand{{\\res{k}}}{{{v}}}" for k, v in M.items()]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- figuras
def save(fig, name: str) -> str:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / name, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return f"latex/figures/{name}"


def figures(R: dict) -> list[str]:
    hist, curve, sel = R["_hist"], R["_curve"], R["selecao"]
    best = sel["epoca"]
    out = []

    fig, ax = plt.subplots(figsize=(3.3, 2.5))
    ax.plot(hist["epoch"], hist["monitor_loss_per_point"], color=NAV, lw=1.3, label="treino (87 viagens)")
    ax.plot(sorted(curve), [curve[e] for e in sorted(curve)], color=PESCA, lw=1.0, label="teste (18 viagens)")
    ax.axvline(best, color=INK, ls="--", lw=0.9)
    ax.annotate(f"época escolhida ({best})", (best, curve[best]), xytext=(0.30, 0.04),
                textcoords="axes fraction", fontsize=7, color=INK2,
                arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6})
    ax.set(xlabel="Época", ylabel="Perda por ponto (BCE)")
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    out.append(save(fig, "final_perda.png"))

    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.9))
    for ax, key, title in ((axes[0], "resultados_treino_baseline", "Treino"),
                           (axes[1], "resultados_test_baseline", "Teste")):
        cm = np.array(R[key]["matriz_confusao_linhas_real_colunas_previsto"])
        rows = cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(rows, cmap="Blues", vmin=0, vmax=1)
        ax.grid(False)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{100 * rows[i, j]:.1f} %", ha="center", va="center", fontsize=7,
                        color=INK if rows[i, j] < 0.6 else "white")
        ax.set_xticks([0, 1], ["nav.", "pesca"], fontsize=7)
        ax.set_yticks([0, 1], ["nav.", "pesca"] if ax is axes[0] else ["", ""], fontsize=7)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("Previsto", fontsize=7)
    axes[0].set_ylabel("Real", fontsize=7)
    fig.tight_layout(w_pad=0.6)
    out.append(save(fig, "final_matriz.png"))

    pv = R["resultados_test_baseline"]["por_viagem"]
    items = sorted(pv.items(), key=lambda kv: kv[1]["accuracy"])
    x = np.arange(len(items))
    fig, ax = plt.subplots(figsize=(6.9, 2.6))
    ax.bar(x, [100 * m["accuracy"] for _, m in items], color=NAV, width=0.7, label="CNN")
    ax.scatter(x, [100 * m["accuracy_maioritaria"] for _, m in items], color=INK, s=14, zorder=3,
               label="prever sempre a classe maioritária da viagem")
    ax.set_xticks(x, [i for i, _ in items], rotation=60, ha="right", fontsize=6)
    ax.set(ylabel="Accuracy (%)", ylim=(0, 102), xlim=(-0.7, len(items) - 0.3),
           xlabel=f"Viagens do conjunto de teste ({len(items)}), por accuracy crescente")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.2), ncol=2)
    out.append(save(fig, "final_viagens.png"))
    return out


def main() -> None:
    R = collect()
    figs = figures(R)
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "resultados.tex").write_text(latex_macros(R), encoding="utf-8")
    R["figuras"] = figs
    R["macros_latex"] = "latex/generated/resultados.tex"
    R.pop("_hist"), R.pop("_curve")
    (FROZEN / "final_results.json").write_text(
        json.dumps(R, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"escrito {FROZEN / 'final_results.json'}, latex/generated/resultados.tex e {len(figs)} figuras")


if __name__ == "__main__":
    main()
