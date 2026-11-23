# Projeto AIS

Segmentação de viagens AIS em pesca e navegação, com uma previsão por ponto, usando uma rede neuronal convolucional unidimensional (CNN 1D). A ordem é: pré-processamento; CNN 1D de referência sobre a viagem completa (feita e fechada); a mesma CNN 1D sobre janelas com sobreposição (por começar); pós-processamento temporal (só se as janelas ajudarem).

## Estado

- **Marcos 1 a 3 fechados.** A CNN de referência (viagem completa) foi treinada só com o treino oficial (87 viagens, 300 épocas) e congelada: época 162 e limiar 0,65, escolhidos no conjunto `test` numa só ronda (REV-038, REV-041). Os números estão em `results/baseline_frozen/final_results.json` e, no relatório, em macros geradas por código.
- **Marco 4 (janelamento com a mesma CNN) por começar:** só há decisões (L = 64; sobreposição de 0 % e 50 %) e a ferramenta de medição por segmento.
- Conjuntos reservados: o `test` serve para selecionar e foi aberto uma só vez; o `validation` é a medição final e **nunca foi aberto**.
- 145 testes sintéticos a passar. Ver `PROGRESS.md` (estado e histórico) e `handoff.md` (para retomar numa nova sessão).

## Estrutura

- `AGENTS.md`: regras e instruções do projeto (fonte única). `CLAUDE.md`: manda ler o `AGENTS.md`.
- `PROGRESS.md`: estado, decisões, pendentes e histórico por entrada. `REVISION_LOG.md`: revisões dos documentos, com ID e cor (REV-001 a REV-044). `handoff.md`: ponto de situação para outra sessão.
- `docs/`: documentação, em quatro ficheiros.
  - `00_projeto_e_decisoes.md`: objetivo, decisões, marcos e política de acesso aos dados.
  - `01_dados_e_preparacao.md`: dicionário das colunas, unidades verificadas, entradas da CNN e preparação.
  - `02_cnn_viagem_completa.md`: a CNN de referência (Marco 3), o que está implementado e o estado.
  - `03_cnn_janelamento.md`: contratos do Marco 4 (janelas e sobreposição), ainda por implementar.
- `src/ais/`: todo o código (pacote `ais`, instalado em modo editável pelo `pyproject.toml`).
  - `phase1/`: biblioteca (dados e sequências, normalizador, CNN 1D, treino, checkpoints, inferência, métricas, segmentos, acesso aos conjuntos reservados, critérios de seleção).
  - `cli/`: programas, que se correm com `python -m ais.cli.<nome>` (ver abaixo).
- `tests/`: testes sintéticos (um lê 3 viagens de treino).
- `configs/`: configurações do treino, protocolo de seleção e autorizações (`authorizations/`).
- `latex/`: proposta (`proposta_pt.tex`, `references.bib`, `figures/`, `generated/resultados.tex` com as macros geradas) e o PDF entregue ao professor (`proposta_IAHC_DINIS_ROSA.pdf`, não se altera).
- `manifests/`: divisão por ID, `split_manifest_seed42.csv` (versionado).
- `data/` e `results/`: dados e resultados gerados. **Não versionados.**
- `requirements.txt`: dependências com versões fixas. `iach-ais-venv-4/`: ambiente local (não versionado).

## Ambiente

```bash
python3 -m venv iach-ais-venv-4
iach-ais-venv-4/bin/python -m pip install -r requirements.txt
iach-ais-venv-4/bin/python -m pip install -e . --no-build-isolation --no-deps   # torna `ais` importável (só no venv)
```

## Programas (`src/ais/cli/`)

Executar a partir da raiz do projeto, por exemplo `iach-ais-venv-4/bin/python -m ais.cli.verify_trip_count`.

| Programa | O que faz |
|---|---|
| `create_split_manifest` | Cria o manifesto de divisão por ID (seed 42, 70/15/15). |
| `verify_trip_count` | Confirma as 123 viagens e que o manifesto coincide com o ficheiro. |
| `check_units_train` | Verifica unidades e convenções só com o treino. |
| `build_clean_dataset --split train\|validation\|test` | Constrói a base limpa (Parquet) de cada conjunto, com `target` 0/1 e grandezas recalculadas. |
| `count_anomalies_train` | Conta saltos (acima de 30 nós) e inversões de rumo (acima de 170°) por viagem, só no treino. |
| `run_phase1_training <config>` | Treina a CNN 1D só com o treino oficial. |
| `select_on_test` | Seleção da época e do limiar no `test`: **uma só ronda**, com autorização e registo de acessos. |
| `freeze_baseline` | Congela a baseline escolhida (checkpoint com hash). |
| `build_final_results` | Gera `final_results.json`, as macros `latex/generated/resultados.tex` e as figuras `latex/figures/final_*.png`. |
| `segment_metrics <previsões.csv>` | Extrai segmentos (sem suavizar) e calcula métricas por segmento. |
| `count_shared_vessels` | Conta navios partilhados entre conjuntos (só lê o manifesto). |
| `plot_phase1_run`, `benchmark_training_speed`, `diagnostic_fit_3_trips`, `plot_diagnostic_3trips` | Figuras e medições de execuções antigas; sem uso no relatório. |

Testes: `iach-ais-venv-4/bin/python -m pytest tests/`.
