# PROGRESS — Projeto AIS

Registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual

- **Marco atual:** 1 — Ambiente, consolidação e divisão mínima por ID.
- **Código de dados:** ainda não existe.
- **Dados:** `data/123_fishing_trajs.csv` presente localmente, não versionado. Só foi lido o cabeçalho e a primeira linha. Nenhuma estatística ou divisão foi calculada.
- **Divisão por ID (manifesto):** criada em `manifests/split_manifest_seed42.csv` (seed 42, 70/15/15). Ver entrada de 2026-11-23b.
- **Conjuntos de validação e teste:** bloqueados para desenvolvimento. Só foram usados IDs e contagens de linhas, nenhum valor de classe ou característica.

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

### 2026-11-23b — Manifesto de divisão por ID

**Decisões confirmadas pelo utilizador**
- Seed `42`.
- Proporções 70/15/15 (treino/validação/teste) por ID completo.
- Regra de arredondamento: validação e teste arredondados ao inteiro mais próximo; treino recebe o resto.
- Aceite um único script versionado, para cumprir AGENTS.md §10.

**Feito**
- Atualizados `docs/01_preparacao_comum.md` (§3) e `docs/00_contexto_projeto_dicionario_dados.md` (§15) com seed 42 e 70/15/15.
- Criado `scripts/create_split_manifest.py`. Lê só a coluna `id`. Conta linhas por ID, sem ler outros valores. Atribui cada ID com `random.Random(42)`. Valida e grava `manifests/split_manifest_seed42.csv`.
- Executado: `iach-ais-venv-4/bin/python scripts/create_split_manifest.py`.

**Resultados estruturais** (só contagens)
- IDs únicos: **123**. Linhas: **1 026 279**.
- Conjuntos (IDs): treino 87, validação 18, teste 18.
- Conjuntos (linhas): treino 713 854, validação 209 016, teste 103 409.

**Validado**
- Cada ID aparece em exatamente um conjunto (`dict` por ID, sem colisões).
- Conjuntos de IDs cobrem todos os IDs (`set` igual).
- Soma das linhas por conjunto = total de linhas.
- Reexecução: mesmo SHA-256 (`d56918bc65f9bebc6aa0a01a1e82213fda2404a9dfab9f39b3a1858c52733539`) do manifesto.

**Problemas e avisos**
- A proposta fala em **128 viagens**. O ficheiro tem **123 IDs únicos**. A diferença ainda não está explicada e fica por verificar com o utilizador. Não altero a divisão por isso.
- A validação (209 016) e o teste (103 409) têm proporções de linhas diferentes de 15%. É esperado, porque a divisão é por viagem e as viagens têm tamanhos diferentes. Não é um erro.
- Os 1 026 279 linhas ficam como contagem estrutural. Não confirmam ainda a proposta de ~1,03 M com precisão, mas são consistentes com ela.
- O manifesto `manifests/split_manifest_seed42.csv` **não é versionado**: a regra `*.csv` do `.gitignore` o exclui. É regenerável com o script e a seed 42 (SHA-256 acima). Decidir se deve ser versionado ou guardado de outra forma (pendente de decisão do utilizador).

**Pendente**
- Explicar a diferença 128 vs 123 IDs.
- Validar a instalação do `requirements.txt` (já feita, ver entrada anterior).
- Definir a estrutura de pacote e de testes quando começarem os marcos seguintes (ainda sem código).

### 2026-11-23c — REVISION_LOG, decisões e verificação de unidades

**Feito**
- Criado `REVISION_LOG.md` com REV-001 (seed/divisão), REV-002 (decisões de âmbito) e REV-003 (unidades).
- Decisões do utilizador registadas em REV-002: overlaps 0% e 50% prioritários; fuso horário ignorado.
- Criado `scripts/check_units_train.py`, que só usa o treino. Gera gráficos e `summary.json` em `results/units_check_train/` (ignorado pelo git).
- Adicionado `matplotlib==3.10.9` ao `requirements.txt` (necessário para os gráficos). Instalado no `iach-ais-venv-4`.
- Executado: `iach-ais-venv-4/bin/python scripts/check_units_train.py`.

