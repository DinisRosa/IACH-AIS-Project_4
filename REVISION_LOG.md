# REVISION_LOG — Projeto AIS

Registo das revisões lógicas dos documentos (AGENTS.md §8). Cada revisão tem um ID sequencial estável e uma cor. O ID é a referência permanente; a cor é apenas auxiliar.

Regras:
- IDs sequenciais (REV-001, REV-002…) e nunca renumerados.
- Uma revisão pode abranger vários ficheiros e commits.
- Marcador no Markdown: `[REV-00N | cor #RRGGBB]`.
- Correspondência no LaTeX: `atualizado`, `não aplicável` ou `pendente` (com motivo).

## Paleta

| ID | Cor | Hexadecimal | RGB |
|---|---|---|---|
| REV-001 | Vermelho | `#C62828` | (198, 40, 40) |
| REV-002 | Azul | `#1565C0` | (21, 101, 192) |
| REV-003 | Verde | `#2E7D32` | (46, 125, 50) |
| REV-004 | Roxo | `#6A1B9A` | (106, 27, 154) |
| REV-005 | Azul-petróleo | `#00838F` | (0, 131, 143) |
| REV-006 | Castanho | `#6D4C41` | (109, 76, 65) |
| REV-007 | Rosa | `#AD1457` | (173, 20, 87) |
| REV-008 | Verde-azulado | `#00695C` | (0, 105, 92) |
| REV-009 | Índigo | `#283593` | (40, 53, 147) |
| REV-010 | Ocre | `#8D6E00` | (141, 110, 0) |
| REV-011 | Laranja | `#E65100` | (230, 81, 0) |
| REV-012 | Cinzento-ardósia | `#455A64` | (69, 90, 100) |
| REV-013 | Oliva | `#808000` | (128, 128, 0) |
| REV-014 | Lilás | `#9575CD` | (149, 117, 205) |
| REV-015 | Turquesa | `#26A69A` | (38, 166, 154) |
| REV-016 | Amarelo-torrado | `#F57F17` | (245, 127, 23) |
| REV-017 | Rosa-choque | `#FF4081` | (255, 64, 129) |
| REV-018 | Azul-ardósia | `#5C6BC0` | (92, 107, 192) |
| REV-019 | Azul-celeste | `#0288D1` | (2, 136, 209) |
| REV-020 | Cinzento-azulado | `#607D8B` | (96, 125, 139) |
| REV-021 | Magenta | `#D500F9` | (213, 0, 249) |
| REV-022 | Verde-azulado escuro | `#00897B` | (0, 137, 123) |

## Revisões

### REV-001 — Confirmação da seed e das proporções da divisão

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Vermelho `#C62828`, RGB (198, 40, 40).
- **O quê:** confirmada a seed `42` e a divisão 70/15/15 por ID completo. Regra de arredondamento: validação e teste arredondados ao inteiro mais próximo; treino recebe o resto.
- **Porquê:** a divisão tem de estar fixada antes de qualquer exploração (docs/01 §2-§3).
- **Ficheiros e secções afetados:**
  - `docs/01_preparacao_comum.md` §3: proporções e seed marcadas como confirmadas.
  - `docs/00_contexto_projeto_dicionario_dados.md` §15, ponto 2.
  - `scripts/create_split_manifest.py` (novo): gera o manifesto.
  - `manifests/split_manifest_seed42.csv` (gerado, não versionado pela regra `*.csv`).
- **Correspondência no LaTeX (`latex/proposta_pt.tex`):** **pendente**. A proposta original fala em divisão por navio. Falta decidir se o texto da proposta deve refletir a divisão por viagem. Não alterado nesta revisão.
- **Validação:**
  - Manifesto: 123 IDs (87 treino, 18 validação, 18 teste). Cada ID num só conjunto; cobertura completa; soma das linhas = 1 026 279.
  - Reexecução do script dá o mesmo SHA-256 (`d56918bc65f9bebc6aa0a01a1e82213fda2404a9dfab9f39b3a1858c52733539`).
- **Pendentes:**
  - Diferença 128 (documentos) vs 123 (ficheiro e LaTeX): documentos corrigidos em REV-004. Por fechar no PDF da proposta, se o PDF ainda disser 128.
  - Decidir se o manifesto deve ser versionado.

### REV-002 — Decisões de âmbito: overlaps prioritários e fuso horário ignorado

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul `#1565C0`, RGB (21, 101, 192).
- **O quê:**
  - Os overlaps 0% e 50% são prioritários. Os 25% e 75% ficam para decisão posterior.
  - O fuso horário de `t` é ignorado. Não é necessário para o projeto.
- **Porquê:** decisões explícitas do utilizador.
- **Ficheiros e secções afetados:**
  - `docs/00_5_orientacoes_execucao_decisoes.md` (secção "Protocolo e dúvidas"): pergunta substituída pela decisão.
  - `docs/00_contexto_projeto_dicionario_dados.md` §18: fuso horário marcado como ignorado.
- **Correspondência no LaTeX:** **não aplicável**. A proposta não define a prioridade dos overlaps.
- **Validação:** não aplicável (decisão, não código).
- **Pendentes:**
  - Decidir mais tarde se os overlaps 25% e 75% entram no âmbito.

### REV-003 — Verificação de unidades e convenções no treino

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde `#2E7D32`, RGB (46, 125, 50).
- **O quê:** registados os resultados de `scripts/check_units_train.py` sobre o conjunto de treino. Confirmadas as unidades de `x`, `y`, `distance_gap`, `time_gap`, `euc_speed`, `bearing` e `signed_turn`. `distanceToShore` ficou por confirmar.
- **Porquê:** as unidades têm de estar confirmadas antes de recalcular variáveis (docs/01 §5).
- **Ficheiros e secções afetados:**
  - `scripts/check_units_train.py` (novo).
  - `docs/00_contexto_projeto_dicionario_dados.md` §18: subsecção "Estado das dúvidas".
  - `requirements.txt`: `matplotlib==3.10.9` (necessário para gerar os gráficos).
  - `results/units_check_train/` (gráficos e `summary.json`, gerados, não versionados).
- **Correspondência no LaTeX:** **pendente**. Não há impacto metodológico na proposta, mas as unidades devem ser refletidas no texto quando a proposta for revista.
- **Validação:**
  - Execução apenas sobre o treino: 713 854 linhas e 713 767 pares consecutivos. Validação e teste não foram lidos além do `id`.
  - Reexecução e hashes registados em `summary.json`.
- **Resultados (medianas):**
  - `x`/`y` vs haversine ≈ 1,002. `distance_gap` / distância plana = 1,0000. Logo, x/y e `distance_gap` em metros num referencial plano.
  - `time_gap` / Δt = 1,0. Logo, segundos.
  - `euc_speed` / (`distance_gap`/`time_gap`) = 1,94384. Logo, nós.
  - `bearing` = azimute inicial do ponto anterior para o atual. Logo, graus a partir do norte.
  - `signed_turn` = variação de `bearing`, normalizada para (-180, 180]. Logo, graus.
- **Anomalias não quantificadas:** `distance_gap` com razão mínima ~0,48; `time_gap` com razão mínima 1/3; `signed_turn` com diferença máxima ~175°.
- **Pendentes:**
  - Quantificar e tratar as anomalias no marco 2 (limpeza).
  - `distanceToShore`: unidade não confirmada. Metros é a hipótese mais plausível.
  - CRS exato de x/y e de longitude/latitude.

### REV-004 — Coerência documental após REV-001 a REV-003

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Roxo `#6A1B9A`, RGB (106, 27, 154).
- **O quê:** alinhamento de todos os Markdown com o estado real do projeto.
  - `PROGRESS.md`: reescrito com estado atual, artefactos e pendentes. Removido "REVISION_LOG por criar".
  - `AGENTS.md`: exemplos de ambiente trocados de `.venv` para `iach-ais-venv-4`; referência à seed 42 e ao manifesto; referência ao `latex/proposta_pt.tex` existente.
  - `README.md`: estrutura completa (scripts, manifests, requirements, REVISION_LOG, PROGRESS, results).
  - `docs/00`: número de viagens corrigido (123 IDs no ficheiro); tabela de unidades atualizada com os resultados de REV-003; dúvidas atualizadas.
  - `docs/00_5`: estado do código atualizado (executado sobre treino; modelos ainda não).
  - `docs/01`: regra de arredondamento definida (REV-001).
- **Porquê:** a documentação tinha afirmações que já não correspondiam ao estado do projeto, como "ainda não existe" e "hipótese" para unidades já verificadas.
- **Ficheiros afetados:** `PROGRESS.md`, `REVISION_LOG.md`, `AGENTS.md`, `README.md`, `docs/00_contexto_projeto_dicionario_dados.md`, `docs/00_5_orientacoes_execucao_decisoes.md`, `docs/01_preparacao_comum.md`.
- **Correspondência no LaTeX (`latex/proposta_pt.tex`):** **pendente**. O ficheiro não foi alterado. Há contagens diferentes (86/19/18 vs 87/18/18), descrições de implementações que não existem e uma lista de características diferente. Ver `PROGRESS.md`, secção "Inconsistências do LaTeX".
- **Validação:** pesquisa por texto desatualizado (`.venv`, "ainda por criar", "128", "70/15/15", "hipótese" nas unidades) em todos os MDs, e revisão dos resultados.
- **Pendentes:**
  - Decidir como tratar o LaTeX (rever ou manter a versão atual).
  - Esclarecer a discrepância 86/19/18 vs 87/18/18.

### REV-005 — Reescrita de `latex/proposta_pt.tex` a partir da proposta IAHC (PDF)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul-petróleo `#00838F`, RGB (0, 131, 143). Aplicada apenas no marcador do registo; o `.tex` **não** usa esta cor, por instrução do utilizador.
- **O quê:**
  - Reescrito `latex/proposta_pt.tex` a partir de `latex/proposta_IAHC_DINIS_ROSA.pdf` (texto original).
  - Removidas todas as cores de tentativas anteriores: verde, amarelo e roxo. Mantido o **vermelho**, por indicação do utilizador (`human-on-the-loop`, o inspetor a supervisionar e o número 123).
  - Removido o texto que descrevia implementações inexistentes (BiGRU, quatro baselines, normalização por mediana e IQR, `t_rel`, janelas de 30 minutos, o caso da trajetória `219429000-2`, resultados de regressão logística e random forest no treino).
  - Número de trajetórias: **123** (PDF dizia 128).
  - Divisão: **por ID completo**, 70/15/15, semente 42, em vez de por navio (PDF). Explicitado que trajetórias do mesmo navio podem ficar em conjuntos diferentes, sem generalização para navios inéditos.
  - Descrição dos dados: 13 colunas, das quais 12 atributos e o rótulo (PDF dizia 13 atributos).
  - Caminho do estilo IJCAI corrigido para `FormattingGuidelines-IJCAI-ECAI-26/` (relativo a `latex/`). O caminho `../` original não resolvia a partir de `latex/`.
- **Porquê:** o utilizador pediu para recomeçar a partir da proposta IAHC, sem o texto de tentativas anteriores.
- **Ficheiros afetados:** `latex/proposta_pt.tex`.
- **Correspondência no LaTeX:** **atualizado**. Este é o próprio ficheiro. Resolve as pendências de REV-001, REV-003 e REV-004 para o `.tex`.
- **Validação:**
  - Compilação com `pdflatex` e `bibtex` a partir de `latex/`, com saída para uma pasta de rascunhos fora do repositório. Resultado: 3 páginas, sem citações nem referências por resolver.
  - Único aviso: `kaggleAIS` em `latex/references.bib` não tem autor (`Warning--to sort, need author or key`). Não alterado.
- **Pendentes:**
  - Decidir se o PDF IAHC deve ser atualizado (ainda diz 128 e divisão por navio).
  - Completar a entrada `kaggleAIS` em `references.bib`.
  - A proposta menciona HMM e Wu et al. como baselines. O `AGENTS.md` fixa o âmbito mínimo sem HMM nem Wu. Confirmar qual prevalece.

### REV-006 — Decisões do utilizador: PDF IAHC intocado, baselines fora por agora, manifesto versionado, autor do dataset

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Castanho `#6D4C41`, RGB (109, 76, 65). Só marcador do registo.
- **O quê:**
  - `latex/proposta_IAHC_DINIS_ROSA.pdf`: **não alterar**. É a versão entregue ao professor.
  - HMM e Wu et al. como baselines: **ficam de fora por agora** por falta de tempo. O `AGENTS.md` mantém-se como fonte fixa. Se houver tempo, retomam-se.
  - `.gitignore`: o manifesto `manifests/split_manifest_seed42.csv` passa a ser versionado, com exceção explícita à regra `*.csv`.
  - `latex/references.bib`, entrada `kaggleAIS`: autor corrigido. A fonte original é o Zenodo, com autor Song Wu (Université Libre de Bruxelles), DOI 10.5281/zenodo.7283281, licença CC BY 4.0, publicado em 2022-11-04. O Kaggle é um espelho (utilizador `thedevastator`). O ano 2026 anterior estava errado.
- **Porquê:** pedido do utilizador.
- **Ficheiros afetados:** `.gitignore`, `latex/references.bib`, `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **atualizado** na bibliografia. O texto do `.tex` não muda com esta revisão. A referência de dados passa a `[Wu, 2022]`.
- **Validação:** `git check-ignore` confirma que o manifesto não está ignorado. Recompilação com `bibtex` sem avisos de autor; a citação `[Wu, 2022]` resolve-se no PDF.
- **Pendentes:**
  - Discrepância de contagens do dataset: o ficheiro Zenodo chama-se `128_fishing_trajs.csv` e a página diz 128 trajetórias. O ficheiro local tem 123 IDs únicos e o mesmo tamanho (~169,6 MB). Confirmar se o ficheiro local é o mesmo e por que razão há 123 IDs.
  - Baselines HMM e Wu et al.: decidir mais tarde.

### REV-007 — Coerência após confirmação de 123 viagens e decisões de REV-006

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Rosa `#AD1457`, RGB (173, 20, 87). Só marcador do registo.
- **O quê:**
  - Confirmado por `scripts/verify_trip_count.py`: 123 IDs únicos, 1 026 279 linhas, igual ao manifesto.
  - `PROGRESS.md`: reescrito com decisões vigentes, pendentes resolvidas e tabela de artefactos.
  - `README.md`: estrutura e scripts atualizados (manifesto versionado, `verify_trip_count.py`, REV-007).
  - `docs/00` §1 (dataset): 123 confirmados; 128 explicado como cifra do Zenodo e da proposta PDF.
  - `AGENTS.md` §6: regra dos CSV atualizada com a exceção do manifesto (REV-006). Nenhuma regra metodológica mudou.
- **Porquê:** após REV-006 e a verificação de contagem, havia documentos com pendências já resolvidas.
- **Ficheiros afetados:** `PROGRESS.md`, `README.md`, `AGENTS.md`, `docs/00_contexto_projeto_dicionario_dados.md`, `REVISION_LOG.md`, `scripts/verify_trip_count.py` (novo).
- **Correspondência no LaTeX:** **não aplicável**. O `.tex` já diz 123 e não é afetado. O PDF IAHC não se altera.
- **Validação:** pesquisa textual por "128", "não versionado", "pendente de decisão" e "sem autor" nos MDs. As ocorrências restantes são históricas ou explicam a cifra do Zenodo.
- **Pendentes:** nenhum para esta revisão.

