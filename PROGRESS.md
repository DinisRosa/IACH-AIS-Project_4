# PROGRESS — Projeto AIS

Estado vivo no topo (estado, decisões, pendências, artefactos); abaixo, o registo cronológico de marcos, validações, problemas, decisões e pendentes (AGENTS.md §5 e §8).
Regra: distinguir **feito**, **validado** e **pendente**. Não declarar testes que não foram executados.

## Estado atual (REV-077, 2026-11-26 00:50 WET; refeito em REV-066)

| Marco | Estado |
|---|---|
| 1 Ambiente, divisão por ID, isolamento | Fechado |
| 2 Preparação auditável (só treino/sintéticos) | Fechado (REV-019) |
| 3 CNN 1D baseline sobre a viagem completa | Fechado por decisão do utilizador (REV-041) |
| 4 Janelamento com a mesma CNN (L = 64; 0 % e 50 %) | Feito (REV-046, REV-047) |
| 5 Pós-processamento | Feito (REV-056 a REV-059): filtro gaussiano de 301 pontos |
| 6 e 7 Congelar e medição final no `validation` | Feito (REV-053), só a baseline |
| Relatório do trabalho feito | **Completo (REV-065); falta a leitura do utilizador** |

- **Baseline:** treinada só com o treino oficial (87 viagens, 300 épocas); época 162 e limiar 0,65, escolhidos no `test` e congelados em `results/baseline_frozen/`. Exatidão por ponto: 94,7 % no `test` (otimista) e 94,4 % no `validation`.
- **J0 e J50:** a mesma CNN em janelas de 64 pontos, sem sobreposição e com 50 %; épocas 8 e 4, limiares 0,60 e 0,75. No `test`, 93,4 % e 93,7 %; J50 fragmenta menos. Não medidas no `validation`.
- **Filtro (301 pontos, só a baseline, `validation`):** exatidão 94,4 % → 94,8 %; segmentos de pesca previstos 486 → 32 (reais 18), de navegação 502 → 49 (reais 35); F1 de segmentos de pesca 0,028 → 0,600; melhoram 11 viagens e pioram 7. **Não é uma medição independente** (houve antes uma versão de 13 pontos, `docs/00` §5.3).
- **Perguntas:** RQ1, as janelas não superam a viagem completa; RQ2, o filtro reduz muito a fragmentação, com a ressalva acima; RQ3, sem resposta.
- **Fonte dos números:** macros em `latex/generated/` e ficheiros em `results/` (não versionados).
- **Conjuntos reservados (`results/access_log.jsonl`):** `test` com 2 aberturas de seleção, 2 leituras de diagnóstico e, sobre previsões guardadas, 3 análises de blocos de erro, 1 avaliação de janelas e 1 geração de figuras do relatório, 1 galeria de viagens (REV-073, gerada de novo em REV-072) e 1 geração de figuras com «baseline» (REV-072). `validation` aberto 1 vez (medição final, **gasto**); as anotações foram depois reutilizadas nas 2 versões do filtro e, em REV-073, lidas com as previsões guardadas para a galeria (2 vezes) e para a Figura 7 (REV-074). Os três conjuntos foram lidos por inteiro só para construir as bases limpas (REV-015).
- **LaTeX:** único documento `latex/relatorio_pt.tex` (completo, 10 páginas, números de linha ligados; todo o texto a preto desde a REV-072; em REV-068 saiu do resumo a ressalva sobre a medição do filtro), compilado para `latex/build/`. A proposta em LaTeX foi retirada (REV-066): etiqueta `proposta-pt-v1` e `latex/proposta_pt.pdf`.
- **Testes:** 256 (sintéticos, mais um que lê 3 viagens de treino), a passar.
- **Ambiente:** `iach-ais-venv-4/` (venv + pip, Python 3.14.4, CPU); pacote `ais` em modo editável; `requirements.txt`.
- **Dados:** `data/123_fishing_trajs.csv` (123 viagens, 1 026 279 linhas); bases limpas com 713 854, 209 016 e 103 409 linhas; manifesto versionado `manifests/split_manifest_seed42.csv`.
- **Git:** remoto `origin`, branch `main`; confirmar com `git status -sb`. Push só a pedido do utilizador (REV-055).
- **Registo de revisões:** REV-001 a REV-077.
- **Documentação:** `docs/00` e `docs/01` (confirmado pelo utilizador); os concluídos estão na etiqueta `docs-historico-v1` (REV-067).

## Decisões do utilizador (vigentes)

- **Divisão (REV-001, REV-002):** seed 42; 70/15/15 por viagem. Fuso de `t` ignorado. Viagens do mesmo navio podem estar em conjuntos diferentes; a questão dos navios partilhados foi desconsiderada (sem quantificar nem refazer). O relatório diz que não se afirma generalização a navios inéditos.
- **Dados (REV-011, REV-012, REV-019, REV-022):** sem limpeza por IQR; anomalias mantidas; `bearing` pela grelha UTM; `distanceToShore` aceite; quatro características (`speed`, `signed_turn`, `time_gap`, `distanceToShore`); ausentes a zero depois de normalizar, com máscara.
- **Papéis dos conjuntos (REV-036):** `test` seleciona; `validation` mede no fim, uma só vez.
- **Modelos (REV-041, REV-046):** baseline fechada; J0 e J50 com os mesmos valores, lote de 32. Fora do projeto: 25 % e 75 % de sobreposição, outros comprimentos, treinar com J0 e prever com J50.
- **Âmbito (REV-006, REV-042):** HMM e Wu et al. não são comparações. Explicabilidade, calibração e *dashboard* «previstos, não concluídos nesta fase».
- **Relatório (REV-065, D1 a D8):** documento novo em vez da proposta; máximo 15 páginas, alvo 13 ou menos; texto a preto nessa revisão (as seguintes com cor); **declarar a versão de 13 pontos** (revê a decisão anterior de a omitir); figuras com «referência» (substituído em REV-072 por «baseline»); título mantido; «Figura» e «Tabela» em português; números de linha até à versão final. Perguntas, objetivos e critérios de sucesso não mudam depois dos resultados.
- **Documentação (REV-067):** ficam `docs/00` e `docs/01`; `docs/05` e `06` não se repõem.
- **Proposta antiga (REV-066):** retirar o `.tex`; manter o PDF e a etiqueta; compilar o relatório para `latex/build/`.
- **Resumo do relatório (REV-068):** sem a frase «este resultado não vem de uma medição independente»; a ressalva mantém-se no corpo (protocolo, resultados, limitações e conclusões). Não a repor no resumo.
- **Filtro no relatório (REV-069):** contar que se testou primeiro 13 pontos (ganho pequeno) e depois 301; estudar mais dimensões e tipos de janela fica para trabalho futuro.
- **Galeria (REV-073):** `viagens/`, com «baseline»; filtro só na baseline; J0 e J50 só no teste.
- **Nome do modelo (REV-072):** o modelo da viagem completa chama-se **baseline** no relatório, na galeria e nos documentos atuais. O utilizador mandou fazer a revisão a preto e passar todo o texto do relatório a preto.
- **Documentos fixos:** `latex/proposta_IAHC_DINIS_ROSA.pdf` não se altera. Autor do dataset: Song Wu, Zenodo 10.5281/zenodo.7283281 (CC BY 4.0); o Kaggle é espelho.

