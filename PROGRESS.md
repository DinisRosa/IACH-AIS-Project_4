# PROGRESS — Projeto AIS

Registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual

- **Marco atual:** 3 em curso (aprovado pelo utilizador, REV-022): CNN 1D de referência sobre viagem completa. Depois: janelamento com sobreposição e a mesma CNN 1D sobre janelas (Marco 4).
- **Ambiente:** `iach-ais-venv-4/` (venv + pip, Python 3.14.4, CPU). Dependências em `requirements.txt`.
- **Scripts (em `scripts/`):**
  - `create_split_manifest.py`: divisão por ID (seed 42, 70/15/15). Executado.
  - `check_units_train.py`: verificação de unidades só com treino. Executado.
  - `verify_trip_count.py`: confirma 123 viagens e coincidência com o manifesto. Executado.
  - `build_clean_dataset.py --split train|validation|test`: bases limpas recalculadas. Executado para os três conjuntos (REV-009, REV-015).
  - `count_anomalies_train.py`: contagem de saltos e inversões de rumo por viagem, só treino. Executado (REV-017).
  - `watch_latex.sh`: visualização da proposta. Não versionado.
  - Ainda não existe código de janelamento nem de pós-processamento.
- **Código da fase 1 (`src/phase1/`, REV-024):** `data.py`, `model.py`, `training.py`, `checks.py`, `utils.py`. Sequências, scaler, máscaras, CNN 1D, perda e passo de época implementados e testados. **Só houve um ensaio curto de ajuste em 3 viagens de treino (REV-027); sem treino completo.**
- **Testes:** `tests/` com 75 testes (15 de REV-016/REV-017 e 60 de REV-024), todos a passar. Ver `pytest tests/`.
- **Dados:** `data/123_fishing_trajs.csv` presente localmente, não versionado. **123 IDs únicos** e **1 026 279 linhas**, confirmados por `verify_trip_count.py` (REV-007).
- **Bases limpas (não versionadas):** `data/123_fishing_trajs_clean_{train,validation,test}.parquet`, com 713 854, 209 016 e 103 409 linhas (87, 18 e 18 viagens). Soma: 1 026 279.
- **Leituras de dados até agora:**
  - Coluna `id` para a divisão e a contagem de viagens.
  - Colunas de treino para a verificação de unidades (REV-003) e para as contagens de anomalias (REV-017).
  - Validação e teste: leitura completa para construir as bases limpas (REV-015), sem análise de resultados nem uso para escolher nada.
- **Divisão por ID (manifesto):** `manifests/split_manifest_seed42.csv`, gerado e **versionado** (REV-006).
- **Registo de revisões:** `REVISION_LOG.md` com REV-001 a REV-030.

## Decisões do utilizador (vigentes)

- Seed `42`; proporções 70/15/15 por ID completo; arredondamento de validação e teste ao inteiro mais próximo, treino com o resto (REV-001).
- Overlaps **0% e 50% prioritários**; 25% e 75% para decisão posterior (REV-002).
- Fuso horário de `t`: **ignorado** (REV-002).
- `latex/proposta_IAHC_DINIS_ROSA.pdf`: **não se altera**; é a versão entregue ao professor (REV-006).
- HMM e Wu et al. como baselines: **fora por agora**, por falta de tempo. O `AGENTS.md` mantém-se como fonte fixa (REV-006).
- Manifesto da divisão: **versionado** no git (REV-006).
- Autor do dataset: **Song Wu**, Zenodo DOI 10.5281/zenodo.7283281 (CC BY 4.0). O Kaggle é espelho (REV-006).

- Limpeza IQR retirada; os dados ficam tal como estão (REV-012, REV-019).
- Anomalias mantidas, incluindo inversões de rumo da viagem `219028021-2` (REV-012, REV-019).
- Robustez a anomalias não é estudo próprio; fica implícita nas métricas globais (REV-019).
- Features da CNN: `speed`, `signed_turn`, `time_gap` e `distanceToShore`. `x` e `y` ficam de fora (REV-019).
- `bearing` a partir de x, y (grelha UTM); `distanceToShore` aceite como correto (REV-011).
- Marco 1: fica só o manifesto de divisão, sem ficheiros separados por conjunto nem `run_preparation` (REV-019).
- Texto da subsecção «Tratamento dos dados» na proposta confirmado (REV-018, REV-019).

## Entradas do registo

### 2026-11-23 — Ambiente e documentação de arranque

