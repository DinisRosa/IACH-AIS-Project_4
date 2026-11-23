# PROGRESS — Projeto AIS

Estado vivo no topo (estado, decisões, pendências, artefactos); abaixo, o registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual (REV-048)

| Marco | Estado |
|---|---|
| 1 Ambiente, divisão por ID, isolamento | Fechado |
| 2 Preparação auditável (só treino/sintéticos) | Fechado (REV-019) |
| 3 CNN 1D de referência sobre a viagem completa | **Fechado por decisão do utilizador (REV-041)** |
| 4 Janelamento com a mesma CNN (L = 64; 0 % e 50 %) | **Feito (REV-046, REV-047)**: J0 e J50 treinadas, selecionadas no `test` numa só abertura e congeladas; resultados no LaTeX (8.2 a 8.4) |
| 5 Pós-processamento | Por fazer; só com decisão do utilizador (o Marco 4 não melhorou a exatidão por ponto; J50 reduz a fragmentação face a J0) |
| 6 e 7 Congelar tudo e medição final no `validation` | Por fazer; precisam de autorização |

- **Baseline (CNN de referência):** treinada só com o treino oficial (87 viagens, 300 épocas, um checkpoint por época). **Época 162 e limiar 0,65**, escolhidos no `test` numa só ronda e congelados em `results/baseline_frozen/` (REV-038). Números em `results/baseline_frozen/final_results.json` e, no LaTeX, em macros geradas (REV-040). Os resultados do `test` são otimistas (serviram a escolher) e a perda no `test` é ruidosa entre épocas.
- **J0 e J50 (REV-046, REV-047):** a mesma CNN sobre janelas de 64 pontos, sem sobreposição (J0) e com 50 % (J50), 300 épocas, lote de 32 janelas. J0 em 9,8 min e 105 300 passos; J50 em 21,3 min e 208 800 passos. Escolhidas no `test` numa só abertura: **J0 época 8, limiar 0,60; J50 época 4, limiar 0,75** (a perda no `test` sobe com o treino). Exatidão por ponto no `test`: referência 94,7 %, J0 93,5 %, J50 93,8 %; J50 reduz a fragmentação face a J0 e à referência, mas o F1 de segmentos de pesca é baixo (cerca de 0,03) nas três. Congeladas em `results/windows_j0_frozen/` e `results/windows_j50_frozen/`; números em `results/windows_final/final_results_windows.json` (fonte única) e, no LaTeX, em macros geradas. Resultados otimistas (serviram a escolher).
- **Conjuntos reservados:** o `test` foi aberto **duas vezes**, cada uma ao abrigo da sua autorização (baseline e janelas) e registada em `results/access_log.jsonl`; o `validation` **nunca foi aberto**. Validação e teste foram lidos por inteiro só para construir as bases limpas (REV-015).
- **Ambiente:** `iach-ais-venv-4/` (venv + pip, Python 3.14.4, CPU), pacote `ais` instalado em modo editável (REV-034). Dependências em `requirements.txt`.
- **Código:** `src/ais/phase1/` (biblioteca) e `src/ais/cli/` (programas, `python -m ais.cli.<nome>`); lista em `README.md` e em `docs/02` §4. O janelamento está em `windows.py`, `run_window_training`, `select_windows_on_test` e `build_window_results`; ainda não existe código de pós-processamento.
- **Testes:** 181 sintéticos (mais um que lê 3 viagens de treino), todos a passar (`pytest tests/`).
- **Dados:** `data/123_fishing_trajs.csv`, 123 viagens e 1 026 279 linhas (REV-007). Bases limpas em `data/123_fishing_trajs_clean_{train,validation,test}.parquet`, com 713 854, 209 016 e 103 409 linhas (87, 18 e 18 viagens). Manifesto `manifests/split_manifest_seed42.csv` (versionado).
- **LaTeX:** `latex/proposta_pt.tex` compila (11 páginas; limite de 15). Texto estável a preto (REV-043); o novo (4.4, Secção 5 em partes, 7.1, Secção 6 e 8.2 a 8.4) tem a cor de REV-046 `#00B0FF`, REV-047 `#4A148C` e REV-048 `#1B5E20`.
- **Git:** os commits locais de REV-046 a REV-048 (a partir de `9896021`) **não foram enviados**; o último estado em `origin/main` no início desta sessão era `696fed2`. Confirmar com `git status -sb`; cada push precisa de autorização explícita nova do utilizador.
- **Registo de revisões:** `REVISION_LOG.md` com REV-001 a REV-048.