### REV-008 — Unidades e CRS confirmados pelo README oficial do Zenodo

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde-azulado `#00695C`, RGB (0, 105, 92).
- **O quê:** `docs/00` atualizado com a fonte oficial:
  - `distanceToShore` em **metros**, distância à costa da Dinamarca (confirmado).
  - `x` e `y` em **SRID 25832** (ETRS89 / UTM zona 32N, EPSG:25832).
  - Longitude e latitude: CRS não indicado; hipótese WGS84 (EPSG:4326), por confirmar.
  - `euc_speed`: o README diz "knots/hour", o que confirma nós (a unidade "por hora" é redundante).
- **Porquê:** o utilizador pediu confirmação de `distanceToShore` e a explicação dos CRS. O README do Zenodo (`128_fishing_trajs_README.txt`, 602 bytes, publicado com o dataset) é a fonte primária.
- **Ficheiros afetados:** `docs/00_contexto_projeto_dicionario_dados.md` (tabela §8, §18), `REVISION_LOG.md`, `PROGRESS.md` (a seguir).
- **Correspondência no LaTeX:** **não aplicável**. A proposta não especifica unidades.
- **Validação:** README obtido em `https://zenodo.org/records/7283281/files/128_fishing_trajs_README.txt` (HTTP 200). Coerente com o treino: distâncias em metros (REV-003) e nós (REV-003).
- **Pendentes:**
  - Confirmar o CRS de longitude/latitude (hipótese WGS84 por verificar com uma projeção de referência, p.ex. `pyproj`, se autorizado instalar).
  - Método de cálculo de `distanceToShore` (não documentado).
- **Verificação adicional (REV-008):** MD5 do `data/123_fishing_trajs.csv` local = `c5953081f511e228b19e46ca85fe304f`, igual ao publicado no Zenodo para `128_fishing_trajs.csv`. Logo é o ficheiro oficial, e as 123 viagens são o conteúdo real. O "128" é só o nome do ficheiro e da proposta.

### REV-009 — Base limpa do treino com bases X, Y, T e distanceToShore

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Índigo `#283593`, RGB (40, 53, 147).
- **O quê:**
  - Criado `scripts/build_clean_dataset.py`. Bases copiadas do original: `x`, `y`, `t`, `distanceToShore`, `label`.
  - Recalculados por viagem: `time_gap_calc_s`, `distance_gap_calc_m`, `bearing_calc_deg`, `signed_turn_calc_deg`, `speed_calc_mps`.
  - `target` binário: 1 pesca (`02-fishing`, `04-fishing`), 0 navegação (`01-sailing`, `03-sailing`, `05-sailing`). Rótulo desconhecido gera erro.
  - Saída: `data/123_fishing_trajs_clean_train.parquet`. Só conjunto de **treino** (713 854 linhas, 87 viagens).
  - Sumário: `results/clean_train/summary.json`, com hashes de entrada e saída.
  - Nenhuma linha removida. Primeiro ponto de cada viagem (87) com valores ausentes nas grandezas que dependem do anterior.
  - `pyarrow==26.0.1` adicionado a `requirements.txt`, para ler e escrever Parquet.
- **Porquê:** pedido do utilizador: base nova, limpa, ordenada por id e tempo, com X, Y, T e distanceToShore como bases.
- **Ficheiros afetados:** `scripts/build_clean_dataset.py` (novo), `requirements.txt`, `README.md`, `REVISION_LOG.md`, `PROGRESS.md`. Saída em `data/` (ignorada pelo git).
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação (só treino):**
  - `time_gap` recalculado difere do original em mais de 1e-6 s em **1,4·10⁻⁶** dos pares (cerca de 10 pares). As anomalias de 1/3 eram casos pontuais.
  - `distance_gap` recalculado (distância plana de x,y) difere do original em mais de 1e-3 m na mesma fração. Mediana da diferença 1,5·10⁻⁹ m: o original foi calculado a partir de x e y.
  - `signed_turn` recalculado difere do original em mais de 1° em **2,8·10⁻⁶** dos pares.
  - `bearing` recalculado a partir de x,y difere do original em mais de 1° em **54 %** dos pares (mediana 1,08°, percentil 95 de 2,58°). É o esperado: `bearing` original está em norte verdadeiro (lat/lon) e o recalculado em norte da grelha UTM. A diferença é a convergência de meridianos. `signed_turn` não é afetado, porque a convergência é quase constante dentro de cada viagem e cancela na variação.
- **Pendentes:**
  - Decidir a base de `bearing`: manter o da grelha (x,y, consistente com as outras features), ou usar o original (norte verdadeiro). Não é o mesmo ângulo.
  - Validação e teste: só depois de autorização explícita do utilizador. Não foram processados.
  - Decidir a regra das anomalias restantes (poucas, ~10 pares de tempo). A limpeza por remoção ou marcação continua pendente.

### REV-010 — Atualização automática de PROGRESS e REVISION_LOG em cada interação

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Ocre `#8D6E00`, RGB (141, 110, 0).
- **O quê:** `AGENTS.md` §5 recebe a regra de atualização automática: no fim de cada interação que altere ficheiros, decisões, validações ou pendentes, o agente atualiza `PROGRESS.md` e `REVISION_LOG.md` sem pedido. Sem entradas vazias quando não há alterações. Verificação de coerência antes de terminar.
- **Porquê:** pedido do utilizador. Os registos estavam a ficar para trás e exigiam pedido explícito.
- **Ficheiros afetados:** `AGENTS.md` §5.
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação:** leitura da alteração em `AGENTS.md`. Não há código.
- **Pendentes:** nenhum.

### REV-011 — Decisões de base: bearing pela grelha e distanceToShore aceite

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Laranja `#E65100`, RGB (230, 81, 0). Só marcador do registo.
- **O quê:**
  - `bearing` mantém-se calculado a partir de x,y (norte da grelha UTM). Não se usa o `bearing` original (norte verdadeiro).
  - `distanceToShore` aceite como correto tal como está no dataset. Não se procura o mapa da costa nem se verifica a sua origem.
- **Porquê:** decisão do utilizador. Coerência com x,y. Verificar `distanceToShore` exigiria mapa de costa e posição, com custo de recursos que o projeto não comporta.
- **Verificação (só treino):** a base limpa do treino não tem anomalias criadas pelo cálculo. `time_gap` e `distance_gap` recalculados coincidem com os originais (diferença acima de 1e-6 em 1,4·10⁻⁶ dos pares). As anomalias existentes estão nos próprios x, y, t, não no cálculo:
  - 87 primeiros pontos sem anterior (já documentados).
  - `time_gap` até 47 172 s (cerca de 13 h) e mínimo 1 s. Nenhum valor ≤ 0. Nenhum `(id, t)` repetido.
  - `distance_gap` máximo 14 797 m num único passo. Velocidade máxima implícita cerca de 90,7 kn; p99,9 de 15,3 kn.
  - `signed_turn`: 3 717 pares com |variação| > 170°, o que indica inversões de rumo reais ou saltos de posição. Nenhum valor fora de (-180, 180].
- **Ficheiros afetados:** `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Pendentes:**
  - Definir a regra para as anomalias de `time_gap`, `distance_gap` e `signed_turn` (marcar, remover ou manter). Esta regra é o Marco 2.
  - Validação e teste: só depois de autorização explícita.

### REV-012 — Anomalias mantidas como estão nos dados

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Cinzento-ardósia `#455A64`, RGB (69, 90, 100). Só marcador do registo.
- **O quê:** nenhuma anomalia é removida, marcada ou corrigida em `time_gap`, `distance_gap`, `signed_turn` ou `speed`. Um gap de 13 h fica como gap de 13 h. Uma velocidade de 90 nós fica como 90 nós. O dataset é tratado como ele próprio.
- **Porquê:** decisão do utilizador. As anomalias são poucas e isoladas, e o modelo deve aprender com dados tal como existem na prática, sem limpeza adicional.
- **Ressalva registada:** a frequência ainda não está medida. Há 3 717 pares com `signed_turn` acima de 170° no treino (cerca de 0,5 %). A contagem de saltos acima de um limiar de velocidade não foi feita. Se estes números forem altos, a decisão deve ser revista.
- **Ficheiros afetados:** `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Pendentes:**
  - Medir a frequência de saltos e de inversões de rumo no treino, para confirmar que são poucos.
  - Validação e teste: só depois de autorização explícita.

### REV-013 — Anomalias explícitas no relatório como teste de robustez

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Oliva `#808000`, RGB (128, 128, 0). Aplicada no `.tex` pela macro `\revtext{rev013}` (parágrafo de Materiais e Dados). Corrigida de `#556B2F` porque essa cor não era visível de forma fiável no PDF; `#808000` é a cor oliva padrão do LaTeX (`olive`).
- **O quê:** `latex/proposta_pt.tex`, secção Materiais e Dados: acrescentado um parágrafo que declara que as anomalias são mantidas, sem limpeza, e que a robustez a elas faz parte da avaliação.
- **Porquê:** decisão do utilizador. O sistema destina-se a dados AIS ao momento, onde estes erros ocorrem. Tratá-los na preparação tornaria a avaliação otimista.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `REVISION_LOG.md`, `PROGRESS.md`. O PDF entregue ao professor (`latex/proposta_IAHC_DINIS_ROSA.pdf`) não foi alterado.
- **Correspondência no LaTeX:** `latex/proposta_pt.tex` alterado. Parágrafo novo em Materiais e Dados, em cor `rev013`, com a macro `\revtext`. Compilação verificada sem erros (`latex/build/`, ignorado pelo git).
- **Pendentes:**
  - Compilação verificada: `pdflatex` sem erros, em `latex/build/`.
  - Decidir se a avaliação de robustez a anomalias entra como estudo próprio na secção Avaliação.

### REV-014 — Regra explícita: toda a alteração ao LaTeX leva cor

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Lilás `#9575CD`, RGB (149, 117, 205). Só marcador do registo.
- **O quê:** `AGENTS.md` §8 passa a dizer de forma explícita que toda a alteração ao `.tex` (texto novo ou substituído) é colorida com a cor do seu ID, pela macro `\revtext`, e que nenhuma revisão fica com cor por atribuir. REV-011 e REV-012 passam a ter cor (laranja e cinzento-ardósia). Antes estavam marcadas "a atribuir". O preâmbulo de `latex/proposta_pt.tex` define `\definecolor{rev013}` e `\revtext`.
- **Porquê:** pedido do utilizador: a regra já tinha sido dada, mas não estava escrita no `AGENTS.md`.
- **Ficheiros afetados:** `AGENTS.md` §8, `REVISION_LOG.md`, `PROGRESS.md`, `latex/proposta_pt.tex` (preâmbulo e parágrafo REV-013).
- **Correspondência no LaTeX:** **não aplicável** a esta revisão. É uma regra do processo, sem texto da proposta. O parágrafo REV-013 já foi atualizado.
- **Validação:** `pdflatex` sem erros após a alteração.
- **Pendentes:** nenhum.

### REV-015 — Bases limpas de validação e teste

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Turquesa `#26A69A`, RGB (38, 166, 154). Só marcador do registo.
- **O quê:**
  - `scripts/build_clean_dataset.py` aceita `--split train|validation|test` (por defeito, `train`). Cada conjunto gera o seu ficheiro e o seu sumário.
  - Gerados `data/123_fishing_trajs_clean_validation.parquet` e `data/123_fishing_trajs_clean_test.parquet`, além do treino.
  - Cada conjunto é construído só com as viagens do seu split, segundo o manifesto. O script falha se as viagens não coincidirem com o manifesto.
- **Porquê:** autorização explícita do utilizador em 2026-11-23 para processar validação e teste. O utilizador considera que não há fuga de dados, porque nenhum valor de validação ou teste é usado para ajustar o processamento.
- **Ficheiros afetados:** `scripts/build_clean_dataset.py`, `README.md`, `REVISION_LOG.md`, `PROGRESS.md`. Saídas em `data/` e `results/` (ignoradas pelo git).
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação (contagens, sem análise de resultados):**
  - Total de linhas: 713 854 (treino) + 209 016 (validação) + 103 409 (teste) = 1 026 279, igual ao CSV original.
  - Viagens: 87 + 18 + 18 = 123, iguais ao manifesto.
  - Sem `time_gap` nulo ou negativo fora do primeiro ponto de cada viagem.
  - Proporção de pesca (`target` = 1): treino 0,754; validação 0,832; teste 0,612. Diferença natural entre conjuntos, não corrigida.
- **Pendentes:**
  - Testes sintéticos da função de construção.
  - Medir a frequência de saltos e de inversões de rumo.
  - Push: feito pelo utilizador.

### REV-016 — Testes sintéticos e correção de `wrap_180`

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Amarelo-torrado `#F57F17`, RGB (245, 127, 23). Só marcador do registo.
- **O quê:**
  - Criada a pasta `tests/` com `test_build_clean_dataset.py`: 10 testes com dados inventados. Cobrem: barco parado, linha reta a norte, rumo a leste, curva positiva no sentido do relógio, rotação pelo zero (350° para 10° dá +20°), primeiro ponto sem anterior, viagens que não se misturam, mapeamento do `target` e rótulo desconhecido.
  - Correção em `scripts/build_clean_dataset.py`: `wrap_180` passa a devolver (-180, 180], como a documentação já dizia. Antes, um ângulo de exatamente 180° saía como -180°.
- **Porquê:** o teste de `wrap_180(180)` falhou e revelou a discrepância entre código e documentação.
- **Verificação:** `pytest tests/` passa (10 testes). Os três conjuntos foram regenerados. O treino ficou igual ao anterior (comparação de conteúdo). Nenhum valor de 180° ou -180° no treino.
- **Ficheiros afetados:** `tests/test_build_clean_dataset.py` (novo), `scripts/build_clean_dataset.py`, `README.md`, `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Pendentes:** medir a frequência de saltos e de inversões de rumo no treino (aguarda pedido de revisão do Marco 2).

### REV-017 — Contagem de saltos e inversões de rumo por viagem (treino)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Rosa-choque `#FF4081`, RGB (255, 64, 129). Só marcador do registo.
- **O quê:**
  - `scripts/count_anomalies_train.py`: conta, por viagem, pares com velocidade acima de 30 nós (salto) e pares com |variação de rumo| acima de 170° (inversão). Só lê o treino e não altera dados.
  - Saídas em `results/anomalies_train/`: `per_trip.csv`, `summary.json`, `jumps_per_trip.png` e `inversions_per_trip.png`.
  - `tests/test_count_anomalies_train.py`: 5 testes sintéticos da contagem e do resumo.
- **Porquê:** pedido do utilizador: contagem por viagem, médias e medianas, e dois gráficos, para confirmar a escala das anomalias antes da revisão do Marco 2. O limiar de 30 nós é um valor de trabalho, não validado.
- **Resultados (treino, 87 viagens):**
  - Saltos acima de 30 nós: 55 no total, em 4 viagens. Média 0,63, mediana 0. Uma viagem tem 48 (`220099000-3`). Taxa de 0,077 por mil pares.
  - Inversões acima de 170°: 3 717 no total, em 70 viagens. Média 42,7, mediana 3. Duas viagens concentram 68 % do total: `219028021-2` com 1 517 (6,4 % dos pares) e `220099000-3` com 1 018 (4,2 %). Taxa de 5,2 por mil pares.
  - 83 viagens sem nenhum salto e 17 sem nenhuma inversão.