**Feito**
- Leitura integral de `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore`, `docs/00` a `docs/03`, cabeçalhos de `docs/04` a `docs/06` e `latex/proposta_pt.tex`.
- Criado o ambiente `iach-ais-venv-4/` com `python3 -m venv` (Python 3.14.4, `/usr/bin/python3`). Python global não alterado.
- Instaladas dependências mínimas no `iach-ais-venv-4/` a partir do `requirements.txt`: `numpy`, `pandas`, `pytest` e `torch` em CPU.
- Criado `requirements.txt` com versões fixas e `PROGRESS.md`.
- Um primeiro ambiente chamado `.venv/` foi criado por engano, sem nome indicado pelo utilizador. Substituído por `iach-ais-venv-4/` e removido.

**Validado**
- `iach-ais-venv-4/bin/python --version` → Python 3.14.4.
- Instalação limpa de `requirements.txt` na `iach-ais-venv-4/` sem erros (depois da renomeação).
- Importação de `numpy 2.5.5`, `pandas 3.1.1`, `torch 2.15.0+cpu`, `pytest 9.2.0`.
- `torch.cuda.is_available()` → `False` (esperado: GPU integrada, começar em CPU).

**Problemas**
- O `.gitignore` tinha `.venv/` e `venv/`, mas não cobria `iach-ais-venv-4/`. Acrescentada essa linha.

### 2026-11-23b — Manifesto de divisão por ID

**Feito**
- Atualizados `docs/01_preparacao_comum.md` (§3) e `docs/00_contexto_projeto_dicionario_dados.md` (§15) com seed 42 e 70/15/15.
- Criado `scripts/create_split_manifest.py`. Lê só a coluna `id`, conta linhas por ID e atribui cada ID com `random.Random(42)`. Grava `manifests/split_manifest_seed42.csv`.

**Resultados estruturais** (só contagens)
- IDs únicos: **123**. Linhas: **1 026 279**.
- Conjuntos (IDs): treino 87, validação 18, teste 18.
- Conjuntos (linhas): treino 713 854, validação 209 016, teste 103 409.

**Validado**
- Cada ID num só conjunto; conjuntos de IDs cobrem todos os IDs; soma das linhas = total.
- Reexecução: mesmo SHA-256 (`d56918bc65f9bebc6aa0a01a1e82213fda2404a9dfab9f39b3a1858c52733539`).

**Problemas resolvidos**
- Número de viagens: os documentos diziam 128. O ficheiro tem 123 (ver 2026-11-23h).
- Contagens do LaTeX antigo (86/19/18) não batiam com o manifesto. O `.tex` foi reescrito em REV-005, sem essa contagem.

### 2026-11-23c — REVISION_LOG, decisões e verificação de unidades

**Feito**
- Criado `scripts/check_units_train.py`, que só usa o treino. Gera gráficos e `summary.json` em `results/units_check_train/` (não versionado).
- Adicionado `matplotlib==3.10.9` ao `requirements.txt`.

**Validado (só treino: 87 IDs, 713 854 linhas, 713 767 pares consecutivos)**
- `x`/`y` em metros: distância plana / haversine ≈ 1,002. `distance_gap` / distância plana = 1,0000.
- `time_gap` em segundos: razão com Δt = 1,0.
- `euc_speed` em nós: razão com `distance_gap/time_gap` em m/s = 1,94384.
- `bearing` em graus a partir do norte: igual ao azimute inicial entre pontos consecutivos.
- `signed_turn` em graus: igual à variação de `bearing`, normalizada para (-180, 180].

**Problemas e limitações**
- Anomalias não quantificadas: `distance_gap` com razão mínima ~0,48; `time_gap` com razão 1/3; `signed_turn` com diferença máxima ~175°. Ficam para o marco 2.
- `distanceToShore`: unidade **não confirmada**. Não pode ser quilómetros pelo valor máximo (~79 mil). Metros é a hipótese mais plausível.
- CRS exato de x/y e de lat/lon: por confirmar.

### 2026-11-23d — Coerência documental (REV-004)

- Alinhados `README.md`, `AGENTS.md`, `docs/00`, `docs/00_5`, `docs/01` e `PROGRESS.md` com o estado do projeto.

### 2026-11-23e — Proposta LaTeX reescrita a partir do PDF (REV-005)

**Feito**
- `latex/proposta_pt.tex` reescrito a partir de `latex/proposta_IAHC_DINIS_ROSA.pdf`, sem cores de tentativas anteriores, mantendo o vermelho.
- Corrigido o caminho do estilo IJCAI (`FormattingGuidelines-IJCAI-ECAI-26/`, relativo a `latex/`).

**Validado**
- Compilação com `pdflatex` e `bibtex`, a partir de `latex/`. 3 páginas, sem citações ou referências por resolver.

