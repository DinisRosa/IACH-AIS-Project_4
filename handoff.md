# Handoff — Projeto AIS

**Data e hora desta atualização:** 2026-11-23 23:41 WET (UTC+00:00). Reescrito de raiz em REV-044, atualizado em REV-045 e de novo em REV-046 a REV-048 (Marco 4 executado). Todas as horas deste ficheiro estão em WET (em novembro igual a UTC).

### Última validação (registada neste handoff)

| Verificação | Resultado | Data e hora (WET) |
|---|---|---|
| Testes (`pytest tests/`) | 181 passaram | 2026-11-23 23:40 |
| LaTeX (`pdflatex` + `bibtex`) | 11 páginas (limite de 15); 0 erros; 0 referências indefinidas | 2026-11-23 23:36 |
| Git | `main` cinco commits à frente de `origin/main` (último em `origin/main`: `696fed2`); **nada enviado** | 2026-11-23 23:36 |
| Treino de J0 e de J50 | os dois completos (300 épocas), 9,8 min e 21,3 min | 22:58 a 23:28 |
| Seleção no `test` (única abertura das janelas) | abertura 23:28:19 e fim 23:29:54, em `results/access_log.jsonl` | 2026-11-23 |
| Números de J0 e J50 (`final_results_windows.json`) | gerados por `build_window_results` | 2026-11-23 23:33 |
| Conjunto `validation` | **nunca aberto** (sem entradas no `access_log`) | verificado em 2026-11-23 23:36 |

Quem retomar deve repetir estas verificações e comparar com as horas acima: o que tiver mudado depois destas horas **não foi** validado por este handoff.

### Cronologia dos últimos commits (hora local WET)

| Commit | Data e hora | Assunto |
|---|---|---|
| `a80ba15` | 2026-11-23 23:35 | Regista REV-046 a REV-048 e alinha README e docs com o Marco 4 executado |
| `867f8d8` | 2026-11-23 23:34 | Acrescenta os resultados de J0 e J50 à proposta LaTeX: secções 8.2, 8.3 e 8.4 (REV-046, REV-047, REV-048) |
| `5abf3ff` | 2026-11-23 23:08 | Reforça o janelamento depois da revisão independente e prepara o gerador de resultados (REV-046) |
| `2d0ca50` | 2026-11-23 22:56 | Prepara a seleção de J0 e J50 no test, com protocolo e autorização novos (REV-046) |
| `9896021` | 2026-11-23 22:56 | Implementa o janelamento com sobreposição e o treino de J0 e J50 (REV-046) |
| `696fed2` | 2026-11-23 19:42 | Acrescenta data, hora e cronologia ao handoff e regista REV-045 (já em `origin/main`) |

O commit deste handoff vem a seguir e não está na tabela.

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas. O `CLAUDE.md` manda lê-lo antes de qualquer ação.
2. Este ficheiro.
3. `docs/00_projeto_e_decisoes.md`, `docs/02_cnn_viagem_completa.md` e `docs/03_cnn_janelamento.md` (decisões e contratos do Marco 4, já implementado); `docs/01_dados_e_preparacao.md` se for preciso.
4. `PROGRESS.md` (estado vivo no topo; histórico por entrada, termina em 2026-11-23bc) e `REVISION_LOG.md` (REV-001 a REV-049).
5. Antes de qualquer ação: `git status` e `git log`, e `iach-ais-venv-4/bin/python -m pytest tests/` (181 testes a passar).

Mensagem sugerida para abrir a nova sessão: «Lê o AGENTS.md e o handoff.md e continua de onde ficámos. Qual é o ponto de situação e o próximo passo?»

## Objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma **CNN 1D**. Ordem de trabalho:
1. Pré-processamento (feito).
2. **CNN de referência sobre a viagem completa** (feita e **fechada**, Marco 3).
3. **A mesma CNN sobre janelas com sobreposição** (Marco 4, **feito**): J0 (0 %) e J50 (50 %), L = 64, para saber se o janelamento melhora face à referência (RQ1).
4. Pós-processamento temporal, só se o utilizador o decidir (Marco 5).
5. Congelar todas as variantes e fazer uma **medição final única** no conjunto `validation` (Marcos 6 e 7).

