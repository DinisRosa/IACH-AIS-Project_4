# Projeto AIS

Segmentação de viagens AIS em pesca e navegação, com uma previsão por ponto, usando redes neuronais convolucionais (CNN).

## Estrutura

- `AGENTS.md`: regras e instruções do projeto (fonte única).
- `CLAUDE.md`: instrução para o Claude Code ler o `AGENTS.md`.
- `PROGRESS.md`: registo de progresso, validações, decisões e pendentes.
- `REVISION_LOG.md`: registo das revisões de documentos, com ID e cor (REV-001 a REV-007).
- `docs/`: contexto, preparação comum, especificações e funções das CNN.
  - `00_contexto_projeto_dicionario_dados.md`: ponto de entrada e dicionário das colunas.
  - `00_5_orientacoes_execucao_decisoes.md`: decisões consolidadas e marcos.
  - `01_preparacao_comum.md` a `06_…`: preparação, CNN com viagem completa e CNN com janelas.
- `latex/`: proposta em LaTeX (`proposta_pt.tex`, reescrita a partir de `proposta_IAHC_DINIS_ROSA.pdf`), o PDF entregue ao professor (não se altera) e a bibliografia.
- `scripts/`: scripts executáveis do projeto.
  - `create_split_manifest.py`: cria o manifesto de divisão por ID (seed 42, 70/15/15).
  - `check_units_train.py`: verifica unidades e convenções só com o conjunto de treino.
  - `verify_trip_count.py`: confirma o número de viagens (123) e a coincidência com o manifesto.
- `data/123_fishing_trajs_clean_train.parquet`: base limpa do treino (gerada, não versionada).
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
```

## Scripts

Executar a partir da raiz do projeto:

```bash
iach-ais-venv-4/bin/python scripts/create_split_manifest.py
iach-ais-venv-4/bin/python scripts/check_units_train.py
iach-ais-venv-4/bin/python scripts/verify_trip_count.py
```

- `create_split_manifest.py` cria `manifests/split_manifest_seed42.csv`.
- `check_units_train.py` gera gráficos e um `summary.json` em `results/units_check_train/`, usando só o conjunto de treino.
- `verify_trip_count.py` confirma 123 viagens e que o manifesto coincide com o ficheiro.
- `build_clean_dataset.py`: constrói a base limpa (Parquet) só com o treino, com target 0/1 e grandezas recalculadas.

## Estado

Marco 1 (ambiente e divisão por ID) em curso. Ver `PROGRESS.md`.