### 2026-11-23f — Compilação automática da proposta

**Feito**
- Criado `scripts/watch_latex.sh`: recompila `latex/proposta_pt.tex` quando o `.tex` ou o `references.bib` mudam. PDF e auxiliares em `latex/build/` (ignorada pelo git).
- `watch_latex.sh` ignorado pelo git: é só de visualização e não faz parte do projeto.

**Validado**
- Uma execução: compilou e gerou `latex/build/proposta_pt.pdf`.

**Pendente**
- Escolha do leitor de PDF com recarregamento automático (a cargo do utilizador).

### 2026-11-23g — Decisões do utilizador e autor do dataset (REV-006)

**Feito**
- `latex/references.bib`, entrada `kaggleAIS`: autor Song Wu, Zenodo DOI 10.5281/zenodo.7283281, CC BY 4.0, 2022.
- `.gitignore`: manifesto versionado (exceção à regra `*.csv`).

**Validado**
- `git check-ignore`: manifesto não ignorado. Recompilação sem avisos de autor.

### 2026-11-23h — Confirmação do número de viagens (REV-007)

**Feito**
- Criado `scripts/verify_trip_count.py`: lê só a coluna `id`, conta IDs únicos e linhas, e compara com o manifesto.

**Validado**
- 1 026 279 linhas; 123 IDs únicos no ficheiro; 123 no manifesto; sem diferenças em nenhum sentido.
- A cifra de 128 é do nome e da página do Zenodo (`128_fishing_trajs.csv`). Não corresponde a este ficheiro local.

## Pendentes (por marco, segundo `docs/00_5`)

### Marco 1 — Ambiente, consolidação e divisão mínima
- [x] Ambiente `iach-ais-venv-4/` criado.
- [x] Dependências mínimas instaladas e versões registadas.
- [x] `requirements.txt` criado e testado numa instalação limpa.
- [x] `PROGRESS.md` criado.
- [x] Manifesto `split_manifest` (id → split) com seed 42 e 70/15/15, lendo só a coluna `id`.
- [x] Invariantes estruturais verificadas (IDs sem interseção, atribuição única, conservação de linhas).
- [x] Número de viagens confirmado: 123.
- [ ] Decidir se é preciso materializar ficheiros separados por conjunto, ou se basta o manifesto.
- [ ] Criar o isolamento: `run_preparation` com `allowed_splits=["train"]` por defeito (ainda não existe código de preparação).

### Marco 2 — Preparação auditável (só treino/sintéticos)
- [x] Recálculo de `time_gap_calc_s`, `distance_gap_calc_m`, `bearing_calc_deg`, `signed_turn_calc_deg` e `speed_calc_mps` (REV-009; validado contra os originais em REV-009 e REV-011).
- [x] Unidades confirmadas no treino: `distance_gap`, `euc_speed`, `time_gap`, `bearing`, `signed_turn` (REV-003). `distanceToShore` em metros confirmado pelo README oficial (REV-008).
- [x] Quantificar as anomalias (REV-017). Tratamento: não tratar, por decisão do utilizador (REV-012). Aguarda revisão.
- [x] Limpeza IQR retirada (REV-019), por decisão do utilizador: os dados ficam tal como estão (REV-012).
- [x] Codificação de rótulos (`target`, REV-009).
- [x] Features da CNN (REV-019): `speed`, `signed_turn`, `time_gap` e `distanceToShore`. `x` e `y` ficam de fora.
- [x] Testes com dados sintéticos de construção e contagem (REV-016, REV-017). Pendentes: janelas, máscaras e alinhamento (ainda não existem no código).
- [x] Revisão pedida e decisões registadas (REV-019). Marco 2 fechado, exceto testes de janelas, máscaras e alinhamento, que pertencem ao Marco 3.

### Marco 3 a 7
Ver `docs/00_5_orientacoes_execucao_decisoes.md`.

## Pendências por decidir ou confirmar

- CRS de longitude/latitude (x/y já indicado como SRID 25832 pelo README oficial, REV-008).
- Método de cálculo de `distanceToShore` (não documentado; a unidade em metros está confirmada, REV-008).
- Unidade, largura e bordas do pós-processamento simples (aprovação do utilizador).
- Orçamento de tempo para execuções longas (AGENTS.md §2).
- Se os overlaps 25% e 75% entram no âmbito (decisão posterior).
- Se HMM e Wu et al. entram como baselines (decisão posterior; ficam fora por agora).

## Artefactos do projeto