## Decisões do utilizador (vigentes)

- **Divisão (REV-001, REV-002):** seed 42; 70/15/15 por ID completo (viagem); validação e teste arredondados ao inteiro mais próximo. Fuso horário de `t` ignorado. Viagens do mesmo navio podem estar em conjuntos diferentes; **a questão dos navios partilhados foi desconsiderada** (sem quantificar, sem refazer, sem declarar no texto).
- **Dados (REV-012, REV-019, REV-011, REV-022):** limpeza IQR retirada; anomalias mantidas; `bearing` pela grelha UTM; `distanceToShore` aceite como correto; características `speed`, `signed_turn`, `time_gap` e `distanceToShore` (`x` e `y` fora); valores em falta a zero depois de normalizar, mais máscara.
- **Baseline fechada (REV-041):** a CNN sobre a viagem completa fica como está (época 162, limiar 0,65); só volta na comparação com as janelas e na escolha final.
- **Papéis dos conjuntos reservados (REV-036):** `test` seleciona; `validation` é a medição final, aberta uma só vez, no fim, com todas as variantes congeladas (REV-037).
- **Marco 4 (REV-041, REV-046):** mesma CNN, mesmos valores da baseline (300 épocas, lr 1e-3, seed 42), sobre janelas de L = 64 com 0 % (J0) e 50 % (J50), lote de 32; a sobreposição é a mesma no treino e na inferência; a última janela fica mais curta (sem pontos falsos); os intervalos de tempo dentro de uma viagem não cortam a sequência; seleção no `test` numa só abertura com o critério da baseline; limite de 45 min por treino; se a época escolhida for ≥ 291 só se regista. **Ficam fora do projeto:** treinar com J0 e prever com J50, 25 % e 75 % de sobreposição, outros L (REV-002).
- **Âmbito (REV-006, REV-042):** HMM e Wu et al. não são comparações (só literatura). Explicabilidade, calibração e *dashboard* fora do mínimo atual.
- **LaTeX (REV-006, REV-043):** `latex/proposta_IAHC_DINIS_ROSA.pdf` não se altera; texto estável a preto, o que pode mudar mantém a cor. Manifesto da divisão versionado. Autor do dataset: Song Wu, Zenodo DOI 10.5281/zenodo.7283281 (CC BY 4.0); o Kaggle é espelho.

## Pendências abertas

- **Critério de seleção (decisão do utilizador):** a menor perda por ponto no `test` escolheu épocas muito cedo (4 e 8), porque a perda no `test` sobe com o treino; a baseline foi escolhida bem mais tarde (162). Mudar o critério (por exemplo, o F1) ou travar o treino mais cedo seria uma decisão metodológica nova, com novo protocolo e nova autorização, e obrigaria a repetir a baseline por igualdade. Por agora fica como está, registado como limitação.
- **Marco 5 e Marcos 6 e 7:** o pós-processamento só avança se o utilizador o decidir; a medição final no `validation` precisa de autorização nova e de todas as variantes congeladas.
- **LaTeX (adiado pelo utilizador):** explicabilidade, calibração e *dashboard* (resumo, objetivo 5, 4.6, 7.3); título com «OOI» e o texto a vermelho «human-on-the-loop»; subsecções 5.3 a 5.6 e 6.1 por reler pelo utilizador; a 7.1 ainda descreve a ablação completa (agora marcada como futura).
- **Pós-processamento (Marco 5):** unidade, largura e bordas do filtro a aprovar, só se o Marco 4 mostrar benefício.
- **Técnicas:** testes dos programas de treino, de figuras e de geração de resultados; unificar `class_metrics`; apagar os restos do ensaio de 3 viagens e das execuções antigas.
- **Dúvidas de dados:** CRS de longitude e latitude (hipótese WGS84); proveniência das anotações; método de cálculo de `distanceToShore`.

## Artefactos do projeto

