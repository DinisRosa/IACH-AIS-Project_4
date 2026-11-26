"""A galeria de viagens em LaTeX e PDF (REV-077), a partir da página `viagens/README.md`.

Converte a página gerada por `build_trip_gallery` (mesmos textos, tabelas e imagens) e compila-a. Não lê
previsões, resultados nem dados: só a página e as imagens já versionadas. Conhece apenas o formato dessa
página; uma construção que não reconheça pára a conversão, para nada se perder em silêncio. Escreve:
  - viagens/galeria_viagens.tex e viagens/galeria_viagens.pdf

Execução (a partir da raiz do projeto, depois de `build_trip_gallery`; precisa de `pdflatex`):
    iach-ais-venv-4/bin/python -m ais.cli.build_trip_gallery_pdf
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / "viagens"
NAME = "galeria_viagens"
NEW_PAGE = {"Teste": "teste", "Validação": "validacao"}  # secções que começam numa página nova, e a sua âncora
BACK = "[Voltar ao topo]"

PREAMBLE = r"""% Gerado por ais.cli.build_trip_gallery_pdf a partir de viagens/README.md. NÃO EDITAR À MÃO.
% Compilar a partir de viagens/.
\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[hmargin=2cm,vmargin=1.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage[hidelinks]{hyperref}
% Sem padrões de hifenização portugueses: não partir palavras.
\hyphenpenalty=10000
\exhyphenpenalty=10000
\emergencystretch=3em
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
"""
AUTHOR = r"Dinis Soveral Botelho Rosa\\University of Coimbra / Department of Informatics Engineering"


def escape(text: str) -> str:
    text = re.sub(r"([&%#_$])", r"\\\1", text)
    return text.replace(" \\%", "\\,\\%").replace("·", r"\textperiodcentered{}")


def inline(text: str) -> str:
    """Ligações, negrito, itálico e código de uma linha."""
    out = []
    for i, part in enumerate(re.split(r"(\[[^\]]*\]\([^)]*\))", text)):
        if i % 2:
            label, url = re.fullmatch(r"\[([^\]]*)\]\(([^)]*)\)", part).groups()
            if url.startswith("#"):
                out.append(rf"\hyperlink{{{url[1:]}}}{{{inline(label)}}}")
            elif url.startswith("http"):
                out.append(rf"\href{{{url}}}{{{inline(label)}}}")
            else:  # ficheiro do repositório: no PDF fica só o texto
                out.append(inline(label))
            continue
        part = escape(part)
        part = re.sub(r"`([^`]*)`", r"\\texttt{\1}", part)
        part = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", part)
        out.append(re.sub(r"\*([^*]+)\*", r"\\emph{\1}", part))
    return "".join(out)


def table(rows: list[str]) -> list[str]:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, rule, body = cells[0], cells[1], cells[2:]
    spec = ["r" if r.endswith(":") else "l" for r in rule]
    for k in range(len(spec)):  # colunas com frases longas passam a parágrafo
        if max(len(row[k]) for row in body) > 60:
            spec[k] = r"p{0.62\linewidth}"
    line = lambda row: " & ".join(inline(c) for c in row) + r" \\"
    return [r"{\centering\small", rf"\begin{{tabular}}{{{''.join(spec)}}}", r"\toprule", line(header), r"\midrule",
            *[line(r) for r in body], r"\bottomrule", r"\end{tabular}\par}"]


def to_latex(page: str) -> str:
    lines, out, title, i, in_trip = page.split("\n"), [], None, 0, False
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith(("<!--", '<a id="')):
            out.append("")
        elif line.startswith("# "):
            title = inline(line[2:])
        elif line.startswith("## "):
            name = line[3:]
            if name in NEW_PAGE:
                out += [r"\clearpage", rf"\hypertarget{{{NEW_PAGE[name]}}}{{}}"]
            out.append(rf"\section*{{{inline(name)}}}")
        elif line.startswith("### "):
            trip = line[4:]
            in_trip = True  # título, imagem e tabela ficam na mesma página
            out += [r"\par\smallskip\noindent\begin{minipage}{\linewidth}\setlength{\parskip}{3pt}",
                    rf"\hypertarget{{{trip}}}{{}}\textbf{{\large {inline(trip)}}}\par"]
        elif line.startswith(BACK):
            if not in_trip:
                raise ValueError("«Voltar ao topo» fora de uma viagem.")
            in_trip = False
            out += [r"\end{minipage}", r"\par"]
        elif m := re.fullmatch(r"!\[[^\]]*\]\(([^)]+)\)", line):
            out.append(rf"{{\centering\includegraphics[width=0.9\linewidth]{{{m.group(1)}}}\par}}")
        elif line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            out += table(block)
            continue
        elif line.startswith("- "):
            out.append(r"\begin{itemize}")
            while i < len(lines) and lines[i].startswith("- "):
                out.append(r"\item " + inline(lines[i][2:]))
                i += 1
            out.append(r"\end{itemize}")
            continue
        elif line.startswith(("<", ">", "```", "    ", "####")):
            raise ValueError(f"Construção não prevista na linha {i + 1}: {line[:60]}")
        else:
            # a lista de viagens não se justifica, para não abrir espaços largos
            text = inline(line)
            out += [rf"{{\raggedright {text}\par}}\medskip" if line.startswith("Viagens:") else text, ""]
        i += 1
    if title is None or in_trip:
        raise ValueError("A página não tem título ou tem uma viagem por fechar.")
    head = [PREAMBLE, rf"\title{{{title}}}", rf"\author{{{AUTHOR}}}", r"\date{}", r"\begin{document}", r"\maketitle"]
    return re.sub(r"\n{3,}", "\n\n", "\n".join([*head, *out, r"\end{document}", ""]))


def compile_pdf(folder: Path) -> Path:
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error"]
    with tempfile.TemporaryDirectory() as tmp:
        for _ in range(2):  # a segunda passagem resolve as ligações internas
            run = subprocess.run([*command, f"-output-directory={tmp}", f"{NAME}.tex"], cwd=folder,
                                 capture_output=True, text=True, errors="replace")
            if run.returncode != 0:
                raise RuntimeError("O pdflatex falhou:\n" + run.stdout[-2000:])
        return Path(shutil.copy(Path(tmp) / f"{NAME}.pdf", folder / f"{NAME}.pdf"))


def main() -> None:
    source = (FOLDER / "README.md").read_text(encoding="utf-8")
    (FOLDER / f"{NAME}.tex").write_text(to_latex(source), encoding="utf-8")
    print(f"escritos viagens/{NAME}.tex e {compile_pdf(FOLDER).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
