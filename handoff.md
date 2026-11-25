# Handoff — Projeto AIS

**Data e hora desta atualização:** 2026-11-24 00:46 WET (UTC+00:00). Reescrito de raiz em REV-054, regra do push atualizada em REV-055, depois de o Marco 4 e a medição final terem sido executados (versões anteriores: REV-044, REV-045, REV-046 a REV-053). Todas as horas deste ficheiro estão em WET (em novembro igual a UTC).

Nota: o utilizador chamou-lhe uma vez «endof.md»; esse ficheiro não existe e o que se leu no arranque foi este `handoff.md`.

### Última validação (registada neste handoff)

| Verificação | Resultado | Data e hora (WET) |
|---|---|---|
| Testes (`pytest tests/`) | 192 passaram | 2026-11-24 00:41 |
| LaTeX (`pdflatex` + `bibtex`) | 11 páginas (limite de 15); 0 erros; 0 referências indefinidas | 2026-11-24 00:41 |
| Git | o estado muda a cada commit e push: confirmar com `git status -sb` e `git log origin/main..HEAD`. Último push a pedido do utilizador: 2026-11-24 (ver `git log origin/main -1`) | 2026-11-24 00:46 |
| Treino de J0 e de J50 | os dois completos (300 épocas), 9,8 min e 21,3 min | 2026-11-23 22:58 a 23:28 |
| Seleção de J0 e J50 no `test` (única abertura das janelas) | abertura 23:28:19 e fim 23:29:54 (UTC) em `results/access_log.jsonl` | 2026-11-23 |
| Medição final no `validation` | escolha do modelo 00:32:09, abertura 00:32:09 e fim 00:32:10 (UTC); só o modelo escolhido; **o `validation` está gasto** | 2026-11-24 00:32 |
| Números gerados (`final_results.json`, `final_results_windows.json`, `final_validation.json`) | gerados por `build_final_results`, `build_window_results` e `final_validation` | 2026-11-23 18:53, 2026-11-23 23:33 e 2026-11-24 00:32 |

Quem retomar deve repetir estas verificações e comparar com as horas acima: o que tiver mudado depois destas horas **não foi** validado por este handoff.

### Cronologia dos últimos commits (hora local WET)

| Commit | Data e hora | Assunto |
|---|---|---|
| `8eca05c` | 2026-11-24 00:42 | Reescreve o handoff depois do Marco 4 e da medição final (REV-054) |
| `d6111f6` | 2026-11-24 00:39 | Corrige o estado do git no handoff e no PROGRESS depois do push de REV-053 |
| `548cb8a` | 2026-11-24 00:36 | Medição final no validation do modelo escolhido e Secção 9 da proposta (REV-053) |
| `9ab2e46` | 2026-11-24 00:32 | Prepara a medição final no validation: protocolo, autorização e programa, antes de abrir (REV-053) |
| `b818aba` | 2026-11-23 23:58 | Corrige o estado do git no handoff e no PROGRESS depois do push do utilizador |
| `09a26b5` | 2026-11-23 23:57 | Refactoring de leitura da proposta LaTeX (REV-052) |
| `bb01a60` | 2026-11-23 23:46 | Gráfico de x por y da viagem 219001624-2, segunda leitura de diagnóstico (REV-051) |
| `780c2e2` | 2026-11-23 23:43 | Leitura de diagnóstico de uma viagem reservada e incidente (REV-050) |
| `a55cf1f` | 2026-11-23 23:40 | Gráfico de diagnóstico de uma viagem do test (REV-049) |
| `e2a0ba0` | 2026-11-23 23:37 | Atualiza o handoff para o Marco 4 executado (REV-046 a REV-048) |
| `867f8d8` | 2026-11-23 23:34 | Resultados de J0 e J50 na proposta LaTeX: secções 8.2, 8.3 e 8.4 (REV-046 a REV-048) |
| `5abf3ff` | 2026-11-23 23:08 | Reforça o janelamento depois da revisão independente (REV-046) |
| `2d0ca50` | 2026-11-23 22:56 | Prepara a seleção de J0 e J50 no test, com protocolo e autorização novos (REV-046) |
| `9896021` | 2026-11-23 22:56 | Implementa o janelamento e o treino de J0 e J50 (REV-046) |
| `696fed2` | 2026-11-23 19:42 | Acrescenta data, hora e cronologia ao handoff (REV-045) |

