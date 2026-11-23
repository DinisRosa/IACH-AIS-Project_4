# PROGRESS — Projeto AIS

Registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual

- **Marco atual:** 1 — Ambiente, consolidação e divisão mínima por ID.
- **Código de dados:** ainda não existe.
- **Dados:** `data/123_fishing_trajs.csv` presente localmente, não versionado. Só foi lido o cabeçalho e a primeira linha. Nenhuma estatística ou divisão foi calculada.
- **Divisão por ID (manifesto):** não criada.
- **Conjuntos de validação e teste:** bloqueados. Não foram abertos.

## Entradas do registo

### 2026-11-23 — Ambiente e documentação de arranque

**Feito**
- Leitura integral de `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore`, `docs/00` a `docs/03`, cabeçalhos de `docs/04` a `docs/06` e `latex/proposta_pt.tex`.
- Criado o ambiente `iach-ais-venv-4/` com `python3 -m venv` (Python 3.14.4, `/usr/bin/python3`). Python global não alterado.
- Instaladas dependências mínimas no `iach-ais-venv-4/` a partir do `requirements.txt`: `numpy`, `pandas`, `pytest` e `torch` em CPU (índice `https://download.pytorch.org/whl/cpu`).
- Um primeiro ambiente chamado `.venv/` foi criado por engano, sem nome indicado pelo utilizador. Substituído por `iach-ais-venv-4/` e removido.
- Criado `requirements.txt` com versões fixas.
- Criado este `PROGRESS.md`.

**Validado**
- `iach-ais-venv-4/bin/python --version` → Python 3.14.4.
- Instalação limpa de `requirements.txt` na `iach-ais-venv-4/` concluída sem erros.
- Importação de `numpy 2.5.5`, `pandas 3.1.1`, `torch 2.15.0+cpu`, `pytest 9.2.0`.
- `torch.cuda.is_available()` → `False` (esperado: GPU integrada, começar em CPU).

**Não validado / não feito**
- Nenhum teste de código do projeto (ainda não existe código).
- `requirements.txt` ainda não foi testado numa instalação limpa a partir do zero.

**Problemas**
- O `.gitignore` tinha `.venv/` e `venv/`, mas não cobria `iach-ais-venv-4/`. Acrescentada a linha `iach-ais-venv-4/`.

**Decisões**
- Ambiente em `iach-ais-venv-4/` com venv+pip. Conda não usado (AGENTS.md §4). Nome indicado pelo utilizador, com `-4` no fim, em minúsculas.
- Torch apenas em CPU, sem CUDA (AGENTS.md §4).
- Versões fixas em `requirements.txt` para reprodutibilidade (AGENTS.md §4).

## Pendentes (por marco, segundo `docs/00_5`)

### Marco 1 — Ambiente, consolidação e divisão mínima
- [x] Ambiente `iach-ais-venv-4/` criado.
- [x] Dependências mínimas instaladas e versões registadas.
- [x] `requirements.txt` criado e testado numa instalação limpa.
- [x] `PROGRESS.md` criado.
- [ ] Commit local destes ficheiros.
- [ ] Criar `split_manifest` (id → split) com seed e proporções fixas (~70/15/15), lendo apenas a coluna `id`.
- [ ] Materializar ficheiros separados por conjunto, sem exploração.
- [ ] Verificar invariantes estruturais: IDs sem interseção, atribuição única, conservação de linhas.
- [ ] Criar o isolamento: `run_preparation` com `allowed_splits=["train"]` por defeito.

### Marco 2 — Preparação auditável (só treino/sintéticos)
- [ ] Recálculo de `time_gap_calc_s`, `distance_gap_calc_m` e `speed_calc_mps`.
- [ ] Confirmar no treino as unidades de `distance_gap`, `euc_speed` e `signed_turn`.
- [ ] Limpeza com auditoria e limites IQR só no treino.
- [ ] Codificação de rótulos (`target`) e features (`speed_calc_mps`, `signed_turn`, `time_gap_calc_s`, `distanceToShore`).
- [ ] Testes com dados sintéticos (gaps, janelas, máscaras, alinhamento).
- [ ] Pedir revisão antes de avançar.

### Marco 3 a 7
Ver `docs/00_5_orientacoes_execucao_decisoes.md`.

## Pendências de decisão (perguntar ao utilizador)

- Overlaps 0% e 50% prioritários, ou os quatro obrigatórios?
- Unidade, largura e bordas do pós-processamento simples (aprovação).
- Orçamento de tempo para execuções longas (AGENTS.md §2).
- Unidades e CRS de `x/y`, `distance_gap`, `distanceToShore`, `signed_turn` e `euc_speed` (hipótese: nós).
- Fuso horário de `t`.

## Artefactos ainda por criar

- `REVISION_LOG.md` (AGENTS.md §8): ainda não existe, porque ainda não há revisões de documentos. Criar quando houver primeira revisão logada.
- Manifesto de divisão por ID.
- Código fonte e testes.
