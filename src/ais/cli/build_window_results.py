"""Resultados de J0 e J50 e comparação com a baseline, para a proposta (Marco 4, REV-047).

Parte das variantes congeladas (`results/windows_j0_frozen`, `results/windows_j50_frozen`), da baseline
congelada (`results/baseline_frozen`) e dos ficheiros que a seleção única no `test` já gerou. NÃO abre o
parquet do `test` nem o `validation`: os números do `test` vêm de `selection_test.json` e de
`test_segment_results.json`; só lê o treino, para avaliar J0 e J50 congeladas nas 87 viagens de treino.

Confirma por hash que as congelações coincidem com as seleções e, no `access_log`, que o `test` foi
aberto uma só vez ao abrigo da autorização das janelas (e uma, antes, ao abrigo da da baseline) e que o
`validation` só foi aberto, no máximo uma vez, pela medição final (`final_validation`). Escreve:
  - results/windows_final/final_results_windows.json : todos os números com proveniência (fonte única);
  - latex/generated/resultados_janelas.tex           : macros \\res... (sem dígitos nos nomes);
  - latex/figures/janelas_*.png                      : figuras geradas dos mesmos números.
O LaTeX só usa estas macros: nenhum número destes resultados é escrito à mão.

Execução (a partir da raiz do projeto, depois de `select_windows_on_test`):
    iach-ais-venv-4/bin/python -m ais.cli.build_window_results
"""
from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from matplotlib.colors import ListedColormap

from ais.cli.build_final_results import (
    GREY, INK, INK2, NAV, PESCA, git_info, load_json, pct, plt, pt, save, thousands, trip_summary,
)
from ais.phase1.artifacts import load_checkpoint
from ais.phase1.data import (
    FEATURE_COLS, apply_scaler, build_full_sequences, load_training_data, validate_training_data,
)
from ais.phase1.inference import tables_for
from ais.phase1.model import receptive_field
from ais.phase1.reserved import read_log, sha256_of
from ais.phase1.windows import WindowSet, predict_window_table

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "results" / "baseline_frozen"
OUT = ROOT / "results" / "windows_final"
GEN_DIR = ROOT / "latex" / "generated"
VARIANTS = {"J0": {"dir": "windows_j0", "label": "j0", "prefix": "JZ", "color": "#2a9d8f"},
            "J50": {"dir": "windows_j50", "label": "j50", "prefix": "JC", "color": "#7b5ea7"}}
BASE_COLOR = GREY
NEW_AUTH = "test_selection_windows_2026-11-23"
OLD_AUTH = "test_selection_2026-11-23"
CLASS_CMAP = ListedColormap([NAV, PESCA])


# ----------------------------------------------------------------------------- recolha
def evaluate_frozen_on_train(v: dict, cfg: dict, frz: dict) -> dict:
    """Previsões da variante congelada nas 87 viagens de TREINO (política de acesso: só treino)."""
    d = ROOT / "results" / f"{v['dir']}_frozen"
    model, ck = load_checkpoint(d / frz["checkpoint"], "cpu")
    df = load_training_data(ROOT / cfg["train_path"], ROOT / cfg["split_manifest_path"])
    validate_training_data(df, FEATURE_COLS)
    seqs = [apply_scaler(s, ck["scaler"]) for s in build_full_sequences(df)]
    ws = WindowSet(seqs, cfg["window_length"], cfg["overlap"])
    pred = predict_window_table(model, ws, df[["point_id", "label"]], torch.device("cpu"), frz["limiar"])
    pred.to_csv(d / "predictions_train_frozen.csv", index=False)
    return tables_for(pred)