O commit deste handoff vem a seguir e não está na tabela.

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas. O `CLAUDE.md` manda lê-lo antes de qualquer ação.
2. Este ficheiro.
3. `docs/00_projeto_e_decisoes.md`, `docs/02_cnn_viagem_completa.md` e `docs/03_cnn_janelamento.md` (decisões e contratos do Marco 4, já implementado); `docs/01_dados_e_preparacao.md` se for preciso.
4. `PROGRESS.md` (estado vivo no topo; histórico por entrada, termina em 2026-11-24a) e `REVISION_LOG.md` (REV-001 a REV-055).
5. Antes de qualquer ação: `git status` e `git log`, e `iach-ais-venv-4/bin/python -m pytest tests/` (192 testes a passar).

Mensagem sugerida para abrir a nova sessão: «Lê o AGENTS.md e o handoff.md e continua de onde ficámos. Qual é o ponto de situação e o próximo passo?»

## Objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma **CNN 1D**. Ordem de trabalho:
1. Pré-processamento (feito).
2. **CNN de referência sobre a viagem completa** (feita e **fechada**, Marco 3).
3. **A mesma CNN sobre janelas com sobreposição** (Marco 4, **feito**): J0 (0 %) e J50 (50 %), L = 64, para saber se o janelamento melhora face à referência (RQ1).
4. Pós-processamento temporal (Marco 5): **por fazer, só com decisão do utilizador**.
5. **Medição final única** no conjunto `validation` (Marcos 6 e 7): **feita (REV-053)**, só do modelo escolhido.

Dataset: 123 viagens, 1 026 279 linhas. Divisão por ID completo (viagem), seed 42, 70/15/15: treino 87 viagens (713 854 linhas), validação 18 (209 016), teste 18 (103 409). Fonte: Zenodo (Song Wu, CC BY 4.0).

## O que se fez (resumo cronológico)

- **Arranque (2026-11-23, tarde):** leitura do `AGENTS.md`, do handoff e dos docs `00` a `03`; ponto de situação com a baseline fechada e o Marco 4 por começar. O utilizador respondeu às dúvidas do Marco 4 (mesma sobreposição no treino e na inferência; mesmos valores da baseline; última janela mais curta, sem pontos falsos; lote de 32; 45 min por treino; uma abertura do `test`; `validation` fechado) e deu autonomia, incluindo subagentes.
- **Implementação do janelamento (REV-046):** `windows.py`, máscara opcional no modelo, treino e seleção (`run_window_training`, `select_windows_on_test`), protocolo e autorização novos. **Revisão independente** (subagente Opus, só leitura) sem erros graves; melhorias aplicadas depois do arranque do J50, sem efeito numérico. Treino de J0 (9,8 min) e de J50 (21,3 min).
- **Seleção no `test` e resultados (REV-047, REV-048):** uma só abertura do `test`: J0 época 8 e limiar 0,60; J50 época 4 e limiar 0,75; baseline medida por segmento sem ser reselecionada. Resultados e Secção 8 do LaTeX. Nenhuma variante supera a referência por ponto; J50 reduz a fragmentação.
- **Diagnóstico da viagem `219001624-2` (REV-049 a REV-051):** J0 acerta 42,0 % por a probabilidade na pesca ficar abaixo do limiar de 0,60. Leitura de diagnóstico de `x` e `y` do `test` com autorização própria; a primeira leitura foi gasta por um erro meu no desenho (corrigido) e pediu-se nova autorização.
- **Refactoring de leitura da proposta (REV-052):** Secção 8 com resumo primeiro, 5 figuras e 3 tabelas, 4.3, 4.4 e Secção 5 condensadas, Anexo A. De 11 para 9 páginas. O utilizador confirmou que o PDF funciona e não tem bloqueios.
- **Medição final (REV-053, 2026-11-24):** a pedido do utilizador, escolheu-se o melhor dos três modelos só com o `test`, com critério declarado antes; abriu-se o `validation` **uma só vez**; Secção 9 da proposta; push dos commits a pedido do utilizador (00:39).
- **Este handoff (REV-054).**

