# Projeto AIS

Segmentação de viagens AIS em pesca e navegação, com uma previsão por ponto, usando uma rede neuronal convolucional unidimensional (CNN 1D). A ordem é: pré-processamento; CNN 1D de referência sobre a viagem completa; janelamento com sobreposição e a mesma CNN 1D sobre janelas; pós-processamento temporal.

## Estrutura

- `AGENTS.md`: regras e instruções do projeto (fonte única).
- `CLAUDE.md`: instrução para o Claude Code ler o `AGENTS.md`.
- `PROGRESS.md`: registo de progresso, validações, decisões e pendentes.
- `REVISION_LOG.md`: registo das revisões de documentos, com ID e cor (REV-001 a REV-034).
- `docs/`: documentação do projeto, em quatro ficheiros (fundidos em REV-033).
  - `00_projeto_e_decisoes.md`: objetivo, decisões, marcos e política de acesso aos dados.
  - `01_dados_e_preparacao.md`: dicionário das colunas, unidades verificadas, entradas da CNN e preparação.
  - `02_cnn_viagem_completa.md`: CNN de referência (Marco 3), com o que já está implementado.
  - `03_cnn_janelamento.md`: CNN com janelas e sobreposição (Marco 4), ainda por implementar.
- `latex/`: proposta em LaTeX (`proposta_pt.tex`, reescrita a partir de `proposta_IAHC_DINIS_ROSA.pdf`), o PDF entregue ao professor (não se altera) e a bibliografia.
- `src/ais/`: todo o código do projeto (pacote `ais`, instalado em modo editável pelo `pyproject.toml`).
  - `phase1/`: biblioteca da fase 1 (sequências, scaler, CNN 1D, perda, treino, checkpoints, métricas).
  - `cli/`: programas executáveis, que se correm com `python -m ais.cli.<nome>`.
    - `create_split_manifest.py`: cria o manifesto de divisão por ID (seed 42, 70/15/15).
    - `check_units_train.py`: verifica unidades e convenções só com o conjunto de treino.
    - `verify_trip_count.py`: confirma o número de viagens (123) e a coincidência com o manifesto.
- `data/123_fishing_trajs_clean_{train,validation,test}.parquet`: bases limpas de cada conjunto (geradas, não versionadas).
- `manifests/`: manifesto da divisão por ID, `split_manifest_seed42.csv` (versionado).
- `results/`: saídas geradas (gráficos e sumários). Não versionados.
- `data/`: dataset local (`123_fishing_trajs.csv`). Não versionado.
- `requirements.txt`: dependências com versões fixas.
- `iach-ais-venv-4/`: ambiente Python local (venv). Não versionado.

## Ambiente

Criar e instalar (Linux/macOS):

```bash
python3 -m venv iach-ais-venv-4
iach-ais-venv-4/bin/python -m pip install -r requirements.txt
iach-ais-venv-4/bin/python -m pip install -e . --no-build-isolation --no-deps   # torna `ais` importável (só no venv)
```

## Programas (`src/ais/cli/`)

Executar a partir da raiz do projeto:

```bash
iach-ais-venv-4/bin/python -m ais.cli.create_split_manifest
iach-ais-venv-4/bin/python -m ais.cli.check_units_train
iach-ais-venv-4/bin/python -m ais.cli.verify_trip_count
```

- `create_split_manifest.py` cria `manifests/split_manifest_seed42.csv`.
- `check_units_train.py` gera gráficos e um `summary.json` em `results/units_check_train/`, usando só o conjunto de treino.
- `verify_trip_count.py` confirma 123 viagens e que o manifesto coincide com o ficheiro.
- `count_anomalies_train.py`: conta saltos (acima de 30 nós) e inversões de rumo (acima de 170°) por viagem, só no treino. Saídas em `results/anomalies_train/`.
- `tests/`: testes sintéticos (dados inventados; um teste lê 3 viagens de treino). Executar: `iach-ais-venv-4/bin/python -m pytest tests/`.
- `build_clean_dataset.py --split train|validation|test`: constrói a base limpa (Parquet) de cada conjunto, com target 0/1 e grandezas recalculadas. Por defeito, treino.

## Estado

Marco 2 (preparação auditável) fechado (REV-019). Marco 3 (CNN 1D de referência sobre viagem completa) em curso: sequências, normalização, CNN, treino com paragem antecipada e checkpoints implementados e testados em `src/ais/phase1/` (REV-024, REV-032); primeira execução de treino feita só com o treino oficial, com resultados provisórios. Janelamento (Marco 4) por fazer. Validação e teste oficiais por abrir. Ver `PROGRESS.md` e `handoff.md`.