def collect() -> dict:
    base = load_json(BASE / "final_results.json")
    base_seg = load_json(BASE / "test_segment_results.json")
    log = read_log(ROOT / "results" / "access_log.jsonl")
    opens = [e for e in log if e.get("event") == "open" and e.get("split") == "test"]
    R = {"variantes": {}}
    checks = {
        "test_aberto_uma_vez_ao_abrigo_da_autorizacao_das_janelas":
            sum(1 for e in opens if e.get("authorization") == NEW_AUTH) == 1,
        "test_aberto_uma_vez_ao_abrigo_da_autorizacao_da_baseline":
            sum(1 for e in opens if e.get("authorization") == OLD_AUTH) == 1,
        "test_so_teve_estas_duas_aberturas": len(opens) == 2,
        # O validation só pode ter sido aberto, no máximo uma vez, pela medição final (REV-053).
        "validation_so_aberto_pela_medicao_final": all(e.get("authorization") == "validation_final_2026-11-24" for e in log if e.get("split") == "validation" and e.get("event") == "open")
            and sum(1 for e in log if e.get("split") == "validation" and e.get("event") == "open") <= 1,
    }
    for name, v in VARIANTS.items():
        run, frozen = ROOT / "results" / v["dir"], ROOT / "results" / f"{v['dir']}_frozen"
        man = load_json(run / "run_manifest.json")
        sel = load_json(run / "selection_test.json")
        frz = load_json(frozen / f"{v['label']}_frozen.json")
        hist = pd.read_csv(run / "training_history.csv")
        cfg = man["config"]
        checks.update({
            f"{name}_treino_completo": man["status"] == "completo" and man["epochs_run"] == cfg["max_epochs"],
            f"{name}_checkpoint_congelado_confere": sha256_of(frozen / frz["checkpoint"]) == frz["checkpoint_sha256"],
            f"{name}_checkpoint_congelado_e_o_escolhido": frz["checkpoint_sha256"] == sel["hashes"]["checkpoint_escolhido"],
            f"{name}_selecao_coincide_com_a_congelacao": sha256_of(run / "selection_test.json") == frz["selecao"]["sha256"],
            f"{name}_epoca_e_limiar_congelados_iguais": frz["epoca"] == sel["epoca_escolhida"]
                                                      and frz["limiar"] == sel["limiar_escolhido"],
            f"{name}_normalizador_igual_ao_da_baseline": man["scaler_igual_ao_da_baseline"] is True,
        })
        curve = {int(k): x for k, x in sel["curva_de_perda_por_epoca"].items()}
        late = [x for e, x in curve.items() if e >= 100]
        train_tables = evaluate_frozen_on_train(v, cfg, frz)
        R["variantes"][name] = {
            "config": cfg, "manifesto_de_treino": {k: man[k] for k in (
                "epochs_run", "n_windows", "steps_per_epoch", "total_steps", "stride", "window_coverage",
                "total_training_seconds", "n_parameters")},
            "selecao": {k: sel[k] for k in (
                "epoca_escolhida", "limiar_escolhido", "possivelmente_nao_convergiu", "n_candidatos",
                "n_viagens_test", "n_pontos_test", "janelas_no_test", "grelha_de_limiares")},
            "perda_test_na_epoca_escolhida": curve[sel["epoca_escolhida"]],
            "perda_test_maxima_desde_a_epoca_100": float(max(late)),
            "perda_treino_na_epoca_escolhida": float(
                hist.loc[hist["epoch"] == sel["epoca_escolhida"], "train_eval_loss_per_point"].iloc[0]),
            "segundos_por_epoca": float(hist["train_seconds"].mean()),
            "treino": train_tables, "test": sel["metricas_no_test_com_limiar_escolhido"],
            "segmentos_test": sel["metricas_por_segmento"], "_hist": hist, "_curve": curve,
            "hashes": {"checkpoint_congelado": frz["checkpoint_sha256"], **sel["hashes"]},
        }
    assert all(checks.values()), f"Proveniência incoerente: {checks}"
    R["baseline"] = {
        "epoca": base["selecao"]["epoca"], "limiar": base["selecao"]["limiar"],
        "treino": base["resultados_treino_baseline"], "test": base["resultados_test_baseline"],
        "segmentos_test": base_seg["metricas_por_segmento"],
        "previsoes_iguais_as_da_selecao_anterior": base_seg["previsoes_iguais_as_da_selecao_anterior"],
        "segundos_total": base["treino"]["segundos_total"], "segundos_por_epoca": base["treino"]["segundos_por_epoca"],
        "viagens": base["treino"]["viagens"], "epocas": base["treino"]["epocas_executadas"],
        "_hist": pd.read_csv(ROOT / "results" / "phase1_select" / "training_history.csv"),
        "_curve": {int(k): x for k, x in load_json(ROOT / "results" / "phase1_select" / "selection_test.json")[
            "curva_de_perda_por_epoca"].items()},
    }
    R["meta"] = {
        "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "comando": "iach-ais-venv-4/bin/python -m ais.cli.build_window_results",
        "git": git_info(), "python": platform.python_version(), "torch": str(torch.__version__),
        "verificacoes": checks, "protocolo": "selecao_janelas_v1", "autorizacao": NEW_AUTH + " (ficheiro test_selection_windows.json)",
        "aviso": "J0 e J50 treinadas nas 87 viagens do treino oficial. Época e limiar foram escolhidos no "
                 "conjunto test numa só abertura; as métricas do test são otimistas por terem servido a "
                 "escolher (para as três variantes, com o mesmo critério). O validation não serviu para escolher nada.",
    }
    return R