## Pendências abertas

- **Leitura do relatório pelo utilizador.** Ajustes entram numa revisão nova (REV-078), com cor, salvo instrução.
- **Por decidir:** traduzir «Abstract» e «References»; versão final sem números de linha (quando pedida).
- **Verificação bibliográfica (`docs/00` §9):** Shneiderman, Guo e Lundberg só pelos resumos no arXiv; a tese de Ghazizadeh não tem texto extraível (não é citada).
- **Limitação registada:** o critério da menor perda no `test` escolheu épocas muito cedo (4 e 8); mudá-lo seria uma decisão metodológica nova.
- **Dúvidas de dados:** CRS de longitude e latitude (hipótese WGS84); 128 trajetórias no artigo e 123 no ficheiro; fiabilidade das anotações; cálculo de `distanceToShore`.
- **Arrumação técnica (opcional):** testes dos programas de treino, de figuras e de resultados; unificar `class_metrics`; figuras sem uso em `latex/figures/` (`diag3_*`, `final_*`, `posproc_viagens` e as `janelas_*` antigas (incluindo as `*_ref`)), que o utilizador optou por manter; execuções antigas em `results/`.

## Artefactos do projeto

| Ficheiro | Estado |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Alinhados em REV-067 |
| `README.md`, `handoff.md` | Alinhados em REV-077 |
| `viagens/` | Galeria gerada por código (REV-073) e a sua versão `galeria_viagens.tex`/`.pdf` (REV-077); não editar à mão |
| `docs/00`, `docs/01` | Vigentes; `docs/00` §9 com a verificação bibliográfica |
| `docs/02` a `docs/06` | Retirados (REV-067); na etiqueta `docs-historico-v1` |
| `src/ais/`, `pyproject.toml`, `tests/` | Código e 256 testes |
| `configs/`, `configs/authorizations/` | Configurações, protocolos e autorizações |
| `latex/relatorio_pt.tex`, `references.bib`, `figures/`, `generated/` | Relatório e artefactos gerados por código |
| `latex/proposta_pt.pdf` | Proposta anterior, só para consulta |
| `latex/proposta_IAHC_DINIS_ROSA.pdf` | Entregue ao professor; não se altera |
| `latex/build/`, `latex/watch_latex.sh`, `docs/bibliografia/` | Locais, não versionados |
| `data/`, `results/` | Locais, não versionados |

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
- Partes do relatório não revistas: ver REV-041 (resumo, secções 1 a 3, 6 e 7). Citam HMM e Wu et al. e quatro taxas de sobreposição, contra o âmbito atual.

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
- Restantes passagens de REV-041 (quatro taxas de sobreposição e ablação, explicabilidade e dashboard, «human-on-the-loop», Secção 6 no futuro); commit local por autorizar; decisões do Marco 4.

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
- Decisão do utilizador: manter o critério de seleção ou mudar (novo protocolo e autorização); Marco 5 (só com decisão); Marcos 6 e 7 (autorização). Passagens adiadas do LaTeX (explicabilidade, calibração e *dashboard*, «human-on-the-loop»). Push dos commits locais, por autorização do utilizador.

### 2026-11-23bd — Gráfico de diagnóstico da viagem 219001624-2 (REV-049), 2026-11-23 23:40 WET

**Feito**
- `plot_trip_diagnostic.py` e o gráfico da viagem `219001624-2` (classe real e prevista pela referência, J0 e J50, mais probabilidades), só com as previsões já geradas.

**Validado**
- Gráfico inspecionado; exatidões calculadas pelo programa (83,7 %, 42,0 % e 80,4 %); `pytest`: 181 passaram.

**Problemas e limitações**
- Em J0 a probabilidade na fase de pesca fica abaixo do limiar escolhido (0,60), por isso quase tudo sai como navegação; a forma da curva é igual à da referência. Uma só viagem. O programa não tem teste automático.

**Pendente**
- O gráfico de `x` por `y` precisa de autorização explícita do utilizador (leitura do ficheiro do `test`, fora do âmbito da autorização das janelas).

### 2026-11-23be — Leitura de diagnóstico da viagem 219001624-2: incidente (REV-050), 2026-11-23 23:43 WET

**Feito**
- Autorização `test_diagnostic_trip_219001624-2.json` (uma leitura de `id`, `point_id`, `t`, `x`, `y`), `load_reserved_diagnostic` em `reserved.py` e `--xy` no `plot_trip_diagnostic`. A leitura foi feita e registada.

**Validado**
- 6 testes novos; `pytest`: 187 passaram. Desenho testado com coordenadas falsas.

**Problemas e limitações**
- O desenho falhou depois da leitura (erro meu) e os dados não estavam guardados: a leitura única ficou gasta sem gráfico. Corrigido (os dados lidos passam a guardar-se antes de desenhar). A autorização não foi alargada por mim.

**Pendente**
- O gráfico de `x` por `y` precisa de **nova autorização** do utilizador para uma leitura.

### 2026-11-23bf — Gráfico de x por y da viagem 219001624-2 (REV-051), 2026-11-23 23:46 WET