- **Ficheiros afetados:** `scripts/count_anomalies_train.py` (novo), `tests/test_count_anomalies_train.py` (novo), `README.md`, `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Pendentes:**
  - Decidir se as inversões concentradas em poucas viagens são erro ou comportamento real (por exemplo, pesca em zigue-zague). Só contar não o distingue.
  - Revisão do Marco 2 pelo utilizador antes do Marco 3.

### REV-018 — Subsecção «Tratamento dos dados» na proposta

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul-ardósia `#5C6BC0`, RGB (92, 107, 192).
- **O quê:** `latex/proposta_pt.tex` ganha a subsecção «Tratamento dos dados», dentro de Materiais e Dados, antes de Avaliação. Descreve: manutenção das anomalias (REV-012 e REV-013); a função de recálculo por viagem (`time_gap`, `distance_gap`, `bearing`, `signed_turn`, velocidade em nós e `target`); o tratamento do primeiro ponto; a concordância com os valores originais acima de 99,99 % dos pares; a convergência de cerca de 1° no rumo; a distância à costa usada sem verificação; e a aplicação por conjunto com base no manifesto e testes sintéticos.
- **Porquê:** pedido do utilizador: o texto sobre gaps (REV-013) pertence aos dados, e a proposta deve descrever o tratamento feito.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `REVISION_LOG.md`, `PROGRESS.md`.
- **Correspondência no LaTeX:** **atualizado**. O parágrafo de REV-013 foi movido para esta subsecção, e o texto novo está em cor REV-018. O texto anterior de REV-013 fica no histórico do Git e no registo.
- **Validação:** `pdflatex` sem erros. A cor azul-ardósia aparece no PDF (página com a subsecção).
- **Pendentes:** confirmar com o utilizador o texto da subsecção antes de a considerar final.

### REV-020 — Alinhamento de todos os documentos com as decisões REV-011 a REV-019

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Cinzento-azulado `#607D8B`, RGB (96, 125, 139). No `.tex`, só no passo 1 do pipeline (`\revtext{rev020}`).
- **O quê:** atualizadas as descrições que tinham ficado para trás:
  - `latex/proposta_pt.tex`, passo 1 do pipeline: deixa de falar de tratamento de outliers e gaps e passa a descrever o recálculo a partir de x, y e t, sem remoção de anomalias, e a seleção das características.
  - `docs/00_contexto_projeto_dicionario_dados.md`: exceção de REV-015 na política de desenvolvimento; features decididas (REV-019); distanceToShore aceite (REV-011); anomalias quantificadas (REV-017) e mantidas (REV-012); dúvidas atualizadas.
  - `docs/01_preparacao_comum.md`: lista de características passa a «decididas» (REV-019).
  - `docs/04_especificacao_funcoes_preparacao.md`: `feature_cols` decidida (REV-019).
  - `README.md`: estado (Marco 2 fechado, Marco 3 à espera) e intervalo de revisões.
  - `PROGRESS.md`: estado atual reescrito (scripts, testes, bases dos três conjuntos, leituras de validação e teste) e decisões vigentes acrescentadas.
- **Porquê:** pedido do utilizador: os documentos devem estar todos em concordância com as decisões.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `docs/00_contexto_projeto_dicionario_dados.md`, `docs/01_preparacao_comum.md`, `docs/04_especificacao_funcoes_preparacao.md`, `README.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado** no passo 1 do pipeline. Compilação verificada sem erros.
- **Validação:** `pdflatex` sem erros. Verificação por leitura dos textos alterados.
- **Pendentes:**
  - `AGENTS.md` não foi alterado (é o ficheiro fixo de regras).
  - `docs/02`, `docs/03`, `docs/05` e `docs/06` já usam as quatro features corretas, sem alterações.
  - Marco 3 só começa com aprovação do utilizador.

### REV-021 — Reorganização do pipeline: CNN 1D de referência antes do janelamento

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Magenta `#D500F9`, RGB (213, 0, 249). No `.tex`, em `\revtext{rev021}`.
- **O quê:**
  - Decisão do utilizador: o modelo é uma **CNN 1D** que devolve uma probabilidade por ponto. A ordem de trabalho é: (1) pré-processamento, concluído; (2) CNN 1D de referência sobre a viagem completa, para obter valores de referência; (3) janelamento com sobreposição e a mesma CNN 1D sobre janelas, para estudar o efeito da sobreposição; (4) pós-processamento temporal; (5) saída e explicabilidade.
  - `latex/proposta_pt.tex`: objetivos 1 e 2 (a CNN 1D passa a ser explícita; o janelamento sai do pré-processamento), abordagem em cinco etapas com a mesma arquitetura nas fases 2 e 3, e figura do pipeline reorganizada (fundo cinzento no bloco de referência).
  - `docs/00_5_orientacoes_execucao_decisoes.md`: marcos 3 e 4 com a CNN 1D de referência e o janelamento.
  - `README.md`: descrição do modelo e da ordem.
- **Porquê:** pedido do utilizador: o pré-processamento e a limpeza estão concluídos; a CNN treina primeiro sobre viagens completas, para servir de referência, e só depois se estudam janelas e sobreposição.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `docs/00_5_orientacoes_execucao_decisoes.md`, `README.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. Compilação verificada sem erros. A figura foi inspecionada visualmente.
- **Validação:** `pdflatex` sem erros; figura e texto verificados na página 2 do PDF.
- **Pendentes:**
  - Aprovação do utilizador para o Marco 3.
  - Política de valores ausentes na CNN (proposta: excluir os 87 primeiros pontos e mascarar os restantes).
  - Os documentos `docs/02`, `docs/03`, `docs/05` e `docs/06` já descrevem a CNN nesta ordem. Não foram alterados.

### REV-022 — Política de valores ausentes na CNN e início oficial do Marco 3

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde-azulado escuro `#00897B`, RGB (0, 137, 123). No `.tex`, em `\revtext{rev022}`.
- **O quê:**
  - **Aprovado pelo utilizador:** política para valores ausentes. Nenhuma linha é removida. Os dois primeiros pontos de cada viagem não têm `time_gap`, `speed` e `signed_turn` (o segundo só não tem `signed_turn`). Esses valores são preenchidos com zero e marcados por um indicador de ausência (máscara) por característica. Esses pontos ficam fora da função de perda. A mesma regra aplica-se a treino, validação e teste.
  - **Nota de interpretação:** a proposta aprovada falava em excluir os primeiros pontos. Os dados mostram que o segundo ponto também não tem `signed_turn` (87 casos em treino). Por isso a regra abrange os dois primeiros pontos. Se preferires excluir esses pontos das entradas em vez de preencher, diz-me.
  - **Marco 3 oficialmente em curso**, aprovado pelo utilizador.
- **Porquê:** decisão do utilizador. A regra evita remover dados e distingue ausência de zero físico, como exigido em `docs/04`.
- **Ficheiros afetados:** `docs/00_contexto_projeto_dicionario_dados.md`, `docs/01_preparacao_comum.md`, `docs/04_especificacao_funcoes_preparacao.md`, `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**, na subsecção «Tratamento dos dados», em cor REV-022. Compilação verificada sem erros.
- **Validação:** `pdflatex` sem erros. Verificação por leitura das alterações.
- **Pendentes:**
  - Ver a lista de próximos passos do Marco 3 em `PROGRESS.md`.
  - Push, por conta do utilizador.

- **Correção (2026-11-23, mesma revisão REV-022):**
  - Quais os pontos com ausências: o **primeiro** ponto de cada viagem não tem `time_gap`, `speed` nem `signed_turn`. O **segundo** só não tem `signed_turn`. A versão anterior dizia que os dois primeiros não tinham as três grandezas, o que estava errado.
  - Porque é que o segundo não tem `signed_turn`: `bearing` existe a partir do segundo ponto (é o rumo do primeiro intervalo). `signed_turn` é a diferença entre dois rumos consecutivos, por isso precisa de dois intervalos. No segundo ponto só há um.
  - O primeiro ponto **mantém-se** no conjunto, com valores ausentes, por decisão do utilizador.
  - A entrada dos pontos iniciais na função de perda **não está decidida**. A versão anterior dizia que ficavam fora, sem confirmação. Fica como pendente.
- **Decisão final (2026-11-23, mesma revisão REV-022):** o primeiro ponto tem `time_gap`, `speed` e `signed_turn` a zero, com máscara. O segundo tem `signed_turn` a zero, com máscara. Não se inventa `bearing` para o primeiro ponto, porque isso criaria uma curva falsa no segundo. Os pontos iniciais **entram** na função de perda, com as máscaras nas entradas. Proposta do utilizador, aceite após análise.

### REV-023 — Reorganização do manuscrito em subsecções

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul `#0277BD`, RGB (2, 119, 189). No `.tex`, em `\revtext{rev023}`, só nos títulos novos.
- **O quê:**
  - «Abordagem» passa a ter cinco subsecções: pré-processamento e características; CNN de referência sobre a viagem completa; janelamento com sobreposição; pós-processamento temporal; saída, explicabilidade e ferramentas. A figura do *pipeline* fica logo a seguir à introdução.
  - «Avaliação» passa a ter três subsecções: métricas e estudo de ablação; divisão dos dados e protocolo; avaliação qualitativa e dimensão humana.
  - O texto antigo foi apenas movido e **mantém as cores originais** (REV-020, REV-021). Única alteração de redação no texto movido: retirada a numeração «(1)» a «(5)» e as etiquetas em itálico que passaram a ser títulos.
- **Porquê:** pedido do utilizador, para o manuscrito ser mais simples de ler.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. Compilação sem erros (4 páginas).
- **Validação:** `pdflatex` sem erros. Não foi inspecionado visualmente o PDF.
- **Pendentes:** revisão do resultado pelo utilizador; mais secções, se pretendido.

### REV-024 — Marco 3: sequências, normalização, CNN 1D e testes (sem treino)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Castanho `#6D4C41`, RGB (109, 76, 65). No `.tex`, em `\revtext{rev024}`.
- **O quê:**
  - Código novo em `src/phase1/`: `data.py` (leitura só de treino, validação, sequências por viagem, scaler, aplicação com máscaras, partição interna por ID, DataLoader), `model.py` (CNN 1D), `training.py` (perda, otimizador, passo de época, avaliação diagnóstica), `checks.py` (smoke test), `utils.py` (semente, dispositivo).
  - Decisões do utilizador desta ronda: 7 canais (4 características + 3 máscaras: speed, signed_turn, time_gap); preenchimento a zero **depois** de normalizar; testes com sintéticos mais 3 viagens reais de treino; reorganização do LaTeX (REV-023).
  - Testes novos: `test_sequences`, `test_point_alignment`, `test_access_policy`, `test_model_shapes`, `test_loss_and_gradients`, `test_integration_phase1`.
  - Subsecção «Verificação da implementação» e dois parágrafos na CNN de referência, no `.tex`.
  - Trabalho delegado: `data.py` e testes ligados (Sonnet); `model.py`, `training.py`, `checks.py`, `utils.py` e testes ligados (Haiku). Integração, revisão e teste de integração por mim.
- **Porquê:** passos 1 a 4 do Marco 3. O treino fica para depois, por decisão do utilizador.
- **Ficheiros afetados:** `src/phase1/*`, `tests/*`, `tests/conftest.py`, `latex/proposta_pt.tex`, `docs/05_funcoes_documentos_cnn_viagem_completa.md`, `README.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado** (Abordagem). Compilação sem erros.
- **Validação:** `pytest tests/` → 75 passaram (15 anteriores + 60 novos), 0 falhas, 0 ignorados. Um teste lê 3 viagens reais de treino (17 844 pontos); validação e teste não foram abertos. Não houve treino.
- **Limitações:**
  - Taxa de aprendizagem 1e-3 é um valor provisório, não validado.
  - O smoke test exige gradiente não nulo em todos os tensores; com dados reais pode ter de ser relaxado.
  - Ordenação global só verificada em 3 viagens reais; `validate_training_data` verifica-a sobre toda a base quando for usado no treino completo.
  - Não existem ainda: segmentos, métricas por segmento, `run_phase1`, configuração JSON e guardar/carregar checkpoint.
  - Não se mediu custo em CPU nem memória das 87 viagens.
- **Pendentes:** proporção da partição interna e orçamento de tempo (decisões do utilizador); commit local por autorizar; push por conta do utilizador.

### REV-025 — Secção «Especificação da CNN 1D de referência» na proposta

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Roxo `#6A1B9A`, RGB (106, 27, 154). No `.tex`, em `\revtext{rev025}`.
- **O quê:**
  - Nova secção 5 com sete subsecções: entrada e saída; arquitetura (tabela com canais, *kernel* e parâmetros por camada); porquê estes valores; campo recetivo (fórmula e consequências); função de perda; otimizador e treino; reprodutibilidade.
  - Cada escolha indica o estado: *decidido*, *adotado como valor inicial sem validação* ou *ainda não definido*. Os 21 761 parâmetros (1 152 + 10 304 + 10 272 + 33) vêm de `count_parameters` no código.
  - A justificação de 32/64/32 e *kernel* 5 declara que estes valores são os da arquitetura inicial do protocolo (`docs/02`), **sem pesquisa nem experiência**; o texto dá o raciocínio de desenho e não o apresenta como evidência. A taxa de aprendizagem 1e-3, as épocas, o critério de paragem e a semente do modelo estão declarados como **não definidos**.
  - Correção em REV-023: quatro parágrafos movidos começavam com minúscula depois de retirada a etiqueta; passam a maiúscula (só redação, cores iguais).
- **Porquê:** pedido do utilizador, para o relatório permitir recriar a rede com os mesmos valores.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` sem erros (6 páginas). Páginas 3 inspecionada visualmente; as restantes não.
- **Validação:** compilação. A tabela e os valores foram conferidos com o código (`build_cnn`, `count_parameters`, `receptive_field`).
- **Pendentes:**
  - Decidir taxa de aprendizagem, épocas, critério de paragem, semente do modelo e partição interna antes do treino.
  - Linha ligeiramente larga (11 pt) no parágrafo do campo recetivo; cosmético.
  - Se o utilizador quiser fundamentar 32/64/32 e *kernel* 5, é preciso uma comparação experimental própria (fora do âmbito atual).

### REV-026 — Figura 2: desenho da CNN 1D de referência

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde `#2E7D32`, RGB (46, 125, 50). No `.tex`, a figura inteira (traços, texto e legenda) e a frase de remissão, em `\color{rev026}` / `\revtext{rev026}`.
- **O quê:**
  - Nova figura em TikZ (sem imagens externas), na subsecção «Arquitetura» da secção 5: cadeia entrada 7×N → Conv1D 7→32 → 32→64 → 64→32 (*kernel* 5, ReLU) → cabeça Conv1D 32→1 (*kernel* 1) → *logits* 1×N → σ só na inferência; abaixo, o esquema do campo recetivo (13 pontos de entrada, de i−6 a i+6, para o logit do ponto i).
  - Frase de remissão à Figura 2 no parágrafo da arquitetura.
  - Equação do campo recetivo simplificada (`R = 1 + 3×4 + 0 = 13`) para caber na coluna (mesmo valor e cor REV-025).