| Ficheiro | Estado |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `README.md` | Existentes; alinhados (REV-004, REV-007); `AGENTS.md` §5 com atualização automática de registos (REV-010) |
| `docs/00` a `docs/06` | Existentes; atualizados (REV-001 a REV-004, REV-007, REV-024 em `docs/05`) |
| `src/phase1/` | `data.py`, `model.py`, `training.py`, `checks.py`, `utils.py` (REV-024); sem treino |
| `tests/` (fase 1) | 6 ficheiros novos, 60 testes (REV-024) |
| `latex/proposta_pt.tex` | Reescrito a partir do PDF IAHC (REV-005); compila com pdflatex/bibtex |
| `latex/proposta_IAHC_DINIS_ROSA.pdf` | Versão entregue ao professor; **não se altera** (REV-006) |
| `latex/references.bib` | Existente; `kaggleAIS` com autor corrigido (REV-006) |
| `requirements.txt` | Existente; testado numa instalação limpa |
| `REVISION_LOG.md` | Existente; REV-001 a REV-010 |
| `scripts/build_clean_dataset.py` | Existente; executado só com treino (REV-009) |
| `data/123_fishing_trajs_clean_train.parquet` | Gerado; não versionado; só treino |
| `PROGRESS.md` | Este ficheiro |
| `scripts/create_split_manifest.py` | Existente; executado |
| `scripts/check_units_train.py` | Existente; executado |
| `scripts/verify_trip_count.py` | Existente; executado |
| `scripts/watch_latex.sh` | Existente; não versionado (só visualização) |
| `manifests/split_manifest_seed42.csv` | Gerado; **versionado** (REV-006) |
| `results/units_check_train/` | Gerado; não versionado |
| `latex/build/` | Gerado; não versionado |
| Código de pré-processamento, modelos e testes automatizados | Ainda não criados |

### 2026-11-23i — Unidades confirmadas pelo README oficial (REV-008)

**Feito**
- `distanceToShore` em metros (distância à costa da Dinamarca), confirmado pelo README do Zenodo.
- `x`/`y` em SRID 25832 (ETRS89 / UTM 32N), segundo o mesmo README.

**Pendente**
- CRS de longitude/latitude: hipótese WGS84, por verificar.
- Método de cálculo de `distanceToShore`: não documentado.

**Verificação adicional:** MD5 do CSV local = `c5953081f511e228b19e46ca85fe304f`, igual ao do Zenodo. O ficheiro é o oficial; as 123 viagens são o conteúdo real.

### 2026-11-23j — Base limpa do treino (REV-009)

**Feito**
- `scripts/build_clean_dataset.py`: bases X, Y, T, distanceToShore; recalculados time_gap, distance_gap, bearing, signed_turn e speed; `target` 0/1.
- Gerado `data/123_fishing_trajs_clean_train.parquet` (só treino).

**Validado (só treino)**
- `time_gap`, `distance_gap` e `signed_turn` recalculados coincidem com os originais em todos os pares, exceto ~10⁻⁶ (anomalias pontuais).
- `bearing` difere do original em 54 % dos pares (mediana 1,08°): norte da grelha UTM versus norte verdadeiro. É a convergência de meridianos.

**Pendente**
- Decidir a base de `bearing` (grelha ou norte verdadeiro).
- Autorização explícita para processar validação e teste.
- Regra para as anomalias restantes.

### 2026-11-23k — Atualização automática de registos (REV-010)

**Feito**
- `AGENTS.md` §5: no fim de cada interação com alterações, `PROGRESS.md` e `REVISION_LOG.md` são atualizados sem pedido.

**Pendente**
- Nenhum.

### 2026-11-23l — Bearing pela grelha e distanceToShore aceite (REV-011)

**Feito**
- Decidido: `bearing` a partir de x,y (grelha UTM). `distanceToShore` aceite como correto, sem verificação externa.
- Verificação no treino: a base limpa não tem anomalias criadas pelo cálculo. As anomalias estão nos dados (gaps até 13 h, saltos até 14,8 km, 3 717 inversões de rumo acima de 170°).

**Pendente**
- Regra para as anomalias de `time_gap`, `distance_gap` e `signed_turn` (Marco 2).
- Autorização explícita para validação e teste.
- Push dos commits locais, só com confirmação explícita.

### 2026-11-23m — Anomalias mantidas como estão (REV-012)

**Feito**
- Decidido: nenhuma anomalia de tempo, distância, velocidade ou rumo é removida ou marcada. O dataset é tratado como ele próprio.

**Pendente**
- Medir a frequência de saltos e de inversões de rumo no treino, para confirmar que são poucos (3 717 inversões acima de 170° já contadas, cerca de 0,5 %).
- Autorização explícita para validação e teste.
- Push dos commits locais, só com confirmação explícita.