Dataset: 123 viagens, 1 026 279 linhas. Divisão por ID completo (viagem), seed 42, 70/15/15: treino 87 viagens (713 854 linhas), validação 18 (209 016), teste 18 (103 409). Fonte: Zenodo (Song Wu, CC BY 4.0).

## Estado atual

| Marco | Estado |
|---|---|
| 1 Ambiente e divisão | Fechado |
| 2 Preparação auditável | Fechado |
| 3 CNN de referência (viagem completa) | **Fechado por decisão do utilizador (REV-041)** |
| 4 Janelamento com a mesma CNN | **Feito (REV-046, REV-047)**: J0 e J50 treinadas, escolhidas no `test` numa só abertura e congeladas |
| 5 Pós-processamento | Por fazer; só com decisão do utilizador |
| 6 e 7 Congelar tudo e medição final no `validation` | Por fazer; precisam de autorização |

- **Baseline (CNN de referência):** 87 viagens de treino, 300 épocas, ~19 min em CPU. **Época 162 e limiar 0,65**, escolhidos no `test` numa só ronda e congelados em `results/baseline_frozen/`. Exatidão por ponto de 93,5 % no treino e de 94,7 % no `test` (regra da classe maioritária: 61,2 %).
- **J0 e J50:** a mesma CNN (21 761 parâmetros, campo recetivo 13), mesmo normalizador, seed 42, Adam lr 1e-3, 300 épocas, **lotes de 32 janelas**, janelas de 64 pontos com passo 64 (J0) e 32 (J50). J0: 11 201 janelas, 351 passos por época, 105 300 passos, 9,8 min. J50: 22 265 janelas, 696 passos por época, 208 800 passos (o dobro), 21,3 min. Escolhidas no `test` numa só abertura: **J0 época 8, limiar 0,60; J50 época 4, limiar 0,75**. Exatidão por ponto no `test`: J0 93,5 %, J50 93,8 %, contra 94,7 % da referência. J0 supera a referência em 7 das 18 viagens e J50 em 5. Congeladas em `results/windows_j0_frozen/` e `results/windows_j50_frozen/`; números em `results/windows_final/final_results_windows.json` (fonte única).
- **Por segmento (`test`, IoU 0,5, sem suavizar):** 18 segmentos reais de pesca; previstos 358 (referência), 377 (J0) e 303 (J50); F1 de segmentos de pesca cerca de 0,03 nas três; razão de fragmentação na pesca 19,9, 20,9 e 16,8 e na navegação 10,4, 11,0 e 8,8. **J50 reduz a fragmentação face a J0 e à referência**, mas a segmentação continua muito fragmentada. Erros de fronteira da pesca sem padrão (5 ou 6 pares correspondidos).
- **Cuidados (limitações registadas):** os números do `test` são **otimistas** (serviram a escolher, nas três variantes com o mesmo critério). **A perda no `test` sobe com o treino** (máximos de 0,79 em J0 e 0,93 em J50 desde a época 100), por isso o critério da menor perda escolheu épocas muito cedo (4 e 8), enquanto a baseline foi escolhida na 162: parte da diferença pode vir do critério e não do janelamento. O lote difere (32 janelas contra uma viagem por passo) e J50 faz o dobro dos passos. Uma semente e 18 viagens de teste. Os resultados foram reportados como saíram, sem repetir nem ajustar.
- **Conjuntos reservados:** o `test` foi aberto **duas vezes**, uma por autorização (baseline às 18:40 UTC; janelas às 23:28 UTC), ambas em `results/access_log.jsonl`. O `validation` **nunca foi aberto**.
- **Testes:** 181, todos sintéticos (mais um que lê 3 viagens de treino).
- **LaTeX** (`latex/proposta_pt.tex`): 11 páginas, limite de 15. A Secção 8 tem 8.1 (referência), 8.2 (J0), 8.3 (J50) e 8.4 (comparação e RQ1), com números e figuras gerados por código. Texto novo com cor: rev046 `#00B0FF`, rev047 `#4A148C`, rev048 `#1B5E20`.
- **Git:** cinco commits locais por enviar (ver cima). Cada push precisa de autorização explícita nova do utilizador.

