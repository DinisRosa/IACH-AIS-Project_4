"""Macros e figuras do pós-processamento para a proposta (Secção 10, REV-057).

Parte de `results/postproc_validation_v2/postproc_validation.json` (v2, 301 pontos) e do CSV de previsões filtradas, gerados pela
execução única de `postproc_validation`. Não volta a filtrar nem a medir. Confirma que os números coincidem com
a verificação independente (`verificacao_independente.json`, de `verify_postproc_independent`). Escreve:
  - latex/generated/resultados_posproc.tex : macros \\resPp... (nomes sem dígitos);
  - latex/figures/posproc_resultados.png e posproc_viagem.png.

Execução (a partir da raiz do projeto, depois de `postproc_validation`):
    iach-ais-venv-4/bin/python -m ais.cli.build_postproc_results
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ais.cli.build_final_results import INK2, NAV, PESCA, plt, pt, pct, save, thousands
from ais.cli.build_window_results import point_macros, segment_macros
from ais.phase1.reserved import read_log
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[3]
VERSION = "posproc_validation_v2"  # REV-059: a v1 (13 pontos) fica só como histórico interno
PP = ROOT / "results" / "postproc_validation_v2"
GEN = ROOT / "latex" / "generated"
CMAP = ListedColormap([NAV, PESCA])


def check_independent(R: dict, V: dict) -> dict:
    """Compara com a verificação independente; falha se algum número diferir."""
    checks = {}
    for k in ("antes", "depois"):
        g, vg = R[k]["ponto"]["global"], V[k]["metricas"]
        checks[f"{k}_exatidao"] = abs(g["accuracy"] - vg["exatidao"]) < 1e-9
        for c, name in ((0, "navegação"), (1, "pesca")):
            for m, vm in (("precisao", "precisao"), ("sensibilidade", "sensibilidade"), ("f1", "f1")):
                checks[f"{k}_{name}_{m}"] = abs(g["por_classe"][name][m] - vg["por_classe"][str(c)][vm]) < 1e-9
        for c, name in ((0, "navegacao"), (1, "pesca")):
            s, vs = R[k]["segmento"][name], V[k]["segmentos"][str(c)]
            checks[f"{k}_seg_{name}"] = (s["n_ref_segments"], s["n_pred_segments"], s["n_matched"]) == (
                vs["n_ref"], vs["n_pred"], vs["n_pares"])
    checks["mudancas"] = (R["mudancas"]["n_mudam"], R["mudancas"]["corrigidos"]) == (
        V["mudancas"]["n_alterados"], V["mudancas"]["n_corrigidos"])
    if not all(checks.values()):
        raise ValueError(f"A verificação independente não confere: {[k for k, v in checks.items() if not v]}")
    return checks


def latex_macros(R: dict) -> str:
    M = {}
    M.update(point_macros("Pp", R["antes"]["ponto"], "Antes"))
    M.update(point_macros("Pp", R["depois"]["ponto"], "Depois"))
    for k, P in (("antes", "PpA"), ("depois", "PpD")):
        M.update(segment_macros(P, R[k]["segmento"]))
    ch = R["mudancas"]
    M.update({"PpMudam": thousands(ch["n_mudam"]), "PpNavParaPesca": thousands(ch["navegacao_para_pesca"]),
              "PpPescaParaNav": thousands(ch["pesca_para_navegacao"]), "PpCorrigidos": thousands(ch["corrigidos"]),
              "PpEstragados": thousands(ch["estragados"]), "PpPercMudam": pct(ch["n_mudam"] / ch["n_pontos"], 2),
              "PpErrosMenos": thousands(R["antes"]["ponto"]["global"]["n_errors"] - R["depois"]["ponto"]["global"]["n_errors"])})
    T = trip_table(R)
    T["d"] = T["acc_depois"] - T["acc_antes"]
    w = T.sort_values(["d", "id"]).iloc[0]
    M.update({"PpNViagens": str(len(T)), "PpViagMelhoram": str(int((T["d"] > 0).sum())),
              "PpViagPioram": str(int((T["d"] < 0).sum())), "PpPiorQuedaViagem": "\\texttt{" + w["id"] + "}",
              "PpPiorQuedaAntes": pct(w["acc_antes"]), "PpPiorQuedaDepois": pct(w["acc_depois"]),
              "PpJanela": str(R["filtro"]["tamanho_pontos"]), "PpSigma": pt(R["filtro"]["sigma_pontos"], 1)})
    lines = [f"% Gerado por ais.cli.build_postproc_results a partir de results/postproc_validation_v2/postproc_validation.json",
             f"% (execução única {R['criado_utc']}, commit {R['git_commit'][:9]}). NÃO EDITAR À MÃO.",
             "% Prefixos: PpAntes/PpDepois = por ponto; PpASeg/PpDSeg = por segmento antes/depois."]
    lines += [f"\\newcommand{{\\res{k}}}{{{v}}}" for k, v in M.items()]
    return "\n".join(lines) + "\n"


def fig_results(R: dict) -> str:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.3))
    x = np.arange(2)
    for i, (name, lab) in enumerate((("pesca", "pesca"), ("navegacao", "navegação"))):
        s0, s1 = R["antes"]["segmento"][name], R["depois"]["segmento"][name]
        a1.bar(i - 0.27, s0["n_pred_segments"], 0.26, color="0.7", label="previstos, antes" if i == 0 else None)
        a1.bar(i, s1["n_pred_segments"], 0.26, color=INK2, label="previstos, depois" if i == 0 else None)
        a1.bar(i + 0.27, s0["n_ref_segments"], 0.26, color=PESCA if name == "pesca" else NAV,
               label="reais" if i == 0 else None)
        for dx, v in ((-0.27, s0["n_pred_segments"]), (0, s1["n_pred_segments"]), (0.27, s0["n_ref_segments"])):
            a1.text(i + dx, v, str(v), ha="center", va="bottom", fontsize=6.5)
        a2.bar(i - 0.15, s0["f1"], 0.3, color="0.7", label="antes" if i == 0 else None)
        a2.bar(i + 0.15, s1["f1"], 0.3, color=INK2, label="depois" if i == 0 else None)
        for dx, v in ((-0.15, s0["f1"]), (0.15, s1["f1"])):
            a2.text(i + dx, v, pt(v, 3), ha="center", va="bottom", fontsize=6.5)
    for a in (a1, a2):
        a.set_xticks(x, ["pesca", "navegação"])
    a1.set_title("Segmentos (validação)")
    a2.set_title("F1 de segmentos (IoU ≥ 0,5)")
    a1.legend(fontsize=6.5, frameon=False)
    a2.legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    return save(fig, "posproc_resultados.png")


def fig_trip(R: dict) -> tuple[str, str]:
    """Viagem com mais segmentos de pesca previstos antes do filtro (regra de apresentação, fixada aqui)."""
    df = pd.read_csv(PP / "predictions_validation_postproc.csv",
                     usecols=["id", "target", "predicted_antes", "predicted_depois"])
    per = R["antes"]["segmento"]["pesca"]["por_viagem"]
    per = pd.DataFrame(per) if not isinstance(per, pd.DataFrame) else per
    trip = per.sort_values(["n_pred", "id"], ascending=[False, True]).iloc[0]["id"]
    p = df[df["id"] == trip]  # já ordenado por tempo em postproc_validation
    rows = (("real", "target"), ("antes", "predicted_antes"), ("depois", "predicted_depois"))
    fig, axes = plt.subplots(3, 1, figsize=(6.9, 1.6), sharex=True)
    for ax, (lab, col) in zip(axes, rows):
        ax.imshow(p[col].to_numpy()[None, :], aspect="auto", cmap=CMAP, vmin=0, vmax=1, interpolation="nearest")
        ax.set_yticks([0], [lab], fontsize=7)
        ax.grid(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0)
    axes[-1].set_xlabel(f"Pontos da viagem {trip} (azul: navegação; laranja: pesca)", fontsize=7)
    fig.tight_layout(h_pad=0.2)
    return save(fig, "posproc_viagem.png"), str(trip)


def trip_table(R: dict) -> pd.DataFrame:
    """Exatidão e erros por viagem, antes e depois (das tabelas já calculadas na execução única)."""
    a, d = R["antes"]["ponto"]["por_viagem"], R["depois"]["ponto"]["por_viagem"]
    rows = [{"id": i, "pontos": a[i]["n_points"], "acc_antes": a[i]["accuracy"], "acc_depois": d[i]["accuracy"],
             "erros_antes": a[i]["n_errors"], "erros_depois": d[i]["n_errors"],
             "acc_maioritaria": a[i]["accuracy_maioritaria"]} for i in a]
    return pd.DataFrame(rows).sort_values(["acc_antes", "id"]).reset_index(drop=True)


def fig_trips(T: pd.DataFrame) -> str:
    """Exatidão por viagem antes e depois do filtro, por ordem crescente de exatidão antes (como a Figura 6)."""
    fig, ax = plt.subplots(figsize=(6.9, 2.4))
    x = np.arange(len(T))
    ax.bar(x - 0.2, 100 * T["acc_antes"], 0.4, color="0.7", label="antes")
    ax.bar(x + 0.2, 100 * T["acc_depois"], 0.4, color=NAV, label="depois do filtro")
    ax.scatter(x, 100 * T["acc_maioritaria"], color="black", s=10, zorder=3,
               label="prever sempre a classe maioritária da viagem")
    ax.set_xticks(x, T["id"], rotation=60, ha="right", fontsize=5.5)
    ax.set(ylabel="Exatidão (%)", ylim=(0, 102), xlim=(-0.7, len(T) - 0.3))
    ax.set_title("Exatidão por viagem, antes e depois (por ordem crescente de exatidão antes)", fontsize=8)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right")
    fig.tight_layout()
    return save(fig, "posproc_viagens.png")


def main() -> None:
    R = json.loads((PP / "postproc_validation.json").read_text(encoding="utf-8"))
    V = json.loads((PP / "verificacao_independente.json").read_text(encoding="utf-8"))
    checks = check_independent(R, V)
    events = [e["event"] for e in read_log(ROOT / "results" / "access_log.jsonl")
              if e.get("event") in ("postproc_start", "postproc_done") and e.get("protocol") == VERSION]
    if events != ["postproc_start", "postproc_done"]:
        raise ValueError(f"Registo inesperado das execuções do pós-processamento: {events}")
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "resultados_posproc.tex").write_text(latex_macros(R), encoding="utf-8")
    f1 = fig_results(R)
    f2, trip = fig_trip(R)
    T = trip_table(R)
    T.to_csv(PP / "exatidao_por_viagem.csv", index=False)
    f3 = fig_trips(T)
    info = {"verificacao_independente_confere": checks, "execucoes_registadas": events,
            "figuras": [f1, f2, f3], "viagem_da_figura": {"id": trip, "regra": "mais segmentos de pesca previstos antes do filtro"},
            "macros_latex": "latex/generated/resultados_posproc.tex"}
    (PP / "build_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"verificação independente: {sum(checks.values())}/{len(checks)} conferem; viagem da figura {trip}")


if __name__ == "__main__":
    main()