- **Porquê:** pedido do utilizador, para visualizar a rede ao lado do esquema do *pipeline* (Figura 1).
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex`+`bibtex` sem erros, sem referências em falta, sem linhas largas (6 páginas). Figura e equação inspecionadas visualmente na página 4.
- **Validação:** valores da figura (canais, *kernel*, 13 pontos) conferidos com a Tabela 1 e o código.
- **Pendentes:** nenhum específico. Nota: o `watch_latex.sh` ativo e compilações manuais em `latex/build/` colidem e corrompem o `.aux`; compilar manualmente em `latex/build/check/`.

### REV-027 — Ensaio curto de ajuste da CNN em 3 viagens de treino

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Lima `#AFB42B`, RGB (175, 180, 43). No `.tex`, em `\revtext{rev027}` (duas frases que corrigem «ainda não houve treino»).
- **O quê:**
  - Pedido do utilizador: tabelas de rótulo vs. previsão e de acertos/erros por classe nas 3 viagens do teste inicial. Como não existiam previsões (REV-024 não treinou nada), o utilizador autorizou, entre três opções, um **ensaio curto de ajuste** só nessas 3 viagens de treino.
  - Novo `scripts/diagnostic_fit_3_trips.py`: 200 épocas (600 passos de Adam), lr 1e-3, seed 42, limiar 0,5, CPU. Scaler ajustado só com estas 3 viagens. Saídas em `results/diagnostic_3trips/` (não versionadas): `predictions.csv`, `tables.json`, `training_history.csv`, `run_manifest.json`.
  - Viagens: `211477000-3`, `211477000-4`, `219001039-2` (17 844 pontos).
  - Correção documental: o LaTeX e o README diziam que não houvera treino; passam a dizer que houve só este ensaio.
- **Resultado (do artefacto, não generalização):** accuracy 95,71 % (17 078 acertos, 766 erros; a classe maioritária daria 73,45 %). Navegação: 4 349 acertos, 388 erros; pesca: 12 729 acertos, 378 erros. Por viagem: 99,09 %, 99,29 % e 90,30 %. Perda por ponto 0,6599 → 0,1058. Treino 12,0 s.
- **Limitações:** treino e previsão nas **mesmas** viagens (sobreajuste); só rótulos 01, 02 e 03 presentes nestas viagens (sem 04 e 05); scaler de 3 viagens; lr, épocas e limiar são escolhas do ensaio, não validadas; o script não tem teste automático.
- **Ficheiros afetados:** `scripts/diagnostic_fit_3_trips.py`, `latex/proposta_pt.tex`, `README.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado** (só a correção; resultados não entram no `.tex`). `pdflatex` sem erros.
- **Validação:** execução do script (14 s) com os artefactos gerados; tabelas lidas dos ficheiros. Validação e teste não abertos.
- **Pendentes:** treino a sério (partição interna, lr, épocas, orçamento); decidir se estes resultados entram no relatório; commit local por autorizar.

### REV-028 — Avaliação do ensaio em 3 outras viagens de treino

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Ciano `#00ACC1`, RGB (0, 172, 193). No `.tex`, em `\revtext{rev028}` (uma frase).
- **O quê:**
  - Pedido do utilizador: voltar a treinar nas 3 viagens e avaliar em **outras** 3 viagens do treino, para a tabela de exemplo.
  - `scripts/diagnostic_fit_3_trips.py` estendido: viagens de ajuste `211477000-3`, `211477000-4`, `219001039-2` (17 844 pontos) e viagens fora da amostra `219001125-3`, `219001149-2`, `219001522-2` (35 290 pontos), as 3 seguintes do manifesto marcadas treino. Scaler ajustado só com as de ajuste. Mesma configuração (200 épocas, lr 1e-3, seed 42, limiar 0,5). Os artefactos de `results/diagnostic_3trips/` foram regenerados; o conjunto de ajuste reproduz os números de REV-027 (perda 0,6599 → 0,1058).
  - Alteração à redação do `.tex` de REV-027: o texto passa a mencionar também esta avaliação.
- **Resultado (dos artefactos):**
  - Ajuste: accuracy 95,71 %.
  - Fora da amostra: accuracy 93,01 % (32 824 acertos, 2 466 erros; maioritária 75,21 %). Navegação: 6 439 acertos, 2 310 erros (sensibilidade 0,736); pesca: 26 385 acertos, 156 erros (sensibilidade 0,994). Por viagem: 86,15 %, 98,28 % e 80,17 %.
- **Limitações:** só treino oficial (não é validação); 3 viagens sem valor estatístico; só 3 viagens de ajuste, um scaler de 3 viagens; configuração não validada; o script não tem teste automático. Viagens fora da amostra incluem os rótulos 04 e 05.
- **Ficheiros afetados:** `scripts/diagnostic_fit_3_trips.py`, `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado** (só qualitativo; sem números). 
- **Validação:** execução do script (cerca de 11 s); tabelas lidas dos artefactos. Validação e teste oficiais não abertos.
- **Pendentes:** treino a sério com partição interna, lr, épocas e orçamento; commit local por autorizar.

### REV-029 — Gráficos e tabelas em imagem do ensaio de 3 viagens

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Castanho-avermelhado `#BF360C`, RGB (191, 54, 12). Só marcador do registo (não houve alteração ao `.tex`).
- **O quê:** pedido do utilizador para ver os resultados em imagem. Novo `scripts/plot_diagnostic_3trips.py`, que lê apenas os artefactos de `results/diagnostic_3trips/` (sem treinar nem abrir os parquet) e gera 6 PNG em `results/diagnostic_3trips/figures/`: curva de perda e accuracy por viagem; matrizes de confusão; sensibilidade, precisão e F1 por classe; rótulo original vs. previsto; linhas temporais das 6 viagens (real, previsto, erro e probabilidade); tabelas resumo, por classe e por viagem. Cores: azul = navegação e laranja = pesca (slots 1 e 2 da paleta de referência); cinza e violeta distinguem ajuste e fora da amostra.
- **Ficheiros afetados:** `scripts/plot_diagnostic_3trips.py`, `PROGRESS.md`, `REVISION_LOG.md`. Imagens não versionadas.
- **Correspondência no LaTeX:** **não aplicável** (as figuras não entram no relatório; decisão pendente).
- **Validação:** execução do script e inspeção visual das 6 imagens; corrigidos 4 defeitos de layout (legendas sobrepostas, rótulo de eixo, espaço vazio nas tabelas). Os números das imagens vêm dos artefactos (percentagens só de apresentação). Sem teste automático do script.
- **Pendentes:** decidir se alguma figura entra no relatório; treino a sério; commit local por autorizar.

### REV-030 — Figuras e subsecção do ensaio preliminar no relatório

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Laranja-âmbar `#FF6F00`, RGB (255, 111, 0). No `.tex`, em `\revtext{rev030}` (títulos, texto e legendas; as imagens em si não levam cor).
- **O quê:**
  - Nova subsecção 7.4 «Ensaio preliminar com poucas viagens» em «Avaliação»: descreve o ensaio (200 épocas, lr 1e-3 não validado, ajuste em 3 viagens, avaliação nessas e noutras 3 de treino), os scripts que o reproduzem, e declara que é um marcador ilustrativo e provisório, sem valor estatístico nem validação oficial.
  - Duas figuras: Figura 3 (matrizes de confusão, ajuste e fora da amostra) e Figura 4 (previsão ao longo das 3 viagens fora da amostra). Ficheiros em `latex/figures/` (`diag3_matrizes_confusao.png`, `diag3_linhas_temporais.png`), cópias das saídas de `scripts/plot_diagnostic_3trips.py`.
  - A impressão de que os erros se concentram nas fronteiras vem da leitura visual e está declarada no texto como **não quantificada**.
  - `scripts/plot_diagnostic_3trips.py`: matriz mais compacta, nova versão `fig5b` (só viagens fora da amostra) e correção de uma variável que gravava um ficheiro `previsto.png` por engano.
- **Porquê:** pedido do utilizador, para ver onde ficam as figuras e o texto dos resultados.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `latex/figures/*`, `scripts/plot_diagnostic_3trips.py`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` sem erros e sem referências em falta (7 páginas). Páginas 5, 6 e 7 inspecionadas.
- **Validação:** compilação e inspeção visual. Os números das figuras vêm dos artefactos do ensaio; o texto não copia números.
- **Limitações:** as figuras são marcadores e serão substituídas pelos resultados do treino completo. As duas figuras flutuantes de largura total ficam em páginas separadas (a Figura 4 sozinha na página 7); a paginação deve ser revista no fim. As PNG em `latex/figures/` não estão ignoradas pelo git e entram no próximo commit.
- **Pendentes:** substituir as figuras pelos resultados reais; quantificar o desfasamento nas fronteiras; commit local por autorizar.

### REV-031 — Figuras do ensaio preliminar passam para um anexo

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul-petróleo `#006064`, RGB (0, 96, 100). No `.tex`, em `\revtext{rev031}` (título e texto novos do anexo e uma frase de remissão).
- **O quê:**
  - Novo Anexo A «Figuras do ensaio preliminar», depois das referências, com a Figura 3 (matrizes de confusão) e a Figura 4 (previsão em 3 viagens não vistas), movidas da subsecção 7.4. Mantêm as legendas em cor REV-030 (texto movido, não recolorido) e passam a `figure*[!t]`.
  - Frase na subsecção 7.4 a remeter para o Anexo A, «para não interromper a leitura do texto».
- **Porquê:** pedido do utilizador, para as figuras grandes não estragarem a leitura do corpo do texto e ficarem seguidas.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` sem erros e sem referências em falta (7 páginas). Páginas 5 a 7 inspecionadas.
- **Validação:** compilação e inspeção visual; as duas figuras ficam juntas na página 7.
- **Pendentes:** substituir as figuras pelos resultados reais; commit local por autorizar.

### REV-032 — Primeira execução de treino da CNN 1D (só treino oficial)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Rosa `#D81B60`, RGB (216, 27, 96). No `.tex`, em `\revtext{rev032}`.
- **O quê:**
  - Decisões aceites pelo utilizador («Podes começar»), segundo a tabela proposta: partição interna de 15 % (13 de 87 viagens, por ID, seed 42, sem estratificar); lr 1e-3, sem procura; máximo de 100 épocas; paragem antecipada na perda por ponto da monitorização interna com paciência 10 e melhor checkpoint; orçamento de 15 minutos; limiar 0,5.
  - Código novo: `src/phase1/artifacts.py` (guardar e carregar checkpoints, só tipos simples), `config.py` (validação; só `stage=development` e ficheiro de treino), `metrics.py` (métricas por classe), `train_model` em `training.py` (paragem antecipada, orçamento, melhor checkpoint); `configs/phase1_run1.json`; `scripts/run_phase1_training.py`; `scripts/plot_phase1_run.py`. Testes novos em `tests/test_checkpoint_and_training_loop.py`.
  - Execução: a base de treino inteira foi validada (87 viagens, 713 854 pontos; ordenação e NaN esperados), a partição interna separou 74 viagens de ajuste (637 422 pontos) e 13 de monitorização (76 432 pontos), e o normalizador foi ajustado só com o ajuste.
  - LaTeX: nova subsecção «Primeira execução de treino» e correção das frases que diziam que não havia treino completo e que lr e épocas não estavam definidos.
- **Resultado (dos artefactos `results/phase1_run1/`):** parou por paragem antecipada após 16 épocas em 39,4 s; melhor época 6 (perda de monitorização 0,1398). Accuracy: ajuste 92,15 %; monitorização 95,00 % (maioritária 74,46 %). Monitorização: navegação sensibilidade 0,875 e precisão 0,925; pesca sensibilidade 0,976 e precisão 0,958. Por viagem de monitorização: de 69,6 % a 99,2 %.
- **Limitações:**
  - A monitorização são 13 viagens do treino, não a validação oficial. A perda de monitorização oscila bastante entre épocas: o «melhor» modelo (época 6) e a paragem são sensíveis a esse ruído, e a perda estava a descer no fim (0,1478 e 0,1532 nas épocas 15 e 16).
  - A accuracy no ajuste (92,15 %) é inferior à da monitorização (95,00 %): a rede parece subajustada.
  - Duas viagens de monitorização (`220006000-3` e `219005909-1`) não superam a regra da classe maioritária.
  - Hiperparâmetros iniciais, não validados. Os scripts não têm teste automático; a lógica nova de treino, checkpoints, configuração e métricas tem 19 testes sintéticos.
  - `class_metrics` existe duas vezes (`phase1/metrics.py` e `scripts/diagnostic_fit_3_trips.py`); não unificado.
- **Ficheiros afetados:** `src/phase1/{artifacts,config,metrics,training}.py`, `configs/phase1_run1.json`, `scripts/run_phase1_training.py`, `scripts/plot_phase1_run.py`, `tests/test_checkpoint_and_training_loop.py`, `latex/proposta_pt.tex`, `docs/05`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` sem erros nem referências em falta (8 páginas). Não foi inspecionado visualmente o PDF desta revisão.
- **Validação:** `pytest tests/` → 94 passaram (75 anteriores e 19 novos), 0 falhas; execução real do treino com checkpoint recarregado do disco para as previsões; figuras inspecionadas. Validação e teste oficiais não foram abertos.
- **Pendentes:** decidir se se repete o treino com paciência maior ou outro lr (o critério atual pode parar cedo); medir o desfasamento e a fragmentação com código; substituir as figuras marcadoras do anexo; commit local por autorizar.

### REV-033 — Fusão e simplificação dos documentos em `docs/`

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Castanho-escuro `#3E2723`, RGB (62, 39, 35). Só no marcador Markdown `[REV-033 | cor #3E2723]` no topo dos quatro documentos; não há alteração ao `.tex`.
- **O quê:**
  - Os oito documentos `docs/00_contexto…`, `00_5_orientacoes…`, `01_preparacao_comum`, `02_cnn_viagem_completa`, `03_cnn_janelamento_sobreposicao`, `04_especificacao_funcoes_preparacao`, `05_funcoes_documentos_cnn_viagem_completa` e `06_funcoes_documentos_cnn_janelamento_sobreposicao` (cerca de 1 900 linhas) passam a quatro: `00_projeto_e_decisoes`, `01_dados_e_preparacao`, `02_cnn_viagem_completa` e `03_cnn_janelamento` (386 linhas). Os sete antigos foram apagados; ficam no histórico do git.
  - Removido o que estava cumprido ou obsoleto: o aviso «Atualização normativa» repetido em seis ficheiros; «Correções obrigatórias aos contratos antigos» e «Estado deste pacote»; as secções de integração com KNIME; o contrato de 25 funções de preparação (`data_io`, `preprocessing`, `trajectory`, `scaling`, `run_preparation`), nunca implementadas como módulos porque a preparação se fez com scripts (REV-019); as dúvidas de unidades já resolvidas.
  - Atualizado ao estado real: nomes das características (`signed_turn_calc_deg`, 7 canais com máscaras), sobreposições prioritárias 0 % e 50 % (REV-002), pós-processamento como ramo separado (Marco 5), tabela de funções do Marco 3 com o que existe, o que está dentro de um script e o que falta, e contratos do Marco 4 marcados como não implementados.
  - Referências corrigidas em `README.md`, `AGENTS.md` §1 (só a frase das leituras iniciais), `handoff.md`, `PROGRESS.md` (secções vivas e artefactos; as entradas datadas ficam como histórico) e nos docstrings de `scripts/check_units_train.py` e `scripts/create_split_manifest.py`.
- **Porquê:** pedido do utilizador, para simplificar e modernizar a documentação em `docs/` depois de várias decisões terem mudado o âmbito e a forma de trabalhar.
- **Ficheiros afetados:** `docs/*`, `README.md`, `AGENTS.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`, `scripts/check_units_train.py`, `scripts/create_split_manifest.py` (só comentários).
- **Correspondência no LaTeX:** **não aplicável**; é só reorganização da documentação Markdown, sem mudança de metodologia, de resultados nem de decisões.
- **Validação:** releitura dos oito documentos antigos contra o código real (`src/phase1/`, `scripts/`, `configs/`, `tests/`) e contra `PROGRESS.md`; procura de referências pendentes aos nomes antigos. Não foram executados testes nem código (só se alteraram comentários e Markdown). Os valores numéricos mantidos nos docs vêm de revisões já registadas (REV-001, REV-003, REV-007, REV-008, REV-017); nenhum cálculo novo.
- **Limitações:** as entradas históricas do `PROGRESS.md` e do `REVISION_LOG.md` continuam a citar `docs/05`, `docs/00_5` e outros nomes antigos; mantêm-se por serem registo do que se fez então. A secção 4 de `docs/02` e o contrato de `docs/03` devem ser revistos quando o Marco 4 começar.
- **Pendentes:** revisão do utilizador; commit local por autorizar.