## Decisões vigentes

**Dados e preparação**
- Características: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`. `x` e `y` ficam de fora. Entrada de **7 canais** (4 normalizadas e 3 máscaras de ausência).
- Valores em falta: nenhuma linha removida; zero depois de normalizar, mais máscara; os pontos iniciais entram na perda. Normalizador só com o treino.
- Anomalias mantidas, sem limpeza IQR. `distanceToShore` aceite como correto. Fuso horário ignorado.
- A divisão é por viagem: viagens do mesmo navio podem estar em conjuntos diferentes. **O utilizador decidiu desconsiderar esta questão.**

**CNN de referência**
- Conv1D 32/64/32 (kernel 5, ReLU, padding same) e cabeça de kernel 1; logits; `BCEWithLogitsLoss` sem pesos de classe nem reamostragem; Adam, lr 1e-3. Campo recetivo de **13 pontos**, **21 761 parâmetros**. Uma viagem por passo na baseline. Valores iniciais, não validados.

**Conjuntos reservados (REV-036, REV-037)**
- Papéis **trocados face ao habitual**: o `test` **seleciona** e o `validation` é a **medição final**, aberta uma só vez, no fim, com todas as variantes congeladas e autorização nova. Só se abre um conjunto reservado com autorização escrita (`configs/authorizations/`), protocolo declarado antes e registo de acesso (`ais.phase1.reserved`).

**Marco 4 (REV-046)**
- A **mesma sobreposição no treino e na inferência**. Mesmos valores da baseline (300 épocas, sem aumentar). **A última janela fica mais curta**, sem pontos falsos: o lote usa enchimento só para empilhar, fora da perda, e o modelo põe-no a zero depois de cada camada (testado: igual à janela isolada). **Os intervalos de tempo dentro de uma viagem não cortam a sequência** (como na baseline; nota: o `AGENTS.md` §5 diz «não atravessar gaps», e o `docs/03` §2 explica que, nesta fase, a regra vale para as viagens). Reconstrução: média simples das probabilidades das janelas que cobrem cada ponto (não é suavização). Critério de seleção igual ao da baseline, aplicado às probabilidades reconstruídas. Limite de 45 min por treino. **Fora do projeto:** treinar com J0 e prever com J50, 25 % e 75 % de sobreposição, outros L.

**Âmbito e LaTeX**
- HMM e Wu et al. **não** são comparações. Explicabilidade, calibração e *dashboard* estão fora do mínimo atual.
- `latex/proposta_IAHC_DINIS_ROSA.pdf` **não se altera**. Toda a alteração ao `.tex` leva cor `\revtext{revNNN}`, igual à do `REVISION_LOG.md`. Próximo ID livre: **REV-050**. As cores já usadas estão no `REVISION_LOG.md` (verificar antes de escolher: duas escolhas iniciais já eram de REV-007 e REV-011).
- Cores no `.tex` em uso: rev021 `#D500F9`, rev023 `#0277BD`, rev040 `#7F0000`, rev041 `#FF1744`, rev042 `#0A3D62`, rev046 `#00B0FF`, rev047 `#4A148C`, rev048 `#1B5E20`. Outras estão definidas, sem uso (rev013, rev018, rev020, rev022, rev024 a rev028, rev030 a rev032, rev035, rev036). Só marcadores Markdown: REV-029, REV-033, REV-034, REV-037, REV-038, REV-039, REV-044, REV-045.

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, este `handoff.md` |
| Documentação | `docs/00_projeto_e_decisoes`, `docs/01_dados_e_preparacao`, `docs/02_cnn_viagem_completa`, `docs/03_cnn_janelamento` (decisões e contratos do Marco 4, implementado) |
| Biblioteca (`src/ais/phase1/`) | `data.py`, `model.py` (com máscara opcional), `training.py`, `checks.py`, `utils.py`, `artifacts.py`, `config.py`, `metrics.py`, `inference.py`, `reserved.py`, `selection.py`, `segments.py`, **`windows.py`** |
| Programas, baseline | `run_phase1_training.py`, `select_on_test.py`, `freeze_baseline.py` (com `label`), `build_final_results.py`, `segment_metrics.py`, `plot_phase1_run.py`, `benchmark_training_speed.py` |
| Programas, janelas (REV-046, REV-047, REV-049) | `run_window_training.py`, `select_windows_on_test.py`, `build_window_results.py`, `plot_trip_diagnostic.py` |
| Programas, preparação | `create_split_manifest.py`, `check_units_train.py`, `verify_trip_count.py`, `build_clean_dataset.py --split train\|validation\|test`, `count_anomalies_train.py`, `count_shared_vessels.py` |
| Programas do ensaio antigo (sem uso) | `diagnostic_fit_3_trips.py`, `plot_diagnostic_3trips.py` |
| Configuração | `configs/phase1_select.json` (baseline), `selection_protocol.json`, `authorizations/test_selection.json`; **`windows_j0.json`, `windows_j50.json`, `selection_protocol_windows.json`, `authorizations/test_selection_windows.json`**; históricos: `phase1_run1.json`, `phase1_final.json` |
| Testes | `tests/` (o `pyproject.toml` põe `src/` no path do pytest); novos: `test_windows.py`, `test_select_windows.py` |
| Dados (não versionados) | `data/123_fishing_trajs_clean_{train,validation,test}.parquet`; manifesto versionado `manifests/split_manifest_seed42.csv` |
| Resultados (não versionados) | `results/phase1_select/`, `results/baseline_frozen/` (inclui `test_segment_results.json`), `results/windows_j0/`, `results/windows_j50/`, `results/windows_j0_frozen/`, `results/windows_j50_frozen/`, `results/windows_final/`, `results/access_log.jsonl`; históricos: `phase1_run1/`, `phase1_final/`, `diagnostic_3trips/` |
| Proposta | `latex/proposta_pt.tex`, `latex/references.bib`, `latex/figures/` (`final_*.png`, `janelas_*.png`), `latex/generated/resultados.tex` e `resultados_janelas.tex` (macros geradas) |

