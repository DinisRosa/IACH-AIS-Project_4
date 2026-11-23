"""Figuras e tabelas em imagem do treino da fase 1 (REV-032).

Lê SÓ os artefactos de results/phase1_run1/ (histórico, tabelas, previsões da monitorização interna).
Não treina, não abre parquet nem validação/teste. Percentagens são só de apresentação.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.plot_phase1_run [results/phase1_run1]
Saídas: <pasta>/figures/*.png (não versionadas).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "phase1_run1"
OUT = SRC / "figures"
NAV, PESCA, FIT_C, MON_C = "#2a78d6", "#eb6834", "#8a8985", "#6250d6"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SETS = {"ajuste": "Ajuste (74 viagens)", "monitor_interna": "Monitorização (13 viagens)"}
SHORT = {"ajuste": "Ajuste (74)", "monitor_interna": "Monitor. (13)"}  # nomes curtos para as tabelas
SET_COLOR = {"ajuste": FIT_C, "monitor_interna": MON_C}

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": GRID,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left"})

T = json.loads((SRC / "tables.json").read_text())
MAN = json.loads((SRC / "run_manifest.json").read_text())
H = pd.read_csv(SRC / "training_history.csv")
PRED = pd.read_csv(SRC / "predictions_monitor.csv")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_loss_and_trips():
    best = MAN["train_result"]["best_epoch"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1, 1.2]})
    a.plot(H["epoch"], H["train_loss_per_point"], color=FIT_C, lw=2, label="treino (média da época)")
    a.plot(H["epoch"], H["monitor_loss_per_point"], color=MON_C, lw=2, label="monitorização interna")
    a.axvline(best, color=INK, ls="--", lw=1)
    a.annotate(f"melhor modelo\n(época {best})", (best, H["monitor_loss_per_point"].min()),
               xytext=(best + 0.4, 0.31), color=INK2, fontsize=9)
    a.annotate("paragem\nantecipada", (H["epoch"].iloc[-1], H["monitor_loss_per_point"].iloc[-1]),
               xytext=(H["epoch"].iloc[-1] - 3.2, 0.27), color=INK2, fontsize=9)
    a.set(xlabel="Época", ylabel="Perda por ponto (BCE)", ylim=(0, 0.4))
    a.set_title("Perda ao longo do treino")
    a.legend(frameon=False, loc="upper right", fontsize=9)

    rows = sorted(T["monitor_interna"]["por_viagem"].items(), key=lambda kv: kv[1]["accuracy"])
    y = np.arange(len(rows))
    for yy, (i, m) in zip(y, rows):
        b.barh(yy, 100 * m["accuracy"], height=0.6, color=MON_C)
        b.plot([100 * m["accuracy_maioritaria"]] * 2, [yy - 0.4, yy + 0.4], color=INK, lw=2)
        b.text(100 * m["accuracy"] + 0.8, yy, f"{100 * m['accuracy']:.1f} %  ({m['n_errors']} erros / {m['n_points']})",
               va="center", fontsize=8, color=INK2)
    b.set_yticks(y, [i for i, _ in rows]); b.set(xlim=(0, 135), xlabel="Accuracy (%)")
    b.xaxis.grid(True); b.yaxis.grid(False)
    b.set_title("Accuracy em cada viagem de monitorização")
    b.legend(handles=[Patch(color=MON_C, label="CNN"), Line2D([0], [0], color=INK, lw=2,
             label="Prever sempre a classe maioritária")], loc="upper center",
             bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False, fontsize=9)
    save(fig, "fig1_perda_e_accuracy_por_viagem.png")


def fig_confusion():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
    for ax, k in zip(axes, SETS):
        cm = np.array(T[k]["matriz_confusao_linhas_real_colunas_previsto"])
        pct = cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(pct, cmap="Blues", vmin=0, vmax=1); ax.grid(False)
        for r in range(2):
            for c in range(2):
                ax.text(c, r, f"{cm[r, c]:,}".replace(",", " ") + f"\n{100 * pct[r, c]:.1f} % da linha",
                        ha="center", va="center", fontsize=8.5, color="white" if pct[r, c] > 0.55 else INK)
        ax.set_xticks([0, 1], ["navegação", "pesca"]); ax.set_yticks([0, 1], ["navegação", "pesca"])
        ax.set(xlabel="Previsto pela CNN", ylabel="Real (rótulo)")
        ax.set_title(f"{SETS[k]}\naccuracy {100 * T[k]['global']['accuracy']:.1f} %", fontsize=10)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.subplots_adjust(wspace=0.8)
    save(fig, "fig2_matrizes_confusao.png")


def fig_class_metrics():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    mets = [("sensibilidade", "Sensibilidade"), ("precisao", "Precisão"), ("f1", "F1")]
    for ax, cls in zip(axes, ("navegação", "pesca")):
        x = np.arange(len(mets))
        for j, k in enumerate(SETS):
            vals = [T[k]["global"]["por_classe"][cls][m] for m, _ in mets]
            ax.bar(x + (j - 0.5) * 0.36, vals, width=0.32, color=SET_COLOR[k], label=SETS[k])
            for xx, v in zip(x + (j - 0.5) * 0.36, vals):
                ax.text(xx, v + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=INK2)
        ax.set_xticks(x, [n for _, n in mets]); ax.set_ylim(0, 1.12); ax.xaxis.grid(False)
        ax.set_title(f"Classe: {cls}", color=NAV if cls == "navegação" else PESCA)
    axes[0].set_ylabel("Valor (0 a 1)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, loc="upper right", ncol=2, fontsize=9, bbox_to_anchor=(0.98, 1.03))
    save(fig, "fig3_metricas_por_classe.png")


def fig_timelines():
    ids = list(T["monitor_interna"]["por_viagem"])
    fig, axes = plt.subplots(len(ids), 1, figsize=(13, 1.75 * len(ids)))
    for ax, i in zip(axes, ids):
        g = PRED[PRED["id"] == i].reset_index(drop=True); n = len(g); x = np.arange(n)
        m = T["monitor_interna"]["por_viagem"][i]
        ax.plot(x, g["p_fishing"], color=INK2, lw=0.7); ax.axhline(0.5, color=GRID, lw=1, ls="--")
        for yy, col, strip in ((1.12, "target", "real"), (1.30, "predicted", "previsto")):
            for cls, colr in ((0, NAV), (1, PESCA)):
                ax.fill_between(x, yy, yy + 0.14, where=(g[col] == cls).to_numpy(), color=colr, step="mid", lw=0)
            ax.text(-0.005 * n, yy + 0.07, strip, ha="right", va="center", fontsize=7, color=INK2)
        err = (g["target"] != g["predicted"]).to_numpy()
        ax.fill_between(x, 1.48, 1.60, where=err, color=INK, step="mid", lw=0)
        ax.text(-0.005 * n, 1.54, "erro", ha="right", va="center", fontsize=7, color=INK2)
        ax.set_xlim(0, n); ax.set_ylim(-0.05, 1.65); ax.set_yticks([0, 1]); ax.xaxis.grid(False)
        ax.set_title(f"{i} · accuracy {100 * m['accuracy']:.1f} % · {m['n_errors']} erros em {n} pontos", fontsize=9)
    axes[-1].set_xlabel("Posição do ponto na viagem (ordem temporal)")
    fig.legend(handles=[Patch(color=NAV, label="navegação"), Patch(color=PESCA, label="pesca"),
                        Patch(color=INK, label="ponto errado")], loc="upper right", ncol=3, frameon=False,
               bbox_to_anchor=(0.98, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    save(fig, "fig4_linhas_temporais_monitor.png")


def draw_table(ax, title, header, rows):
    ax.axis("off"); ax.set_title(title, pad=8)
    t = ax.table(cellText=rows, colLabels=header, loc="upper center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.45)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID); cell.set_facecolor("#ecebe7" if r == 0 else SURF)
        if r == 0:
            cell.set_text_props(weight="bold")


def fmt(v, p=3):
    return "—" if v is None else f"{v:.{p}f}"


def sp(n):
    return f"{n:,}".replace(",", " ")


def fig_tables():
    fig, axes = plt.subplots(3, 1, figsize=(12, 10.5), gridspec_kw={"height_ratios": [0.75, 1.2, 2.4]})
    r = MAN["train_result"]
    rows = []
    for k in SETS:
        g = T[k]["global"]
        rows.append([SHORT[k], sp(g["n_points"]), sp(g["n_correct"]), sp(g["n_errors"]),
                     f"{100 * g['accuracy']:.2f} %", f"{100 * g['accuracy_maioritaria']:.2f} %"])
    draw_table(axes[0], "Resumo global (melhor modelo: época %d, parou após %d épocas em %.0f s)" % (
        r["best_epoch"], r["epochs_run"], r["total_seconds"]),
        ["Conjunto", "Pontos", "Acertos", "Erros", "Accuracy", "Classe maioritária"], rows)
    rows = [[SHORT[k], c, sp(v["n_real"]), sp(v["n_predicted"]), sp(v["acertos"]), sp(v["erros"]),
             fmt(v["sensibilidade"]), fmt(v["precisao"]), fmt(v["f1"]), fmt(v["iou"])]
            for k in SETS for c, v in T[k]["global"]["por_classe"].items()]
    draw_table(axes[1], "Por classe (positivo = a própria classe)",
               ["Conjunto", "Classe", "Reais", "Previstos", "Acertos", "Erros", "Sensib.", "Precisão", "F1", "IoU"], rows)
    rows = [[i, sp(m["n_points"]), sp(m["n_correct"]), sp(m["n_errors"]), f"{100 * m['accuracy']:.2f} %",
             f"{100 * m['accuracy_maioritaria']:.2f} %", fmt(m["por_classe"]["navegação"]["sensibilidade"], 2),
             fmt(m["por_classe"]["pesca"]["sensibilidade"], 2)]
            for i, m in sorted(T["monitor_interna"]["por_viagem"].items(), key=lambda kv: kv[1]["accuracy"])]
    draw_table(axes[2], "Por viagem de monitorização (da pior para a melhor)",
               ["Viagem", "Pontos", "Acertos", "Erros", "Accuracy", "Maioritária", "Sensib. nav.", "Sensib. pesca"], rows)
    fig.suptitle("Treino da CNN 1D de referência: só treino oficial, sem validação nem teste", x=0.01,
                 ha="left", fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(fig, "fig5_tabelas.png")


if __name__ == "__main__":
    for f in (fig_loss_and_trips, fig_confusion, fig_class_metrics, fig_timelines, fig_tables):
        f()
    print("figuras:", sorted(p.name for p in OUT.glob("*.png")))