**Feito**
- Nova autorização (uma leitura, mesmo âmbito) e leitura única de `id`, `point_id`, `t`, `x`, `y` da viagem; `--auth` no `plot_trip_diagnostic`; gráfico de `x` por `y` com a classe real e a prevista pela referência, J0 e J50.

**Validado**
- `pytest`: 187 passaram; gráfico inspecionado. Os dados lidos ficaram guardados antes do desenho.

**Problemas e limitações**
- Uma só viagem. Duas leituras de diagnóstico no `access_log` (a primeira foi gasta por um erro de desenho).

**Pendente**
- Nenhum deste pedido. Pendências gerais no topo.

### 2026-11-23bg — Refactoring de leitura da proposta (REV-052), 2026-11-23 23:57 WET

**Feito**
- Secção 8 reordenada (resumo e tabela primeiro; 8.1 a 8.3 curtas; 8.4 com comparação, RQ1 e limitações em lista); 5 figuras e 3 tabelas em vez de 9 e 6; 4.3, 4.4 e Secção 5 condensadas; Anexo A com os pormenores do janelamento e a tabela por classe; `placeins`.
- `build_window_results` passou a gerar as figuras fundidas e as macros da referência; retiradas as figuras por variante.

**Validado**
- `pdflatex` + `bibtex`: 9 páginas (antes 11), 0 erros, 0 referências indefinidas, sem caixas largas; páginas inspecionadas. `pytest`: 187 passaram.

**Problemas e limitações**
- Um `%` nu num marcador de título comentou o resto da linha e partiu a compilação; corrigido (usar «por cento» nos marcadores). O texto reescrito não foi lido pelo utilizador. A cor de REV-052 cobre agora grande parte do texto.

**Pendente**
- Leitura do utilizador; passagens adiadas de REV-041; push dos commits locais.

### 2026-11-24a — Medição final no `validation` e Secção 9 (REV-053), 2026-11-24 00:37 WET

**Feito**
- A pedido do utilizador: protocolo e autorização escritos antes de abrir; **escolha do modelo** pelo critério declarado (maior F1 médio por ponto no `test`): **a referência** (época 162, limiar 0,65); **uma só abertura do `validation`** (00:32:09 UTC) e medição só desse modelo; macros, figuras e **Secção 9** da proposta; frases do LaTeX sobre o `validation` atualizadas.
- Resultado: exatidão por ponto de 94,4 % (11 662 erros em 209 016 pontos; regra da classe maioritária 83,2 %), contra 94,7 % no `test`; precisão da navegação 0,760 (0,900 no `test`); exatidão por viagem de 40,4 % a 99,7 %; segmentação muito fragmentada (pesca: 18 reais, 486 previstos).

**Validado**
- 192 testes sintéticos a passar; medição testada de ponta a ponta com dados sintéticos antes de abrir; proveniência verificada (uma abertura, escolha gravada antes, hashes). `pdflatex` + `bibtex`: 11 páginas, 0 erros, 0 referências indefinidas.

**Problemas e limitações**
- Uma só medição em 18 viagens, sem incerteza; J0 e J50 não medidas no `validation`; **o `validation` está gasto** e já não pode avaliar um pós-processamento.

**Pendente**
- Decisão do utilizador sobre o pós-processamento (só avaliável no `test`); passagens adiadas do LaTeX; push dos commits locais.

### 2026-11-24b — Handoff reescrito (REV-054), 2026-11-24 00:42 WET

**Feito**
- `handoff.md` reescrito de raiz para outra sessão, com um resumo cronológico do que se fez, o estado atual (Marco 4 e medição final executados), as decisões, os ficheiros, o que falhou e o que falta.

**Validado**
- `pytest`: 192 passaram; `pdflatex` + `bibtex`: 11 páginas, 0 erros, 0 referências indefinidas (00:41 WET). Horas e commits lidos do `date` e do `git log`.

**Problemas e limitações**
- O `AGENTS.md` §6 («o agente nunca faz push») continua em conflito com o push que o utilizador autorizou; registado no handoff, sem alterar a regra.

**Pendente**
- Decisão do utilizador sobre o Marco 5 (só avaliável no `test`); passagens adiadas do LaTeX; push de `d6111f6` e deste commit, a pedido do utilizador.

### 2026-11-24c — Regra do push atualizada (REV-055), 2026-11-24 00:46 WET

**Feito**
- A pedido do utilizador, o `AGENTS.md` §6, o `CLAUDE.md` e o handoff passam a dizer: se o utilizador pede push (no chat ou no handoff), o agente envia como se fosse ele, sem pedir confirmação nem repetir a autorização; por iniciativa própria, ou a trabalhar sozinho sem pedido explícito, nunca; sem `--force` (que exige pedido próprio); subagentes nunca fazem push.
- Estado do git nos documentos deixa de nomear commits «por enviar» (ficava sempre desatualizado depois do push).

**Validado**
- Releitura dos documentos à procura de contradições sobre o push (`AGENTS.md`, `CLAUDE.md`, `handoff.md`, `PROGRESS.md`). Código e LaTeX não foram alterados.

**Pendente**
- Os de sempre (Marco 5, passagens adiadas do LaTeX, arrumação técnica).

### 2026-11-25a — Pendências do LaTeX e plano do Marco 5 (REV-056), 2026-11-25 19:13 WET

**Feito**
- Retiradas todas as menções ao «OOI» (o utilizador tirou-o do título; sem REV próprio, por decisão dele) e corrigidas linhas desatualizadas do estado (contagem de testes, pendência do `validation`).
- Decisões do Marco 5 registadas em `docs/04_pos_processamento.md` (plano de ação): janela gaussiana de 13 pontos (campo recetivo), σ = 13/6, só a referência, aplicada uma vez às previsões já guardadas do `validation` (segunda utilização, decidida pelo utilizador).
- `src/ais/phase1/postprocessing.py` (filtro), `tests/test_postprocessing.py` (11 testes sintéticos), `src/ais/cli/plot_postprocessing_kernel.py` e `latex/figures/posproc_janela.png` (pesos e exemplo sintético).
- Proposta: nova **Secção 10** (pós-processamento: filtro, tamanho e forma, objetivo e medição, figura) e frase da 4.5 atualizada, em `rev056` `#D84315`.