## Estado atual

| Marco | Estado |
|---|---|
| 1 Ambiente e divisão | Fechado |
| 2 Preparação auditável | Fechado |
| 3 CNN de referência (viagem completa) | **Fechado por decisão do utilizador (REV-041)** |
| 4 Janelamento com a mesma CNN | **Feito (REV-046, REV-047)**: J0 e J50 treinadas, escolhidas no `test` numa só abertura e congeladas |
| 5 Pós-processamento | **Feito (REV-056, REV-057)**: ver `docs/04_pos_processamento.md` |
| 6 e 7 Congelar e medição final no `validation` | **Feito (REV-053)**: só o modelo escolhido (a referência), uma só vez |

- **Baseline (CNN de referência):** 87 viagens de treino, 300 épocas, ~19 min em CPU. **Época 162 e limiar 0,65**, escolhidos no `test` numa só ronda e congelados em `results/baseline_frozen/`. Exatidão por ponto de 93,5 % no treino e de 94,7 % no `test` (regra da classe maioritária: 61,2 %).
- **J0 e J50:** a mesma CNN (21 761 parâmetros, campo recetivo 13), mesmo normalizador, seed 42, Adam lr 1e-3, 300 épocas, **lotes de 32 janelas**, janelas de 64 pontos com passo 64 (J0) e 32 (J50). J0: 11 201 janelas, 351 passos por época, 105 300 passos, 9,8 min. J50: 22 265 janelas, 696 passos por época, 208 800 passos (o dobro), 21,3 min. Escolhidas no `test`: **J0 época 8, limiar 0,60; J50 época 4, limiar 0,75**. Exatidão por ponto no `test`: J0 93,5 %, J50 93,8 %, contra 94,7 % da referência. J0 supera a referência em 7 das 18 viagens e J50 em 5. Congeladas em `results/windows_j0_frozen/` e `results/windows_j50_frozen/`; números em `results/windows_final/final_results_windows.json` (fonte única).
- **Por segmento (`test`, IoU 0,5, sem suavizar):** 18 segmentos reais de pesca; previstos 358 (referência), 377 (J0) e 303 (J50); F1 de segmentos de pesca cerca de 0,03 nas três; razão de fragmentação na pesca 19,9, 20,9 e 16,8 e na navegação 10,4, 11,0 e 8,8. **J50 reduz a fragmentação face a J0 e à referência**, mas a segmentação continua muito fragmentada.
- **Medição final (REV-053):** critério declarado antes de abrir e só com o `test`: maior F1 médio por ponto, empate pela exatidão. Escolhida a **referência** (0,945; J50 0,934; J0 0,931), época 162 e limiar 0,65. No `validation` (18 viagens, 209 016 pontos): **exatidão 94,4 %** (11 662 erros; regra da classe maioritária 83,2 %; no `test` 94,7 %); pesca com sensibilidade 0,938 e precisão 0,995; navegação com sensibilidade 0,976 e **precisão 0,760** (0,900 no `test`). Por viagem de 40,4 % (`219020187-4`) a 99,7 %, mediana 98,2 %; uma viagem não supera a regra da classe maioritária. Por segmento a pesca tem 18 reais e 486 previstos (fragmentação 27,0; F1 de segmentos 0,028) e a navegação 35 e 502 (F1 0,119). J0 e J50 **não** foram medidas no `validation`. Números em `results/final_validation/final_validation.json`.
- **Cuidados (limitações registadas):** os números do `test` são **otimistas** (serviram a escolher). **A perda no `test` sobe com o treino** de J0 e J50 (máximos de 0,79 e 0,93 desde a época 100), por isso o critério da menor perda escolheu épocas muito cedo (8 e 4), enquanto a baseline foi escolhida na 162: parte da diferença pode vir do critério e não do janelamento. O lote difere (32 janelas contra uma viagem por passo) e J50 faz o dobro dos passos. Uma semente, 18 viagens por conjunto, sem intervalo de incerteza. Como J0 e J50 não foram medidas no `validation`, a resposta à RQ1 assenta só no `test`. Os resultados foram reportados como saíram, sem repetir nem ajustar.
- **Conjuntos reservados (`results/access_log.jsonl`):** o `test` foi aberto **duas vezes** para seleção, uma por autorização (baseline às 18:40 UTC; janelas às 23:28 UTC), e teve **duas leituras de diagnóstico** da viagem `219001624-2` (colunas `id`, `point_id`, `t`, `x`, `y`; a primeira foi gasta por um erro de desenho). O `validation` foi aberto **uma só vez** (`validation_final_2026-11-24`) e **está gasto**: já não pode medir mais nada, incluindo um futuro pós-processamento.
- **Testes:** 192, todos sintéticos (mais um que lê 3 viagens de treino).
- **LaTeX** (`latex/proposta_pt.tex`): 11 páginas, limite de 15. Secção 8 com resumo e tabela primeiro, 8.1 a 8.4, **Secção 9** (medição final) antes do **Anexo A**. Números e figuras gerados por código. Cores do texto novo: rev046 `#00B0FF`, rev047 `#4A148C`, rev048 `#1B5E20`, rev052 `#880E4F` (reescrito) e rev053 `#0D47A1` (Secção 9).
- **Git:** `origin/main` tinha tudo até `548cb8a` (REV-053) às 00:39; os commits seguintes (REV-054 e REV-055, só documentação) foram enviados a pedido do utilizador. Confirmar com `git status -sb`.