### REV-034 — Código unificado em `src/ais/` e `pyproject.toml`

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde-lima `#7CB342`, RGB (124, 179, 66). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:**
  - `scripts/` (10 programas) e `src/phase1/` passam a um só pacote `src/ais/`: `ais/phase1/` (biblioteca, sem alterações de lógica) e `ais/cli/` (programas, corridos com `python -m ais.cli.<nome>`). `scripts/watch_latex.sh` (não versionado) foi para `latex/watch_latex.sh`.
  - Novo `pyproject.toml` (metadados mínimos do pacote `ais` e `pythonpath` do pytest). Instalação editável só no venv do projeto, sem dependências novas; as versões continuam em `requirements.txt`.
  - Removidos os `sys.path.insert` dos três programas e o `tests/conftest.py`. Imports `phase1` → `ais.phase1`; raiz do projeto `parents[1]` → `parents[3]`; campos `script` da proveniência e docstrings com os novos caminhos.
  - Documentos vivos atualizados: `README.md`, `AGENTS.md`, `handoff.md`, `docs/*`, secções vivas do `PROGRESS.md`, `.gitignore` (`latex/watch_latex.sh`, `*.egg-info/`).
- **Porquê:** pedido do utilizador: duas pastas de código (`scripts/` e `src/`) sem separação consistente (só 4 dos 10 scripts usavam a biblioteca, via `sys.path`), com a preparação num lado e a modelação no outro.
- **Ficheiros afetados:** `src/ais/**`, `tests/*` (imports e dois caminhos), `pyproject.toml`, `.gitignore`, `latex/watch_latex.sh`, `README.md`, `AGENTS.md`, `handoff.md`, `docs/*`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (organização do código; o `.tex` não cita caminhos de código). Não verificado por compilação.
- **Validação:** `pytest tests/` → 94 passaram; 20 módulos de `ais` importados; `python -m ais.cli.verify_trip_count` executado (123 viagens). Treino, figuras, benchmark e ensaio de 3 viagens **não** foram reexecutados, para não sobrescrever `results/`.
- **Limitações:** a proveniência de artefactos antigos em `results/` continua a registar `scripts/…`; as entradas históricas de `PROGRESS.md` e `REVISION_LOG.md` mantêm os caminhos antigos. `class_metrics` continua duplicada e a lógica de preparação continua dentro de `cli/`.
- **Pendentes:** revisão do utilizador; commit local por autorizar.

### REV-035 — Treino final com todo o treino e números do LaTeX gerados por código

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Violeta `#6200EA`, RGB (98, 0, 234). No `.tex`, em `\revtext{rev035}` e `\rv{...}`.
- **O quê:**
  - Treino final da CNN 1D (viagem completa, sem janelas) com **as 87 viagens do treino oficial** e sem monitorização interna (pedido do utilizador): `configs/phase1_final.json` (seed 42, Adam lr 1e-3, máx. 100 épocas, **paciência 30**, orçamento 15 min, limiar 0,5). Sem viagens de fora, a paragem antecipada e o melhor modelo usam a perda por ponto avaliada sobre o próprio treino (interpretação minha da instrução «paciência 30 e 0 % de monitorização»; ver Limitações).
  - Código: `internal_monitor_fraction` aceita 0 em `config.py`; `train_model` suporta monitor vazio (`stop_criterion`); `run_phase1_training` trata esse caso e grava `predictions_train.csv`. Novo `src/ais/cli/build_final_results.py`: lê só artefactos já gerados, confirma por hash que os sumários da preparação correspondem à base de treino e ao manifesto, e escreve `results/phase1_final/final_results.json` (fonte única), `latex/generated/resultados.tex` (macros `\res...`) e `latex/figures/final_{perda,matriz,viagens}.png`. Testes novos: configuração com 0, treino sem monitor, formatação dos números.
  - LaTeX: a subsecção «Primeira execução de treino» (REV-032) passa a «Treino final e resultados no treino», com tabela e três figuras; removidos o ensaio de 3 viagens (REV-027, REV-028, REV-030) e o Anexo A (REV-031). Números do texto que vêm de código (viagens e linhas, parâmetros, campo recetivo, versão do PyTorch, coincidência com os originais, rumo, configuração e resultados do treino) passam a macros. Referências a `phase1_run1` e à «primeira execução» corrigidas.
- **Resultado (de `results/phase1_final/final_results.json`):** terminou ao atingir o **máximo de 100 épocas**, sem disparar a paragem antecipada, em cerca de 361 s; melhor época 95; accuracy no treino 94,6 % contra 75,4 % da classe maioritária; 1 das 87 viagens (`219429000-2`) não supera a regra da classe maioritária da viagem. Os valores completos e a proveniência estão no ficheiro.
- **Limitações:**
  - As métricas são medidas **nas mesmas viagens que ajustaram a rede**: são ajuste, não generalização. Validação e teste oficiais não foram abertos.
  - A rede não convergiu no sentido do critério: a melhor época é a 95 de 100 e a perda ainda variava no fim. Mais épocas (com orçamento maior) podem melhorar o ajuste; é decisão do utilizador.
  - A instrução «paciência 30 com 0 % de monitorização» não define sozinha o critério; usei a perda no treino. A monitorização com os 15 % reservados fica para a etapa de validação, que só se abre com autorização explícita.
  - Os sumários da preparação (`results/clean_*`, `anomalies_train`) são de 2026-11-23, verificados por hash, mas não foram regenerados nesta revisão.
  - Os programas do ensaio (`diagnostic_fit_3_trips`, `plot_diagnostic_3trips`), as PNG `latex/figures/diag3_*` e `results/phase1_run1/` ficam no repositório/disco, já sem uso no texto.
- **Ficheiros afetados:** `src/ais/phase1/{config,training}.py`, `src/ais/cli/{run_phase1_training,build_final_results}.py`, `configs/phase1_final.json`, `tests/test_checkpoint_and_training_loop.py`, `tests/test_final_results_format.py`, `latex/proposta_pt.tex`, `latex/generated/resultados.tex`, `latex/figures/final_*.png`, `PROGRESS.md`, `REVISION_LOG.md`, `handoff.md`, `docs/02_cnn_viagem_completa.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` + `bibtex` sem erros nem referências em falta (7 páginas); páginas 5 e 6 inspecionadas visualmente.
- **Validação:** `pytest tests/` → 99 passaram (94 anteriores, mais 5 novos); treino real com checkpoint recarregado do disco para as previsões; verificação por hash da base de treino e do manifesto; figuras e PDF inspecionados.
- **Pendentes:** decidir se se treina mais tempo (aumentar épocas/orçamento); validação e teste só com autorização; commit local por autorizar; remover os restos do ensaio, se o utilizador quiser.

### REV-036 — Papéis dos conjuntos reservados: `test` seleciona, `validation` mede no fim

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde `#00C853`, RGB (0, 200, 83). No `.tex`, em `\revtext{rev036}`.
- **O quê:** por decisão do utilizador, os papéis dos conjuntos reservados ficam **trocados face ao habitual**: o conjunto `test` (18 viagens) é o de **seleção** (número de épocas, limiar, se treinar mais compensa, escolha entre variantes) e o conjunto `validation` (18 viagens) é a **medição final**, aberta **uma só vez** com o modelo e o protocolo congelados. Os nomes dos ficheiros e do manifesto não mudam (renomear mudaria os hashes). Os marcos 6 e 7 e as etapas B e C foram reescritos em conformidade.
- **Porquê:** pedido do utilizador; a regra anterior (validação seleciona, teste mede) estava escrita no `AGENTS.md`, em `docs/00` e no LaTeX.
- **Ficheiros afetados:** `AGENTS.md` §3 (única regra alterada; nota no padrão de «Papéis dos conjuntos reservados»), `docs/00_projeto_e_decisoes.md`, `docs/02_cnn_viagem_completa.md`, `docs/03_cnn_janelamento.md`, `handoff.md`, `latex/proposta_pt.tex` (subsecção «Divisão dos dados e protocolo» e a frase final do treino), `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` + `bibtex` sem erros nem referências em falta (7 páginas). Não foi inspecionado visualmente o PDF desta revisão.
- **Validação:** revisão manual e procura de contradições nos documentos. Nada foi executado nem aberto: nem o `test` nem o `validation` foram lidos além do que já constava (REV-015).
- **Limitações:** o código e os comentários só falam genericamente em «validação/teste» (recusa de ambos no desenvolvimento) e continuam corretos. Resultados no `test` serão otimistas por terem servido para escolher; o número final da proposta será o do `validation`. O `test` tem menos pontos (103 409) do que o `validation` (209 016), o que torna a seleção mais ruidosa. Esta revisão **não é autorização** para abrir nenhum dos conjuntos.
- **Pendentes:** autorização explícita para abrir o `test` (com âmbito e critérios declarados), programa de avaliação reservada com registo de acesso, decisão sobre treinar mais, commit local por autorizar.

### REV-037 — Plano atualizado: segmentos no início do Marco 4 e medição final só no fim

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Âmbar `#FFAB00`, RGB (255, 171, 0). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** por decisão do utilizador, as métricas por segmento não entram na baseline: ficam para o **início do Marco 4**, como ferramenta de medição (extrair segmentos sem suavizar, fragmentação, erro de fronteira), distinta do pós-processamento, que só avança no Marco 5 se o Marco 4 mostrar benefício da sobreposição. A medição final no `validation` passa a ser **uma só vez, no fim, com todas as variantes congeladas** (e não já para a baseline). `docs/00` §4 reescrito em conformidade.
- **Porquê:** a prova de que a sobreposição ajuda é sobre fronteiras e fragmentação (RQ1), e abrir o `validation` já para a baseline obrigaria a reabri-lo depois.
- **Ficheiros afetados:** `docs/00_projeto_e_decisoes.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (plano; sem mudança de metodologia descrita no `.tex`).
- **Validação:** revisão manual. Nada foi aberto nem executado.
- **Pendentes:** nenhum além dos de REV-038 e REV-039.

### REV-038 — Acesso reservado, seleção no `test` e baseline congelada

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Índigo `#304FFE`, RGB (48, 79, 254). Só marcador do registo.
- **O quê:**
  - Código novo: `ais/phase1/reserved.py` (autorização, protocolo, registo de acessos em `results/access_log.jsonl`, uma só ronda, `validation` recusado sem autorização própria e execução congelada, só uma abertura), `selection.py` (época pela menor perda por ponto; limiar da grelha 0,05 a 0,95 pelo F1 médio), `inference.py` (a inferência saiu do script de treino), e os programas `select_on_test` e `freeze_baseline`. `train_model` e a configuração passam a aceitar um checkpoint por época (`checkpoint_every_epoch`).
  - Antes de abrir qualquer conjunto: protocolo declarado (`configs/selection_protocol.json`) e autorização (`configs/authorizations/test_selection.json`, com a citação literal do utilizador, o âmbito `test`, finalidade seleção e 1 ronda).
  - Treino de seleção (`configs/phase1_select.json`): só treino (87 viagens), 300 épocas, paragem antecipada desativada (a escolha da época passou para o `test`), um checkpoint por época; 1164 s.
  - Seleção no `test` (uma ronda, 18 viagens, 103 409 pontos): **época 162 de 300**, **limiar 0,65**. Resultados em `results/phase1_select/selection_test.json`; baseline congelada em `results/baseline_frozen/` (hash do checkpoint conferido).
- **Resultado (de `selection_test.json`):** no `test`, com o limiar escolhido, accuracy 94,7 % contra 61,2 % da classe maioritária; navegação sensibilidade 0,971, precisão 0,900, F1 0,934; pesca sensibilidade 0,931, precisão 0,981, F1 0,955. **Otimistas**, por terem servido a escolher.
- **Limitações:**
  - A perda no `test` oscila muito entre épocas (0,18 na época 162; 0,30 na 200; a época 52 empata com a 162). O mínimo escolhido é estreito, pelo que a escolha pode ter seguido ruído, e a seleção usa só 18 viagens. A ronda era uma só, por isso não se repetiu. Decisão do utilizador pendente.
  - A distribuição de classes do `test` (61 % de pesca) difere do treino (75 %).
  - O `test` foi aberto uma vez, sob autorização escrita a partir da instrução do utilizador («Concordo com tudo o que disseste… podes parar»); o utilizador pode considerar a autorização demasiado implícita.
  - O mecanismo de acesso é uma salvaguarda do código, não impede quem tenha acesso ao disco de ler os ficheiros.
  - **O `validation` não foi aberto.**
- **Ficheiros afetados:** `src/ais/phase1/{reserved,selection,inference,config,training}.py`, `src/ais/cli/{select_on_test,freeze_baseline,run_phase1_training}.py`, `configs/{phase1_select,selection_protocol}.json`, `configs/authorizations/test_selection.json`, `tests/{test_reserved_access,test_checkpoint_and_training_loop}.py`, `docs/00`, `docs/02`, `README.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **pendente**. O `.tex` ainda descreve o treino de 100 épocas e métricas no treino (REV-035) e não menciona a seleção no `test`, a baseline congelada nem os navios partilhados; falta decidir o que apresentar, face ao ruído da seleção.
- **Validação:** `pytest tests/` → 145 passaram (política de acesso, uma só ronda, recusa do `validation`, protocolo e finalidade, ficheiro errado, ids fora do conjunto, checkpoint escolhido, congelação com deteção de alteração); execução real da seleção e da congelação com verificação do hash.
- **Pendentes:** decisão sobre o ruído da seleção; atualizar o LaTeX; commit local por autorizar.

### REV-039 — Métricas por segmento e navios partilhados (subagentes)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde-água `#1DE9B6`, RGB (29, 233, 182). Só marcador do registo.
- **O quê:**
  - `ais/phase1/segments.py` e `ais/cli/segment_metrics.py` (subagente Sonnet): extração de segmentos **sem suavizar**, IoU temporal em segundos com intervalo meio-aberto, emparelhamento um-para-um guloso com IoU ≥ 0,5, precisão/sensibilidade/F1 por segmento, erro de fronteira com sinal e fragmentação; agregação micro; divisões por zero dão `None`.
  - `ais/cli/count_shared_vessels.py` (subagente Haiku): lê só o manifesto. Resultado: 9 das 18 viagens de `validation` e 8 das 18 de `test` têm navio presente no treino; 2 navios partilhados entre `validation` e `test` (`results/shared_vessels/summary.json`).
  - Revistos por mim: li `segments.py`, conferi à mão o exemplo de 34 pontos (2 referências, 3 previstos, 2 pares, F1 0,8, fragmentação 1,5, erros de início 0 e 2 s, de fim −5 e 0 s), recalculei as contagens dos navios com lógica independente e reimplementei os segmentos com loops puros: sobre as previsões do **treino** da execução de 100 épocas dá o mesmo que a ferramenta (pesca: 88 referências, 1 459 previstos, 59 pares).
