"""Galeria de viagens para o GitHub (REV-073): uma imagem por viagem do `test` e do `validation`.

Parte só de previsões já guardadas; não abre parquets nem corre a CNN. No `test` mostra o real, a baseline,
J0, J50 e a baseline depois do filtro gaussiano de 301 pontos (calculado sobre as probabilidades guardadas);
no `validation` mostra o real, a baseline e a baseline filtrada (saída da execução única já registada).
Antes de escrever, confirma por viagem a exatidão e os segmentos de pesca contra os resultados já gravados e
confirma que as viagens são as do manifesto da divisão; qualquer diferença pára a execução.

Exige `configs/authorizations/{test,validation}_trip_gallery.json` e regista cada leitura. Escreve:
  - viagens/README.md, viagens/teste/*.png, viagens/validacao/*.png e viagens/proveniencia.json

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.build_trip_gallery
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from ais.cli.build_final_results import NAV, PESCA, plt, pt
from ais.cli.postproc_validation import THRESHOLD, apply_filter, order_points
from ais.phase1.postprocessing import gaussian_kernel
from ais.phase1.reserved import log_access, sha256_of
from ais.phase1.segments import compute_segment_metrics

ROOT = Path(__file__).resolve().parents[3]
SIZE = 301
CMAP = ListedColormap([NAV, PESCA])
REAL, BASE, PP = "real", "baseline", "baseline + pós-processamento"
SETS = {
    "test": {"dir": "teste", "title": "Teste", "rows": (BASE, "J0", "J50", PP),
             "auth": "configs/authorizations/test_trip_gallery.json",
             "sources": {BASE: "results/baseline_frozen/predictions_test_baseline.csv",
                         "J0": "results/windows_j0/predictions_test_selected.csv",
                         "J50": "results/windows_j50/predictions_test_selected.csv"},
             "checks": ("results/windows_final/final_results_windows.json",
                        "results/postproc_window_analysis/test_eval.json")},
    "validation": {"dir": "validacao", "title": "Validação", "rows": (BASE, PP),
                   "auth": "configs/authorizations/validation_trip_gallery.json",
                   "sources": {BASE: "results/postproc_validation_v2/predictions_validation_postproc.csv"},
                   "checks": ("results/postproc_validation_v2/postproc_validation.json",)},
}
MANIFEST = "manifests/split_manifest_seed42.csv"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_authorization(root: Path, split: str) -> str:
    auth = _json(root / SETS[split]["auth"])
    if (auth.get("conjuntos_autorizados") != [split] or auth.get("finalidade") != "galeria_viagens"
            or bool(auth.get("validation_autorizado")) != (split == "validation")):
        raise PermissionError(f"Autorização inválida para a galeria do '{split}'.")
    return auth["id"]


# ----------------------------------------------------------------------------- previsões
def load_test(root: Path) -> pd.DataFrame:
    """Uma linha por ponto: id, t, real e a classe prevista por cada linha da imagem."""
    src = SETS["test"]["sources"]
    saved = _json(root / SETS["test"]["checks"][1])
    if sha256_of(root / src[BASE]) != saved["fonte_sha256"]:
        raise ValueError("As previsões da baseline no test não são as já avaliadas (hash diferente).")
    base = order_points(pd.read_csv(root / src[BASE],
                                    usecols=["id", "point_id", "t", "target", "p_fishing", "predicted"]))
    base = apply_filter(base, THRESHOLD, gaussian_kernel(SIZE, SIZE / 6))
    out = pd.DataFrame({"id": base["id"], "t": base["t"], REAL: base["target"], BASE: base["predicted"]})
    for name in ("J0", "J50"):
        p = pd.read_csv(root / src[name], usecols=["id", "point_id", "target", "predicted"]).set_index("point_id")
        if not p.index.is_unique or set(p.index) != set(base["point_id"]):
            raise ValueError(f"{name}: os pontos não são os mesmos da baseline.")
        p = p.loc[base["point_id"]]
        if (p["id"].to_numpy() != base["id"].to_numpy()).any() or (p["target"].to_numpy() != base["target"].to_numpy()).any():
            raise ValueError(f"{name}: viagem ou classe real diferente da baseline no mesmo ponto.")
        out[name] = p["predicted"].to_numpy()
    out[PP] = base["predicted_filtrado"].to_numpy()
    return out


def load_validation(root: Path) -> pd.DataFrame:
    p = pd.read_csv(root / SETS["validation"]["sources"][BASE],
                    usecols=["id", "point_id", "t", "target", "p_fishing", "predicted_antes", "predicted_depois"])
    p = order_points(p.rename(columns={"predicted_antes": "predicted"}))
    return pd.DataFrame({"id": p["id"], "t": p["t"], REAL: p["target"], BASE: p["predicted"],
                         PP: p["predicted_depois"]})


# ----------------------------------------------------------------------------- valores e conferência
def trip_values(points: pd.DataFrame, rows) -> dict:
    """Por linha e por viagem: exatidão e segmentos de pesca (previstos e reais)."""
    out = {}
    for row in rows:
        seg = compute_segment_metrics(points, class_col=row, cls=1, target_col=REAL)["por_viagem"].set_index("id")
        acc = (points[row] == points[REAL]).groupby(points["id"]).mean()
        out[row] = {i: {"accuracy": float(acc[i]), "n_pred": int(seg.loc[i, "n_pred"]),
                        "n_ref": int(seg.loc[i, "n_ref"])} for i in seg.index}
    return out


def _saved(tables: dict, segments) -> dict:
    seg = pd.DataFrame(segments).set_index("id")
    return {i: {"accuracy": m["accuracy"], "n_pred": int(seg.loc[i, "n_pred"]), "n_ref": int(seg.loc[i, "n_ref"])}
            for i, m in tables.items()}


def saved_values(root: Path, split: str) -> tuple[dict, int | None]:
    """Valores já gravados para conferir e, no `test`, o total de segmentos de pesca depois do filtro."""
    paths = SETS[split]["checks"]
    if split == "validation":
        R = _json(root / paths[0])
        return {row: _saved(R[k]["ponto"]["por_viagem"], R[k]["segmento"]["pesca"]["por_viagem"])
                for row, k in ((BASE, "antes"), (PP, "depois"))}, None
    W, E = _json(root / paths[0]), _json(root / paths[1])
    out = {BASE: _saved(W["baseline"]["test"]["por_viagem"], W["baseline"]["segmentos_test"]["pesca"]["por_viagem"])}
    for name in ("J0", "J50"):
        v = W["variantes"][name]
        out[name] = _saved(v["test"]["por_viagem"], v["segmentos_test"]["pesca"]["por_viagem"])
    # Do filtro no test só se gravaram a exatidão por viagem e o total de segmentos.
    out[PP] = {i: {"accuracy": a} for i, a in E["exatidao_por_viagem"][str(SIZE)].items()}
    total = next(r for r in E["resumo"] if r["janela"] == SIZE)["seg_pesca_previstos"]
    return out, int(total)


def verify(values: dict, saved: dict, total_pp: int | None) -> int:
    """Compara com os resultados gravados; devolve o número de valores conferidos ou falha."""
    n, bad = 0, []
    for row, trips in values.items():
        if set(trips) != set(saved[row]):
            raise ValueError(f"'{row}': as viagens não são as dos resultados gravados.")
        for i, v in trips.items():
            for key, expected in saved[row][i].items():
                n += 1
                if abs(v[key] - expected) > 1e-9:
                    bad.append(f"{row} / {i} / {key}: {v[key]} contra {expected}")
    if total_pp is not None:
        n += 1
        got = sum(v["n_pred"] for v in values[PP].values())
        if got != total_pp:
            bad.append(f"total de segmentos depois do filtro: {got} contra {total_pp}")
    if bad:
        raise ValueError("Os valores não coincidem com os resultados gravados:\n" + "\n".join(bad[:10]))
    return n


def manifest_ids(root: Path, split: str) -> set:
    m = pd.read_csv(root / MANIFEST)
    return set(m.loc[m["split"] == split, "id"])


# ----------------------------------------------------------------------------- imagens e página
def draw_trip(trip: pd.DataFrame, rows, trip_id: str, path: Path) -> None:
    """Uma faixa por linha (azul: navegação; laranja: pesca), como a figura da linha temporal do relatório."""
    names = (REAL, *rows)
    fig, axes = plt.subplots(len(names), 1, figsize=(9.0, 0.34 * len(names) + 0.45), sharex=True, squeeze=False)
    for ax, name in zip(axes[:, 0], names):
        # Mistura de cores ao reduzir: um bloco mais estreito do que um píxel esbate-se em vez de desaparecer.
        ax.imshow(trip[name].to_numpy()[None, :], aspect="auto", cmap=CMAP, vmin=0, vmax=1,
                  interpolation="antialiased", interpolation_stage="rgba")
        ax.set_yticks([0], [name], fontsize=7.5)
        ax.grid(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(length=0, labelsize=7)
    axes[-1, 0].set_xlabel(f"Pontos da viagem {trip_id} (azul: navegação; laranja: pesca)", fontsize=7.5)
    fig.tight_layout(h_pad=0.2)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _pct(x: float) -> str:
    return pt(100 * x, 1) + " %"


def _count(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def trip_order(values: dict) -> list:
    return sorted(values[BASE], key=lambda i: (values[BASE][i]["accuracy"], i))


def markdown(data: dict) -> str:
    """Página da galeria. `data[split]` = {"values": ..., "points": {viagem: n}}."""
    L = ["# Viagens: o que cada modelo previu", "",
         "<!-- Gerado por ais.cli.build_trip_gallery. Não editar à mão. -->", "",
         "Uma imagem por viagem dos conjuntos de teste e de validação, com a classe de cada ponto: "
         "**azul** é navegação e **laranja** é pesca. O método e a discussão estão no relatório "
         "([`latex/relatorio_pt.tex`](../latex/relatorio_pt.tex)).", "",
         "| Linha | O que é |", "|---|---|",
         "| real | classe anotada no conjunto de dados |",
         "| baseline | CNN 1D sobre a viagem completa (no relatório chama-se «referência») |",
         "| J0 | a mesma CNN em janelas de 64 pontos, sem sobreposição |",
         "| J50 | a mesma CNN em janelas de 64 pontos, com 50 % de sobreposição |",
         f"| {PP} | a baseline depois de um filtro gaussiano de {SIZE} pontos sobre as probabilidades |", "",
         "## Como ler estes resultados", "",
         "- O conjunto de **teste** serviu para escolher épocas, limiares e a janela do filtro: os seus "
         "resultados são **otimistas**.",
         "- Na **validação**, só a baseline é a medição final. O filtro **não é uma medição independente**: antes "
         "dele aplicou-se à validação uma versão de 13 pontos. J0 e J50 não foram medidos neste conjunto.",
         "- O filtro aplica-se só à baseline. Estas imagens servem para ver, não para escolher valores.",
         "- O eixo horizontal conta pontos e não tempo. Nas viagens longas há vários pontos por píxel, e um bloco "
         "muito curto aparece esbatido ou quase não se vê: a tabela conta todos os segmentos.",
         "- Em cada conjunto, as viagens estão por ordem crescente de exatidão da baseline.", "",
         "Dados: Song Wu, *Detailed Labelled Fishing Trajectories from AIS*, Zenodo, "
         "[10.5281/zenodo.7283281](https://doi.org/10.5281/zenodo.7283281), "
         "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). As imagens são derivadas desses dados "
         "e das previsões deste projeto.", "",
         "**Conjuntos:** " + " · ".join(f"[{SETS[s]['title']} ({len(data[s]['points'])} viagens)](#{SETS[s]['dir']})"
                                      for s in data), ""]
    for split, d in data.items():
        spec, values = SETS[split], d["values"]
        order = trip_order(values)
        L += [f'<a id="{spec["dir"]}"></a>', "", f"## {spec['title']}", "",
              "Viagens: " + " · ".join(f"[{i}](#{i})" for i in order), ""]
        for i in order:
            L += [f"### {i}", "", f"![Viagem {i}: classe de cada ponto, real e prevista]({spec['dir']}/{i}.png)", "",
                  f"{_count(d['points'][i])} pontos; segmentos de pesca reais: {values[BASE][i]['n_ref']}.", "",
                  "| Linha | Exatidão | Segmentos de pesca previstos |", "|---|---:|---:|"]
            L += [f"| {row} | {_pct(values[row][i]['accuracy'])} | {values[row][i]['n_pred']} |" for row in spec["rows"]]
            L += ["", "[Voltar ao topo](#viagens-o-que-cada-modelo-previu)", ""]
    return "\n".join(L)


def _git(root: Path) -> dict:
    def run(*a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"),
            "codigo_ou_configs_por_commitar": bool(run("status", "--porcelain", "--", "src", "configs"))}


def build(root: Path = ROOT) -> dict:
    auths = {s: check_authorization(root, s) for s in SETS}  # as duas antes de ler qualquer previsão
    data, frames, sources, checked = {}, {}, {}, {}
    for split, spec in SETS.items():
        files = [*spec["sources"].values(), *spec["checks"]]
        sources.update({f: sha256_of(root / f) for f in files})
        log_access(root / "results" / "access_log.jsonl",
                   {"event": "trip_gallery", "split": split, "authorization": auths[split],
                    "files": {f: sources[f] for f in files}})
        points = (load_test if split == "test" else load_validation)(root)
        if set(points["id"]) != manifest_ids(root, split):
            raise ValueError(f"As viagens lidas não são as do '{split}' no manifesto.")
        values = trip_values(points, spec["rows"])
        checked[split] = verify(values, *saved_values(root, split))
        data[split] = {"values": values, "points": points.groupby("id").size().to_dict()}
        frames[split] = points
    # Só se escreve depois de todas as conferências passarem.
    out, images = root / "viagens", {}
    for split, points in frames.items():
        folder = out / SETS[split]["dir"]
        folder.mkdir(parents=True, exist_ok=True)
        for trip_id, trip in points.groupby("id", sort=False):
            path = folder / f"{trip_id}.png"
            draw_trip(trip, SETS[split]["rows"], trip_id, path)
            images[str(path.relative_to(root))] = sha256_of(path)
    (out / "README.md").write_text(markdown(data), encoding="utf-8")
    info = {"criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "comando": "iach-ais-venv-4/bin/python -m ais.cli.build_trip_gallery", "git": _git(root),
            "versoes": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                        "matplotlib": matplotlib.__version__},
            "autorizacoes": auths, "filtro": {"tamanho_pontos": SIZE, "sigma": "tamanho/6", "limiar": THRESHOLD},
            "manifesto": {MANIFEST: sha256_of(root / MANIFEST)}, "fontes_sha256": sources,
            "valores_conferidos_com_resultados_gravados": checked, "imagens_sha256": images}
    (out / "proveniencia.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return info


def main() -> None:
    info = build()
    print(f"valores conferidos: {info['valores_conferidos_com_resultados_gravados']}; "
          f"imagens: {len(info['imagens_sha256'])}; página: viagens/README.md")


if __name__ == "__main__":
    main()