## Comandos úteis (a partir da raiz do projeto)

```bash
iach-ais-venv-4/bin/python -m pytest tests/                                          # testes
iach-ais-venv-4/bin/python -m ais.cli.run_window_training configs/windows_j0.json    # treino de J0 (já feito)
iach-ais-venv-4/bin/python -m ais.cli.build_final_results                            # regenera os números da baseline
iach-ais-venv-4/bin/python -m ais.cli.build_window_results                           # regenera os números de J0 e J50
iach-ais-venv-4/bin/python -m ais.cli.segment_metrics CAMINHO_PREVISOES.csv          # métricas por segmento
```

**Não voltar a correr** `select_on_test` nem `select_windows_on_test` (cada autorização era de **uma** abertura; os programas recusam a segunda). Compilar o LaTeX à mão **sem colidir com o vigilante** (a partir de `latex/`): `-output-directory=build/check`, duas passagens de `pdflatex` e `bibtex` com `BIBINPUTS`/`BSTINPUTS` a apontar para `latex/`.

## O que falhou ou exigiu correção

- `torch.__version__` impedia carregar o checkpoint com `weights_only=True`; corrigido com `str()`.
- Testes e subagentes a correr em paralelo abrandam muito o treino (uma época de 2 s passou a 12 s com o `pytest`); **não correr CPU em paralelo durante treinos**.
- LaTeX: caracteres `«»` não existem na codificação do modelo (usar `` `` ''); o vigilante e compilações manuais em `latex/build/` corromperam o `.aux` (compilar em `build/check/`).
- Cores de revisão: duas escolhidas à primeira (`#E65100`, `#AD1457`) já pertenciam a REV-011 e REV-007; apanhado antes do commit com cor. **Verificar sempre no `REVISION_LOG.md`.**
- `grep -c` devolve código 1 quando conta zero; cuidado em cadeias com `&&`.
- Smoke test estrito: exige gradiente não nulo em todos os tensores; pode ter de ser relaxado.
- `class_metrics` está duplicada (`ais/phase1/metrics.py` e `ais/cli/diagnostic_fit_3_trips.py`), por unificar.
- Os programas de treino, de figuras e de geração de resultados **não têm teste automático** (só a seleção das janelas, as funções de janelas e as de formatação e de acesso).
- O `docs/03` ainda é fiel ao que foi implementado, mas o desenho inicial previa vários módulos (`windowing`, `reconstruction`, `experiments`…) que foram agrupados em `windows.py`.