- **Porquê:** plano aprovado (REV-037); a prova do Marco 4 precisa destas medidas.
- **Ficheiros afetados:** `src/ais/phase1/segments.py`, `src/ais/cli/{segment_metrics,count_shared_vessels}.py`, `tests/{test_segments_and_metrics,test_count_shared_vessels}.py`, `docs/02`, `README.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **pendente** (as definições de segmento e os navios partilhados ainda não estão no texto).
- **Validação:** `pytest tests/` → 145 passaram (24 de segmentos e 11 dos navios, sintéticos). Só treino e manifesto foram lidos.
- **Limitações:** as métricas por segmento **não foram calculadas sobre a baseline congelada** (precisa de autorização, por usar o `test`); o teste de fumo foi só sobre previsões do treino de outra execução e serve para validar a ferramenta, não como resultado. Os subagentes não atualizaram os registos (limitados a poucos ficheiros).
- **Pendentes:** commit local por autorizar; medição por segmento da baseline no Marco 4.

### REV-040 — LaTeX atualizado com a baseline congelada (300 épocas, seleção no `test`)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Castanho-avermelhado `#7F0000`, RGB (127, 0, 0). No `.tex`, em `\revtext{rev040}` e na cor da tabela.
- **O quê:**
  - `src/ais/cli/build_final_results.py` reescrito: parte da baseline congelada (`results/baseline_frozen/`) e do treino de seleção (`results/phase1_select/`). Confirma por hash a coerência do manifesto, dos sumários, do checkpoint e da seleção, e que o `validation` nunca foi aberto e o `test` só uma vez (`access_log.jsonl`). Avalia a baseline nas 87 viagens de treino (permitido) e lê os números do `test` de `selection_test.json`, sem abrir o parquet do `test`. Escreve `results/baseline_frozen/final_results.json`, `latex/generated/resultados.tex` e `latex/figures/final_{perda,matriz,viagens}.png`.
  - LaTeX: a subsecção do treino passa a «Treino, seleção e resultados»: 300 épocas sem paragem antecipada, escolha da época e do limiar no `test` com critérios declarados antes, tabela por classe com treino e teste, matrizes de confusão (treino e teste), perda por época (treino e teste) e exatidão por viagem de teste. Frases sobre 100 épocas, paragem antecipada, `phase1_final.json` e «validação e teste não foram abertos» corrigidas (o `test` serviu para escolher; o `validation` não foi aberto). Substitui o texto e as figuras de REV-035.
  - Por decisão do utilizador, **não** se acrescentou ao texto nada sobre navios partilhados entre conjuntos; a frase já existente (não afirmar generalização para navios inéditos) mantém-se.
- **Porquê:** pedido do utilizador: valores recentes, calculados por código e consistentes com a baseline congelada, em vez dos do treino de 100 épocas.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `latex/generated/resultados.tex`, `latex/figures/final_*.png`, `src/ais/cli/build_final_results.py`, `docs/02_cnn_viagem_completa.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` + `bibtex` sem erros nem referências em falta (7 páginas); páginas 5 e 6 inspecionadas. Dois avisos de «overfull» pequenos (5,8 e 16 pt). Sem macros indefinidas.
- **Validação:** `build_final_results` executado com as verificações de proveniência a passar; o registo de acessos manteve 2 entradas (a geração não abriu nenhum conjunto); figuras e PDF inspecionados. `pytest tests/` → 145 passaram depois da revisão (o gerador só tem teste das funções de formatação).
- **Limitações:**
  - Os resultados do `test` são **otimistas** (esse conjunto serviu para escolher); o texto di-lo. A perda no `test` oscila muito entre épocas e o texto também o refere.
  - A medição final no `validation` ainda não existe. As métricas por segmento ainda não estão no texto.
  - O gerador não tem teste automático além das funções de formatação.
- **Pendentes:** decisão do utilizador sobre o ruído da seleção; commit local por autorizar; Marco 4.

### REV-041 — Baseline fechada; CNN de referência única e secção de Resultados

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Vermelho vivo `#FF1744`, RGB (255, 23, 68). No `.tex`, em `\revtext{rev041}`.
- **O quê:**
  - Decisão do utilizador: a CNN 1D sobre a viagem completa fica **fechada** como está (época 162, limiar 0,65), e passa a ser a CNN de referência; só se volta a ela na comparação com as janelas e na escolha final. Marco 4: a mesma CNN sobre janelas, com L = 64 pontos e sobreposição de 0 % (controlo) e 50 %, e depois testar outros L.
  - LaTeX: a subsecção 4.2 passa a «CNN de referência» (curta: é a mesma rede nas duas experiências, porque se escolheu esta referência, entrada) e deixa de repetir a arquitetura, a perda e o treino, que ficam só na Secção 5. A Secção 5 passa a valer para a viagem completa e para as janelas (entrada, figura, perda e lote). A subsecção 4.4 (janelamento) fica definida: L = 64, 0 % e 50 %, média por ponto, preenchimento ignorado, o que está por decidir e que ainda não foi implementado. Nova Secção 8 «Resultados»: 8.1 «CNN de referência sobre a viagem completa» (movida da Secção 5, com a nota de que está fechada) e 8.2 «CNN de referência com janelamento» (marcador: ainda não feito). Objetivo 2 e esquema do pipeline dizem «a mesma rede».
  - `docs/00` (marcos 3 e 4), `docs/03` (L = 64 e baseline fechada), README e handoff atualizados.
- **Porquê:** pedido do utilizador: um só texto da CNN de referência (sem duplicação entre 4.2 e 5), resultados separados por experiência e a baseline como termo de comparação.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `docs/00_projeto_e_decisoes.md`, `docs/03_cnn_janelamento.md`, `README.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` + `bibtex` sem erros nem referências em falta (8 páginas); páginas 3 e 7 inspecionadas. Dois avisos de overfull pequenos (5,8 e 16 pt).
- **Validação:** compilação e inspeção visual. Nenhum número novo: os resultados continuam a vir das macros geradas (REV-040). Código e testes não foram alterados.
- **Limitações:** o texto das secções 1, 2, 3 (objetivos), 6 e 7, o resumo e o título não foram revistos nesta revisão (ver lista em PROGRESS); o resumo, os objetivos e a Avaliação ainda citam HMM e Wu et al. como comparações e as quatro taxas de sobreposição, embora o âmbito atual os deixe de fora (REV-006, REV-002).
- **Pendentes:** decidir o que fazer com essas passagens; decisões do Marco 4 (sobreposição no treino/inferência, orçamento, autorização para medir a baseline por segmento); commit local por autorizar.

### REV-042 — HMM e Wu et al. deixam de ser comparações no LaTeX

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul-marinho `#0A3D62`, RGB (10, 61, 98). No `.tex`, em `\revtext{rev042}`.
- **O quê:** por decisão já registada (REV-006: HMM e Wu et al. fora por agora) e a pedido do utilizador, o texto deixa de os apresentar como comparações. Resumo: a avaliação compara a CNN sobre a viagem completa com a CNN sobre janelas sobrepostas. Objetivo 2: a CNN sobre a viagem completa é a referência com que se compara a das janelas (removido «Como baselines, Wu et al. e um HMM»). Critérios de sucesso (objetivos): efeito das componentes face à CNN de referência, e já não face a «baselines». Avaliação 7.1: compara a CNN sobre janelas com a CNN de referência. Pós-processamento (4.5): deixa de dar o HMM como exemplo; passa a votação por vizinhança, com unidade e largura por definir (conforme o `docs/00`, Marco 5).
- **O que se manteve:** a Contexto continua a citar os HMM (Peel e Good, Vermard et al.) como história do problema e o Wu et al. (2022) como trabalho de referência na literatura, incluindo a frase «a referência central deste projeto» e a de posicionamento face ao Wu et al.; são literatura, não comparação.
- **Porquê:** o texto contradizia o âmbito atual.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`, `handoff.md`.
- **Correspondência no LaTeX:** **atualizado**. `pdflatex` + `bibtex` sem erros nem referências em falta (8 páginas); página 1 inspecionada. Os termos HMM e Wu só restam na Contexto e na bibliografia.
- **Validação:** compilação, inspeção visual e procura por HMM, Wu e «baseline» no PDF. Nenhum código nem número alterado.
- **Limitações:** continuam por resolver as outras passagens da lista de REV-041: as quatro taxas de sobreposição e a ablação (7.1), a explicabilidade, calibração e *dashboard* (resumo, objetivo 5, 4.6, 7.3), o texto a vermelho «human-on-the-loop» e a Secção 6 no futuro. A expressão «referência central» (Wu et al.) pode confundir-se com «CNN de referência».
- **Pendentes:** decidir essas passagens; commit local por autorizar.

### REV-043 — Texto estável do LaTeX passa a preto (cor definitiva)

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** nenhuma nova: o texto que o utilizador e eu consideramos estável passa a **preto**; o que ainda pode mudar mantém a cor da sua revisão. Por instrução expressa do utilizador («o que já não vai ser modificado, mete como cor definitiva a preto»).
- **O quê:**
  - **A preto (estável):** objetivos 1 e 2 e os critérios de sucesso; 4.1 Pré-processamento; 4.2 CNN de referência; 4.3 Verificação da implementação (exceto a última frase); Secção 5 (especificação da CNN) exceto as partes de janelas; Secção 6 (tratamento dos dados); 7.2 Divisão dos dados e protocolo; 8.1 Resultados da CNN de referência sobre a viagem completa (texto, tabela e legendas).
  - **Mantém a cor (pode mudar):** o esquema do pipeline (Figura 1); 4.4 Janelamento (rev041); 4.5 Pós-processamento (rev021, rev042); 4.6 Saída, explicabilidade e ferramentas (rev021); a frase final da 4.3 sobre o conjunto de validação (rev040, deixa de ser verdade quando o `validation` for aberto); as partes de janelas da Secção 5 (entrada e saída, perda, otimizador, figura e frase inicial, rev041); 7.1 e 7.3 (títulos rev023 e a frase da 7.1, rev042); o resumo (frase rev042); a Secção 8 (título e introdução) e 8.2 (rev041).
  - Números gerados (`\rv`) deixam de ter cor própria: herdam a do texto que os rodeia. A figura da CNN passa a cinzentos neutros em vez do verde de rev026.
- **Porquê:** pedido do utilizador, para distinguir o que está fechado do que ainda se vai rever.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `PROGRESS.md`, `REVISION_LOG.md`, `handoff.md`.
- **Correspondência no LaTeX:** **atualizado** (só cores). `pdflatex` + `bibtex` sem erros nem referências em falta (8 páginas). **Verificação de conteúdo:** compilei a versão anterior e a nova e comparei o texto extraído dos dois PDFs: igual (as 6 linhas de diferença são só a posição da numeração de linhas). Páginas 3 e 6 inspecionadas.
- **Validação:** comparação de texto antes e depois e inspeção visual. Nenhum código nem número alterado.
- **Limitações:** a classificação «estável» é minha; o utilizador não leu em pormenor as subsecções 5.3 a 5.6 nem a 6.1 depois das alterações, por isso a preto não significa «revisto». O texto original sem cor (por exemplo, as quatro taxas de sobreposição e a ablação na 7.1) continua a preto sem estar fechado; fica na lista de pendentes. As cores antigas continuam definidas no preâmbulo, sem uso.
- **Pendentes:** passagens abertas de REV-041 e REV-042; decisões do Marco 4.

### REV-044 — Handoff reescrito e documentos alinhados

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Cinzento `#9E9E9E`, RGB (158, 158, 158). Só marcador do registo e dos documentos; não há alteração ao `.tex`.
- **O quê:**
  - `handoff.md` reescrito de raiz para outra sessão: data, como retomar, objetivo, estado (marcos, baseline, conjuntos reservados, testes, LaTeX, git), decisões vigentes, ficheiros principais, comandos, resultados e ensaios, o que falhou, próximos passos, regras e preferências do utilizador. Corrigidas as incoerências do anterior (estado do git, duas linhas de push, lista partida, 7 páginas em vez de 8).
  - `PROGRESS.md`: estado, decisões, pendências e artefactos passam para o topo e foram atualizados; removidos os blocos antigos a meio do histórico (pendentes por marco, pendências e tabela de artefactos, com itens como «Marco 3 em curso», `scripts/` e «código ainda não criado»). As entradas datadas ficam como estavam.
  - `README.md` reescrito: estado, estrutura, ambiente e tabela de todos os programas.
  - `docs/00` (marco 4 «por começar»), `docs/02` (§3 passa a descrever o treino da baseline; apagadas a descrição da execução com monitorização, as linhas «Por fazer» substituídas e a referência ao ensaio retirado; §6 passa a «Marco 3: fechado») e `docs/03` (janelamento por implementar, mas a ferramenta de segmentos existe; fluxo final alinhado com os papéis dos conjuntos).
- **O que se eliminou dos `docs/`:** só passagens já feitas ou obsoletas (acima). Nenhum dos quatro ficheiros ficou inteiramente por apagar: todos têm conteúdo ainda em uso, incluindo o `docs/03` (Marco 4, por fazer).
- **Porquê:** pedido do utilizador: um handoff para outra sessão e todos os ficheiros coerentes entre si.
- **Ficheiros afetados:** `handoff.md`, `PROGRESS.md`, `README.md`, `docs/00_projeto_e_decisoes.md`, `docs/02_cnn_viagem_completa.md`, `docs/03_cnn_janelamento.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (documentação Markdown; o `.tex` não foi alterado).
- **Validação:** releitura de todos os documentos e procura de contradições (estado dos marcos, contagem de testes, caminhos, números de REV, configurações); os números citados no handoff vêm de `results/baseline_frozen/final_results.json`; `pytest tests/` → 145 passaram. Código e LaTeX não foram alterados.
- **Limitações:** as entradas históricas do `PROGRESS.md` e do `REVISION_LOG.md` mantêm caminhos e estados antigos (`scripts/`, «em curso»), por serem registo. Os commits desta revisão foram enviados em `d1f30e0..1bc3d8c`, com autorização do utilizador.
- **Pendentes:** as pendências abertas do topo do `PROGRESS.md`.

### REV-045 — Handoff com data e hora da escrita e da última validação

- **Data:** 2026-11-23 19:42 WET.
- **Cor:** Taupe `#BCAAA4`, RGB (188, 170, 164). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** por pedido do utilizador, o `handoff.md` passa a indicar sempre a data e a hora (fuso WET, igual a UTC em novembro) da atualização e da última validação. Acrescentados: uma tabela «Última validação» (testes, compilação do LaTeX, estado do git, geração dos números da baseline, congelação, seleção no `test` e confirmação de que o `validation` não foi aberto, cada uma com a sua hora) e a cronologia dos últimos commits com data e hora, gerada a partir do `git log`. Regra nova em `AGENTS.md` §5 e no handoff: horas obtidas com `date`, nunca estimadas.
- **Porquê:** para o utilizador e o próximo agente saberem o que foi verificado e a que horas; o que mudar depois dessas horas não está validado pelo handoff.
- **Ficheiros afetados:** `AGENTS.md` (uma regra), `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação:** `pytest tests/` → 145 passaram e `pdflatex` + `bibtex` → 8 páginas, 0 erros, às 19:41 WET (as horas da tabela são as medidas nessas execuções); horas da baseline, da congelação e da seleção lidas dos ficheiros de resultados e do `access_log`.
- **Limitações:** a tabela fica desatualizada assim que algo mudar; o handoff diz-o. As horas anteriores a esta revisão não foram registadas nos documentos, por isso a cronologia só cobre os commits.
- **Pendentes:** nenhum.

### REV-046 — Janelamento implementado, J0 e J50 treinadas

- **Data:** 2026-11-23, até às 23:34 WET (código e testes até às 23:08; treinos 22:58–23:28; commits `9896021`, `2d0ca50`, `5abf3ff`).
- **Cor:** Azul-céu `#00B0FF`, RGB (0, 176, 255). (`#E65100` e `#AD1457`, escolhidas primeiro, já eram as de REV-011 e REV-007 e foram trocadas antes de qualquer commit com cor. A paleta está cheia: o ID é a referência permanente.)
- **O quê:**
  - `src/ais/phase1/windows.py`: passo, inícios das janelas, `WindowSet` (extração sob pedido, cobertura, tabela janela↔ponto), perda mascarada, época de treino, inferência e reconstrução por média das probabilidades. `FullTripCNN.forward` aceita uma máscara opcional (sem ela, a baseline não muda).
  - `src/ais/cli/run_window_training.py` e `configs/windows_j0.json` (0 %) e `configs/windows_j50.json` (50 %): mesma CNN, seed 42, Adam lr 1e-3, 300 épocas, um checkpoint por época, lote de 32 janelas, L = 64, normalizador igual ao da baseline (verificado), 45 minutos de limite.
  - Treinos: J0 em 9,8 min (11 201 janelas, 351 passos por época, 105 300 passos) e J50 em 21,3 min (22 265 janelas, 696 passos por época, 208 800 passos), ambos completos.
  - Decisões do utilizador registadas: a mesma sobreposição no treino e na inferência; mesmos valores da baseline (sem aumentar épocas); a última janela fica mais curta, sem pontos falsos; os intervalos de tempo dentro de uma viagem não cortam a sequência (como na baseline); lote de 32 igual nas duas variantes; ficam fora do projeto treinar com J0 e prever com J50, as sobreposições de 25 % e 75 % e outros L.
  - `docs/03` reescrito com as decisões e os contratos tal como implementados.
