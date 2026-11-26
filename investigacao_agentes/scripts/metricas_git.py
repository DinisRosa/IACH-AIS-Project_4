"""Métricas do histórico git das quatro tentativas do projeto AIS (REV-084).

Lê clones locais (só leitura) e grava, em investigacao_agentes/gerado/:
  - metricas.json   todos os números usados no documento, com o comando de origem;
  - metricas.tex    macros LaTeX com esses números (não editar à mão);
  - fig_*.pdf       gráficos usados no documento.

Uso (a partir da raiz do projeto):
  iach-ais-venv-4/bin/python investigacao_agentes/scripts/metricas_git.py \
      P1=<clone IACH-AIS-Project> P2=<clone _2> P3=<clone _3> P4=<clone _4>

Só usa comandos git de leitura; não altera os clones.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "gerado"
# Paleta categórica por defeito (ordem fixa, validada para daltonismo).
COLORS = {"P1": "#2a78d6", "P2": "#eb6834", "P3": "#1baf7a", "P4": "#eda100"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md")
BOOKKEEPING = {"PROGRESS.md", "REVISION_LOG.md", "handoff.md", "README.md"}

CATEGORIES = [
    ("Código", lambda p: p.endswith((".py", ".ipynb", ".sh", ".r", ".R")) and not is_test(p)),
    ("Testes", lambda p: is_test(p)),
    ("Documentação (.md)", lambda p: p.endswith(".md")),
    ("LaTeX/bibliografia", lambda p: p.endswith((".tex", ".bib", ".sty", ".bst", ".cls"))),
    ("Figuras e PDF", lambda p: p.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".pdf", ".gif"))),
    ("Dados", lambda p: p.lower().endswith((".csv", ".parquet", ".npz", ".npy", ".pkl", ".xlsx", ".zip"))),
]


def is_test(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return path.endswith(".py") and ("tests/" in path or name.startswith("test_"))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True).stdout


def default_branch(repo: Path) -> str:
    ref = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
    return ref or "HEAD"


def categorize(paths: list[str]) -> dict[str, int]:
    counts = Counter()
    for p in paths:
        for name, rule in CATEGORIES:
            if rule(p):
                counts[name] += 1
                break
        else:
            counts["Outros"] += 1
    return {name: counts.get(name, 0) for name, _ in CATEGORIES} | {"Outros": counts.get("Outros", 0)}


def count_lines(repo: Path, rev: str, paths: list[str]) -> int:
    total = 0
    for p in paths:
        try:
            total += git(repo, "show", f"{rev}:{p}").count("\n")
        except subprocess.CalledProcessError:
            pass
    return total


def instruction_history(repo: Path, rev: str) -> dict[str, list[tuple[str, int]]]:
    """Número de linhas de cada ficheiro de instruções em cada commit que o alterou."""
    history = {}
    for f in INSTRUCTION_FILES:
        log = git(repo, "log", rev, "--format=%H %cI", "--", f).split("\n")
        points = []
        for line in reversed([x for x in log if x]):
            sha, date = line.split(" ", 1)
            try:
                n = git(repo, "show", f"{sha}:{f}").count("\n")
            except subprocess.CalledProcessError:
                n = 0  # ficheiro apagado nesse commit
            points.append((date, n))
        if points:
            history[f] = points
    return history


def repo_metrics(repo: Path) -> dict:
    branch = default_branch(repo)
    commits = [l.split("\x1f") for l in
               git(repo, "log", "--all", "--format=%H\x1f%cI\x1f%an\x1f%B\x1e").split("\x1e")
               if l.strip()]
    commits = [(c[0].strip(), c[1], c[2], c[3]) for c in commits]
    dates = sorted(datetime.fromisoformat(c[1]) for c in commits)
    days = Counter(d.astimezone(timezone.utc).date().isoformat() for d in dates)
    trailers = Counter()
    for _, _, _, body in commits:
        for line in body.splitlines():
            if line.lower().startswith("co-authored-by:"):
                trailers[line.split(":", 1)[1].split("<")[0].strip()] += 1
    files_main = [p for p in git(repo, "ls-tree", "-r", "--name-only", branch).split("\n") if p]
    files_all = set()
    branches = [b.strip() for b in git(repo, "branch", "-r", "--format=%(refname:short)").split("\n")
                if b.strip() and not b.strip().endswith("/HEAD") and b.strip() != "origin"]
    for b in branches:
        files_all.update(p for p in git(repo, "ls-tree", "-r", "--name-only", b).split("\n") if p)
    # Commits que só tocam em ficheiros de registo (PROGRESS, REVISION_LOG, handoff, README).
    bookkeeping_only = 0
    md_only = 0
    rev_mentions = 0
    for sha, _, _, body in commits:
        touched = [p for p in git(repo, "show", "--format=", "--name-only", sha).split("\n") if p]
        if touched and all(p.rsplit("/", 1)[-1] in BOOKKEEPING for p in touched):
            bookkeeping_only += 1
        if touched and all(p.endswith(".md") for p in touched):
            md_only += 1
        if "REV-" in body:
            rev_mentions += 1
    py = [p for p in files_main if p.endswith(".py")]
    md = [p for p in files_main if p.endswith(".md")]
    tests = [p for p in files_main if is_test(p)]
    test_funcs = sum(git(repo, "show", f"{branch}:{p}").count("\ndef test_") for p in tests)
    return {
        "default_branch": branch,
        "branches": branches,
        "commits_all_branches": len(commits),
        "first_commit": dates[0].isoformat(),
        "last_commit": dates[-1].isoformat(),
        "active_days": len(days),
        "commits_per_day": dict(sorted(days.items())),
        "authors": dict(Counter(c[2] for c in commits)),
        "co_author_trailers": dict(trailers),
        "commits_bookkeeping_only": bookkeeping_only,
        "commits_md_only": md_only,
        "commits_mentioning_rev": rev_mentions,
        "files_default_branch": len(files_main),
        "files_all_branches": len(files_all),
        "categories_all_branches": categorize(sorted(files_all)),
        "py_lines_default_branch": count_lines(repo, branch, [p for p in py if not is_test(p)]),
        "test_py_lines_default_branch": count_lines(repo, branch, tests),
        "test_functions_default_branch": test_funcs,
        "md_lines_default_branch": count_lines(repo, branch, md),
        "instruction_files_history": instruction_history(repo, "--all"),
        "commit_dates": [d.isoformat() for d in dates],
    }


def style(ax, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def fig_cumulative(metrics: dict) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.3), sharey=False)
    for ax, (key, m) in zip(axes, metrics.items()):
        d = [datetime.fromisoformat(x) for x in m["commit_dates"]]
        ax.step(d, range(1, len(d) + 1), where="post", color=COLORS[key], linewidth=2)
        style(ax, f"{key} ({len(d)} commits)")
        ax.set_xticks([d[0], d[0] + (d[-1] - d[0]) / 2, d[-1]])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True, nbins=4))
    axes[0].set_ylabel("commits acumulados", fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(OUT / "fig_commits_acumulados.pdf")
    plt.close(fig)


def fig_agents(metrics: dict) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for key, m in metrics.items():
        pts = m["instruction_files_history"].get("AGENTS.md")
        if not pts:
            continue
        d = [datetime.fromisoformat(x) for x, _ in pts]
        n = [y for _, y in pts]
        ax.step(d, n, where="post", color=COLORS[key], linewidth=2, label=key)
        ax.plot(d, n, "o", color=COLORS[key], markersize=3)
        ax.annotate(key, (d[-1], n[-1]), xytext=(4, 0), textcoords="offset points",
                    fontsize=8, color=INK, va="center")
    style(ax, "Linhas do AGENTS.md em cada commit que o alterou")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_agents_md.pdf")
    plt.close(fig)


def fig_composition(metrics: dict) -> None:
    names = [n for n, _ in CATEGORIES] + ["Outros"]
    shades = ["#1f5fa8", "#5b9be0", "#9aa3ad", "#c9a227", "#d98c6a", "#7a5c99", "#d9d8d3"]
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    keys = list(metrics)
    for i, key in enumerate(keys):
        cats = metrics[key]["categories_all_branches"]
        total = sum(cats.values()) or 1
        left = 0.0
        for name, color in zip(names, shades):
            w = 100 * cats[name] / total
            ax.barh(i, w, left=left, color=color, edgecolor="white", linewidth=1.5,
                    label=name if i == 0 else None)
            if w >= 7:
                ax.text(left + w / 2, i, f"{cats[name]}", ha="center", va="center",
                        fontsize=7, color="white" if name not in ("Outros",) else INK)
            left += w
    ax.set_yticks(range(len(keys)), [f"{k} ({sum(metrics[k]['categories_all_branches'].values())})"
                                      for k in keys])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("% dos ficheiros versionados (todas as branches; número dentro da barra)",
                  fontsize=8, color=INK2)
    style(ax, "Composição dos repositórios por tipo de ficheiro")
    ax.grid(False)
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.32))
    fig.tight_layout()
    fig.savefig(OUT / "fig_composicao.pdf")
    plt.close(fig)


def write_macros(metrics: dict) -> None:
    roman = {"P1": "Um", "P2": "Dois", "P3": "Tres", "P4": "Quatro"}
    lines = ["% Gerado por investigacao_agentes/scripts/metricas_git.py (REV-084). Não editar."]
    for key, m in metrics.items():
        r = roman[key]
        first = datetime.fromisoformat(m["first_commit"]).strftime("%d/%m/%Y")
        last = datetime.fromisoformat(m["last_commit"]).strftime("%d/%m/%Y")
        agents = m["instruction_files_history"].get("AGENTS.md", [])
        vals = {
            "Commits": m["commits_all_branches"], "Dias": m["active_days"],
            "Branches": len(m["branches"]), "Primeiro": first, "Ultimo": last,
            "Ficheiros": m["files_all_branches"], "LinhasPy": m["py_lines_default_branch"],
            "LinhasTestes": m["test_py_lines_default_branch"],
            "FuncTestes": m["test_functions_default_branch"],
            "LinhasMd": m["md_lines_default_branch"],
            "Registo": m["commits_bookkeeping_only"], "ComRev": m["commits_mentioning_rev"],
            "AgentsVersoes": len(agents), "AgentsLinhas": agents[-1][1] if agents else 0,
            "CoAutor": sum(m["co_author_trailers"].values()),
            "CoAutorCopilot": sum(v for k, v in m["co_author_trailers"].items() if "Copilot" in k),
            "CoAutorHaiku": sum(v for k, v in m["co_author_trailers"].items() if "Haiku" in k),
            "CoAutorSonnet": sum(v for k, v in m["co_author_trailers"].items() if "Sonnet" in k),
            "CoAutorOpus": sum(v for k, v in m["co_author_trailers"].items() if "Opus" in k),
            "SoMd": m["commits_md_only"],
            "AgentsPrimeiro": agents[0][1] if agents else 0,
        }
        for name, v in vals.items():
            lines.append(f"\\newcommand{{\\m{r}{name}}}{{{v}}}")
    (OUT / "metricas.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    repos = dict(a.split("=", 1) for a in argv)
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = {k: repo_metrics(Path(v)) for k, v in sorted(repos.items())}
    for k, v in sorted(repos.items()):
        metrics[k]["head"] = git(Path(v), "rev-parse", "--short", metrics[k]["default_branch"]).strip()
    meta = {
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "comando": "iach-ais-venv-4/bin/python investigacao_agentes/scripts/metricas_git.py "
                   "P1=<clone> P2=<clone> P3=<clone> P4=<clone>",
        "fontes": {k: f"https://github.com/DinisRosa/IACH-AIS-Project{'' if k == 'P1' else '_' + k[1]}"
                   for k in metrics},
        "notas": "Commits contados em todas as branches remotas (git log --all). Linhas e testes "
                 "na branch por defeito. Categorias de ficheiros na união das branches.",
    }
    (OUT / "metricas.json").write_text(json.dumps({"meta": meta, "repos": metrics}, indent=1,
                                                  ensure_ascii=False), encoding="utf-8")
    fig_cumulative(metrics)
    fig_agents(metrics)
    fig_composition(metrics)
    write_macros(metrics)
    for k, m in metrics.items():
        print(k, m["head"], m["commits_all_branches"], "commits;", m["files_all_branches"], "ficheiros;",
              m["test_functions_default_branch"], "testes;", m["commits_bookkeeping_only"], "só registo")


if __name__ == "__main__":
    main(sys.argv[1:])