## Decisões vigentes

**Dados e preparação**
- Características: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`. `x` e `y` ficam de fora. Entrada de **7 canais** (4 normalizadas e 3 máscaras de ausência).
- Valores em falta: nenhuma linha removida; zero depois de normalizar, mais máscara; os pontos iniciais entram na perda. Normalizador só com o treino.
- Anomalias mantidas, sem limpeza IQR. `distanceToShore` aceite como correto. Fuso horário ignorado.
- A divisão é por viagem: viagens do mesmo navio podem estar em conjuntos diferentes. **O utilizador decidiu desconsiderar esta questão.**

**CNN de referência**
- Conv1D 32/64/32 (kernel 5, ReLU, padding same) e cabeça de kernel 1; logits; `BCEWithLogitsLoss` sem pesos de classe nem reamostragem; Adam, lr 1e-3. Campo recetivo de **13 pontos**, **21 761 parâmetros**. Uma viagem por passo na baseline. Valores iniciais, não validados.

**Conjuntos reservados (REV-036, REV-037)**
- Papéis **trocados face ao habitual**: o `test` **seleciona** e o `validation` é a **medição final**. Só se abre um conjunto reservado com autorização escrita (`configs/authorizations/`), protocolo declarado antes e registo de acesso (`ais.phase1.reserved`). **Leitura de diagnóstico** de uma viagem: via própria (`load_reserved_diagnostic`, REV-050), com autorização de finalidade `diagnostico`, viagem e colunas nomeadas, e só no `test`.

**Marco 4 (REV-046)**
- A **mesma sobreposição no treino e na inferência**. Mesmos valores da baseline (300 épocas, sem aumentar). **A última janela fica mais curta**, sem pontos falsos: o lote usa enchimento só para empilhar, fora da perda, e o modelo põe-no a zero depois de cada camada (testado: igual à janela isolada). **Os intervalos de tempo dentro de uma viagem não cortam a sequência** (como na baseline; o `AGENTS.md` §5 diz «não atravessar gaps» e o `docs/03` §2 explica que, nesta fase, a regra vale para as viagens). Reconstrução: média simples das probabilidades das janelas que cobrem cada ponto (não é suavização). Critério de seleção igual ao da baseline, aplicado às probabilidades reconstruídas. Limite de 45 min por treino. **Fora do projeto:** treinar com J0 e prever com J50, 25 % e 75 % de sobreposição, outros L.

**Âmbito e LaTeX**
- HMM e Wu et al. **não** são comparações. Explicabilidade, calibração e *dashboard* estão fora do mínimo atual.
- `latex/proposta_IAHC_DINIS_ROSA.pdf` **não se altera**. Toda a alteração ao `.tex` leva cor `\revtext{revNNN}`, igual à do `REVISION_LOG.md`. Próximo ID livre: **REV-058**. Verificar sempre no `REVISION_LOG.md` se uma cor já foi usada (duas escolhas iniciais já eram de REV-011 e REV-007).
- Cores no `.tex` em uso: rev021 `#D500F9`, rev023 `#0277BD`, rev040 `#7F0000`, rev041 `#FF1744`, rev042 `#0A3D62`, rev046 `#00B0FF`, rev047 `#4A148C`, rev048 `#1B5E20`, rev052 `#880E4F`, rev053 `#0D47A1`. Outras estão definidas, sem uso (rev013, rev018, rev020, rev022, rev024 a rev028, rev030 a rev032, rev035, rev036). Só marcadores Markdown: REV-029, REV-033, REV-034, REV-037 a REV-039, REV-044, REV-045, REV-049 a REV-051 e REV-054 (`#00BFA5`).

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, este `handoff.md` |
| Documentação | `docs/00_projeto_e_decisoes`, `docs/01_dados_e_preparacao`, `docs/02_cnn_viagem_completa`, `docs/03_cnn_janelamento` (decisões e contratos do Marco 4, implementado) |
| Biblioteca (`src/ais/phase1/`) | `data.py`, `model.py` (com máscara opcional), `training.py`, `checks.py`, `utils.py`, `artifacts.py`, `config.py`, `metrics.py`, `inference.py`, `reserved.py` (acesso reservado e leitura de diagnóstico), `selection.py`, `segments.py`, `windows.py` |
| Programas, preparação | `create_split_manifest.py`, `check_units_train.py`, `verify_trip_count.py`, `build_clean_dataset.py --split train\|validation\|test`, `count_anomalies_train.py`, `count_shared_vessels.py` |
| Programas, baseline | `run_phase1_training.py`, `select_on_test.py`, `freeze_baseline.py` (com `label`), `build_final_results.py`, `segment_metrics.py`, `plot_phase1_run.py`, `benchmark_training_speed.py` |
| Programas, janelas (REV-046, REV-047) | `run_window_training.py`, `select_windows_on_test.py`, `build_window_results.py` |
| Programas, diagnóstico (REV-049 a REV-051) | `plot_trip_diagnostic.py` (`--xy --auth` para as coordenadas) |
| Programas, medição final (REV-053) | `final_validation.py`, `build_validation_results.py` |
| Programas, pós-processamento (REV-056, REV-057) | `postproc_validation.py` (execução única, já feita), `build_postproc_results.py`, `verify_postproc_independent.py`, `plot_postprocessing_kernel.py` |
| Programas do ensaio antigo (sem uso) | `diagnostic_fit_3_trips.py`, `plot_diagnostic_3trips.py` |
| Configuração | `configs/phase1_select.json` (baseline), `windows_j0.json`, `windows_j50.json`; protocolos `selection_protocol.json`, `selection_protocol_windows.json`, `selection_protocol_validation.json`; autorizações em `configs/authorizations/` (`test_selection`, `test_selection_windows`, `test_diagnostic_trip_219001624-2` e `..._leitura2`, `validation_final`); históricos `phase1_run1.json`, `phase1_final.json` |
| Testes | `tests/` (o `pyproject.toml` põe `src/` no path do pytest); novos nesta sessão: `test_windows.py`, `test_select_windows.py`, `test_reserved_diagnostic.py`, `test_final_validation.py` |
| Dados (não versionados) | `data/123_fishing_trajs_clean_{train,validation,test}.parquet`; manifesto versionado `manifests/split_manifest_seed42.csv` |
| Resultados (não versionados) | `results/phase1_select/`, `results/baseline_frozen/` (inclui `test_segment_results.json`), `results/windows_j0/`, `results/windows_j50/`, `results/windows_j0_frozen/`, `results/windows_j50_frozen/`, `results/windows_final/`, `results/final_validation/` (`model_choice.json`, `final_validation.json`, `predictions_validation.csv`), `results/diagnostic_trip/`, `results/access_log.jsonl`; históricos: `phase1_run1/`, `phase1_final/`, `diagnostic_3trips/` |
| Proposta | `latex/proposta_pt.tex`, `latex/references.bib`, `latex/figures/` (`final_*.png`, `janelas_*.png`, `validacao_*.png`), `latex/generated/resultados.tex`, `resultados_janelas.tex` e `resultados_validacao.tex` (macros geradas) |