### 2026-11-23n — Anomalias declaradas no relatório (REV-013)

**Feito**
- `latex/proposta_pt.tex`: parágrafo em Materiais e Dados que declara a manutenção das anomalias como teste de robustez para dados ao momento. Cor REV-013 (oliva `#808000`, RGB 128,128,0) aplicada com `\revtext`.

**Pendente**
- Decidir se a robustez a anomalias entra como estudo na secção Avaliação.
- Medir a frequência de saltos e de inversões de rumo no treino.
- Autorização explícita para validação e teste. Push só com confirmação explícita.

### 2026-11-23o — Regra de cor para alterações ao LaTeX (REV-014)

**Feito**
- `AGENTS.md` §8: toda a alteração ao `.tex` leva cor do seu ID, pela macro `\revtext`. Sem cor por atribuir.
- REV-011 (laranja), REV-012 (cinzento-ardósia) e REV-013 (verde-oliva) com cores atribuídas.
- REV-013 aplicado no `.tex` com `\revtext{rev013}`. Compila sem erros.

**Pendente**
- Medir a frequência de saltos e de inversões de rumo no treino.
- Autorização explícita para validação e teste. Push só com confirmação explícita.

### 2026-11-23p — Bases limpas de validação e teste (REV-015)

**Feito**
- Autorização explícita para processar validação e teste.
- `scripts/build_clean_dataset.py --split` gera as três bases. Contagens verificadas: 1 026 279 linhas e 123 viagens, iguais ao CSV e ao manifesto.

**Pendente**
- Testes sintéticos da função de construção.
- Medir a frequência de saltos e de inversões de rumo.
- Push feito pelo utilizador.

### 2026-11-23q — Testes sintéticos e correção de wrap_180 (REV-016)

**Feito**
- `tests/test_build_clean_dataset.py`: 10 testes sintéticos, todos a passar.
- `wrap_180` corrigido para (-180, 180], em linha com a documentação. Os dados do treino não mudam.

**Pendente**
- Contagem de saltos e inversões de rumo no treino. Aguarda o pedido de revisão do Marco 2.
- Push do `2f24970` feito pelo utilizador.

### 2026-11-23r — Contagem de saltos e inversões por viagem (REV-017)

**Feito**
- `scripts/count_anomalies_train.py` e resultados em `results/anomalies_train/` (por viagem, resumo e dois gráficos). Testes: 15 a passar no total.
- Saltos acima de 30 nós: 55 no total, 4 viagens afetadas. Inversões acima de 170°: 3 717 no total, 70 viagens afetadas, com 68 % concentrado em duas viagens.

**Pendente**
- Decidir se as inversões concentradas são erro ou comportamento real.
- Revisão do Marco 2 pelo utilizador.
- Commits das alterações desde 2f24970 ainda não feitos.

### 2026-11-23s — Proposta: subsecção «Tratamento dos dados» (REV-018)

**Feito**
- `latex/proposta_pt.tex`: nova subsecção em Materiais e Dados. O parágrafo de REV-013 foi movido para lá, em cor REV-018 (azul-ardósia `#5C6BC0`).
- Compila sem erros.

**Pendente**
- Confirmação do utilizador sobre o texto da subsecção.
- Push de `2f24970` e `562e7ee`, por conta do utilizador.

### 2026-11-23t — Decisões do utilizador e fecho do Marco 2 (REV-019)

**Feito**
- IQR retirado. Features da CNN: `speed`, `signed_turn`, `time_gap`, `distanceToShore`. `x` e `y` de fora. Inversões mantidas. Robustez não é estudo próprio. Texto da subsecção confirmado.
- Marco 2 fechado, exceto os testes de janelas, máscaras e alinhamento, que pertencem ao Marco 3.

**Pendente**
- Aprovação do utilizador para começar o Marco 3.
- Tratamento de valores ausentes na CNN (primeiro ponto, `time_gap` e `speed` nulos).
- Push de `2f24970`, `562e7ee` e `d6b1289`, por conta do utilizador.

### 2026-11-23u — Alinhamento de todos os documentos (REV-020)

**Feito**
- Documentos alinhados com REV-011 a REV-019: `docs/00`, `docs/01`, `docs/04`, `README.md`, `PROGRESS.md` e o passo 1 do pipeline em `latex/proposta_pt.tex` (cor REV-020, `#607D8B`). Compila sem erros.
- Corrigida a falta da linha REV-019 na tabela de cores do registo.

**Pendente**
- Commit destas alterações, a pedido do utilizador.
- Aprovação do utilizador para o Marco 3.
- Push, por conta do utilizador.

