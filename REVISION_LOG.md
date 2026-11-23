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