## Comandos úteis (a partir da raiz do projeto)

```bash
iach-ais-venv-4/bin/python -m pytest tests/                                          # testes
iach-ais-venv-4/bin/python -m ais.cli.build_final_results                            # regenera os números da baseline
iach-ais-venv-4/bin/python -m ais.cli.build_window_results                           # regenera os números de J0 e J50
iach-ais-venv-4/bin/python -m ais.cli.build_validation_results                       # regenera macros e figuras da Secção 9 (não reabre o validation)
iach-ais-venv-4/bin/python -m ais.cli.plot_trip_diagnostic 219001624-2               # gráfico das classes de uma viagem do test (só previsões já geradas)
iach-ais-venv-4/bin/python -m ais.cli.segment_metrics CAMINHO_PREVISOES.csv          # métricas por segmento
```

**Não voltar a correr** `select_on_test`, `select_windows_on_test` nem `final_validation` (cada autorização era de **uma** abertura; os programas recusam a segunda). Compilar o LaTeX à mão **sem colidir com o vigilante** (a partir de `latex/`): `-output-directory=build/check`, duas passagens de `pdflatex` e `bibtex` com `BIBINPUTS`/`BSTINPUTS` a apontar para `latex/`.

## O que falhou ou exigiu correção

- `torch.__version__` impedia carregar o checkpoint com `weights_only=True`; corrigido com `str()`.
- Testes e subagentes a correr em paralelo abrandam muito o treino (uma época de 2 s passou a 12 s com o `pytest`); **não correr CPU em paralelo durante treinos**.
- LaTeX: caracteres `«»` não existem na codificação do modelo; o vigilante e compilações manuais em `latex/build/` corromperam o `.aux` (compilar em `build/check/`). Um `%` nu no 2.º argumento de `\texorpdfstring` comenta o resto da linha e parte a compilação (usar «por cento» nos marcadores).
- Cores de revisão: duas escolhidas à primeira (`#E65100`, `#AD1457`) já pertenciam a REV-011 e REV-007; apanhado antes do commit com cor.
- **Leitura de diagnóstico gasta:** a primeira leitura de `x` e `y` foi consumida por um erro meu no desenho (os dados lidos não estavam guardados). Passou a guardar-se o que é lido antes de desenhar, e pediu-se nova autorização.
- **Horas escritas à frente do relógio:** escrevi nos registos horas que ainda não tinham acontecido; corrigidas. Usar sempre `date`.
- `grep -c` devolve código 1 quando conta zero; cuidado em cadeias com `&&`.
- Smoke test estrito: exige gradiente não nulo em todos os tensores; pode ter de ser relaxado.
- `class_metrics` está duplicada (`ais/phase1/metrics.py` e `ais/cli/diagnostic_fit_3_trips.py`), por unificar.
- Os programas de treino, de figuras e de geração de resultados **não têm teste automático** (só a seleção das janelas, as funções de janelas, a leitura de diagnóstico, a medição final e as funções de formatação e de acesso).
- O desenho inicial do janelamento previa vários módulos (`windowing`, `reconstruction`, `experiments`…) que foram agrupados em `windows.py`.