| Ficheiro | Estado |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `README.md`, `handoff.md` | Alinhados em REV-044; `AGENTS.md` §3 com os papéis dos conjuntos (REV-036) |
| `docs/00` a `docs/03` | Fundidos em REV-033; atualizados em REV-036, REV-038, REV-041, REV-044 e REV-046 (`docs/03` reescrito) |
| `src/ais/phase1/`, `src/ais/cli/` | Código do projeto (REV-034 a REV-040) |
| `pyproject.toml` | Pacote `ais` e configuração do pytest (REV-034) |
| `tests/` | 181 testes |
| `configs/` | `phase1_select.json` (baseline), `selection_protocol.json`, `authorizations/test_selection.json`; `windows_j0.json`, `windows_j50.json`, `selection_protocol_windows.json`, `authorizations/test_selection_windows.json` (REV-046, REV-047); históricos `phase1_run1.json` e `phase1_final.json` |
| `manifests/split_manifest_seed42.csv` | Gerado; **versionado** (REV-006) |
| `latex/proposta_pt.tex`, `latex/references.bib`, `latex/figures/`, `latex/generated/resultados.tex`, `latex/generated/resultados_janelas.tex` | Proposta; macros e figuras geradas por `build_final_results` e `build_window_results` |
| `latex/proposta_IAHC_DINIS_ROSA.pdf` | Versão entregue ao professor; **não se altera** |
| `data/`, `results/`, `latex/build/` | Gerados; não versionados |
| `results/baseline_frozen/`, `results/phase1_select/`, `results/access_log.jsonl` | Baseline, seleção e registo de acessos (REV-038) |
| `results/windows_j0/`, `results/windows_j50/`, `results/windows_j0_frozen/`, `results/windows_j50_frozen/`, `results/windows_final/` | Treinos (checkpoints por época, histórico), seleção, congelações e `final_results_windows.json` (REV-046, REV-047) |

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

### 2026-11-23ai — Figuras do ensaio num anexo (REV-031)

**Feito**
- Figuras 3 e 4 movidas da subsecção 7.4 para o Anexo A, depois das referências; remissão no texto.
- O utilizador fez o push dos commits até `005b0f5` para `origin/main` (o pendente «push» das entradas anteriores fica resolvido até esse commit).

**Validado**
- `pdflatex` sem erros nem referências em falta (7 páginas); páginas 5 a 7 vistas.

**Pendente**
- Commit local desta alteração por autorizar; push por conta do utilizador.
- Substituir as figuras marcadoras pelos resultados reais. Decisões de treino em aberto.

### 2026-11-23aj — Vigilante do LaTeX limpa o `build/`

**Feito**
- `scripts/watch_latex.sh` (não versionado, está no `.gitignore`): depois de cada compilação bem-sucedida apaga os ficheiros soltos de `latex/build/` exceto o PDF (`.aux`, `.bbl`, `.blg`, `.log`, `.out`). Se a compilação falha, mantém-nos para se ver o erro. Não toca em subpastas (`build/check/`).
- Limpeza única dos auxiliares que já estavam em `latex/build/`.

**Validado**
- Testado numa cópia isolada do projeto (sem tocar no `build/` real): sucesso deixa só o PDF; erro mantém `.aux`, `.bbl`, `.blg`, `.log` e `.out`. Sintaxe verificada com `bash -n`.

**Pendente**
- O vigilante já em execução continua com a versão antiga até ser reiniciado (Ctrl+C e `bash scripts/watch_latex.sh`).

### 2026-11-23ak — Push autorizado pelo utilizador

**Feito**
- A pedido explícito do utilizador no chat, executei `git push origin main` (`005b0f5..4752fc1`, sem `--force`). Foi uma autorização pontual: a regra do `AGENTS.md` §6 (push exclusivo do utilizador) mantém-se para os pushes seguintes, que exigem nova autorização.

**Pendente**
- Decisões de treino do utilizador: partição interna, lr, épocas, critério de paragem, orçamento de tempo.
- Esta entrada fica num commit local, por enviar (push por autorização).

### 2026-11-23al — Medição da velocidade de treino em CPU