## O que fazer a seguir

1. **Perguntar ao utilizador, antes de qualquer trabalho:**
   - Quer **manter o critério de seleção** (menor perda no `test`), que escolheu as épocas 4 e 8, ou mudá-lo (por exemplo, F1, ou travar o treino mais cedo)? Mudar implica novo protocolo e nova autorização, e repetir a seleção da baseline para a comparação ser justa.
   - Quer avançar para o **Marco 5** (pós-processamento), dado que J50 reduz a fragmentação mas a segmentação continua muito fragmentada? A unidade e a largura do filtro teriam de ser aprovadas.
   - Quando fazer os **Marcos 6 e 7** (congelar tudo e medir no `validation`, uma só vez, com autorização nova).
2. **LaTeX, passagens ainda abertas** (o utilizador adiou-as): explicabilidade, calibração e *dashboard* (resumo, objetivo 5, 4.6, 7.3); o título começa por «OOI» e há texto a vermelho «human-on-the-loop»; o texto das subsecções 5.3 a 5.6 e 6.1 não foi relido pelo utilizador; a 7.1 ainda descreve a ablação completa.
3. **Arrumação:** testes dos programas de treino e de figuras; unificar `class_metrics`; apagar os restos do ensaio de 3 viagens e das execuções antigas, se o utilizador quiser.
4. **Gráfico `x` por `y` da viagem `219001624-2` (REV-049):** o utilizador pediu-o; falta autorização explícita para ler o ficheiro do `test` (uso novo, fora da autorização das janelas). O gráfico das classes já está feito (J0 acerta 42,0 % nesta viagem por a probabilidade na pesca ficar abaixo do limiar de 0,60).
5. **Push:** os cinco commits locais só seguem quando o utilizador autorizar.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. Validação e teste só com autorização explícita; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado e executável (AGENTS §10); no LaTeX, só por macros geradas. Não afirmar o que não foi medido; distinguir feito, validado e pendente.
- **Nunca `git push`** sem autorização explícita **nova** do utilizador. Commits após explicação; alterações substanciais com mensagem completa (O quê, Porquê, Como, Impacto, Validação, Pendente) e a linha de coautoria. Selecionar ficheiros explicitamente.
- No fim de cada interação que altere ficheiros: atualizar `PROGRESS.md` e `REVISION_LOG.md` (REV novo, cor nova, marcador `[REV-NNN | cor #HEX]`) e confirmar que `README.md`, `docs/` e o LaTeX não se contradizem.
- Explicar comandos e alterações antes de os executar. Pedir autorização para alterações metodológicas, execuções prolongadas e instalações.
- **Subagentes:** só com contrato fechado, regras explícitas no prompt e ficheiros distintos; nunca confiar só no relatório: rever o código, conferir à mão e correr os testes. (Nesta sessão: Opus, só leitura, para rever o janelamento; sem erros graves, melhorias aplicadas.)
- **Todo o handoff indica a data e a hora (com fuso) da escrita e da última validação** (testes, compilação do LaTeX, estado do git). Usar `date`, não estimar.
- Comunicar em português europeu; funções e variáveis em inglês.

## Preferências do utilizador observadas

- Quer um **plano** e uma explicação antes de avançar, e que as dúvidas lhe sejam colocadas **antes** de o trabalho autónomo começar; depois dá autonomia para executar tudo, incluindo subagentes, treinos e LaTeX.
- Prefere resultados em **imagens e tabelas** e um resumo final claro; se o resultado for pior que a baseline, quer apenas que lho digam.
- Decide depressa e deixa decisões claras («está fechado», «desconsidera»): registá-las como estão, sem as reabrir.
- Quer commits **divididos por tema**, com mensagens completas, e o push só quando o autoriza.
- Quer o LaTeX sempre coerente e com valores **gerados por código**, e **a cor da revisão em todo o texto novo**.
- Aceita valores recomendados em bloco quando vêm numa tabela com valor proposto e justificação.