- **Porquê:** Marco 4 (RQ1), a pedido do utilizador.
- **Ficheiros afetados:** `src/ais/phase1/windows.py`, `src/ais/phase1/model.py`, `src/ais/cli/run_window_training.py`, `configs/windows_j0.json`, `configs/windows_j50.json`, `tests/test_windows.py`, `docs/03_cnn_janelamento.md`.
- **Correspondência no LaTeX:** **atualizado** (4.4, entrada e saída, perda, otimizador e reprodutibilidade da Secção 5), com a cor desta revisão.
- **Validação:** 31 testes sintéticos de janelas (equivalência do lote com enchimento e da janela isolada, cobertura, reconstrução com valores conhecidos, perda mascarada, reprodutibilidade); suite completa: 181 passaram. Revisão independente (subagente Opus, só leitura) sem erros graves; as melhorias que sugeriu foram aplicadas depois do arranque do J50, sem efeito numérico (o enchimento do lote já era zero).
- **Limitações:** J50 faz cerca do dobro dos passos de J0 no mesmo número de épocas; o lote (32 janelas) difere do da baseline (uma viagem por passo); uma só semente; os checkpoints não guardam o otimizador. O `docs/03` ainda cita, como no desenho inicial, módulos que foram agrupados em `windows.py`.
- **Pendentes:** os de REV-047 e REV-048.

### REV-047 — Seleção de J0 e J50 no `test`, resultados e secções 8.2 a 8.4

- **Data:** 2026-11-23, 23:28 a 23:34 WET (abertura do `test` às 23:28:19 WET; `selection_done` às 23:29:54; commit `867f8d8`).
- **Cor:** Violeta escuro `#4A148C`, RGB (74, 20, 140). (`#AD1457` foi trocada por já ser a de REV-007.)
- **O quê:**
  - Autorização nova `configs/authorizations/test_selection_windows.json` (uma abertura do `test`) e protocolo novo `configs/selection_protocol_windows.json` (`selecao_janelas_v1`), declarados antes de abrir. Os ficheiros da baseline não se alteraram.
  - `src/ais/cli/select_windows_on_test.py`: **uma só abertura** avaliou as 600 épocas candidatas, escolheu época e limiar de J0 e de J50, mediu por ponto e por segmento (IoU 0,5, sem suavizar) a baseline congelada, J0 e J50, e congelou J0 e J50 (`results/windows_j0_frozen`, `results/windows_j50_frozen`). Os critérios são os da baseline, aplicados às probabilidades reconstruídas.
  - Resultado: **J0 época 8, limiar 0,60; J50 época 4, limiar 0,75.** Exatidão por ponto no `test`: referência 94,7 %, J0 93,5 %, J50 93,8 % (regra da classe maioritária: 61,2 %); J0 supera a referência em 7 das 18 viagens e J50 em 5. Por segmento, a pesca tem 18 segmentos reais e 358, 377 e 303 previstos (referência, J0, J50), com F1 de segmentos de cerca de 0,03 nas três; a razão de fragmentação na pesca é 19,9, 20,9 e 16,8, e na navegação 10,4, 11,0 e 8,8. A perda no `test` sobe com as épocas (máximos de 0,79 e 0,93 desde a época 100), o que é compatível com ajuste excessivo e explica as épocas escolhidas.
  - `src/ais/cli/build_window_results.py`: `results/windows_final/final_results_windows.json`, `latex/generated/resultados_janelas.tex` e 7 figuras `latex/figures/janelas_*.png`. `build_final_results` passou a contar a abertura do `test` por autorização.
  - Secções 8.2 (J0), 8.3 (J50) e nova 8.4 (comparação e resposta à RQ1).
- **Porquê:** pedido do utilizador: treinar J0 e J50, fechá-las, medi-las no `test` e apresentar os resultados como os da referência.
- **Ficheiros afetados:** `configs/selection_protocol_windows.json`, `configs/authorizations/test_selection_windows.json`, `src/ais/cli/select_windows_on_test.py`, `src/ais/cli/build_window_results.py`, `src/ais/cli/build_final_results.py`, `src/ais/cli/freeze_baseline.py` (parâmetro `label`), `tests/test_select_windows.py`, `latex/proposta_pt.tex`, `latex/generated/resultados_janelas.tex`, `latex/figures/janelas_*.png`.
- **Correspondência no LaTeX:** **atualizado**; `pdflatex` + `bibtex` sem erros, 11 páginas (limite de 15), 0 referências indefinidas, páginas 9 e 10 inspecionadas; 2 caixas largas que já existiam.
- **Validação:** 5 testes sintéticos de ponta a ponta da seleção (uma só abertura, segunda recusada, bloqueio antes de abrir se o treino estiver incompleto, faltarem checkpoints ou a baseline não conferir). Verificações de proveniência no `final_results_windows.json`: `test` aberto uma vez por autorização (duas no total), `validation` nunca aberto, hashes dos checkpoints e das seleções coincidem, normalizador igual ao da baseline. As previsões da baseline recalculadas na abertura coincidem com as da seleção anterior.
- **Limitações:** os resultados do `test` são **otimistas** (serviram a escolher, para as três variantes, com o mesmo critério). As épocas escolhidas são muito cedo e a baseline foi escolhida bem mais tarde: parte da diferença pode vir do critério e não do janelamento. Lote e passos diferem. Uma semente e 18 viagens. O F1 de segmentos de pesca é baixo por a segmentação estar muito fragmentada e por cada viagem ter em geral um só segmento de pesca. O `test` foi aberto mais uma vez (duas aberturas no total): fica registado em `results/access_log.jsonl`.
- **Pendentes:** decisão do utilizador sobre o critério de seleção (ver `PROGRESS.md`); Marco 5; Marcos 6 e 7.

### REV-048 — Restante texto do LaTeX atualizado ao estado real

- **Data:** 2026-11-23, 23:30 a 23:34 WET (commit `867f8d8`).
- **Cor:** Verde-floresta `#1B5E20`, RGB (27, 94, 32). (`#827717`, escolhida primeiro, era demasiado próxima de `#808000`, a de REV-013.)
- **O quê:** Secção 6 passa ao presente («Usa-se»); 7.1 passa a dizer o que se mediu (referência, J0 e J50 por ponto e por segmento) e que o estudo de ablação e as taxas de 25 % e 75 % ficam por fazer, só avançando se o janelamento mostrar benefício.
- **Porquê:** pedido do utilizador para atualizar o resto do LaTeX no que fizesse sentido.
- **Ficheiros afetados:** `latex/proposta_pt.tex`.
- **Correspondência no LaTeX:** **atualizado**.
- **Validação:** compilação (ver REV-047).
- **Limitações:** **não** alterei o que o utilizador adiou ou que muda o âmbito (explicabilidade, calibração e *dashboard* no resumo, objetivo 5, 4.6 e 7.3; texto a vermelho «human-on-the-loop»). O texto a preto de REV-043 que descreve a referência manteve-se.
- **Pendentes:** as passagens adiadas acima.

### REV-049 — Gráfico de diagnóstico de uma viagem do `test`

- **Data:** 2026-11-23, 23:40 WET.
- **Cor:** Salmão `#FF8A80`, RGB (255, 138, 128). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** novo programa `src/ais/cli/plot_trip_diagnostic.py`, pedido pelo utilizador para ver porque a exatidão de J0 na viagem `219001624-2` é baixa. Lê só as previsões por ponto já geradas na abertura autorizada do `test` e desenha a classe real e a prevista pela referência, J0 e J50, e as probabilidades de pesca (`results/diagnostic_trip/219001624-2_classes.png`, não versionado).
- **Observado (apenas desta viagem, 1 053 pontos, 633 de pesca real):** exatidão da referência 83,7 %, de J0 42,0 % e de J50 80,4 %. As três curvas de probabilidade têm a mesma forma (sobem no início da pesca e descem nas mesmas pausas), mas em J0 a probabilidade na fase de pesca fica por volta de 0,3 a 0,5, abaixo do seu limiar de 0,60, pelo que J0 prevê quase tudo como navegação; a referência (cerca de 0,7, limiar 0,65) e J50 (cerca de 0,8 a 0,9, limiar 0,75) ficam acima do limiar. As três partem o segmento real de pesca em pedaços nas mesmas pausas. Não se sabe, só com este gráfico, o que representam as pausas.
- **Porquê:** diagnóstico pedido pelo utilizador. Não serve para escolher nada nem altera resultados.
- **Não feito:** o gráfico das coordenadas `x` por `y` desta viagem. Exige ler o ficheiro do `test`, um uso novo do conjunto reservado que a autorização das janelas (uma só abertura, já usada) não cobre; fica à espera de autorização explícita do utilizador.
- **Ficheiros afetados:** `src/ais/cli/plot_trip_diagnostic.py`, `README.md`, `PROGRESS.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (o `.tex` não foi alterado).
- **Validação:** o gráfico foi gerado e inspecionado; as exatidões saem do próprio programa. `pytest tests/`: 181 passaram (23:40 WET). O programa não tem teste automático.
- **Limitações:** uma única viagem, sem valor estatístico.
- **Pendentes:** autorização para as coordenadas.

### REV-050 — Leitura de diagnóstico de uma viagem do `test` (mecanismo e incidente)

- **Data:** 2026-11-23, 23:43 WET (leitura registada às 23:42:48 UTC).
- **Cor:** Violeta-claro `#B388FF`, RGB (179, 136, 255). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:**
  - `ais.phase1.reserved.load_reserved_diagnostic`: via própria para ler **uma viagem e algumas colunas** de um conjunto reservado, só para diagnóstico. Exige uma autorização com `finalidade = "diagnostico"`, `viagens_autorizadas`, `colunas_autorizadas` e `max_leituras`; recusa sempre o `validation`; regista o evento `diagnostic_read` (distinto de `open`, que continua a contar só as aberturas de seleção) antes de ler; só lê as linhas dessa viagem e as colunas pedidas.
  - `configs/authorizations/test_diagnostic_trip_219001624-2.json`: autorização escrita a partir da resposta do utilizador («sim, autorizo»), para **uma** leitura de `id`, `point_id`, `t`, `x` e `y` da viagem `219001624-2`, só para o gráfico de `x` por `y`.
  - `plot_trip_diagnostic --xy` desenha a trajetória por classe (real, referência, J0, J50), alinhada por `point_id`.
- **Incidente:** a leitura autorizada foi feita e registada, mas o **desenho falhou** (erro meu: opção de proporção inválida com eixos partilhados) e os dados lidos **não tinham sido guardados**. A leitura única ficou gasta sem produzir o gráfico. Não se reutilizou nem se aumentou a autorização por iniciativa própria: pediu-se nova autorização ao utilizador. O programa passou a **guardar os dados lidos antes de desenhar** (`results/diagnostic_trip/<id>_xy_lido.csv`) e o desenho foi testado com coordenadas falsas, sem dados reservados.
- **Porquê:** pedido do utilizador, para perceber a exatidão baixa de J0 nesta viagem.
- **Ficheiros afetados:** `src/ais/phase1/reserved.py`, `src/ais/cli/plot_trip_diagnostic.py`, `configs/authorizations/test_diagnostic_trip_219001624-2.json`, `tests/test_reserved_diagnostic.py`, `README.md`, `PROGRESS.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação:** 6 testes sintéticos novos (só a viagem e as colunas autorizadas, registo, segunda leitura recusada, recusas sem registo, finalidade errada, `validation`, ficheiro errado); `pytest tests/`: 187 passaram (23:43 WET). Exposição: o `access_log` tem um `diagnostic_read` de `219001624-2` (colunas `x`, `y`, `point_id`, `t`, `id`); nenhum valor foi visto nem usado.
- **Limitações:** o programa de desenho continua sem teste automático (só o teste manual com dados falsos). O gráfico de `x` por `y` **ainda não existe**.
- **Pendentes:** nova autorização do utilizador para uma leitura (com o âmbito acima).

### REV-051 — Segunda leitura de diagnóstico e gráfico de `x` por `y` da viagem 219001624-2

- **Data:** 2026-11-23, 23:46 WET (leitura registada às 23:45:53 UTC).
- **Cor:** Pêssego `#FFCC80`, RGB (255, 204, 128). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** nova autorização `configs/authorizations/test_diagnostic_trip_219001624-2_leitura2.json` (uma leitura de `id`, `point_id`, `t`, `x`, `y` da viagem `219001624-2`), escrita a partir do «sim, autorizo» do utilizador, porque a leitura de REV-050 ficou gasta sem gráfico. A anterior não se alterou. `plot_trip_diagnostic` ganhou `--auth` para indicar o ficheiro. A leitura foi feita **uma vez** e registada (`diagnostic_read`, 23:45:53 UTC); os dados lidos ficaram guardados em `results/diagnostic_trip/219001624-2_xy_lido.csv` e o gráfico em `results/diagnostic_trip/219001624-2_xy.png` (não versionados).
- **Observado (só desta viagem):** a pesca real é um troço retilíneo de cerca de 6 km no extremo sul, percorrido de ida e volta. A referência e J50 apanham a maior parte desse troço, mas dão navegação nos extremos (nas viragens). J0 dá navegação em quase todo o troço e só acerta uns pontos de pesca; o resto da viagem (a transição até à zona de pesca) é navegação nas quatro.
- **Porquê:** diagnóstico pedido pelo utilizador. Não escolhe nada nem altera resultados.
- **Ficheiros afetados:** `src/ais/cli/plot_trip_diagnostic.py`, `configs/authorizations/test_diagnostic_trip_219001624-2_leitura2.json`, `PROGRESS.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação:** `pytest tests/`: 187 passaram (23:46 WET); gráfico inspecionado. O programa de desenho não tem teste automático.
- **Limitações:** uma única viagem. O `access_log` tem agora **duas** leituras de diagnóstico desta viagem (a primeira, gasta sem gráfico, e esta); nenhuma é uma abertura de seleção.
- **Pendentes:** nenhum deste pedido.

### REV-052 — Refactoring de leitura da proposta LaTeX

- **Data:** 2026-11-23, 23:57 WET.
- **Cor:** Bordô `#880E4F`, RGB (136, 14, 79) (verificada contra o registo: não repete nenhuma cor anterior).
- **O quê:** a pedido do utilizador, que sentia dificuldade em ler o relatório (figuras acumuladas, texto pouco corrido). Decisões dele: condensar com anexo; fundir figuras; manter as cores; Secção 8 com resumo e comparação primeiro.
  - **Secção 8:** abre com um resumo de três pontos e uma tabela de resumo por ponto; 8.1, 8.2 e 8.3 reduzidas a um parágrafo ou dois cada; 8.4 com a comparação (por ponto, por segmento), a resposta à RQ1 e as limitações em lista. 9 figuras e 6 tabelas passaram a **5 figuras** (perda; matrizes e exatidão por viagem; segmentos e linha temporal, em três blocos) e **3 tabelas** em texto, com as métricas por classe no anexo.
  - **4.3 e 4.4** condensadas; a 4.4 ganhou uma tabela com o protocolo das três experiências. **Secção 5** condensada (frases curtas, listas em «Porquê estes valores»); a tabela da arquitetura e o desenho da rede ficaram como estavam.
  - **Anexo A** novo: pormenores do janelamento (última janela, lotes e enchimento, perda e reconstrução, treino) e a tabela de métricas por classe.
  - `placeins` com a opção `section`, para as figuras não saltarem de secção.
  - `build_window_results`: figuras fundidas `janelas_perda.png` e `janelas_matrizes.png` (a referência entra nas curvas de perda e nas matrizes) e macros `\resBsPassos`, `\resBsPassosTotal`, `\resBsEpocas` e `\resBsSegundos`. As quatro figuras por variante deixaram de se gerar e foram retiradas do repositório.