**Feito**
- `scripts/benchmark_training_speed.py`: mede o tempo de treino da CNN 1D (CPU, 10 threads, seed 42, lr 1e-3) com 1 viagem, 2 viagens e a maior viagem do treino (2 épocas de aquecimento descartadas, 20 medidas, 3 repetições). Saídas em `results/benchmark_speed/` (não versionadas). Só treino oficial.
- Medido (mediana da época): 1 viagem (5 475 pontos) 0,013 s; 2 viagens (10 853 pontos) 0,040 s; maior viagem do treino `235008380-3` (45 251 pontos) 0,151 s. Cerca de 2,4 a 3,7 µs por ponto em treino e 1,0 a 1,6 µs por ponto em avaliação.
- Projeção por nº de pontos (estimativa, não medição): época sobre o treino todo (713 854 pontos) entre 1,7 e 2,6 s; 100 épocas entre 2,8 e 4,4 min. Pico de memória do processo medido: cerca de 822 MB.
- A maior viagem do treino tem 45 251 pontos (não 23 151, que era a maior das 6 do ensaio).

**Validado**
- Script executado duas vezes (corrigida uma coluna enganadora da projeção). Sem teste automático.

**Limitações**
- Poucas viagens e custo assumido proporcional ao nº de pontos; variação entre épocas visível (ex.: 0,023 a 0,053 s com 2 viagens). A projeção para as 74 e 87 viagens tem de ser confirmada medindo.

**Pendente**
- Decisões do utilizador (partição interna, lr, épocas, paragem, orçamento); commit local do script e desta entrada por autorizar.

### 2026-11-23am — Primeira execução de treino da CNN 1D (REV-032)

**Feito**
- Utilizador aceitou os valores propostos: partição interna 15 % (13 de 87), lr 1e-3, máx. 100 épocas, paragem antecipada (paciência 10, melhor checkpoint), orçamento 15 min.
- Implementados checkpoints, configuração validada, métricas por classe e `train_model`; 19 testes novos (94 no total).
- Treino real só com o treino oficial: base inteira validada; 74 viagens de ajuste e 13 de monitorização; scaler só do ajuste. Parou por paragem antecipada após 16 épocas (39,4 s); melhor época 6. Accuracy 92,15 % no ajuste e 95,00 % na monitorização (maioritária 74,46 %). Artefactos em `results/phase1_run1/` (não versionados).
- LaTeX: subsecção «Primeira execução de treino» e correção de frases desatualizadas.

**Validado**
- `pytest`: 94 passaram. Checkpoint recarregado do disco para as previsões. `pdflatex` sem erros (8 páginas). Figuras inspecionadas. Validação e teste oficiais não abertos.

**Problemas e limitações**
- Bug apanhado pelos testes: `torch.__version__` impedia o carregamento seguro do checkpoint; corrigido.
- Monitorização de 13 viagens é ruidosa; o critério de paragem pode ter parado cedo (perda ainda a descer nas épocas 15 e 16). Rede possivelmente subajustada (ajuste pior que monitorização). Resultados provisórios.
- Observação visual (não quantificada): erros em blocos longos de navegação previstos como pesca e fragmentação da pesca em duas viagens.

**Pendente**
- Decidir se se repete com paciência maior ou outro lr; medir erros por tipo com código; substituir figuras do anexo; commit local por autorizar; push por autorização.

### 2026-11-23an — Handoff reescrito para nova conversa

**Feito**
- `handoff.md` reescrito de raiz: como retomar, objetivo, estado atual (incluindo o que está por commitar), decisões vigentes, tabela de ficheiros, comandos úteis, ensaio curto, medição de velocidade, primeira execução de treino, o que falhou, próximos passos, regras e preferências do utilizador. Inclui a lista de cores de revisão em uso e o próximo ID livre (REV-033).

**Validado**
- Estado conferido contra `git status`, `git log`, `pytest` (94 passaram) e `REVISION_LOG.md`. Sem alterações a código nem a dados.

**Pendente**
- Commit local do trabalho de REV-032 e deste ficheiro, por autorizar. Push por autorização.

### 2026-11-23ao — Commits locais de REV-032

**Feito**
- Três commits locais autorizados pelo utilizador: `2b5197c` (código, configuração, scripts e testes), `2a177ac` (LaTeX) e `e9fef3c` (registos, `docs/05` e handoff). Nenhum push.
- `handoff.md` corrigido para refletir que o trabalho está commitado e que há commits por enviar.

**Pendente**
- Push, por autorização do utilizador. Decisão sobre repetir o treino (paciência maior ou outro lr).

### 2026-11-23ap — Fusão e simplificação dos docs (REV-033)