# ----------------------------------------------------------------------------- comparação por viagem
def paired_trips(R: dict) -> dict:
    """Em quantas viagens de teste cada variante tem exatidão maior, igual ou menor do que a baseline."""
    b = {i: m["accuracy"] for i, m in R["baseline"]["test"]["por_viagem"].items()}
    out = {}
    for name in VARIANTS:
        v = {i: m["accuracy"] for i, m in R["variantes"][name]["test"]["por_viagem"].items()}
        diffs = {i: v[i] - b[i] for i in b}
        out[name] = {"melhor": sum(d > 1e-12 for d in diffs.values()), "igual": sum(abs(d) <= 1e-12 for d in diffs.values()),
                     "pior": sum(d < -1e-12 for d in diffs.values()),
                     "diferenca_mediana_pontos_percentuais": float(100 * np.median(list(diffs.values())))}
    return out


# ----------------------------------------------------------------------------- macros LaTeX
SEG_KEYS = (("NRef", "n_ref_segments", "int"), ("NPred", "n_pred_segments", "int"),
            ("NPar", "n_matched", "int"), ("Prec", "precision", 3), ("Sens", "sensitivity", 3),
            ("F", "f1", 3), ("IoUMed", "mean_iou_matched", 3), ("IniMed", "median_abs_start_error_s", 0),
            ("FimMed", "median_abs_end_error_s", 0), ("Frag", "fragmentation_ratio", 2))


def point_macros(P: str, tables: dict, kind: str) -> dict:
    g = tables["global"]
    nav, fish = g["por_classe"]["navegação"], g["por_classe"]["pesca"]
    cm = tables["matriz_confusao_linhas_real_colunas_previsto"]
    n = kind
    return {
        f"{P}{n}Pontos": thousands(g["n_points"]), f"{P}{n}Erros": thousands(g["n_errors"]),
        f"{P}{n}Acc": pct(g["accuracy"]), f"{P}{n}AccMaj": pct(g["accuracy_maioritaria"]),
        f"{P}{n}NavPrec": pt(nav["precisao"], 3), f"{P}{n}NavSens": pt(nav["sensibilidade"], 3),
        f"{P}{n}NavF": pt(nav["f1"], 3), f"{P}{n}NavIoU": pt(nav["iou"], 3),
        f"{P}{n}PescaPrec": pt(fish["precisao"], 3), f"{P}{n}PescaSens": pt(fish["sensibilidade"], 3),
        f"{P}{n}PescaF": pt(fish["f1"], 3), f"{P}{n}PescaIoU": pt(fish["iou"], 3),
        f"{P}{n}NavReal": thousands(nav["n_real"]), f"{P}{n}PescaReal": thousands(fish["n_real"]),
        f"{P}{n}TN": thousands(cm[0][0]), f"{P}{n}FP": thousands(cm[0][1]),
        f"{P}{n}FN": thousands(cm[1][0]), f"{P}{n}TP": thousands(cm[1][1]),
    }


def segment_macros(P: str, seg: dict) -> dict:
    M = {}
    for cls, cname in (("pesca", "Pesca"), ("navegacao", "Nav")):
        for key, field, fmt in SEG_KEYS:
            x = seg[cls][field]
            M[f"{P}Seg{cname}{key}"] = "n/d" if x is None else (thousands(int(x)) if fmt == "int" else pt(x, fmt))
    return M


