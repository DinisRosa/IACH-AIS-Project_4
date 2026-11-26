# Projeto AIS

Segmentação de trajetórias AIS de navios de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma rede neuronal convolucional unidimensional (CNN 1D).

Para retomar o trabalho: ler `AGENTS.md` (regras) e `handoff.md` (ponto de situação).

## Viagens em imagens

**[Ver o que cada modelo previu em cada viagem](viagens/README.md)**: 18 viagens de teste (real, baseline, J0, J50 e baseline com pós-processamento) e 18 de validação (real, baseline e baseline com pós-processamento). A mesma galeria em PDF: [`viagens/galeria_viagens.pdf`](viagens/galeria_viagens.pdf).

## Estado

| Parte | Estado |
|---|---|
| Divisão por viagem e preparação | Feito |
| CNN baseline sobre a viagem completa | Fechada: época 162, limiar 0,65 |
| A mesma CNN sobre janelas (J0 sem sobreposição, J50 com 50 %) | Feito |
| Medição final no `validation` (só a baseline) | Feita, uma única abertura |
| Filtro temporal gaussiano de 301 pontos | Feito |
| Relatório `latex/relatorio_pt.tex` | Completo (10 páginas); falta a leitura do autor |

Os números estão no relatório (gerados por código) e em `PROGRESS.md`. Em resumo: as janelas não superam a viagem completa; o filtro reduz muito a fragmentação, numa medição que **não é independente**; a interação entre os dois (RQ3) fica sem resposta.

Conjuntos reservados: o `test` serve para **selecionar** e o `validation` para a **medição final** (papéis trocados face ao habitual). O `validation` está gasto. Qualquer novo acesso a um deles exige autorização explícita (`AGENTS.md` §3).

Testes: 256 a passar (`iach-ais-venv-4/bin/python -m pytest tests/`).

## Relatório

O PDF é gerado em `latex/build/relatorio_pt.pdf` (pasta não versionada). Para recompilar automaticamente a cada alteração, usar o vigilante local (não versionado):

```bash
bash latex/watch_latex.sh
```

O vigilante só reage a alterações em `relatorio_pt.tex` e `references.bib`; depois de gerar macros ou figuras, pará-lo (Ctrl+C) e iniciá-lo de novo. Para compilar uma só vez: `bash latex/watch_latex.sh --once`. Basta um vigilante a correr de cada vez.

À mão, a partir de `latex/`:

```bash
pdflatex -interaction=nonstopmode -output-directory=build relatorio_pt.tex
```

```bash
(cd build && BIBINPUTS=..: BSTINPUTS=..: bibtex relatorio_pt)
```

Depois, repetir o primeiro comando pelo menos três vezes, até o `.aux` deixar de mudar: com menos passagens, alguns números de linha aparecem entre as colunas. Os números do relatório vêm das macros em `latex/generated/`, que não se editam à mão.

## Proposta anterior

A proposta em LaTeX (`latex/proposta_pt.tex`) foi substituída pelo relatório e retirada da pasta. Ficam o PDF em `latex/proposta_pt.pdf` e, no git, a etiqueta **`proposta-pt-v1`** (commit `7d60861`) com a versão completa.

Ver a versão antiga, com todos os seus ficheiros, numa pasta à parte:

```bash
git worktree add ../proposta-pt-v1 proposta-pt-v1
```

Trazer de volta para o projeto só o ficheiro fonte antigo:

```bash
git restore --source=proposta-pt-v1 -- latex/proposta_pt.tex
```

Não repor a pasta `latex/` inteira a partir da etiqueta: o `references.bib` antigo não tem uma entrada que o relatório usa. Se a etiqueta faltar numa cópia do repositório, correr `git fetch --tags`.

## Documentos arquivados

Os documentos concluídos (`docs/02` a `docs/06`) saíram da pasta e estão no git, na etiqueta **`docs-historico-v1`**. Para ler um deles:

```bash
git show docs-historico-v1:docs/04_pos_processamento.md
```

## Estrutura

- `AGENTS.md`: regras do projeto (fonte única). `CLAUDE.md`: manda lê-las.
- `handoff.md`: ponto de situação para uma nova conversa.
- `PROGRESS.md`: estado, decisões, pendências e histórico. `REVISION_LOG.md`: revisões dos documentos, com ID e cor (REV-001 a REV-079).
- `docs/`:
  - `00_projeto_e_decisoes.md`: objetivo, decisões, marcos, modelos e protocolos, acesso aos dados e referências verificadas.
  - `01_dados_e_preparacao.md`: colunas, unidades, entradas da CNN e preparação.
  - `bibliografia/`: PDF dos artigos (local, não versionado).