**Validado**
- `pytest tests/`: 203 passaram. `pdflatex` + `bibtex` em `latex/build/check`: 13 páginas (limite de 15), 0 erros; páginas 10 e 11 inspecionadas.

**Problemas e limitações**
- Nenhum dado reservado aberto. A reutilização do `validation` é uma exceção à regra de REV-053, decidida pelo utilizador.

**Pendente**
- Protocolo curto e «sim» do utilizador; aplicação do filtro; resultados na Secção 10.
- Esclarecido com o utilizador: não se reabrem os dados do `validation` nem se volta a correr a CNN; usam-se as probabilidades e as anotações já guardadas, e só as anotações contam como reutilização (para medir). Secção 10.3 e `docs/04` §1.1 atualizadas.

### 2026-11-25b — Pós-processamento executado e resultados (REV-057), 2026-11-25 19:50 WET

**Feito**
- Protocolo `configs/postproc_protocol.json` commitado antes de medir (`3359890`).
- `ais.cli.postproc_validation` (execução única sobre as previsões guardadas, sem reabrir os dados nem correr a CNN), `build_postproc_results` (macros e figuras) e `verify_postproc_independent` (segunda implementação, escrita pela Abacus só a partir da descrição).
- Execução única em 2026-11-25: exatidão 94,4 % → 94,5 %; segmentos de pesca previstos 486 → 255 (reais 18), de navegação 502 → 272 (reais 35); F1 de segmentos de pesca 0,028 → 0,066 e de navegação 0,119 → 0,221; 784 pontos mudam (514 corrigidos, 270 estragados).
- Proposta: Subsecções 10.4 (Resultados) e 10.5 (Limitações), tabela e figura novas, frase final da 10.3 e limitação «Fragmentação» da Secção 9, em `rev057` `#B8860B`.

**Validado**
- `pytest tests/`: 224 passaram. Verificação independente: 19/19 números iguais. `pdflatex` + `bibtex`: 14 páginas (limite de 15), 0 erros, páginas inspecionadas.

**Problemas e limitações**
- Subagente (testes) e Abacus (revisão) encontraram um erro antes da execução: `np.convolve(mode="same")` devolvia 13 valores em viagens mais curtas que a janela; corrigido. Outras proteções acrescentadas a partir da revisão (nada é registado antes de tudo estar calculado; bloqueio para qualquer id; limiar e origem fixados).
- O script `delegate.sh` da skill não existe na pasta do plugin; usou-se `abacusai -p` diretamente, a partir do scratchpad, só com código e descrições (nenhum dado enviado).
- Segunda utilização das anotações do `validation` (decisão do utilizador). RQ3 sem resposta.

**Pendente**
- Passagens adiadas do LaTeX; arrumação técnica; push só a pedido.

### 2026-11-25c — Análise dos buracos no `test` para uma nova janela (REV-058), 2026-11-25 20:00 WET

**Contexto (registo interno; não vai para a proposta)**
- O utilizador considerou insuficiente a janela de 13 pontos (REV-057) e decidiu refazer o pós-processamento com outra janela, tratando a primeira aplicação como se não tivesse existido **no relatório**. Fica registado aqui e no `REVISION_LOG.md` que a primeira aplicação ao `validation` (13 pontos) **aconteceu** (`results/postproc_validation/`, eventos `postproc_start`/`postproc_done`) e que a nova janela é escolhida depois de ver esse resultado. A nova escolha faz-se no `test` (conjunto de seleção), com autorização própria (`configs/authorizations/test_postproc_window.json`), sobre as previsões já guardadas da referência.

**Feito**
- `error_runs`, `summarize_runs`, `max_removable_island` em `postprocessing.py` (testes sintéticos) e `ais.cli.analyze_error_runs --split test|train` (recusa o `validation`). Resultados em `results/postproc_window_analysis/`.
- `test`: 373 buracos (5 502 pontos de erro); média 14,8 pontos, mediana 5, p90 37, p95 55, máximo 286. 79 % dos pontos de erro são navegação prevista no meio de pesca (média 17,2, p90 47). Segmentos reais: pesca ≥ 633 pontos, navegação ≥ 127 (treino: ≥ 584 e ≥ 102).
- Com o limiar 0,65 e σ = tamanho/6, a janela de 13 só remove navegação isolada de 1 ponto (pesca até 4): explica o pouco efeito de REV-057.

**Validado**
- `pytest tests/`: 227 passaram. Leituras do `test` registadas no `access_log.jsonl` (`postproc_window_analysis`).

**Pendente**
- Decisão do utilizador sobre a nova janela; depois, protocolo v2 e aplicação única ao `validation`; atualizar figuras e valores da Secção 10 mantendo o texto.

### 2026-11-25d — Janela de 301 pontos aplicada às previsões do `test` (REV-058), 2026-11-25 20:07 WET

**Feito**
- O utilizador escolheu 301 pontos. Autorização `configs/authorizations/test_postproc_eval.json`; programa `ais.cli.eval_postproc_test` (13, 201, 301 e 401; 301 é a escolha). Resultados em `results/postproc_window_analysis/test_eval.json` e `test_eval_resumo.csv`.
- `test`, referência antes → 301: exatidão 94,7 % → 95,7 % (5 502 → 4 422 erros); segmentos de pesca previstos 358 → 32 (reais 18), F1 de segmentos 0,032 → 0,600; navegação 376 → 50 (reais 36), F1 0,151 → 0,814. Fronteiras: erro mediano do fim da pesca 100 s → 154 s. Melhoram 9 viagens e pioram 8; `219001624-2` cai de 83,7 % para 48,4 % e `220006000-2` de 74,0 % para 66,2 %.

**Validado**
- `pytest tests/`: 229 passaram. Leitura do `test` registada (`postproc_test_eval`).

**Pendente**
- «Sim» do utilizador para o protocolo v2 (301 pontos) e a aplicação única ao `validation`; depois, números e figuras da Secção 10 (texto mantido).

### 2026-11-25e — Pós-processamento v2 (301 pontos) no `validation` e Secção 10 (REV-059), 2026-11-25 20:33 WET