def latex_macros(R: dict, paired: dict) -> str:
    M = {}
    M.update(point_macros("Bs", R["baseline"]["treino"], "Treino"))
    M.update(point_macros("Bs", R["baseline"]["test"], "Teste"))
    M.update(segment_macros("Bs", R["baseline"]["segmentos_test"]))
    M["BsEpoca"], M["BsLimiar"] = str(R["baseline"]["epoca"]), pt(R["baseline"]["limiar"], 2)
    M.update({"BsPassos": str(R["baseline"]["viagens"]),
              "BsPassosTotal": thousands(R["baseline"]["viagens"] * R["baseline"]["epocas"]),
              "BsEpocas": str(R["baseline"]["epocas"]), "BsSegundos": pt(R["baseline"]["segundos_total"] / 60, 0)})
    bt = R["baseline"]["test"]["por_viagem"]
    for name, v in VARIANTS.items():
        P, r = v["prefix"], R["variantes"][name]
        cfg, man, sel = r["config"], r["manifesto_de_treino"], r["selecao"]
        M.update({
            f"{P}L": str(cfg["window_length"]), f"{P}Sobrep": pct(cfg["overlap"], 0), f"{P}Passo": str(man["stride"]),
            f"{P}Lote": str(cfg["batch_size"]), f"{P}Janelas": thousands(man["n_windows"]),
            f"{P}JanelasCurtas": thousands(man["window_coverage"]["n_short_windows"]),
            f"{P}Passos": thousands(man["steps_per_epoch"]), f"{P}PassosTotal": thousands(man["total_steps"]),
            f"{P}Epocas": str(man["epochs_run"]), f"{P}Segundos": pt(man["total_training_seconds"] / 60, 0),
            f"{P}SegPorEpoca": pt(r["segundos_por_epoca"], 1),
            f"{P}OrcamentoMin": pt(cfg["time_budget_seconds"] / 60, 0),
            f"{P}Epoca": str(sel["epoca_escolhida"]), f"{P}Limiar": pt(sel["limiar_escolhido"], 2),
            f"{P}NaoConvergiu": "sim" if sel["possivelmente_nao_convergiu"] else "não",
            f"{P}JanelasTeste": thousands(sel["janelas_no_test"]["n_windows"]),
            f"{P}PerdaTeste": pt(r["perda_test_na_epoca_escolhida"], 3),
            f"{P}PerdaTesteMax": pt(r["perda_test_maxima_desde_a_epoca_100"], 3),
            f"{P}PerdaTreino": pt(r["perda_treino_na_epoca_escolhida"], 3),
            f"{P}ViagMelhor": str(paired[name]["melhor"]), f"{P}ViagIgual": str(paired[name]["igual"]),
            f"{P}ViagPior": str(paired[name]["pior"]),
            f"{P}ViagDifMed": pt(paired[name]["diferenca_mediana_pontos_percentuais"], 1),
        })
        M.update(point_macros(P, r["treino"], "Treino"))
        M.update(point_macros(P, r["test"], "Teste"))
        M.update(segment_macros(P, r["segmentos_test"]))
        rv = trip_summary(r["test"]["por_viagem"])
        M.update({f"{P}TesteViagMin": pct(rv["accuracy_minima"]), f"{P}TesteViagMed": pct(rv["accuracy_mediana"]),
                  f"{P}TesteViagMax": pct(rv["accuracy_maxima"]),
                  f"{P}TesteNViagNaoSuperam": str(len(rv["viagens_que_nao_superam_a_classe_maioritaria"]))})
    M["BsTesteViagMed"] = pct(trip_summary(bt)["accuracy_mediana"])
    M["JCPassosVezes"] = pt(R["variantes"]["J50"]["manifesto_de_treino"]["total_steps"]
                            / R["variantes"]["J0"]["manifesto_de_treino"]["total_steps"], 1)
    lines = [f"% Gerado por ais.cli.build_window_results em {R['meta']['criado_utc']} "
             f"(commit {R['meta']['git']['commit'][:9]}).",
             "% NÃO EDITAR À MÃO: volta a gerar-se a partir de results/windows_final/final_results_windows.json.",
             "% Prefixos: Bs = baseline (viagem completa); JZ = J0 (0 % de sobreposição); JC = J50 (50 %)."]
    lines += [f"\\newcommand{{\\res{k}}}{{{v}}}" for k, v in M.items()]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- figuras