- `src/ais/`: código (pacote `ais`): `phase1/` (biblioteca) e `cli/` (programas).
- `tests/`: testes com dados sintéticos (um lê 3 viagens de treino).
- `configs/`: configurações, protocolos e autorizações (`authorizations/`).
- `latex/`: `relatorio_pt.tex`, `references.bib`, `figures/`, `generated/`, o modelo IJCAI, `proposta_pt.pdf` (proposta anterior) e `proposta_IAHC_DINIS_ROSA.pdf` (entregue ao professor, não se altera).
- `manifests/`: divisão por viagem, `split_manifest_seed42.csv` (versionado).
- `viagens/`: galeria gerada por `build_trip_gallery` (página, uma imagem por viagem de teste e de validação e `proveniencia.json`) e a sua versão `galeria_viagens.tex` e `.pdf`, gerada por `build_trip_gallery_pdf`.
- `data/` e `results/`: dados e resultados. **Não versionados**: existem só na máquina do autor.
- `requirements.txt`: dependências com versões fixas. `iach-ais-venv-4/`: ambiente local.

## Ambiente

```bash
python3 -m venv iach-ais-venv-4
```

```bash
iach-ais-venv-4/bin/python -m pip install -r requirements.txt
```

```bash
iach-ais-venv-4/bin/python -m pip install -e . --no-build-isolation --no-deps
```

## Programas (`src/ais/cli/`)

Executar a partir da raiz, com `iach-ais-venv-4/bin/python -m ais.cli.<nome>`. Os marcados **não repetir** já abriram ou mediram um conjunto reservado.

| Programa | O que faz |
|---|---|
| `create_split_manifest` | Cria o manifesto de divisão por viagem (seed 42, 70/15/15). Não refazer. |
| `verify_trip_count` | Confirma as 123 viagens e o manifesto. |
| `check_units_train` | Verifica unidades e convenções no treino. |
| `build_clean_dataset --split train\|validation\|test` | Constrói a base limpa de cada conjunto. |
| `count_anomalies_train` | Conta saltos e inversões de rumo no treino. |
| `run_phase1_training <config>` | Treina a CNN sobre a viagem completa. |
| `select_on_test` | Escolhe época e limiar da baseline no `test`. **Não repetir.** |
| `freeze_baseline` | Congela a baseline escolhida. |
| `build_final_results` | Macros `resultados.tex` e figuras `final_*.png` (estas já não entram no relatório). |
| `run_window_training <config>` | Treina a CNN sobre janelas. |
| `select_windows_on_test` | Escolhe J0 e J50 no `test`. **Não repetir.** |
| `build_window_results [--report-figures-only]` | Macros `resultados_janelas.tex` e figuras `janelas_*`; com a opção, só as três figuras do relatório com o nome do modelo (`janelas_viagens_baseline`, `janelas_linha_temporal_baseline`, `janelas_perda`; exige a autorização `test_report_figures_baseline` e regista o acesso). |
| `final_validation` | Medição final no `validation`. **Não repetir.** |
| `build_validation_results [--worst-trip-figure-only]` | Macros e figuras da medição final, a partir de resultados guardados; com a opção, só a linha temporal da Figura 7 (exige a autorização `validation_report_figure_baseline` e regista a leitura). |
| `analyze_error_runs --split test\|train` | Blocos de erro (o `test` exige autorização). |
| `eval_postproc_test` | Efeito de várias janelas no `test` (exige autorização). |
| `postproc_validation --version <protocolo>` | Filtro sobre as previsões guardadas do `validation`. **Não repetir** (as duas versões já correram). |
| `build_postproc_results` | Macros e figuras do filtro, a partir de resultados guardados; `--first-version-only` gera só as macros da versão de 13 pontos e `--results-figure-only` só a figura dos segmentos e do F1. |
| `verify_postproc_independent [--size N] <csv>` | Segunda implementação das métricas do filtro. |
| `build_trip_gallery` | Galeria `viagens/` a partir das previsões guardadas do `test` e do `validation` (exige as autorizações `*_trip_gallery` e regista as leituras). Depois, correr `build_trip_gallery_pdf`. |
| `build_trip_gallery_pdf` | A galeria em LaTeX e PDF (`viagens/galeria_viagens.*`), a partir da página já gerada; não lê dados nem resultados; precisa de `pdflatex`. |
| `build_window_analysis_macros` | Macros dos blocos de erro (`resultados_buracos.tex`) a partir dos resumos guardados. |
| `plot_postprocessing_kernel` | Figura da janela gaussiana, com dados sintéticos. |
| `plot_trip_diagnostic <viagem>` | Diagnóstico de uma viagem do `test` (com `--xy`, exige autorização própria). |
| `segment_metrics <previsões.csv>` | Métricas por segmento. |
| `count_shared_vessels` | Navios partilhados entre conjuntos (só o manifesto). |
| `plot_phase1_run`, `benchmark_training_speed`, `diagnostic_fit_3_trips`, `plot_diagnostic_3trips` | Execuções antigas, sem uso no relatório. |