### 2026-11-23v — Reorganização do pipeline: CNN 1D primeiro sobre viagens completas (REV-021)

**Feito**
- Decisão do utilizador: o modelo é uma CNN 1D com uma probabilidade por ponto. Ordem: pré-processamento; CNN de referência sobre a viagem completa; janelamento com sobreposição e a mesma CNN sobre janelas; pós-processamento temporal; explicabilidade.
- `latex/proposta_pt.tex`: objetivos 1 e 2, abordagem (cinco etapas) e figura do pipeline atualizados. Texto novo em cor REV-021 (magenta `#D500F9`). Compila sem erros.
- `docs/00_5` (marcos 3 e 4) e `README.md` alinhados.

**Pendente**
- Aprovação do utilizador para o Marco 3.
- Política de valores ausentes na CNN (primeiro ponto, `time_gap` e `speed` nulos). Proposta: excluir os 87 primeiros pontos e mascarar os restantes casos. Decisão do utilizador.
- Push dos commits, por conta do utilizador.

### 2026-11-23w — Política de ausências aprovada e Marco 3 em curso (REV-022)

**Feito**
- Política de ausências aprovada: nenhuma linha removida, preenchimento com zero e máscara de ausência por característica. O primeiro ponto mantém-se, sem `time_gap`, `speed` nem `signed_turn`. O segundo só não tem `signed_turn` (porque `signed_turn` precisa de dois intervalos).
- Marco 3 oficialmente em curso.

**Próximos passos do Marco 3 (por ordem)**
1. Construir as sequências por viagem só com o treino, ordenadas por `t` e `point_id`, com as quatro características na ordem decidida e as máscaras de ausência.
2. Ajustar o normalizador (StandardScaler) só com o treino, e guardar a ordem, a média e o desvio-padrão. Os valores ausentes não entram no ajuste.
3. Implementar a CNN 1D de referência: uma probabilidade por ponto, arquitetura conforme `docs/02`. Função de perda que ignora os pontos iniciais.
4. Testes sintéticos: alinhamento (saída i corresponde ao ponto i), máscaras, forward e backward com tensores pequenos, e ausência de vazamento (o normalizador não vê validação nem teste).
5. Treino de ensaio só com o treino. Se for preciso monitorizar, criar uma partição interna só dentro do treino, por ID completo. Pedir ao utilizador o orçamento de tempo antes de qualquer treino longo.
6. Medir o custo (tempo por época e memória, em CPU) e registar as métricas de referência internas.
7. Pedido de revisão do Marco 3 ao utilizador. Validação e teste não são usados para escolher nada antes da autorização explícita (Marco 6).

**Pendente**
- Decisão do utilizador: partição interna de monitorização dentro do treino (proporção por ID) e orçamento de tempo para treino.
- Push dos commits, por conta do utilizador.

**Decidido (2026-11-23x, REV-022):** os pontos iniciais entram na função de perda. O primeiro ponto tem `time_gap`, `speed` e `signed_turn` a zero com máscara; o segundo tem `signed_turn` a zero com máscara. Não se inventa `bearing` para o primeiro ponto.

### 2026-11-23x — Pontos iniciais: zero com máscara, entram na perda (REV-022)

**Feito**
- Decisão do utilizador, após análise: zero com máscara nos valores em falta; não se inventa `bearing` para o primeiro ponto; os pontos iniciais entram na função de perda.
- Documentos e proposta alinhados. Compila sem erros.

**Próximos passos do Marco 3**
1. Construir as sequências por viagem, só com o treino, com as quatro características na ordem decidida, e as máscaras.
2. Ajustar o normalizador (StandardScaler) só com o treino, sem contar os valores em falta; guardar média e desvio-padrão e a ordem das características.
3. Implementar a CNN 1D de referência: uma probabilidade por ponto, arquitetura conforme `docs/02`, perda sobre todos os pontos.
4. Testes sintéticos: alinhamento, máscaras, forward e backward com tensores pequenos, e ausência de vazamento.
5. Treino de ensaio só com o treino. Se for preciso monitorização, partição interna dentro do treino, por ID completo.
6. Medir o custo em CPU e registar as métricas internas de referência.
7. Pedido de revisão do Marco 3 ao utilizador.

**Pendente**
- Proporção da partição interna de monitorização (decisão do utilizador).
- Orçamento de tempo para o treino (decisão do utilizador).
- Push, por conta do utilizador.

### 2026-11-23y — Ficheiro de passagem de sessão

**Feito**
- Criado `handoff.md` na raiz: objetivo, estado, ficheiros, alterações, falhas e próximos passos do Marco 3. Não altera decisões nem dados.

