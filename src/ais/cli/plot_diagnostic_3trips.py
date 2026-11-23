"""Gráficos e tabelas em imagem do ensaio de ajuste em 3 viagens (REV-029).

Lê SÓ os artefactos já gerados por src/ais/cli/diagnostic_fit_3_trips.py (results/diagnostic_3trips/);
não treina, não abre os parquet nem validação/teste. Nenhum número é calculado aqui além de
percentagens de apresentação sobre contagens guardadas.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.plot_diagnostic_3trips
Saídas: results/diagnostic_3trips/figures/*.png (não versionadas).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "results" / "diagnostic_3trips"
OUT = SRC / "figures"

# Paleta de referência (slots 1 e 2, validados); tinta e superfície neutras.
NAV, PESCA = "#2a78d6", "#eb6834"
FIT_C, EVAL_C = "#8a8985", "#6250d6"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SETS = {"ajuste": "Ajuste (treinado)", "fora_da_amostra": "Fora da amostra"}
SET_COLOR = {"ajuste": FIT_C, "fora_da_amostra": EVAL_C}

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
})

T = json.loads((SRC / "tables.json").read_text())
MAN = json.loads((SRC / "run_manifest.json").read_text())
PRED = pd.read_csv(SRC / "predictions.csv")
HIST = pd.read_csv(SRC / "training_history.csv")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def trips():
    """(conjunto, id, métricas) pela ordem ajuste -> fora da amostra."""
    return [(k, i, m) for k in SETS for i, m in T[k]["por_viagem"].items()]


def fig_loss_accuracy():
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
    a.plot(HIST["epoch"], HIST["mean_loss_per_point"], color=INK2, lw=2)
    a.set(xlabel="Época", ylabel="Perda por ponto (BCE)", ylim=(0, None))
    a.set_title("Perda no treino (3 viagens de ajuste)")
    a.annotate(f"{HIST['mean_loss_per_point'].iloc[0]:.3f}", (1, HIST["mean_loss_per_point"].iloc[0]),
               xytext=(8, -2), textcoords="offset points", color=INK2)
    a.annotate(f"{HIST['mean_loss_per_point'].iloc[-1]:.3f}", (HIST["epoch"].iloc[-1], HIST["mean_loss_per_point"].iloc[-1]),
               xytext=(-34, 10), textcoords="offset points", color=INK2)

    rows = trips()
    y = np.arange(len(rows))[::-1]
    for yy, (k, i, m) in zip(y, rows):
        b.barh(yy, 100 * m["accuracy"], height=0.55, color=SET_COLOR[k])
        b.plot([100 * m["accuracy_maioritaria"]] * 2, [yy - 0.38, yy + 0.38], color=INK, lw=2)
        b.text(100 * m["accuracy"] + 0.8, yy, f"{100 * m['accuracy']:.1f} %  ({m['n_errors']} erros)",
               va="center", color=INK2, fontsize=9)
    b.set_yticks(y, [i for _, i, _ in rows])
    b.set(xlim=(0, 122), xlabel="Accuracy (%)")
    b.xaxis.grid(True); b.yaxis.grid(False)
    b.set_title("Accuracy por viagem")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    b.legend(handles=[Patch(color=FIT_C, label="Ajuste (treinado)"), Patch(color=EVAL_C, label="Fora da amostra"),
                      Line2D([0], [0], color=INK, lw=2, label="Prever sempre a classe maioritária")],
             loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=False, fontsize=9)
    save(fig, "fig1_perda_e_accuracy.png")


def fig_confusion():
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4))
    for ax, k in zip(axes, SETS):
        cm = np.array(T[k]["matriz_confusao_linhas_real_colunas_previsto"])
        pct = cm / cm.sum(axis=1, keepdims=True)
        ax.imshow(pct, cmap="Blues", vmin=0, vmax=1)
        ax.grid(False)
        for r in range(2):
            for c in range(2):
                ax.text(c, r, f"{cm[r, c]:,}".replace(",", " ") + f"\n{100 * pct[r, c]:.1f} % da linha",
                        ha="center", va="center", color="white" if pct[r, c] > 0.55 else INK, fontsize=8.5)
        ax.set_xticks([0, 1], ["navegação", "pesca"]); ax.set_yticks([0, 1], ["navegação", "pesca"])
        ax.set(xlabel="Previsto pela CNN", ylabel="Real (rótulo)")
        ax.set_title(f"{SETS[k]}: accuracy {100 * T[k]['global']['accuracy']:.1f} %")
        for s in ax.spines.values():
            s.set_visible(False)
    fig.subplots_adjust(wspace=0.8)
    save(fig, "fig2_matrizes_confusao.png")


def fig_class_metrics():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    mets = [("recall_acerto_da_classe", "Sensibilidade"), ("precisao", "Precisão"), ("f1", "F1")]
    for ax, cls in zip(axes, ("navegação", "pesca")):
        x = np.arange(len(mets))
        for j, k in enumerate(SETS):
            vals = [T[k]["global"]["por_classe"][cls][m] for m, _ in mets]
            ax.bar(x + (j - 0.5) * 0.36, vals, width=0.32, color=SET_COLOR[k], label=SETS[k])
            for xx, v in zip(x + (j - 0.5) * 0.36, vals):
                ax.text(xx, v + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=INK2)
        ax.set_xticks(x, [n for _, n in mets]); ax.set_ylim(0, 1.12)
        ax.xaxis.grid(False)
        ax.set_title(f"Classe: {cls}", color=NAV if cls == "navegação" else PESCA)
    axes[0].set_ylabel("Valor (0 a 1)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, loc="upper right", ncol=2, fontsize=9, bbox_to_anchor=(0.98, 1.02))
    save(fig, "fig3_metricas_por_classe.png")


def fig_labels():
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), sharex=False)
    for ax, k in zip(axes, SETS):
        d = pd.DataFrame(T[k]["rotulo_original_vs_previsto"]).set_index("label")
        d = d[["navegação", "pesca"]]
        y = np.arange(len(d))[::-1]
        tot = d.sum(axis=1)
        ax.barh(y, d["navegação"] / tot * 100, color=NAV, height=0.6, label="previsto navegação")
        ax.barh(y, d["pesca"] / tot * 100, left=d["navegação"] / tot * 100, color=PESCA, height=0.6,
                label="previsto pesca", edgecolor=SURF, linewidth=2)
        for yy, (lab, r) in zip(y, d.iterrows()):
            ax.text(101, yy, f"n = {int(r.sum()):,}".replace(",", " "), va="center", fontsize=9, color=INK2)
        ax.set_yticks(y, d.index); ax.set(xlim=(0, 125), xlabel="% dos pontos com este rótulo original")
        ax.yaxis.grid(False); ax.set_title(SETS[k])
    axes[0].legend(frameon=False, loc="lower left", bbox_to_anchor=(0, -0.35), ncol=2, fontsize=9)
    save(fig, "fig4_rotulos_originais_vs_previsto.png")


def fig_timelines(only=None, name="fig5_linhas_temporais.png", width=13):
    rows = [r for r in trips() if only is None or r[0] in only]
    fig, axes = plt.subplots(len(rows), 1, figsize=(width, 2.15 * len(rows)))
    for ax, (k, i, m) in zip(axes, rows):
        g = PRED[(PRED["id"] == i)].reset_index(drop=True)
        n = len(g)
        x = np.arange(n)
        ax.plot(x, g["p_fishing"], color=INK2, lw=0.8)
        ax.axhline(0.5, color=GRID, lw=1, ls="--")
        for yy, col, strip in ((1.12, "target", "real"), (1.30, "predicted", "previsto")):
            for cls, colr in ((0, NAV), (1, PESCA)):
                ax.fill_between(x, yy, yy + 0.14, where=(g[col] == cls).to_numpy(), color=colr, step="mid", lw=0)
            ax.text(-0.005 * n, yy + 0.07, strip, ha="right", va="center", fontsize=8, color=INK2)
        err = (g["target"] != g["predicted"]).to_numpy()
        ax.fill_between(x, 1.48, 1.60, where=err, color=INK, step="mid", lw=0)
        ax.text(-0.005 * n, 1.54, "erro", ha="right", va="center", fontsize=8, color=INK2)
        ax.set_xlim(0, n); ax.set_ylim(-0.05, 1.65)
        ax.set_yticks([0, 0.5, 1]); ax.set_ylabel("p(pesca)", fontsize=8)
        ax.xaxis.grid(False)
        ax.set_title(f"{SETS[k]} · {i} · accuracy {100 * m['accuracy']:.1f} % · {m['n_errors']} erros em {n} pontos",
                     fontsize=10)
    axes[-1].set_xlabel("Posição do ponto na viagem (ordem temporal)")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=NAV, label="navegação"), Patch(color=PESCA, label="pesca"),
                        Patch(color=INK, label="ponto errado")],
               loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.98, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(fig, name)


def draw_table(ax, title, header, rows, widths=None):
    ax.axis("off"); ax.set_title(title, pad=8)
    t = ax.table(cellText=rows, colLabels=header, loc="upper center", cellLoc="center", colWidths=widths)
    t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1, 1.5)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_facecolor("#ecebe7"); cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor(SURF)


def fmt(v, p=3):
    return "—" if v is None else f"{v:.{p}f}"


def fig_tables():
    fig, axes = plt.subplots(3, 1, figsize=(12, 7.4), gridspec_kw={"height_ratios": [0.75, 1.2, 1.5]})
    rows = []
    for k in SETS:
        g = T[k]["global"]
        rows.append([SETS[k], f"{len(T[k]['por_viagem'])}", f"{g['n_points']:,}".replace(",", " "),
                     f"{g['n_correct']:,}".replace(",", " "), f"{g['n_errors']:,}".replace(",", " "),
                     f"{100 * g['accuracy']:.2f} %", f"{100 * g['accuracy_maioritaria']:.2f} %"])
    draw_table(axes[0], "Resumo global", ["Conjunto", "Viagens", "Pontos", "Acertos", "Erros", "Accuracy",
                                          "Classe maioritária"], rows)
    rows = []
    for k in SETS:
        for cls, v in T[k]["global"]["por_classe"].items():
            rows.append([SETS[k], cls, f"{v['n_real']:,}".replace(",", " "), f"{v['n_predicted']:,}".replace(",", " "),
                         f"{v['acertos']:,}".replace(",", " "), f"{v['erros']:,}".replace(",", " "),
                         fmt(v["recall_acerto_da_classe"]), fmt(v["precisao"]), fmt(v["f1"]), fmt(v["iou"])])
    draw_table(axes[1], "Por classe (positivo = a própria classe)",
               ["Conjunto", "Classe", "Reais", "Previstos", "Acertos", "Erros", "Sensib.", "Precisão", "F1", "IoU"], rows)
    rows = [[SETS[k], i, f"{m['n_points']:,}".replace(",", " "), f"{m['n_correct']:,}".replace(",", " "),
             f"{m['n_errors']:,}".replace(",", " "), f"{100 * m['accuracy']:.2f} %",
             f"{100 * m['accuracy_maioritaria']:.2f} %",
             fmt(m["por_classe"]["navegação"]["recall_acerto_da_classe"], 2),
             fmt(m["por_classe"]["pesca"]["recall_acerto_da_classe"], 2)] for k, i, m in trips()]
    draw_table(axes[2], "Por viagem", ["Conjunto", "Viagem", "Pontos", "Acertos", "Erros", "Accuracy", "Maioritária",
                                       "Sensib. nav.", "Sensib. pesca"], rows)
    fig.suptitle("Ensaio de ajuste em 3 viagens de treino — tabelas (sem validação nem teste)", x=0.01, ha="left",
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(fig, "fig6_tabelas.png")


if __name__ == "__main__":
    for f in (fig_loss_accuracy, fig_confusion, fig_class_metrics, fig_labels, fig_timelines, fig_tables):
        f()
    # versão para o relatório: só as viagens fora da amostra, mais estreita
    fig_timelines(only=("fora_da_amostra",), name="fig5b_linhas_temporais_fora_da_amostra.png", width=10)
    print("figuras em", OUT, sorted(p.name for p in OUT.glob("*.png")))