**Feito**
- Protocolo `configs/postproc_protocol_v2.json` e programa (uma execução por versão; a v1 continua bloqueada; escrita atómica; hash da fonte fixado; código commitado obrigatório) commitados antes de medir.
- Trabalho delegado: a Abacus gerou o programa, os testes e a verificação independente com `--size`, e reviu o código (G1 a G3 corrigidos); um subagente Sonnet diagnosticou o teste que falhava (erro do teste).
- Execução única da v2: exatidão 94,4 % → 94,8 % (11 662 → 10 790 erros); segmentos de pesca previstos 486 → 32 (reais 18), de navegação 502 → 49 (reais 35); F1 de segmentos de pesca 0,028 → 0,600 e de navegação 0,119 → 0,786; 4 100 pontos mudam (2 486 corrigidos, 1 614 estragados); melhoram 11 viagens e pioram 7, a pior `219020187-4` de 40,4 % para 19,7 %. Verificação independente 19/19.
- Proposta: tamanho, σ, justificação do 301, fórmula, legendas, resultados (10.4) e limitações (10.5) em `rev059` `#8B008B`; figuras e macros regeneradas. A v1 não é mencionada na proposta (decisão do utilizador); está em `docs/04` §5.

**Validado**
- `pytest tests/`: 243 passaram. `pdflatex`: 14 páginas (limite de 15), 0 erros; páginas 10 e 11 inspecionadas.

**Problemas e limitações**
- Anotações do `validation` usadas pela terceira vez (medição final, v1, v2); a decisão de procurar outra janela foi tomada depois de ver a v1.
- A viagem `219020187-4` piora de 40,4 % para 19,7 %; as fronteiras deslocam-se.

**Pendente**
- Passagens adiadas do LaTeX; arrumação técnica; push só a pedido.

### 2026-11-25f — Secção de conclusões na proposta (REV-060), 2026-11-25 20:39 WET

**Feito**
- Nova Secção 11 «Conclusões» em `rev060` `#C71585`, antes do anexo: respostas à RQ1 (janelamento não supera a referência; J50 fragmenta menos; resposta só no teste) e à RQ2 (o filtro reduz muito a fragmentação, a exatidão sobe pouco); a RQ3 fica sem resposta, com as razões (só a referência foi filtrada; não há conjunto limpo; modelos pouco comparáveis; efeitos sobrepostos) e o desenho fatorial que seria preciso; critérios de sucesso (i) a (iii); trabalho futuro. Todos os números por macros geradas.

**Validado**
- `pdflatex`: 15 páginas (o limite), 0 erros; página 13 inspecionada.

**Pendente**
- A proposta está no limite de 15 páginas: novos acrescentos exigem cortar noutro sítio. Passagens adiadas do LaTeX; handoff; arrumação técnica; push só a pedido.

### 2026-11-25g — Handoff reescrito e push (REV-061), 2026-11-25 20:47 WET

**Feito**
- `handoff.md` reescrito de raiz: validação, cronologia dos commits, o que se fez na sessão (pós-processamento v1 e v2, análise no `test`, conclusões), estado, decisões, ficheiros, comandos (incluindo a delegação na Abacus), falhas, próximos passos, regras e preferências. Registado que a v1 fica fora da proposta, mas nos registos internos.
- `docs/00`: a linha do Marco 6 deixa de dizer que o pós-processamento não existe.

**Validado**
- `pytest tests/`: 243 passaram; `pdflatex` + `bibtex`: 15 páginas, 0 erros, 0 referências indefinidas (20:46 WET).

**Pendente**
- Passagens adiadas do LaTeX; número de páginas (depois); arrumação técnica.

### 2026-11-25h — Passagens adiadas da proposta (REV-062), 2026-11-25 21:14 WET

**Feito**
- Pontos 1 a 11 do plano aprovado (resumo, objetivos 3 e 5, figura da abordagem a tracejado, contribuições, 4.6, 7.1 sem ablação, 7.3, trabalho futuro), em `rev062` `#4682B4`. Lidos os PDFs de `docs/bibliografia/`: o artigo de base (Wu et al., 2022) não refere Kaggle nem Zenodo; mantém-se «(Kaggle)». `docs/bibliografia/` no `.gitignore`.

**Validado**
- `pdflatex`: 16 páginas, 0 erros.

**Pendente**
- Decisão do utilizador sobre a lista da releitura (velocidade em nós, Wu et al. e MDL, figura da abordagem, 7.1, 7.2, Contexto, resumo).

### 2026-11-25i — Tabela da releitura da proposta (REV-063), 2026-11-25 21:23 WET

**Feito**
- `docs/05_releitura_proposta.md`: tabela A a H das passagens ainda por corrigir, com a recomendação para cada uma (ponto G ajustado pelo utilizador). Handoff, README e registo atualizados.

**Validado**
- `pytest tests/`: 243 passaram; `pdflatex` + `bibtex`: 16 páginas, 0 erros, 0 referências indefinidas (21:22 WET).

**Problemas**
- Detetado na releitura: a Secção 10.2 (REV-059) tem números dos blocos de erro escritos à mão, contra o AGENTS §10; a corrigir com macros geradas junto com o ponto G.

**Pendente**
- Aplicar A a H (REV-064) quando o utilizador o pedir; número de páginas depois; arrumação técnica.

### 2026-11-25j — Plano de reescrita da proposta (REV-064), 2026-11-25 21:59 WET

**Feito**
- Leitura de preparação (handoff, regras, registos, `docs/00` a `05`, `.tex`, macros, PDF; dos artigos só as primeiras páginas, e a tese de Ghazizadeh sem texto extraível).
- O utilizador aprovou reescrever a proposta como relatório do trabalho feito, com a estrutura base. Escrito `docs/06_plano_reescrita.md`; `docs/05` e `README.md` alinhados; no «Estado atual» corrigidas linhas desatualizadas (exatidões de J0 e J50, LaTeX, git, intervalo de REV).

**Validado**
- Antes das alterações (21:26 WET): `pytest tests/`, 243 passaram; LaTeX compilado para uma pasta temporária, 16 páginas, sem erros nem referências indefinidas. Depois só mudaram ficheiros Markdown.