def fig_loss(R: dict, name: str) -> str:
    v, r = VARIANTS[name], R["variantes"][name]
    hist, curve, best = r["_hist"], r["_curve"], r["selecao"]["epoca_escolhida"]
    fig, ax = plt.subplots(figsize=(3.3, 2.5))
    ax.plot(hist["epoch"], hist["train_eval_loss_per_point"], color=NAV, lw=1.3, label="treino (87 viagens)")
    ax.plot(sorted(curve), [curve[e] for e in sorted(curve)], color=PESCA, lw=1.0, label="teste (18 viagens)")
    ax.axvline(best, color=INK, ls="--", lw=0.9)
    ax.annotate(f"época escolhida ({best})", (best, curve[best]), xytext=(0.30, 0.22),
                textcoords="axes fraction", fontsize=7, color=INK2,
                arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.6})
    ax.set(xlabel="Época", ylabel="Perda por ponto (BCE)")
    ax.legend(frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    return save(fig, f"janelas_{v['label']}_perda.png")


def fig_matrix(R: dict, name: str) -> str:
    v, r = VARIANTS[name], R["variantes"][name]
    fig, axes = plt.subplots(1, 2, figsize=(3.4, 1.9))
    for ax, key, title in ((axes[0], "treino", "Treino"), (axes[1], "test", "Teste")):
        cm = np.array(r[key]["matriz_confusao_linhas_real_colunas_previsto"])
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
    return save(fig, f"janelas_{v['label']}_matriz.png")


def fig_loss_all(R: dict) -> str:
    """Curvas de perda (treino e teste) da referência, de J0 e de J50, lado a lado."""
    items = [("Referência", R["baseline"]["_hist"]["monitor_loss_per_point"], R["baseline"]["_curve"], R["baseline"]["epoca"])]
    for name in VARIANTS:
        r = R["variantes"][name]
        items.append((name, r["_hist"]["train_eval_loss_per_point"], r["_curve"], r["selecao"]["epoca_escolhida"]))
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.3), sharey=True)
    for ax, (title, train, curve, best) in zip(axes, items):
        ax.plot(np.arange(1, len(train) + 1), train, color=NAV, lw=1.2, label="treino (87 viagens)")
        ax.plot(sorted(curve), [curve[e] for e in sorted(curve)], color=PESCA, lw=0.9, label="teste (18 viagens)")
        ax.axvline(best, color=INK, ls="--", lw=0.9)
        ax.set_title(f"{title} (época {best})", fontsize=8)
        ax.set_xlabel("Época", fontsize=7)
    axes[0].set_ylabel("Perda por ponto (BCE)", fontsize=7)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout(w_pad=0.8)
    return save(fig, "janelas_perda.png")


def fig_matrix_all(R: dict) -> str:
    """Matrizes de confusão por ponto no teste da referência, de J0 e de J50, lado a lado."""
    items = [("Referência", R["baseline"]["test"])] + [(n, R["variantes"][n]["test"]) for n in VARIANTS]
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.1), sharey=True)
    for ax, (title, t) in zip(axes, items):
        cm = np.array(t["matriz_confusao_linhas_real_colunas_previsto"])
        rows = cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(rows, cmap="Blues", vmin=0, vmax=1)
        ax.grid(False)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{100 * rows[i, j]:.1f} %", ha="center", va="center", fontsize=7,
                        color=INK if rows[i, j] < 0.6 else "white")
        ax.set_xticks([0, 1], ["nav.", "pesca"], fontsize=7)
        ax.set_yticks([0, 1], ["nav.", "pesca"], fontsize=7)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("Previsto", fontsize=7)
    axes[0].set_ylabel("Real", fontsize=7)
    fig.tight_layout(w_pad=0.8)
    return save(fig, "janelas_matrizes.png")


def fig_trips(R: dict) -> str:
    bt = {i: m["accuracy"] for i, m in R["baseline"]["test"]["por_viagem"].items()}
    order = sorted(bt, key=lambda i: bt[i])
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(6.9, 2.6))
    ax.plot(x, [100 * bt[i] for i in order], color=BASE_COLOR, lw=1.0, marker="o", ms=4, label="baseline (viagem completa)")
    for name, v in VARIANTS.items():
        pv = R["variantes"][name]["test"]["por_viagem"]
        ax.plot(x, [100 * pv[i]["accuracy"] for i in order], color=v["color"], lw=1.0, marker="s" if name == "J0" else "^",
                ms=4, label=f"{name} (janelas de 64)")
    ax.set_xticks(x, order, rotation=60, ha="right", fontsize=6)
    ax.set(ylabel="Exatidão (%)", xlabel=f"Viagens do conjunto de teste ({len(order)}), por exatidão crescente da baseline",
           xlim=(-0.5, len(order) - 0.5))
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.2), ncol=3)
    return save(fig, "janelas_viagens.png")