**Feito**
- Leitura integral de `AGENTS.md`, `handoff.md`, `README.md` e dos oito documentos de `docs/`, comparados com o código real.
- Os oito documentos passam a quatro (`docs/00_projeto_e_decisoes`, `01_dados_e_preparacao`, `02_cnn_viagem_completa`, `03_cnn_janelamento`), de cerca de 1 900 para 386 linhas. Removidos o texto repetido, o que já estava cumprido, o KNIME e o contrato de 25 funções de preparação nunca implementadas. Atualizados nomes das características, overlaps prioritários e estado dos marcos.
- Referências corrigidas em `README.md`, `AGENTS.md` §1, `handoff.md`, nas secções vivas deste ficheiro e em dois docstrings. Corrigidos também pontos desatualizados do «Estado atual» e do Marco 1 neste ficheiro.

**Validado**
- Releitura contra `src/phase1/`, `scripts/`, `configs/` e `REVISION_LOG.md`; procura de referências pendentes aos nomes antigos. Não foram executados testes nem código.

**Problemas e limitações**
- Entradas históricas continuam a citar nomes antigos de `docs/`, por serem registo.

**Decisões**
- Estrutura de quatro documentos escolhida por mim, a pedido do utilizador de simplificar; sujeita a revisão.

**Pendente**
- Revisão do utilizador; commit local por autorizar; push por autorização. Decisão sobre repetir o treino (paciência maior ou outro lr).

### 2026-11-23aq — Código unificado em `src/ais/` (REV-034)

**Feito**
- A pasta `scripts/` e o antigo `src/phase1/` passam a um só pacote: `src/ais/phase1/` (biblioteca) e `src/ais/cli/` (os 10 programas). Movido com `git mv`, para preservar o histórico. `watch_latex.sh` (não versionado) passou para `latex/`.
- Criado `pyproject.toml` mínimo (pacote `ais`, `pythonpath` do pytest). Instalado em modo editável **só** no `iach-ais-venv-4/`, sem rede e sem dependências novas. Removidos os três `sys.path.insert` e o `tests/conftest.py`.
- Comandos passam a `iach-ais-venv-4/bin/python -m ais.cli.<nome>`. Imports, raízes do projeto (`parents[3]`), campos de proveniência e documentos vivos atualizados; entradas históricas deste ficheiro e do `REVISION_LOG.md` ficam com os caminhos antigos.

**Validado**
- `pytest tests/`: 94 passaram. Importados os 20 módulos de `ais`. `python -m ais.cli.verify_trip_count` correu e confirmou 123 viagens (só lê o `id`). Os restantes programas não foram executados; só mudaram imports, a raiz do projeto e textos.

**Problemas e limitações**
- Os programas de treino, figuras e benchmark não foram reexecutados (para não sobrescrever `results/`); o ajuste de raiz e imports neles está só verificado por importação.
- Lógica de preparação continua dentro dos programas de `cli/` (ex.: `build`, `assign_splits`) e `class_metrics` continua duplicada. Não se mudou lógica.

**Pendente**
- Revisão do utilizador; commit local por autorizar. Mover a lógica de preparação reutilizável para `ais/` e unificar `class_metrics`, se o utilizador quiser.

### 2026-11-23ar — Treino final com todo o treino e números do LaTeX gerados (REV-035)

**Feito**
- Treino final da CNN 1D com as 87 viagens do treino oficial, sem monitorização interna (`configs/phase1_final.json`: seed 42, lr 1e-3, máx. 100 épocas, paciência 30 sobre a perda no treino). Terminou ao atingir as 100 épocas (melhor época 95) em cerca de 361 s; accuracy no treino 94,6 % contra 75,4 % da maioritária.
- `ais.cli.build_final_results` escreve o ficheiro único `results/phase1_final/final_results.json`, as macros `latex/generated/resultados.tex` e três figuras. O LaTeX passou a usar essas macros; removidos o ensaio de 3 viagens e o Anexo A. A subsecção do treino foi reescrita.

**Validado**
- `pytest tests/`: 99 passaram. Hash da base de treino e do manifesto confere com os sumários da preparação. `pdflatex` + `bibtex` sem erros (7 páginas), páginas inspecionadas. Validação e teste oficiais não foram abertos.

**Problemas e limitações**
- Métricas medidas no próprio treino (ajuste, não generalização). A paragem antecipada não disparou: a rede pode não ter convergido.
- «Paciência 30 e 0 % de monitorização» exigiu uma interpretação (critério = perda no treino); a monitorização com os 15 % reservados fica para a etapa de validação, com autorização.

