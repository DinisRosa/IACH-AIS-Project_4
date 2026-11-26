# Investigação de agentes: comparação dos fluxos de trabalho

[REV-084 | cor #1F4E79] [REV-085 | cor #3C3C3C: texto do documento a preto]

Estudo de como o projeto AIS foi feito com agentes de IA ao longo de quatro tentativas
(quatro repositórios GitHub), para recomeçar bem no próximo projeto.

**Documento:** [`comparacao_workflows.pdf`](comparacao_workflows.pdf) (18 páginas; fonte em
`comparacao_workflows.tex`). Gerado com IA (Claude Code), como declarado no próprio documento.

| Pasta / ficheiro | O que é |
|---|---|
| `comparacao_workflows.tex` / `.pdf` | O documento: as quatro tentativas, comparação por eixos, balanço, lições e kit |
| `kit/` | Modelos prontos a copiar: `AGENTS_modelo.md`, `handoff_modelo.md`, `PROGRESS_modelo.md`, `checklist_arranque.md` |
| `scripts/metricas_git.py` | Lê clones dos quatro repositórios (só leitura) e gera `gerado/` |
| `gerado/` | `metricas.json`, `metricas.tex` (macros usadas no documento) e as três figuras; não editar à mão |

## Regenerar

```bash
git clone https://github.com/DinisRosa/IACH-AIS-Project.git /tmp/r/P1
git clone https://github.com/DinisRosa/IACH-AIS-Project_2.git /tmp/r/P2
git clone https://github.com/DinisRosa/IACH-AIS-Project_3.git /tmp/r/P3
git clone https://github.com/DinisRosa/IACH-AIS-Project_4.git /tmp/r/P4
iach-ais-venv-4/bin/python investigacao_agentes/scripts/metricas_git.py P1=/tmp/r/P1 P2=/tmp/r/P2 P3=/tmp/r/P3 P4=/tmp/r/P4
cd investigacao_agentes && pdflatex comparacao_workflows.tex && pdflatex comparacao_workflows.tex
```

Os auxiliares do LaTeX não se versionam; apagar depois de compilar (ou compilar com
`-output-directory=build` e copiar o PDF).