def fig_segments(R: dict) -> str:
    series = [("baseline", R["baseline"]["segmentos_test"], BASE_COLOR)] + [
        (n, R["variantes"][n]["segmentos_test"], v["color"]) for n, v in VARIANTS.items()]
    panels = [("F1 de segmentos (IoU ≥ 0,5)", "f1", (0, 1.02)),
              ("Fragmentação (previstos / reais)", "fragmentation_ratio", None),
              ("Erro de fronteira, mediana (s)", ("median_abs_start_error_s", "median_abs_end_error_s"), None)]
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.3))
    classes = [("pesca", "pesca"), ("navegacao", "navegação")]
    for ax, (title, key, ylim) in zip(axes, panels):
        w = 0.8 / len(series)
        if isinstance(key, str):
            groups = [c for c, _ in classes]
            for k, (lab, seg, col) in enumerate(series):
                ax.bar(np.arange(2) + k * w, [seg[c][key] or 0 for c in groups], w, color=col, label=lab)
            ax.set_xticks(np.arange(2) + w, [n for _, n in classes])
            if key == "fragmentation_ratio":
                ax.axhline(1, color=INK, ls="--", lw=0.8)
        else:
            groups = [(c, k) for c in ("pesca", "navegacao") for k in key]
            for k, (lab, seg, col) in enumerate(series):
                ax.bar(np.arange(4) + k * w, [seg[c][kk] or 0 for c, kk in groups], w, color=col, label=lab)
            ax.set_xticks(np.arange(4) + w, ["pesca\nínicio", "pesca\nfim", "nav.\ninício", "nav.\nfim"], fontsize=6)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_title(title, fontsize=8)
    axes[0].legend(frameon=False, fontsize=6, loc="lower left")
    fig.tight_layout(w_pad=1.0)
    return save(fig, "janelas_segmentos.png")


def fig_timeline(R: dict) -> tuple[str, str]:
    """Uma viagem de teste: real, baseline, J0 e J50. Regra de escolha: a viagem com mais segmentos reais."""
    seg = R["baseline"]["segmentos_test"]
    n_ref = {}
    for cls in ("pesca", "navegacao"):
        for row in seg[cls]["por_viagem"]:
            n_ref[row["id"]] = n_ref.get(row["id"], 0) + int(row["n_ref"])
    trip = sorted(n_ref, key=lambda i: (-n_ref[i], i))[0]
    rows = [("real", None)]
    base = pd.read_csv(BASE / "predictions_test_baseline.csv", usecols=["id", "t", "target", "predicted"])
    base = base[base["id"] == trip].sort_values("t")
    arrs = {"real": base["target"].to_numpy(), "baseline": base["predicted"].to_numpy()}
    for name, v in VARIANTS.items():
        p = pd.read_csv(ROOT / "results" / v["dir"] / "predictions_test_selected.csv",
                        usecols=["id", "t", "predicted"])
        arrs[name] = p[p["id"] == trip].sort_values("t")["predicted"].to_numpy()
    assert len({len(a) for a in arrs.values()}) == 1
    fig, axes = plt.subplots(len(arrs), 1, figsize=(6.9, 1.7), sharex=True)
    for ax, (lab, a) in zip(axes, arrs.items()):
        ax.imshow(a[None, :], aspect="auto", cmap=CLASS_CMAP, vmin=0, vmax=1, interpolation="nearest")
        ax.set_yticks([0], [lab], fontsize=7)
        ax.grid(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0)
    axes[-1].set_xlabel(f"Pontos da viagem {trip} (azul: navegação; laranja: pesca)", fontsize=7)
    fig.tight_layout(h_pad=0.2)
    return save(fig, "janelas_linha_temporal.png"), trip


def main() -> None:
    R = collect()
    paired = paired_trips(R)
    figs = [fig_loss_all(R), fig_matrix_all(R), fig_trips(R), fig_segments(R)]
    tl, trip = fig_timeline(R)
    figs.append(tl)
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "resultados_janelas.tex").write_text(latex_macros(R, paired), encoding="utf-8")
    R["comparacao_por_viagem_com_a_baseline"] = paired
    R["viagem_da_linha_temporal"] = {"id": trip, "regra": "a viagem de teste com mais segmentos de referência"}
    R["figuras"], R["macros_latex"] = figs, "latex/generated/resultados_janelas.tex"
    for r in list(R["variantes"].values()) + [R["baseline"]]:
        r.pop("_hist"), r.pop("_curve")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "final_results_windows.json").write_text(
        json.dumps(R, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"escrito {OUT / 'final_results_windows.json'}, latex/generated/resultados_janelas.tex e {len(figs)} figuras")


if __name__ == "__main__":
    main()