**Decisões**
- Todos os números do LaTeX vindos de código passam a macros geradas; nenhum se escreve à mão.

**Pendente**
- Decidir se se treina mais épocas; commit local por autorizar; push por autorização.

### 2026-11-23as — Papéis dos conjuntos reservados (REV-036)

**Feito**
- Atualizada a regra dos conjuntos reservados a pedido do utilizador: `test` = seleção (épocas, limiar, treinar mais, variantes); `validation` = medição final única com o modelo congelado. `AGENTS.md` §3, `docs/00`, `docs/02`, `docs/03`, `handoff.md` e a subsecção do protocolo no LaTeX alinhados.

**Validado**
- Procura de contradições nos documentos; `pdflatex` + `bibtex` sem erros (7 páginas). Nada foi aberto: validação e teste continuam por abrir (exceto o que consta em REV-015).

**Problemas e limitações**
- Resultados no `test` serão otimistas por terem servido a selecionar. O `test` é mais pequeno que o `validation`, logo a seleção é mais ruidosa.

**Decisões**
- Papéis trocados face ao habitual, por decisão do utilizador; nomes dos ficheiros mantidos.

**Pendente**
- Autorização explícita para abrir o `test`, com o âmbito declarado; programa de avaliação reservada com registo de acessos; plano da seleção; commit local por autorizar.

### 2026-11-23au — Fases 1 a 5 do plano: seleção no `test`, baseline congelada e métricas por segmento (REV-037 a REV-039)

**Feito**
- Plano atualizado (REV-037). Protocolo de seleção e autorização gravados antes de abrir o `test` (`configs/selection_protocol.json`, `configs/authorizations/test_selection.json`).
- Treino de seleção: só treino (87 viagens), 300 épocas, um checkpoint por época (1164 s). Seleção no `test` numa só ronda: época 162, limiar 0,65 (`results/phase1_select/selection_test.json`). Baseline congelada em `results/baseline_frozen/`. O `validation` **não** foi aberto.
- Código de acesso reservado, seleção, congelação e inferência como módulo (REV-038). Subagentes: métricas por segmento (Sonnet) e navios partilhados (Haiku), ambos revistos e conferidos por mim (REV-039).

**Validado**
- `pytest`: 145 passaram. Verificação do hash do checkpoint congelado. Contagens de navios recalculadas com lógica independente; segmentos reimplementados com loops puros e iguais à ferramenta sobre as previsões do treino.

**Problemas e limitações**
- A perda no `test` é muito ruidosa entre épocas; a época 162 é um mínimo estreito e a seleção usa só 18 viagens. Os resultados no `test` são otimistas.
- O `test` tem 61 % de pesca e o treino 75 %. Metade das viagens reservadas vem de navios presentes no treino.
- LaTeX desatualizado em relação à baseline congelada (pendente).
- Durante o treino, testes e subagentes em paralelo abrandaram-no muito; o orçamento chegou, mas foi apertado.

**Decisões**
- Autorização lida a partir da instrução do utilizador e registada com a citação literal; o âmbito ficou limitado a uma ronda no `test`.

**Pendente**
- O utilizador decide como lidar com o ruído da seleção; atualizar o LaTeX; commit local por autorizar; Marco 4 (janelas) fica por iniciar, como pedido.

### 2026-11-23av — LaTeX atualizado com a baseline congelada (REV-040)

**Feito**
- Decisão do utilizador: manter a divisão por viagem e desconsiderar os navios partilhados (sem quantificar, sem refazer, sem declarar no texto).
- `build_final_results` reescrito para a baseline congelada. LaTeX reescrito: 300 épocas, seleção no `test`, tabela e figuras com treino e teste, todos os números vindos de macros geradas de `results/baseline_frozen/final_results.json`.

**Validado**
- Verificações de proveniência (hashes, `validation` por abrir, `test` aberto uma só vez) a passar; PDF compilado (7 páginas) e inspecionado; sem macros indefinidas; `pytest` 145 passaram.

**Problemas e limitações**
- Resultados do `test` otimistas e perda do `test` ruidosa (ambos escritos no texto). O gerador só tem teste das funções de formatação.

**Pendente**
- Decisão sobre o ruído da seleção; commit local por autorizar; Marco 4.

### 2026-11-23aw — Commits locais e push (REV-035 a REV-040)