**Problemas**
- Na releitura: contradições novas na proposta (9.2 diz que o pós-processamento não foi estudado; erros de fronteira prometidos na 10.3 e não apresentados; «única diferença» do janelamento) e a 10.3 sugere uma medição independente do filtro. Todas em `docs/06` §5.

**Pendente**
- Decisões D1 a D6; reescrita (REV-065); commit destes documentos; arrumação técnica.

### 2026-11-25k — Plano revisto: ficheiro novo e versão de segurança (REV-064), 2026-11-25 22:25 WET

**Feito**
- O utilizador propôs escrever num ficheiro novo (ou reescrever o atual com indicação no `README.md` de como recuperar a versão anterior) e quer decidir antes de se avançar. `docs/06` ganha D7, D8, a §2.1 (versão de segurança) e uma fase própria. Nenhum `.tex`, etiqueta ou commit criado.

**Validado**
- `latex/` igual ao do commit `7d60861`, que está em `origin/main`; o `.tex` de `1ab2376` é anterior a REV-062. Comando de recuperação ensaiado num clone temporário.

**Pendente**
- Decisões D1 a D8; commit dos documentos; reescrita (REV-065).

### 2026-11-25l — Relatório novo: método, protocolo e resultados (REV-065), 2026-11-25 22:44 WET

**Feito**
- O utilizador aceitou D1 a D8. Commit do plano; etiqueta local `proposta-pt-v1` (commit `7d60861`) e instruções no `README.md`; `AGENTS.md` §8 ajustado.
- `latex/relatorio_pt.tex`: secções 4, 5 e 6, anexo e limitações; as contradições I a N, Q e R do plano tratadas nestas secções; frase sobre a versão de 13 pontos (D3).
- `build_window_analysis_macros` (macros dos blocos de erro) e `build_window_results --report-figures-only` (duas figuras com «referência», nomes novos), com a autorização `test_report_figures` e registo do acesso às previsões guardadas do `test`.
- Verificação bibliográfica (`docs/06` §8).
- `latex/watch_latex.sh` (não versionado) aponta para o relatório.

**Validado**
- 247 testes a passar; relatório compilado (7 páginas, sem erros nem referências indefinidas) e páginas inspecionadas; nenhum ficheiro antigo de `latex/` alterado face à etiqueta; recuperação pela etiqueta ensaiada num clone temporário; procura de números escritos à mão no corpo: só nomes e valores de configuração.

**Problemas**
- «Até cerca de 20 % da captura mundial» não está no artigo de Agnew; o artigo de Cheng classifica tipos de navio. O artigo de Wu descreve a anotação dos dados com 128 trajetórias e 1 080 220 pontos, mais do que o ficheiro público. Shneiderman, Guo e Lundberg não verificados.
- Afirmação corrigida no relatório: nem toda a leitura dos conjuntos reservados está no registo de acessos (a preparação das bases, REV-015, é anterior).

**Pendente**
- Revisão do utilizador; resto do relatório; commits por enviar (push e etiqueta só a pedido).

### 2026-11-25m — Relatório completo em rascunho; revisão independente pedida (REV-065), 2026-11-25 22:55 WET

**Feito**
- Escritas as secções 3, 2, 7 (ética e dimensão humana), 1, 8 e o resumo, e a bibliografia. Resumos de Shneiderman, Guo e Lundberg confirmados nas páginas do arXiv.
- `docs/00`, `docs/03` e `docs/05` alinhados (Marco 5 e fecho da releitura).
- Pedida uma revisão só de leitura a um subagente (Opus), sem acesso a `data/` nem `results/`.

**Validado**
- 10 páginas, sem erros nem citações por resolver; 247 testes; ficheiros antigos de `latex/` iguais aos da etiqueta.

**Pendente**
- Achados da revisão, PDF final e registos finais.

### 2026-11-25n — Achados da revisão independente aplicados e fecho (REV-065), 2026-11-25 23:00 WET

**Feito**
- Revisão só de leitura por um subagente (Opus): sem erros graves; 4 achados médios e vários menores. Confirmados nos registos e nos artigos antes de corrigir.
- Corrigido no relatório: a janela de 301 foi escolhida sem regra declarada antes e o efeito no `test` só se mediu depois (o relatório dizia «comparando várias dimensões»); o critério da medição final foi declarado já com os resultados do teste conhecidos; a diferença de fragmentação entre J0 e J50 não se atribui só à sobreposição; o resumo indica a regra maioritária e as viagens que pioram; três usos das anotações da validação; precisão por segmento; AIS; 128 viagens; entrada de Ferreira com os quatro autores (entrada nova no `.bib`).

**Validado**
- 247 testes (23:00 WET); relatório com 10 páginas, sem erros nem citações por resolver; páginas 1 e 9 revistas depois das correções; face à etiqueta, em `latex/` só `references.bib` mudou entre os ficheiros antigos (uma entrada acrescentada).

**Problemas e limitações**
- Não aplicado: traduzir «Abstract» e «References» (a decisão D6 só abrangeu «Figura» e «Tabela»). A revisão não abriu `results/`.
- Duas horas escritas à frente do relógio nesta sessão, corrigidas.

**Pendente**
- Leitura do utilizador; push dos commits e da etiqueta, só a pedido; arrumação técnica antiga.

### 2026-11-25o — Envio para o GitHub a pedido do utilizador (REV-065), 2026-11-25 23:03 WET

**Feito**
- O utilizador pediu o envio («Sim, envia»): `main` e etiqueta `proposta-pt-v1`, sem `--force`.

**Validado antes de enviar**
- `main` remoto em `7d60861`, avanço simples; sem etiquetas no remoto; sem ficheiros de dados, resultados ou segredos nos commits.

**Pendente**
- Leitura do utilizador; arrumação técnica antiga.

### 2026-11-25p — Retirada a proposta em LaTeX e documentos preparados para nova conversa (REV-066), 2026-11-25 23:12 WET

**Feito**
- A pedido do utilizador: `latex/proposta_pt.tex` removido; o seu PDF passou de `latex/build/` para `latex/proposta_pt.pdf`; o relatório compila direto para `latex/build/`; apagadas `latex/build/check` e `latex/build/relatorio`.
- `README.md` refeito, topo deste ficheiro refeito, `AGENTS.md`, `CLAUDE.md`, `docs/00`, `01`, `04`, `05`, `06`, `REVISION_LOG.md` e `handoff.md` atualizados.