**Pendente**
- Nenhuma alteração ao plano. Commit de `handoff.md` e `PROGRESS.md` a pedido do utilizador.

### 2026-11-23z — Reorganização do manuscrito e código da fase 1 (REV-023, REV-024)

**Feito**
- REV-023: «Abordagem» (5 subsecções) e «Avaliação» (3) reorganizadas no LaTeX; texto antigo com as cores originais.
- REV-024: `src/phase1/` com sequências por viagem, scaler só do treino, 7 canais (4 + 3 máscaras), zero depois de normalizar, partição interna por ID, DataLoader, CNN 1D (32/64/32, kernel 5, campo recetivo 13), perda BCE sobre logits, Adam, passo de época, avaliação diagnóstica e smoke test.
- Ordenação por `id, t, point_id`: a base já vinha ordenada (`build_clean_dataset.py`); `validate_training_data` verifica-a e rejeita se não estiver.
- Subsecção «Verificação da implementação» e parágrafos da CNN no `.tex` (REV-024).
- Delegação: agente Sonnet (`data.py`), agente Haiku (modelo e treino); revisão e integração minhas.

**Validado**
- `pytest tests/`: 75 passaram, 0 falharam, 0 ignorados. 3 viagens reais de treino (17 844 pontos) usadas num teste. Validação e teste não abertos.
- `pdflatex` sem erros (4 páginas). PDF não inspecionado visualmente.

**Problemas e limitações**
- Dois testes do agente B falharam durante o desenvolvimento e foram corrigidos por ele (smoke test: ordem da verificação de forma; teste da ausência de sigmoide).
- Taxa de aprendizagem 1e-3 provisória. Smoke test estrito (gradiente não nulo em todos os tensores).
- Faltam `config` JSON, checkpoints, segmentos, métricas por segmento, `run_phase1` e medição de custo.

**Pendente**
- Proporção da partição interna e orçamento de tempo (utilizador); depois, treino de ensaio só com treino (passo 5) e medição de custo (passo 6).
- Commit local por autorizar (alteração substancial, AGENTS §6). Push por conta do utilizador.

### 2026-11-23aa — Secção da CNN na proposta (REV-025)

**Feito**
- Nova secção «Especificação da CNN 1D de referência» no LaTeX: entrada e saída, arquitetura com tabela de parâmetros (total 21 761), justificação das escolhas, campo recetivo de 13 pontos, perda, otimizador e reprodutibilidade.
- Declarado no texto que 32/64/32, *kernel* 5, Adam e lr 1e-3 são valores iniciais **não validados**; épocas, paragem e semente do modelo **não definidos**.
- Corrigidas maiúsculas em quatro parágrafos movidos em REV-023.

**Validado**
- `pdflatex` sem erros (6 páginas). Valores da tabela conferidos com o código. Só a página 3 foi vista.

**Pendente**
- Decisões do utilizador: taxa de aprendizagem, épocas, critério de paragem, partição interna, orçamento de tempo.
- Commit local por autorizar. Push por conta do utilizador.

### 2026-11-23ab — Figura do desenho da CNN (REV-026)

**Feito**
- Figura 2 em TikZ na secção da CNN: cadeia de camadas e esquema do campo recetivo de 13 pontos. Equação do campo recetivo simplificada para caber na coluna.

**Validado**
- `pdflatex` e `bibtex` sem erros nem referências em falta; sem linhas largas. Figura e equação vistas no PDF (página 4).

**Problemas**
- O `watch_latex.sh` (ativo) e as minhas compilações em `latex/build/` colidiram e corromperam o `.aux` e o PDF. Reconstruí `build/` e passei a compilar manualmente em `latex/build/check/`.

**Pendente**
- Commit local por autorizar; push por conta do utilizador. Decisões de treino em aberto (lr, épocas, paragem, partição interna, orçamento).

### 2026-11-23ac — Ensaio curto de ajuste em 3 viagens (REV-027)

**Feito**
- `scripts/diagnostic_fit_3_trips.py`: 200 épocas, lr 1e-3, seed 42, só 3 viagens de treino (17 844 pontos). Resultados em `results/diagnostic_3trips/`.
- Accuracy 95,71 % (766 erros em 17 844; maioritária 73,45 %); navegação 4 349/388, pesca 12 729/378 (acertos/erros). Perda por ponto 0,6599 → 0,1058; 12,0 s.
- Corrigidas as frases «ainda não houve treino» no LaTeX e no README.

**Validado**
- Execução do script e leitura dos artefactos; `pdflatex` sem erros. Sem teste automático do script.