**Feito**
- Oito commits locais por tema (`2d7fb39` a `3d8bc0c`), com mensagem completa e ficheiros selecionados à mão. Push de `main` para `origin` (`8f6857d..3d8bc0c`), autorizado pelo utilizador na mensagem desta sessão («dou-te permissão para dares push no final»), sem *force*.

**Validado**
- `pytest` no HEAD: 145 passaram. Só o manifesto aprovado está versionado como dados; nenhum parquet, checkpoint nem `results/`.

**Problemas e limitações**
- Os commits intermédios não foram testados isoladamente (só o estado final). A autorização de push foi pontual: o próximo push precisa de nova autorização.

**Pendente**
- Decisão sobre o ruído da seleção; Marco 4.

### 2026-11-23ax — Baseline fechada e LaTeX reestruturado (REV-041)

**Feito**
- Decisão do utilizador: baseline (CNN 1D sobre a viagem completa) fechada como está; Marco 4 = a mesma CNN sobre janelas (L = 64; 0 % e 50 %; depois outros L).
- LaTeX: 4.2 «CNN de referência» sem duplicar a Secção 5; Secção 5 serve as duas experiências; 4.4 (janelamento) definida; nova Secção 8 «Resultados» (8.1 viagem completa, 8.2 janelamento por fazer). Docs, README e handoff alinhados.

**Validado**
- `pdflatex` + `bibtex` sem erros (8 páginas), páginas 3 e 7 inspecionadas. Sem alterações a código nem a números.

**Problemas e limitações**
- Partes do relatório não revistas: ver REV-041 (resumo, secções 1 a 3, 6 e 7, título com «OOI»). Citam HMM e Wu et al. e quatro taxas de sobreposição, contra o âmbito atual.

**Decisões**
- Baseline fechada e finalizada; só volta na comparação final.

**Pendente**
- Rever essas passagens; decisões do Marco 4; commit local por autorizar.

### 2026-11-23ay — HMM e Wu et al. deixam de ser comparações no LaTeX (REV-042)

**Feito**
- Resumo, objetivo 2, critérios de sucesso, Avaliação 7.1 e exemplo do pós-processamento corrigidos: a comparação é entre a CNN de referência (viagem completa) e a CNN com janelas. HMM e Wu et al. ficam só como literatura na Contexto.

**Validado**
- `pdflatex` + `bibtex` sem erros (8 páginas); página 1 inspecionada; procura por HMM, Wu e «baseline» no PDF.

**Pendente**
- Restantes passagens de REV-041 (quatro taxas de sobreposição e ablação, explicabilidade e dashboard, título «OOI», «human-on-the-loop», Secção 6 no futuro); commit local por autorizar; decisões do Marco 4.

### 2026-11-23az — Texto estável do LaTeX a preto (REV-043)

**Feito**
- Por instrução do utilizador, o texto que considero estável passa a preto (objetivos 1 e 2, 4.1 a 4.3, Secção 5 exceto janelas, Secção 6, 7.2, 8.1) e o que ainda pode mudar mantém a cor (janelamento, pós-processamento, saída, 7.1, 7.3, 8.2 e partes de janelas). Lista completa em REV-043.

**Validado**
- Texto extraído do PDF antes e depois: igual. Compilação sem erros (8 páginas); páginas 3 e 6 inspecionadas.

**Problemas e limitações**
- «Preto» não significa «revisto pelo utilizador». Texto original sem cor que ainda pode mudar (ablação e quatro taxas de sobreposição em 7.1) fica a preto sem estar fechado.

**Pendente**
- Passagens abertas de REV-041 e REV-042; decisões do Marco 4.

### 2026-11-23ba — Handoff reescrito e documentos alinhados (REV-044)

**Feito**
- `handoff.md` reescrito de raiz para outra sessão (data, como retomar, objetivo, estado, decisões, ficheiros, comandos, resultados e ensaios, o que falhou, próximos passos, regras e preferências).
- `PROGRESS.md`: estado, decisões, pendências e artefactos passam para o topo e foram atualizados; removidos os blocos antigos (pendentes por marco, pendências e tabela de artefactos) que estavam a meio do histórico.
- `README.md` reescrito; `docs/00`, `docs/02` e `docs/03` limpos: apagados a descrição da execução antiga (§3 do `docs/02`), as linhas «Por fazer» de coisas já substituídas e a referência ao ensaio retirado.