**Validado**
- Antes de remover, o `.tex` era igual ao da etiqueta `proposta-pt-v1`, presente no GitHub. Relatório compilado em `latex/build` (10 páginas, sem referências em falta); 247 testes. Num clone de ensaio, os dois comandos de recuperação do `README.md` funcionaram e a proposta antiga compilou.

**Problemas**
- O vigilante iniciado antes (ainda com a proposta) falhou ao desaparecer o `.tex` e deixou um `texput.log`, apagado; precisa de ser reiniciado.

**Pendente**
- Leitura do relatório; push dos commits desta revisão, só a pedido.

### 2026-11-25q — Documentos concluídos arquivados (REV-067), 2026-11-25 23:17 WET

**Feito**
- A pedido do utilizador: etiqueta `docs-historico-v1` com `docs/00` a `docs/06`; `docs/00` reescrito como referência única (junta o essencial de `02` a `04` e a verificação bibliográfica de `06`); `docs/02` a `06` retirados. `README.md`, `AGENTS.md`, `handoff.md` e `REVISION_LOG.md` atualizados. Envio para o GitHub pedido pelo utilizador («podem ir para o GitHub»).

**Validado**
- A etiqueta contém os sete documentos. Sem alterações ao código nem ao relatório.

**Problemas**
- Entradas antigas deste ficheiro, protocolos em `configs/` e comentários citam documentos arquivados pelo nome: ficam como registo.

**Pendente**
- Leitura do relatório.

### 2026-11-25r — Confirmação da pasta docs e do estado no GitHub (REV-067), 2026-11-25 23:21 WET

**Feito**
- O utilizador confirmou que a pasta `docs` fica como está (não repor `05` nem `06`) e iniciou o vigilante novo (23:14), que compilou o relatório.
- A pedido, `git push` do `main` e das duas etiquetas: já estava tudo atualizado. Depois, `handoff.md`, `README.md`, este ficheiro e `REVISION_LOG.md` atualizados para novo commit e push, também pedidos.

**Validado (23:21 WET)**
- `main` local e remoto em `7b9005a` antes deste commit; etiquetas presentes; árvore limpa; 247 testes; relatório com 10 páginas.

**Problemas**
- Continua aberto o vigilante antigo (iniciado às 18:54, processo 22891), que procura a proposta retirada; fica para o utilizador parar.

**Pendente**
- Leitura do relatório pelo utilizador.

### 2026-11-25s — Vigilante antigo parado (REV-067), 2026-11-25 23:23 WET

**Feito**
- O utilizador parou o vigilante antigo do LaTeX; `handoff.md` e `REVISION_LOG.md` acertados.

**Validado**
- Só corre o vigilante iniciado às 23:14; `latex/build/` tem apenas o PDF do relatório.

**Pendente**
- Leitura do relatório pelo utilizador.

### 2026-11-25t — Nenhum vigilante a correr (REV-067), 2026-11-25 23:24 WET

**Feito**
- O utilizador parou também o vigilante novo; `handoff.md` e `REVISION_LOG.md` acertados.

**Validado**
- Nenhum processo `watch_latex.sh`; `latex/build/` tem o PDF do relatório.

**Pendente**
- Leitura do relatório pelo utilizador.

### 2026-11-25u — Ressalva retirada do resumo (REV-068), 2026-11-25 23:35 WET