- **Porquê:** legibilidade. Nenhum resultado, número ou conclusão mudou: todos os números continuam a vir de macros geradas e o texto das conclusões e das limitações é o mesmo, mais curto.
- **Ficheiros afetados:** `latex/proposta_pt.tex`, `latex/generated/resultados_janelas.tex`, `latex/figures/janelas_*.png`, `src/ais/cli/build_window_results.py`, `PROGRESS.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**; `pdflatex` + `bibtex` sem erros, **9 páginas** (antes 11; limite de 15), 0 referências indefinidas, sem caixas largas; páginas inspecionadas.
- **Validação:** compilação e inspeção visual das páginas; `pytest tests/`: 187 passaram (23:57 WET). Não se alterou código de treino, de seleção nem de dados.
- **Limitações:** o texto reescrito é meu; o utilizador ainda não o leu. O texto que ficou a preto das revisões anteriores (por exemplo, a tabela da arquitetura, a Secção 6 e 7.2) não foi tocado. Tudo o que foi reescrito está agora na cor desta revisão, por isso a cor deixa de distinguir o que é de revisões anteriores. As quatro figuras `final_*.png` da referência continuam geradas mas já não são usadas.
- **Pendentes:** as passagens adiadas de REV-041 (explicabilidade, calibração e *dashboard*, «human-on-the-loop»).

### REV-053 — Medição final no `validation` e Secção 9

- **Data:** 2026-11-24, 00:30 a 00:37 WET (escolha do modelo gravada às 00:32:09 UTC, abertura do `validation` às 00:32:09 UTC, fim às 00:32:10; commit de preparação `9ab2e46`).
- **Cor:** Azul-escuro `#0D47A1`, RGB (13, 71, 161) (verificada contra o registo: não repete nenhuma cor anterior).
- **O quê:**
  - Pedido do utilizador: escolher o melhor dos três modelos, medi-lo no `validation` e acrescentar uma Secção 9 antes dos anexos. Escrevi, **antes de abrir**, o protocolo `configs/selection_protocol_validation.json` (`medicao_final_v1`) e a autorização `configs/authorizations/validation_final.json` (uma abertura, só do modelo escolhido).
  - **Critério de escolha (declarado antes, só com o `test`):** maior F1 médio por ponto; empate pela exatidão e depois pela ordem referência, J0, J50. Resultado: **referência** (F1 médio 0,945; exatidão 94,7 %), à frente de J50 (0,934; 93,7 %) e J0 (0,931; 93,4 %). Época 162 e limiar 0,65.
  - `src/ais/cli/final_validation.py`: verifica os três modelos congelados, escolhe o modelo e grava a escolha **antes** de abrir, abre o `validation` **uma só vez** e mede só o modelo escolhido; `build_validation_results.py` gera macros e figuras a partir dos ficheiros já gerados, sem reabrir. `build_final_results` e `build_window_results` passaram a aceitar a abertura do `validation` pela medição final.
  - **Resultado no `validation` (18 viagens, 209 016 pontos):** exatidão 94,4 % (11 662 erros; regra da classe maioritária: 83,2 %); no `test`, a mesma rede teve 94,7 % (61,2 %). Pesca: sensibilidade 0,938 e precisão 0,995. Navegação: sensibilidade 0,976 e **precisão 0,760** (0,900 no `test`), porque 10 836 pontos de pesca são previstos como navegação e a navegação é minoritária (35 052 pontos). Por viagem: de 40,4 % (viagem `219020187-4`) a 99,7 %, mediana 98,2 %; uma viagem não supera a regra da classe maioritária. Por segmento: pesca com 18 segmentos reais e 486 previstos (fragmentação 27,0; F1 de segmentos 0,028), navegação com 35 e 502 (F1 0,119).
  - **Secção 9** da proposta (9.1 escolha, 9.2 resultados, 9.3 leitura e limitações), antes do anexo, e as frases que diziam que o `validation` não tinha sido aberto foram atualizadas.
- **Porquê:** Marcos 6 e 7, a pedido do utilizador.
- **Ficheiros afetados:** `configs/selection_protocol_validation.json`, `configs/authorizations/validation_final.json`, `src/ais/cli/final_validation.py`, `src/ais/cli/build_validation_results.py`, `src/ais/cli/build_window_results.py`, `src/ais/cli/build_final_results.py`, `tests/test_final_validation.py`, `latex/proposta_pt.tex`, `latex/generated/resultados_validacao.tex`, `latex/figures/validacao_*.png`, `README.md`, `PROGRESS.md`, `handoff.md`, `docs/00`, `docs/02`, `docs/03`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**; `pdflatex` + `bibtex` sem erros, 11 páginas (limite de 15), 0 referências indefinidas, páginas inspecionadas.
- **Validação:** 5 testes sintéticos de ponta a ponta da medição (escolha e desempates, uma só abertura, segunda recusada, modelo de janelas, bloqueio antes de abrir se o modelo estiver adulterado, autorização sem a bandeira do `validation`); 192 testes a passar antes e depois da medição. Proveniência verificada em `build_validation_results`: `validation` aberto uma só vez ao abrigo da autorização da medição final, escolha gravada antes da abertura, só o modelo escolhido medido, checkpoints congelados conferem por hash.
- **Limitações:** uma só medição, em 18 viagens, sem intervalo de incerteza; J0 e J50 **não** foram medidas no `validation`, pelo que a resposta à RQ1 continua a assentar no `test`, que é otimista; a divisão é por viagem (não se afirma generalização a navios inéditos). **O `validation` ficou gasto:** já não pode servir para medir mais nada, incluindo um futuro pós-processamento (seria uma segunda abertura, proibida pelo protocolo).
- **Pendentes:** decisão do utilizador sobre o pós-processamento (RQ2 e RQ3), que só poderia ser avaliado no `test`.

### REV-054 — Handoff reescrito depois do Marco 4 e da medição final

- **Data:** 2026-11-24 00:42 WET.
- **Cor:** Verde-água `#00BFA5`, RGB (0, 191, 165). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** a pedido do utilizador, `handoff.md` reescrito de raiz, no mesmo formato dos anteriores: data e hora, tabela da última validação (testes, LaTeX, git, treinos, seleção, medição final), cronologia dos commits, como retomar, objetivo, **resumo cronológico do que se fez** (novo), estado, decisões, ficheiros, comandos, o que falhou, o que fazer a seguir, regras e preferências. Corrigidas as duplicações e as contagens desatualizadas do handoff anterior (187 testes, uma frase repetida sobre o push, o diagnóstico descrito duas vezes) e registado o conflito entre o pedido de push do utilizador e o `AGENTS.md` §6.
- **Porquê:** pedido do utilizador, para outra sessão retomar com o que foi feito e o que falta.
- **Ficheiros afetados:** `handoff.md`, `PROGRESS.md`, `README.md` (intervalo de REV), `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (o `.tex` não foi alterado).
- **Validação:** `pytest tests/`: 192 passaram e `pdflatex` + `bibtex`: 11 páginas, 0 erros, 0 referências indefinidas (ambos às 00:41 WET); horas e commits lidos do relógio e do `git log`; números copiados de `final_validation.json`, `final_results_windows.json` e do `access_log`.
- **Limitações:** a tabela da última validação fica desatualizada assim que algo mudar; o handoff diz-o. O `AGENTS.md` §6 e a autorização de push continuam em conflito, sem decisão do utilizador.
- **Pendentes:** os do handoff («O que fazer a seguir»); push de `d6111f6` e deste commit, só a pedido do utilizador.

### REV-055 — Regra do push: só a pedido explícito do utilizador

- **Data:** 2026-11-24 00:46 WET.
- **Cor:** Rosa-claro `#F06292`, RGB (240, 98, 146). Só marcador do registo; não há alteração ao `.tex`.
- **O quê:** por instrução do utilizador, a regra do push muda. **Antes** (`AGENTS.md` §6): o agente nunca faz push, o push é exclusivo do utilizador. **Agora:** quando o utilizador pede push, no chat ou nas suas instruções (por exemplo, no handoff), o agente envia como se fosse ele, sem pedir confirmação nem repetir a autorização; por iniciativa própria, ou a trabalhar sozinho sem pedido explícito, nunca; `--force` só com pedido próprio e risco explicado; os subagentes nunca fazem push; antes de enviar, verificar branch, remoto e commits (sem dados nem segredos).
- **Porquê:** o utilizador resolveu o conflito entre o §6 e os pedidos de push que ia fazendo.
- **Ficheiros afetados:** `AGENTS.md` (§6), `CLAUDE.md`, `handoff.md`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável**.
- **Validação:** releitura dos documentos à procura de contradições sobre o push. Sem código nem LaTeX alterados.
- **Limitações:** a regra é mais permissiva, mas continua a exigir pedido explícito; um pedido genérico («continua») não é pedido de push.
- **Pendentes:** nenhum.

### REV-056 — Pós-processamento: método na proposta, filtro e plano do Marco 5

- **Data:** 2026-11-25 19:13 WET.
- **Cor:** Laranja-escuro `#D84315`, RGB (216, 67, 21).
- **O quê:** decisões do utilizador para o Marco 5 (janela gaussiana de 13 pontos, σ = 13/6, sobre as probabilidades da referência, limiar 0,65, aplicada uma vez às previsões guardadas do `validation`); plano de ação em `docs/04_pos_processamento.md`; filtro em `postprocessing.py` com testes; figura gerada; nova Secção 10 da proposta e frase da 4.5. Na mesma interação, retiradas as menções ao «OOI» dos documentos (sem revisão própria, por decisão do utilizador).
- **Porquê:** o utilizador quer descrever o método na proposta antes dos resultados.
- **Ficheiros afetados:** `latex/proposta_pt.tex` (preâmbulo, 4.5, rótulo da 5.4, Secção 10), `latex/figures/posproc_janela.png`, `src/ais/phase1/postprocessing.py`, `src/ais/cli/plot_postprocessing_kernel.py`, `tests/test_postprocessing.py`, `docs/04_pos_processamento.md`, `PROGRESS.md`, `README.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado** (método); resultados pendentes.
- **Validação:** 203 testes a passar; `pdflatex` + `bibtex` 13 páginas, 0 erros.
- **Limitações:** as anotações do `validation` são usadas uma segunda vez para medir, a partir das previsões já guardadas, sem reabrir os dados nem voltar a correr a CNN (esclarecido com o utilizador; protocolo curto e confirmação no chat em vez de autorização formal); o exemplo da figura é sintético.
- **Pendentes:** protocolo curto (depois do «sim» do utilizador), aplicação única e resultados.

### REV-057 — Pós-processamento executado: resultados no validation

- **Data:** 2026-11-25 19:50 WET.
- **Cor:** Dourado-escuro `#B8860B`, RGB (184, 134, 11).
- **O quê:** protocolo `posproc_validation_v1` commitado antes; programa de execução única, testes, verificação independente, macros e figuras; execução única; Subsecções 10.4 e 10.5 da proposta, frase final da 10.3 e limitação «Fragmentação» da Secção 9. Resultados: exatidão 94,4 % → 94,5 %; segmentos de pesca previstos 486 → 255 (reais 18), de navegação 502 → 272 (reais 35); F1 de segmentos de pesca 0,028 → 0,066 e de navegação 0,119 → 0,221; 784 pontos mudam (514 corrigidos, 270 estragados).
- **Porquê:** decisão do utilizador de medir o pós-processamento sobre as previsões já guardadas da medição final.
- **Ficheiros afetados:** `configs/postproc_protocol.json`, `src/ais/cli/postproc_validation.py`, `src/ais/cli/build_postproc_results.py`, `src/ais/cli/verify_postproc_independent.py`, `src/ais/phase1/postprocessing.py`, `tests/test_postproc_validation.py`, `tests/test_postprocessing.py`, `latex/proposta_pt.tex`, `latex/generated/resultados_posproc.tex`, `latex/figures/posproc_resultados.png`, `latex/figures/posproc_viagem.png`, `docs/00`, `docs/04`, `PROGRESS.md`, `README.md`, `handoff.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **atualizado**; 14 páginas, 0 erros.
- **Validação:** 224 testes; verificação independente 19/19; execução registada (`postproc_start`, `postproc_done`) em `results/access_log.jsonl`.
- **Limitações:** segunda utilização das anotações do `validation`; só a referência (RQ3 sem resposta); uma semente, 18 viagens, sem intervalo de incerteza. A segunda implementação foi escrita por um modelo externo a partir da descrição; confere com a do projeto, mas partilha as mesmas convenções descritas.
- **Pendentes:** nenhum do Marco 5.

### REV-058 — Análise dos buracos no test para escolher uma nova janela do pós-processamento

- **Data:** 2026-11-25 20:00 WET.
- **Cor:** Azul-acinzentado `#546E7A`, RGB (84, 110, 122). Só marcador do registo; o `.tex` não foi alterado.
- **O quê:** funções e programa de análise do comprimento dos blocos de erro ("buracos") nas previsões da referência no `test` e no treino; cobertura de cada janela candidata (13 a 401 pontos).
- **Porquê:** o utilizador considerou insuficiente a janela de 13 (REV-057) e quer escolher outra no `test` antes de uma nova aplicação única ao `validation`. **Registo de integridade:** a aplicação de REV-057 ao `validation` existiu e a nova escolha é posterior a esse resultado; por decisão do utilizador isto não entra na proposta.
- **Ficheiros afetados:** `src/ais/phase1/postprocessing.py`, `src/ais/cli/analyze_error_runs.py`, `tests/test_postprocessing.py`, `configs/authorizations/test_postproc_window.json`, `PROGRESS.md`, `REVISION_LOG.md`.
- **Correspondência no LaTeX:** **não aplicável** (por agora).
- **Validação:** 227 testes; leituras do `test` registadas.
- **Pendentes:** protocolo v2 (301 pontos, escolhidos pelo utilizador; efeito no `test` em `results/postproc_window_analysis/test_eval.json`), aplicação única, atualização dos números e figuras da Secção 10.