**Validado**
- Procura de contradições entre README, PROGRESS, handoff e docs (estado dos marcos, contagem de testes, caminhos, REV); `pytest`: 145 passaram. Código e LaTeX não foram alterados.

**Problemas e limitações**
- Nenhum documento dos `docs/` ficou inteiro por apagar: todos têm conteúdo ainda útil (o `docs/03` descreve o Marco 4, por fazer).

**Pendente**
- Pendências abertas listadas no topo deste ficheiro. Push dos commits de REV-044 feito em `d1f30e0..1bc3d8c`, autorizado pelo utilizador.

### 2026-11-23bb — Handoff com data e hora (REV-045), 2026-11-23 19:42 WET

**Feito**
- `handoff.md`: data e hora da atualização, tabela «Última validação» (testes e LaTeX às 19:41 WET, estado do git, geração e congelação da baseline, seleção no `test`, `validation` por abrir) e cronologia dos últimos commits. Regra nova em `AGENTS.md` §5.

**Validado**
- `pytest`: 145 passaram; `pdflatex` + `bibtex`: 8 páginas, 0 erros (19:41 WET). Horas lidas do relógio, do `git log` e dos ficheiros de resultados.

**Pendente**
- Pendências abertas do topo deste ficheiro; push dos commits de REV-045, por autorização.

### 2026-11-23bc — Janelamento: J0 e J50 treinadas, selecionadas e na proposta (REV-046, REV-047, REV-048), 2026-11-23 23:34 WET

**Feito**
- Respostas do utilizador às dúvidas do Marco 4 registadas (mesma sobreposição no treino e na inferência; mesmos valores da baseline; última janela mais curta; lote de 32; 45 min por treino; uma abertura do `test`; `validation` fechado; fora do projeto: 25 %, 75 %, outros L e treinar com J0 e prever com J50).
- `windows.py` e `FullTripCNN.forward` com máscara; programas de treino, de seleção e de resultados; configurações, protocolo e autorização novos. Treino de J0 (9,8 min) e de J50 (21,3 min), ambos completos.
- **Uma só abertura do `test`** (23:28:19 WET): épocas e limiares escolhidos (J0 época 8, limiar 0,60; J50 época 4, limiar 0,75); baseline, J0 e J50 medidas por ponto e por segmento; J0 e J50 congeladas.
- Resultados, macros e figuras gerados por código; LaTeX com as secções 8.2, 8.3 e 8.4, e 4.4, Secção 5, 7.1 e Secção 6 atualizadas. `docs/03` reescrito, `README.md`, `docs/00` e `docs/02` alinhados.
- Commits locais por tema (código, seleção, LaTeX e documentos); **nada enviado**.

**Validado**
- 181 testes sintéticos passaram; seleção testada de ponta a ponta com dados sintéticos antes de abrir o `test` real. Revisão independente (Opus, só leitura) sem erros graves. Proveniência confirmada no `final_results_windows.json`: `test` aberto duas vezes (uma por autorização), `validation` nunca aberto, hashes coerentes.
- `pdflatex` + `bibtex`: 11 páginas, 0 erros, 0 referências indefinidas.

**Resultados e limitações**
- J0 e J50 não superam a referência por ponto no `test` (93,5 % e 93,8 % contra 94,7 %); J50 reduz a fragmentação face a J0 e à referência, mas a segmentação continua muito fragmentada e o F1 de segmentos de pesca é baixo nas três. Os erros de fronteira na pesca não mostram padrão (5 ou 6 pares). Reportado como saiu, sem repetir nem ajustar.
- As épocas escolhidas (4 e 8) são muito cedo: a perda no `test` sobe com o treino. O critério fixado antes é o da baseline e não foi alterado. Lote e passos diferem da baseline; J50 faz o dobro dos passos de J0. Uma semente, 18 viagens de teste, resultados otimistas.
- Duas das cores escolhidas primeiro já pertenciam a REV-007 e REV-011 e foram trocadas antes do commit com cor.

**Pendente**
- Decisão do utilizador: manter o critério de seleção ou mudar (novo protocolo e autorização); Marco 5 (só com decisão); Marcos 6 e 7 (autorização). Passagens adiadas do LaTeX (explicabilidade, calibração e *dashboard*, título «OOI», «human-on-the-loop»). Push dos commits locais, por autorização do utilizador.