## O que fazer a seguir

0. **Marco 5 feito (REV-057, 2026-11-25 19:50 WET):** exatidão 94,4 % → 94,5 %; segmentos de pesca previstos 486 → 255 (reais 18), de navegação 502 → 272 (reais 35); F1 de segmentos de pesca 0,028 → 0,066 e de navegação 0,119 → 0,221; 784 pontos mudam (514 corrigidos, 270 estragados). **Não voltar a correr `postproc_validation`** (execução única). Próximo ID livre: **REV-058**. Os pontos sobre o Marco 5 abaixo estão ultrapassados.
1. **Perguntar ao utilizador:**
   - Quer avançar para o **Marco 5** (pós-processamento), dado que a segmentação continua muito fragmentada (pesca: 18 segmentos reais e 486 previstos no `validation`)? A unidade e a largura do filtro teriam de ser aprovadas, e **só se poderia avaliar no `test`** (otimista), porque o `validation` está gasto. A resposta às RQ2 e RQ3 depende disto.
   - O critério de seleção por menor perda (épocas 8 e 4) **já não muda o resultado final**: o modelo medido foi a referência. Recomendação anterior: manter e deixar como limitação.
2. **LaTeX, passagens ainda abertas** (o utilizador adiou-as): explicabilidade, calibração e *dashboard* (resumo, objetivo 5, 4.6, 7.3); há texto a vermelho «human-on-the-loop»; a 7.1 ainda descreve a ablação completa; as secções 6 e 7.2 e as partes a preto das revisões anteriores não foram relidas.
3. **Arrumação:** testes dos programas de treino e de figuras; unificar `class_metrics`; apagar os restos do ensaio de 3 viagens e das execuções antigas, se o utilizador quiser.
4. **Push:** só quando o utilizador o pedir (ver as regras); quando pede, enviar sem mais perguntas.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. Validação e teste só com autorização explícita; uma flag no código não é autorização. **O `validation` já não se abre mais.**
- Todo o número usado como evidência vem de código versionado e executável (AGENTS §10); no LaTeX, só por macros geradas. Não afirmar o que não foi medido; distinguir feito, validado e pendente.
- **Push (REV-055):** o utilizador definiu a regra: **se ele pede (no chat ou no handoff), o agente faz push, como se fosse ele, sem pedir confirmação nem lembrar a autorização**. Por iniciativa própria, ou a trabalhar sozinho sem pedido explícito, **nunca**. Sem `--force`. Antes de enviar, ver branch, remoto e commits a enviar. Está no `AGENTS.md` §6.
- Commits após explicação; alterações substanciais com mensagem completa (O quê, Porquê, Como, Impacto, Validação, Pendente) e a linha de coautoria. Selecionar ficheiros explicitamente.
- No fim de cada interação que altere ficheiros: atualizar `PROGRESS.md` e `REVISION_LOG.md` (REV novo, cor nova, marcador `[REV-NNN | cor #HEX]`) e confirmar que `README.md`, `docs/` e o LaTeX não se contradizem.
- Explicar comandos e alterações antes de os executar. Pedir autorização para alterações metodológicas, execuções prolongadas e instalações.
- **Subagentes:** só com contrato fechado, regras explícitas no prompt e ficheiros distintos; nunca confiar só no relatório: rever o código, conferir à mão e correr os testes. (Nesta sessão: Opus, só leitura, para rever o janelamento; sem erros graves, melhorias aplicadas.)
- **Todo o handoff indica a data e a hora (com fuso) da escrita e da última validação** (testes, compilação do LaTeX, estado do git). Usar `date`, não estimar.
- Comunicar em português europeu; funções e variáveis em inglês.

## Preferências do utilizador observadas

- Quer um **plano** e uma explicação antes de avançar, e que as dúvidas lhe sejam colocadas **antes** de o trabalho autónomo começar; depois dá autonomia para executar tudo, incluindo subagentes, treinos e LaTeX.
- Prefere resultados em **imagens e tabelas** e um resumo final claro; se o resultado for pior que a baseline, quer apenas que lho digam.
- Decide depressa e deixa decisões claras («está fechado», «desconsidera», «sim, autorizo»): registá-las como estão, sem as reabrir.
- Quer commits **divididos por tema**, com mensagens completas; o push só quando o pede (e, quando pede, sem mais perguntas).
- Quer o LaTeX sempre coerente e com valores **gerados por código**, e **a cor da revisão em todo o texto novo**; também quer o relatório **fácil de ler** (poucas figuras acumuladas, texto corrido, resumo primeiro).
- Aceita valores recomendados em bloco quando vêm numa tabela com valor proposto e justificação.