[REV-068 | cor #A0522D]

**Feito**
- A pedido do utilizador, retirado do resumo do relatório «; este resultado não vem de uma medição independente»; PDF recompilado.

**Validado**
- `pdflatex` + `bibtex` + 2 × `pdflatex`: 10 páginas, sem erros nem referências em falta; frase ausente do PDF.
- Testes não repetidos (sem alterações a código).

**Decisões**
- O resumo fica sem a ressalva; o corpo do relatório mantém-na.

**Pendente**
- Leitura do relatório pelo utilizador.

**Envio (23:37 WET)**
- O utilizador pediu o envio da REV-068 para o GitHub.

### 2026-11-25v — Handoff preparado para uma nova conversa (REV-068), 2026-11-25 23:39 WET

**Feito**
- `handoff.md` atualizado: validação, cronologia, próximo passo e o ponto em aberto no resumo.

**Validado (23:39 WET)**
- 247 testes; relatório com 10 páginas, sem erros nem referências em falta; `main` local e remoto em `6249d54`; as duas etiquetas no remoto; nenhum vigilante a correr.

**Pendente**
- Leitura do relatório pelo utilizador e decisão sobre a frase do filtro no resumo.

### 2026-11-25w — Primeira janela do filtro contada no relatório (REV-069), 2026-11-25 23:55 WET

[REV-069 | cor #7B68EE]

**Feito**
- Relatório: resumo, escolha da janela, resultados do filtro e trabalho futuro.
- `build_postproc_results --first-version-only` e `resultados_posproc_v1.tex`; teste sintético novo.

**Validado**
- 248 testes; v1 confere com a verificação independente (19/19); relatório com 10 páginas, sem erros nem referências em falta.
- Lidos só os resumos agregados guardados da v1; nenhuma previsão nem conjunto reservado foi aberto, e nada voltou a ser medido.

**Decisões**
- A nova frase do resumo começa por «Sobre as previsões dessa medição», o que fecha o ponto em aberto sobre os 94,8 % se lerem como medição final.

**Pendente**
- Leitura do relatório pelo utilizador. Commit local; sem push (não pedido).

### 2026-11-25x — Números de linha nas margens (REV-070), 2026-11-25 23:59 WET

[REV-070 | cor #2F4F4F]

**Feito**
- Vigilante do LaTeX compila até o `.aux` estabilizar e aceita `--once`; procedimento manual do `README.md` corrigido.

**Problemas**
- Desde pelo menos a REV-069, o PDF tinha números de linha entre as colunas; a validação só via erros, referências e páginas.

**Validado**
- Compilação do zero: 10 páginas; 647 números de linha, todos nas margens exteriores; páginas revistas em imagem.

**Observação (sem alteração)**
- A página 7 fica com a coluna direita vazia e muito espaço em branco antes do anexo.

**Pendente**
- Reiniciar o vigilante em execução (usa a versão antiga). Leitura do relatório. Envio para o GitHub depois de o utilizador ver o PDF.

### 2026-11-26a — Página 8 preenchida (REV-071), 2026-11-26 00:03 WET

[REV-071 | cor #483D8B]

**Feito**
- A barreira de figuras passou de antes do anexo para antes das referências; o anexo preenche a coluna direita da página 8.

**Validado**
- 10 páginas, sem referências em falta; 647 números de linha nas margens; páginas 8 e 9 revistas em imagem.
- O utilizador reiniciou o vigilante (00:00); a versão nova compilou em 3 passagens.

**Correção**
- A observação da REV-070 sobre a «página 7» referia-se à página 8.

**Pendente**
- Leitura do relatório. Envio para o GitHub, a pedido.

### 2026-11-26b — Envio das REV-069 a REV-071 (REV-071), 2026-11-26 00:04 WET

**Feito**
- O utilizador pediu o envio do `main` para o GitHub, depois de ver o PDF.

**Validado**
- Antes do envio: `main` 4 commits à frente de `origin/main` e nenhum atrás; só código, teste, relatório e documentos.

**Pendente**
- Leitura do relatório.

### 2026-11-26c — Galeria de viagens (REV-073), 2026-11-26 00:22 WET

[REV-073 | cor #006400]

**Feito**
- Autorizações gravadas com as palavras do utilizador; `build_trip_gallery` e testes (commit `abd8cab`, antes de executar).
- Uma execução: `viagens/README.md`, 36 imagens e `proveniencia.json`; ligação no `README.md`.

**Validado**
- 253 testes; 181 valores do teste e 108 da validação iguais aos já gravados; viagens iguais às do manifesto.
- Lidas só previsões guardadas e resultados; sem parquets, sem CNN e sem escolhas. Duas entradas `trip_gallery` no registo de acessos.

**Limitações**
- `viagens/` ocupa 3,5 MB (acima do 1 a 2 MB estimado no plano). Blocos muito curtos aparecem esbatidos nas viagens longas.
- Apresentação no GitHub não verificada (falta enviar).

**Decisões**
- REV-072 («referência» → «baseline» no relatório) fica por aplicar.

**Pendente**
- Envio a pedido; REV-072; leitura do relatório.

### 2026-11-26d — «Baseline» no relatório e texto todo a preto (REV-072), 2026-11-26 00:27 WET

**Feito**
- A pedido, enviadas para o GitHub as REV-073 (galeria).
- Relatório: «referência» trocada por *baseline* no texto, tabelas, esquema e figuras 4, 5 e 6; retirada a cor da REV-069.
- Galeria sem a nota sobre o nome antigo; README, `docs/00`, estado deste ficheiro e `handoff.md` atualizados.

**Validado**
- 253 testes; 10 páginas, sem referências em falta; 647 números de linha nas margens; nenhuma «referênci…» no texto do PDF; páginas revistas em imagem.
- Figuras refeitas só com ficheiros guardados do teste (autorização `test_report_figures_baseline`); na galeria, 181 e 108 valores conferidos e imagens inalteradas.

**Pendente**
- Leitura do relatório. O utilizador pediu commit e envio.

### 2026-11-26e — Figura 7 com «baseline» (REV-074), 2026-11-26 00:31 WET

[REV-074 | cor #8B0000]

**Feito**
- A linha «previsto» da Figura 7 passou a «baseline»; só essa figura foi gerada de novo, das previsões guardadas da medição final.

**Validado**
- 254 testes; relatório com 10 páginas; 647 números de linha nas margens; página 8 revista em imagem.
- Uma leitura registada das previsões do `validation` (autorização própria); sem parquet, sem CNN e sem medições.

**Observação (sem alteração)**
- A Figura 8 usa «antes» e «depois» para a baseline sem e com filtro.

**Pendente**
- Envio a pedido; leitura do relatório.

### 2026-11-26f — Legendas das Figuras 3 e 8 (REV-075), 2026-11-26 00:38 WET

[REV-075 | cor #191970]

**Feito**
- Legendas movidas para o canto superior direito; as duas figuras geradas de novo por código.

**Validado**
- 254 testes; figuras e páginas 4 e 9 revistas em imagem; 10 páginas; 647 números de linha nas margens.
- Sem leituras de previsões nem de conjuntos reservados.

**Pendente**
- Envio a pedido (REV-074 e REV-075); leitura do relatório.

### 2026-11-26g — Envio das REV-074 e REV-075, 2026-11-26 00:40 WET

**Feito**
- O utilizador pediu o envio do `main` para o GitHub.

**Validado**
- Antes do envio: `main` 4 commits à frente de `origin/main` e nenhum atrás; código, teste, autorização, três figuras e documentos.

**Pendente**
- Leitura do relatório.

### 2026-11-26h — Legenda da Tabela 6 (REV-076), 2026-11-26 00:45 WET

[REV-076 | cor #2E8B57]

**Feito**
- Nova legenda da Tabela 6, que diz porque os valores do teste são otimistas. O utilizador pediu commit e envio.

**Validado**
- 10 páginas, sem referências em falta; 647 números de linha nas margens; páginas 8 e 9 revistas.

**Decisões**
- Texto a preto só nesta revisão; as seguintes levam cor, salvo nova instrução.

**Pendente**
- Leitura do relatório.

### 2026-11-26i — Galeria em LaTeX e PDF (REV-077), 2026-11-26 00:50 WET

[REV-077 | cor #9932CC]

**Feito**
- `build_trip_gallery_pdf` converte a página da galeria em `viagens/galeria_viagens.tex` e compila o PDF.

**Validado**
- 256 testes; PDF com 12 páginas e as 36 viagens; páginas revistas em imagem.
- Sem leituras de dados, previsões ou conjuntos reservados.

**Pendente**
- Envio a pedido; leitura do relatório.

### 2026-11-26j — Envio da REV-077, 2026-11-26 00:51 WET

**Feito**
- O utilizador pediu o envio do `main` para o GitHub.

**Validado**
- Antes do envio: `main` 2 commits à frente de `origin/main` e nenhum atrás; código, teste, galeria em `.tex` e PDF e documentos.

**Pendente**
- Leitura do relatório.
