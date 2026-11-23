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
