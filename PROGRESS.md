# PROGRESS — Projeto AIS

Registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual

- **Marco atual:** 1 — Ambiente, consolidação e divisão mínima por ID. Em curso; faltam os itens de isolamento e materialização indicados abaixo.
- **Ambiente:** `iach-ais-venv-4/` (venv + pip, Python 3.14.4, CPU). Dependências em `requirements.txt`.
- **Scripts:**
  - `scripts/create_split_manifest.py`: divisão por ID (seed 42, 70/15/15). Executado.
  - `scripts/check_units_train.py`: verificação de unidades só com treino. Executado.
  - Ainda não existe código de pré-processamento, modelo ou testes automatizados.
- **Dados:** `data/123_fishing_trajs.csv` presente localmente, não versionado. O ficheiro tem **123 IDs únicos** e **1 026 279 linhas**.
- **Leituras de dados até agora:**
  - Coluna `id` para a divisão.
  - Colunas de treino para a verificação de unidades (REV-003).
  - Validação e teste: só o `id` e as contagens de linhas. Nenhum valor de validação ou teste foi lido ou analisado.
- **Divisão por ID (manifesto):** `manifests/split_manifest_seed42.csv`, gerado e não versionado (ver 2026-11-23b).
- **Conjuntos de validação e teste:** bloqueados para desenvolvimento.
- **Registo de revisões:** `REVISION_LOG.md` com REV-001 a REV-005.

## Entradas do registo

### 2026-11-23 — Ambiente e documentação de arranque

**Feito**
- Leitura integral de `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore`, `docs/00` a `docs/03`, cabeçalhos de `docs/04` a `docs/06` e `latex/proposta_pt.tex`.
- Criado o ambiente `iach-ais-venv-4/` com `python3 -m venv` (Python 3.14.4, `/usr/bin/python3`). Python global não alterado.
- Instaladas dependências mínimas no `iach-ais-venv-4/` a partir do `requirements.txt`: `numpy`, `pandas`, `pytest` e `torch` em CPU (índice `https://download.pytorch.org/whl/cpu`).
- Criado `requirements.txt` com versões fixas.
- Criado este `PROGRESS.md`.
- Um primeiro ambiente chamado `.venv/` foi criado por engano, sem nome indicado pelo utilizador. Substituído por `iach-ais-venv-4/` e removido.

**Validado**
- `iach-ais-venv-4/bin/python --version` → Python 3.14.4.
- Instalação limpa de `requirements.txt` na `iach-ais-venv-4/` concluída sem erros (confirmado a 2026-11-23, depois da renomeação).
- Importação de `numpy 2.5.5`, `pandas 3.1.1`, `torch 2.15.0+cpu`, `pytest 9.2.0`.
- `torch.cuda.is_available()` → `False` (esperado: GPU integrada, começar em CPU).

**Problemas**
- O `.gitignore` tinha `.venv/` e `venv/`, mas não cobria `iach-ais-venv-4/`. Acrescentada a linha `iach-ais-venv-4/`.

**Decisões**
- Ambiente em `iach-ais-venv-4/` com venv+pip. Conda não usado (AGENTS.md §4). Nome indicado pelo utilizador, com `-4` no fim, em minúsculas.
- Torch apenas em CPU, sem CUDA (AGENTS.md §4).
- Versões fixas em `requirements.txt` para reprodutibilidade (AGENTS.md §4).

### 2026-11-23b — Manifesto de divisão por ID

**Decisões confirmadas pelo utilizador** (REV-001)
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
- Número de viagens: a `docs/00` cita 128 (valor da proposta PDF). O ficheiro e o `latex/proposta_pt.tex` dizem **123**. O ficheiro tem **123 IDs únicos**, pelo que o valor 128 nos documentos está desatualizado (corrigido em REV-004).
- A validação (209 016 linhas) e o teste (103 409 linhas) não têm 15% das linhas. É esperado, porque a divisão é por viagem.
- O manifesto `manifests/split_manifest_seed42.csv` **não é versionado**: a regra `*.csv` do `.gitignore` o exclui. É regenerável com o script e a seed 42. Decisão pendente do utilizador (ver abaixo).
- **Discrepância com o LaTeX:** o `latex/proposta_pt.tex` indica **86 / 19 / 18** trajetórias (treino/validação/teste) e 706 522 / 173 532 / 146 225 pontos. O manifesto dá **87 / 18 / 18** IDs e 713 854 / 209 016 / 103 409 linhas. Ambas as contagens não podem estar certas com a mesma seed e o mesmo critério. Por esclarecer.

**Pendente**
- Decidir se o manifesto deve ser versionado.
- Esclarecer a discrepância 86/19/18 (LaTeX) vs 87/18/18 (manifesto).

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
- Atualizar `latex/proposta_pt.tex` com as unidades (ver REV-003 no `REVISION_LOG.md`).

### 2026-11-23d — Coerência documental (REV-004)

**Feito**
- Corrigidos `README.md`, `AGENTS.md`, `docs/00`, `docs/00_5`, `docs/01` e este `PROGRESS.md` para refletir o estado atual.
- Removido o item "REVISION_LOG por criar" (o ficheiro existe desde REV-001).
- Substituído `.venv` por `iach-ais-venv-4` nos exemplos do `AGENTS.md`.
- Atualizadas as unidades confirmadas nas tabelas de `docs/00` §8.

**Validado**
- Pesquisa por `.venv`, "ainda por criar", "128" e "70/15/15" em todos os MDs. Resultados revistos.

**Pendente**
- Atualizar o LaTeX (ver abaixo).

### 2026-11-23e — Proposta LaTeX reescrita a partir do PDF (REV-005)