**Validado (só treino: 87 IDs, 713 854 linhas, 713 767 pares consecutivos)**
- `x`/`y` em metros: distância plana / haversine ≈ 1,002. `distance_gap` / distância plana = 1,0000.
- `time_gap` em segundos: razão com Δt = 1,0.
- `euc_speed` em nós: razão com `distance_gap/time_gap` em m/s = 1,94384 (percentis 5 e 95 iguais).
- `bearing` em graus a partir do norte: igual ao azimute inicial entre pontos consecutivos.
- `signed_turn` em graus: igual à variação de `bearing`, normalizada para (-180, 180].

**Problemas e limitações**
- Anomalias não quantificadas: `distance_gap` com razão mínima ~0,48; `time_gap` com razão 1/3; `signed_turn` com diferença máxima ~175°. Ficam para o marco 2.
- `distanceToShore`: unidade **não confirmada**. Não pode ser quilómetros pelo valor máximo (~79 mil). Metros é a hipótese mais plausível.
- CRS exato de x/y e de lat/lon: por confirmar. A escala de ~1,002 face à haversine indica um referencial plano em metros, sem identificar o CRS.
- Gráfico 03 (velocidade): a distribuição fica numa única linha de largura quase nula, ou seja, a razão é praticamente exata. A leitura visual é pouco informativa, mas a estatística é clara.

**Pendente**
- Quantificar e tratar as anomalias no marco 2.
- Definir o protocolo para `distanceToShore` e para o CRS.
- Atualizar `latex/proposta_pt.tex` com as unidades e a divisão por viagem (REV-001 e REV-003 marcadas como pendentes no LaTeX).

## Pendentes (por marco, segundo `docs/00_5`)

### Marco 1 — Ambiente, consolidação e divisão mínima
- [x] Ambiente `iach-ais-venv-4/` criado.
- [x] Dependências mínimas instaladas e versões registadas.
- [x] `requirements.txt` criado e testado numa instalação limpa.
- [x] `PROGRESS.md` criado.
- [ ] Commit local destes ficheiros.
- [x] Criar `split_manifest` (id → split) com seed 42 e 70/15/15, lendo apenas a coluna `id`.
- [ ] Materializar ficheiros separados por conjunto, sem exploração (pendente: decidir se é preciso ou se basta o manifesto).
- [x] Verificar invariantes estruturais: IDs sem interseção, atribuição única, conservação de linhas.
- [ ] Criar o isolamento: `run_preparation` com `allowed_splits=["train"]` por defeito.

### Marco 2 — Preparação auditável (só treino/sintéticos)
- [ ] Recálculo de `time_gap_calc_s`, `distance_gap_calc_m` e `speed_calc_mps`.
- [x] Confirmar no treino as unidades de `distance_gap`, `euc_speed`, `time_gap`, `bearing`, `signed_turn` (REV-003). `distanceToShore` ainda por confirmar.
- [ ] Limpeza com auditoria e limites IQR só no treino.
- [ ] Codificação de rótulos (`target`) e features (`speed_calc_mps`, `signed_turn`, `time_gap_calc_s`, `distanceToShore`).
- [ ] Testes com dados sintéticos (gaps, janelas, máscaras, alinhamento).
- [ ] Pedir revisão antes de avançar.

### Marco 3 a 7
Ver `docs/00_5_orientacoes_execucao_decisoes.md`.

## Pendências de decisão

**Decididas pelo utilizador** (ver REV-002 em `REVISION_LOG.md`)
- Overlaps **0% e 50% prioritários**. Os 25% e 75% ficam para decisão posterior.
- Fuso horário de `t`: **ignorado**, não é necessário para o projeto.

**Por decidir**
- Unidade, largura e bordas do pós-processamento simples (aprovação).
- Orçamento de tempo para execuções longas (AGENTS.md §2).
- Se os overlaps 25% e 75% entram no âmbito (decisão posterior).
- Se o manifesto de divisão deve ser versionado (ver entrada 2026-11-23b).

**Verificadas no treino** (ver REV-003)
- Unidades de `x`, `y` e `distance_gap` (metros), `time_gap` (segundos), `euc_speed` (nós), `bearing` e `signed_turn` (graus).
- Por confirmar: unidade de `distanceToShore` (metros é a hipótese mais plausível) e CRS de x/y e de lat/lon.

## Artefactos ainda por criar

- `REVISION_LOG.md` (AGENTS.md §8): ainda não existe, porque ainda não há revisões de documentos. Criar quando houver primeira revisão logada.
- Manifesto de divisão por ID.
- Código fonte e testes.