**Problemas e limitações**
- Treino e previsão nas mesmas viagens: sobreajuste, não generalização. Só rótulos 01, 02 e 03 nestas viagens. Viagem `219001039-2` é a mais difícil (90,30 %).

**Pendente**
- Partição interna, lr, épocas e orçamento para o treino a sério. Commit local por autorizar; push por conta do utilizador.

### 2026-11-23ad — Ajuste em 3 viagens e avaliação noutras 3 de treino (REV-028)

**Feito**
- `scripts/diagnostic_fit_3_trips.py` estendido: ajuste em 3 viagens, avaliação em outras 3 do treino (35 290 pontos), scaler só do ajuste.
- Fora da amostra: accuracy 93,01 % (2 466 erros; maioritária 75,21 %). Navegação com sensibilidade 0,736 (2 310 erros, muitos previstos como pesca); pesca com sensibilidade 0,994. Ajuste: 95,71 %.
- Frase qualitativa no `.tex` (sem números).

**Validado**
- Execução do script (≈11 s) e leitura dos artefactos; ajuste reproduz REV-027. `pdflatex` a verificar na compilação seguinte.

**Problemas e limitações**
- 3 viagens: ilustrativo, sem valor estatístico. Não é validação oficial. Script sem teste automático.

**Pendente**
- Partição interna, lr, épocas e orçamento para o treino a sério. Commit local por autorizar; push por conta do utilizador.

### 2026-11-23ae — Gráficos e tabelas do ensaio em imagem (REV-029)

**Feito**
- `scripts/plot_diagnostic_3trips.py`: 6 imagens em `results/diagnostic_3trips/figures/` (perda e accuracy, matrizes de confusão, métricas por classe, rótulos originais vs. previsto, linhas temporais por viagem, tabelas).

**Validado**
- Script executado e imagens inspecionadas. Sem teste automático.

**Observação (das imagens)**
- Nas viagens fora da amostra com mais erros, os erros formam blocos contínuos junto às fronteiras do segmento de pesca (a pesca prevista começa antes e acaba depois da real), e não ruído disperso. Por confirmar com código (medir o desfasamento) antes de usar como evidência.

**Pendente**
- Decidir se alguma figura vai para o relatório; treino a sério; commit local por autorizar; push por conta do utilizador.

### 2026-11-23af — Figuras do ensaio preliminar no relatório (REV-030)

**Feito**
- Subsecção 7.4 «Ensaio preliminar com poucas viagens» e duas figuras (matrizes de confusão; previsão em 3 viagens não vistas) no LaTeX, como marcador dos resultados. Imagens em `latex/figures/`.
- Corrigido no script das figuras um nome de ficheiro sobreposto por engano.

**Validado**
- `pdflatex` sem erros nem referências em falta (7 páginas); páginas 5 a 7 vistas. Nome do script no texto corrigido depois de verificado.

**Problemas e limitações**
- Resultados ilustrativos (3 viagens, sem validação oficial); declarado no texto. Paginação das figuras de largura total a rever.
- Observação sobre fronteiras ainda não quantificada.

**Pendente**
- Quantificar o desfasamento; treino a sério e substituição das figuras; commit local por autorizar (inclui `latex/figures/`); push por conta do utilizador.

### 2026-11-23ag — Commits locais do Marco 3

**Feito**
- Três commits locais, autorizados pelo utilizador: `fa391a5` (código, testes e scripts), `7fe7693` (LaTeX e figuras) e `11a0d97` (documentação). Nenhum push.
- Os pendentes «commit local por autorizar» das entradas anteriores ficam resolvidos por estes commits.
- `handoff.md` ficou fora dos commits: está desatualizado (anterior ao código da fase 1) e fica por atualizar ou descartar a pedido do utilizador.

**Pendente**
- Push, por conta do utilizador (`main` está 3 commits à frente de `origin/main`, antes deste registo).
- Decisões de treino: partição interna, lr, épocas, critério de paragem e orçamento de tempo.

### 2026-11-23ah — Atualização do ficheiro de passagem de sessão

**Feito**
- `handoff.md` reescrito para o estado atual: código da fase 1, 75 testes, decisões desta sessão (7 canais, zero depois de normalizar), ensaio curto e seus resultados ilustrativos, problemas encontrados, correção da compilação do LaTeX, pendentes e próximos passos do Marco 3.

**Validado**
- Revisão por leitura contra `PROGRESS.md`, `REVISION_LOG.md` e os artefactos do ensaio. Sem alterações a código nem a dados.

**Pendente**
- Commit de `handoff.md` e desta entrada, a pedido do utilizador. Push por conta do utilizador.