**Feito**
- `latex/proposta_pt.tex` reescrito a partir de `latex/proposta_IAHC_DINIS_ROSA.pdf`, sem cores de tentativas anteriores, mantendo o vermelho.
- Corrigido o caminho do estilo IJCAI (`FormattingGuidelines-IJCAI-ECAI-26/`, relativo a `latex/`).

**Validado**
- Compilação com `pdflatex` e `bibtex`, a partir de `latex/`, com saída fora do repositório. 3 páginas, sem citações ou referências por resolver.

**Problemas**
- `kaggleAIS` em `references.bib` sem autor (aviso do `bibtex`). Não alterado.

**Pendente**
- Decidir se o PDF IAHC original deve ser atualizado (diz 128 e divisão por navio).
- Confirmar se HMM e Wu et al. são baselines (proposta) ou ficam fora do âmbito mínimo (`AGENTS.md`).

## Pendentes (por marco, segundo `docs/00_5`)

### Marco 1 — Ambiente, consolidação e divisão mínima
- [x] Ambiente `iach-ais-venv-4/` criado.
- [x] Dependências mínimas instaladas e versões registadas.
- [x] `requirements.txt` criado e testado numa instalação limpa.
- [x] `PROGRESS.md` criado.
- [ ] Commit local destes ficheiros (feito em `c055c67` e seguintes; a confirmar em cada novo commit).
- [x] Criar `split_manifest` (id → split) com seed 42 e 70/15/15, lendo apenas a coluna `id`.
- [ ] Materializar ficheiros separados por conjunto, sem exploração (pendente: decidir se é preciso ou se basta o manifesto).
- [x] Verificar invariantes estruturais: IDs sem interseção, atribuição única, conservação de linhas.
- [ ] Criar o isolamento: `run_preparation` com `allowed_splits=["train"]` por defeito (ainda não existe código de preparação).

### Marco 2 — Preparação auditável (só treino/sintéticos)
- [ ] Recálculo de `time_gap_calc_s`, `distance_gap_calc_m` e `speed_calc_mps`.
- [x] Confirmar no treino as unidades de `distance_gap`, `euc_speed`, `time_gap`, `bearing`, `signed_turn` (REV-003). `distanceToShore` ainda por confirmar.
- [ ] Quantificar e tratar as anomalias de `distance_gap`, `time_gap` e `signed_turn`.
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
- HMM e Wu et al. como baselines (proposta) vs âmbito mínimo do `AGENTS.md` sem eles.

**Verificadas no treino** (ver REV-003)
- Unidades de `x`, `y` e `distance_gap` (metros), `time_gap` (segundos), `euc_speed` (nós), `bearing` e `signed_turn` (graus).
- Por confirmar: unidade de `distanceToShore` (metros é a hipótese mais plausível) e CRS de x/y e de lat/lon.

## LaTeX (`latex/proposta_pt.tex`) — reescrito a partir do PDF (REV-005)

- O `.tex` foi reescrito a partir de `latex/proposta_IAHC_DINIS_ROSA.pdf`, por pedido do utilizador. Removidas as cores de tentativas anteriores (verde, amarelo, roxo) e mantido o vermelho.
- Removido o texto que descrevia implementações inexistentes (BiGRU, baselines treinados, `t_rel`, janelas de 30 minutos, caso `219429000-2`, métricas de ajuste).
- Trajetórias: **123** (o PDF dizia 128).
- Divisão: **por ID completo**, 70/15/15, semente 42 (o PDF dizia por navio).
- Compila com `pdflatex` e `bibtex` (3 páginas), a partir de `latex/`.
- Pendente: `kaggleAIS` em `references.bib` sem autor (aviso do `bibtex`). E o PDF IAHC original ainda diz 128 e por navio.
- Pendente de decisão: a proposta usa HMM e Wu et al. como baselines, mas o `AGENTS.md` fixa o mínimo sem HMM nem Wu. Confirmar qual prevalece.

## Artefactos do projeto

| Ficheiro | Estado |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `README.md` | Existentes; atualizados em REV-004 |
| `docs/00` a `docs/06` | Existentes; atualizados em REV-001 a REV-004 |
| `latex/proposta_pt.tex` | Reescrito a partir do PDF IAHC (REV-005); compila com pdflatex/bibtex |
| `latex/proposta_IAHC_DINIS_ROSA.pdf`, `references.bib` | Existentes; não alterados (ver aviso `kaggleAIS` acima) |
| `requirements.txt` | Existente; testado numa instalação limpa |
| `REVISION_LOG.md` | Existente; REV-001 a REV-005 |
| `PROGRESS.md` | Este ficheiro |
| `scripts/create_split_manifest.py` | Existente; executado |
| `scripts/check_units_train.py` | Existente; executado |
| `manifests/split_manifest_seed42.csv` | Gerado; **não versionado** (pendente de decisão) |
| `results/units_check_train/` | Gerado; não versionado (ignorado pelo `.gitignore`) |
| Código de pré-processamento, modelos e testes automatizados | Ainda não criados |

### 2026-11-23f — Compilação automática da proposta

**Feito**
- Criado `scripts/watch_latex.sh`: recompila `latex/proposta_pt.tex` quando o `.tex` ou o `references.bib` mudam (pdflatex, bibtex, pdflatex x2). PDF e auxiliares em `latex/build/`.
- Acrescentado `latex/build/` ao `.gitignore`.

**Validado**
- Uma execução: compilou e gerou `latex/build/proposta_pt.pdf`. `git check-ignore` confirma que fica fora do git.

**Pendente**
- Visualização em leitor de PDF com recarregamento automático: a escolha do leitor é do utilizador.
