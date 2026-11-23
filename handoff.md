# Handoff — Projeto AIS

Data: 2026-11-23. Reescrito de raiz em REV-044 para retomar o trabalho numa nova sessão.

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas. O `CLAUDE.md` manda lê-lo antes de qualquer ação.
2. Este ficheiro.
3. `docs/00_projeto_e_decisoes.md` e `docs/02_cnn_viagem_completa.md`; depois `docs/03_cnn_janelamento.md` (Marco 4) e `docs/01_dados_e_preparacao.md` se for preciso.
4. `PROGRESS.md` (estado vivo no topo; histórico por entrada, termina em 2026-11-23ba) e `REVISION_LOG.md` (REV-001 a REV-044).
5. Antes de qualquer ação: `git status` e `git log`, e `iach-ais-venv-4/bin/python -m pytest tests/` (145 testes a passar).

Mensagem sugerida para abrir a nova sessão: «Lê o AGENTS.md e o handoff.md e continua de onde ficámos. Qual é o ponto de situação e o próximo passo?»

## Objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma **CNN 1D**. Ordem de trabalho:
1. Pré-processamento (feito).
2. **CNN de referência sobre a viagem completa** (feita e **fechada**, Marco 3).
3. **A mesma CNN sobre janelas com sobreposição** (Marco 4): saber se o janelamento melhora face à referência (RQ1).
4. Pós-processamento temporal, só se o Marco 4 mostrar benefício (Marco 5).
5. Congelar todas as variantes e fazer uma **medição final única** no conjunto `validation` (Marcos 6 e 7).

Dataset: 123 viagens, 1 026 279 linhas. Divisão por ID completo (viagem), seed 42, 70/15/15: treino 87 viagens (713 854 linhas), validação 18 (209 016), teste 18 (103 409). Fonte: Zenodo (Song Wu, CC BY 4.0).

## Estado atual

| Marco | Estado |
|---|---|
| 1 Ambiente e divisão | Fechado |
| 2 Preparação auditável | Fechado |
| 3 CNN de referência (viagem completa) | **Fechado por decisão do utilizador (REV-041)** |
| 4 Janelamento com a mesma CNN | **Por começar**: só decisões; ferramenta de medição por segmento já existe |
| 5 Pós-processamento | Por fazer; condicional ao Marco 4 |
| 6 e 7 Congelar tudo e medição final no `validation` | Por fazer; precisam de autorização |

- **Baseline (CNN de referência):** treinada nas 87 viagens de treino, 300 épocas, um checkpoint por época, cerca de 19 minutos em CPU. **Época 162 e limiar 0,65**, escolhidos no conjunto `test` numa só ronda e congelados em `results/baseline_frozen/`. Números em `results/baseline_frozen/final_results.json` (fonte única, gerado por código): exatidão por ponto de 93,5 % no treino e de 94,7 % no `test` (regra da classe maioritária: 61,2 % no `test`); no `test`, navegação com sensibilidade 0,971 e precisão 0,900, pesca com sensibilidade 0,931 e precisão 0,981.
- **Cuidado (limitação registada):** os números do `test` são **otimistas** (serviram a escolher) e a perda no `test` oscila muito de época para época, por isso a escolha da época pode ter seguido ruído. O utilizador decidiu **aceitar a baseline como está**.
- **Conjuntos reservados:** o `test` foi aberto **uma só vez** (seleção, REV-038), registado em `results/access_log.jsonl`. O `validation` **nunca foi aberto**.
- **Testes:** 145 a passar, todos sintéticos (mais um que lê 3 viagens de treino).
- **LaTeX** (`latex/proposta_pt.tex`): compila, 8 páginas. Os números dos resultados vêm de macros geradas. **Cores (REV-043):** o texto estável está a preto e só o que ainda pode mudar mantém a cor da revisão.
- **Git:** `origin/main` está em `d1f30e0` (REV-043). Os commits de REV-044 (este handoff e a limpeza dos documentos) estão **só locais**. O push precisa de autorização explícita nova.

## Decisões vigentes

**Dados e preparação**
- Características: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`. `x` e `y` ficam de fora. Entrada de **7 canais** (4 normalizadas e 3 máscaras de ausência).
- Valores em falta: nenhuma linha removida; zero depois de normalizar, mais máscara; os pontos iniciais entram na perda. Normalizador só com o treino.
- Anomalias mantidas, sem limpeza IQR. `distanceToShore` aceite como correto. Fuso horário ignorado.
- A divisão é por viagem: viagens do mesmo navio podem estar em conjuntos diferentes. **O utilizador decidiu desconsiderar esta questão** (sem quantificar, sem refazer, sem declarar no texto).

**CNN de referência**
- Conv1D 32/64/32 (kernel 5, ReLU, padding same) e cabeça de kernel 1; logits; `BCEWithLogitsLoss` sem pesos de classe nem reamostragem; Adam, lr 1e-3. Campo recetivo de **13 pontos**, **21 761 parâmetros**. Uma viagem por passo. Valores iniciais, não validados.
- A mesma rede é usada nas duas experiências; a baseline não se treina de novo.

**Conjuntos reservados (REV-036, REV-037)**
- Papéis **trocados face ao habitual**: o `test` **seleciona** (épocas, limiar, variantes) e o `validation` é a **medição final**, aberta uma só vez, no fim, com todas as variantes congeladas e autorização nova. Os nomes dos ficheiros mantêm-se.
- Só se abre um conjunto reservado com autorização escrita (`configs/authorizations/`), protocolo declarado antes (`configs/selection_protocol.json`) e registo de acesso (`ais.phase1.reserved`).

**Marco 4 (decisões do utilizador; nada implementado)**
- Mesma CNN sobre janelas de **L = 64** pontos, com sobreposição de **0 %** (controlo) e **50 %**; depois testar se aumentar ou diminuir L compensa. 25 % e 75 % ficam para depois.
- As métricas por segmento (`ais.cli.segment_metrics`, sem suavizar) vêm primeiro e são ferramenta de medição, distinta do pós-processamento.

**Âmbito e LaTeX**
- HMM e Wu et al. **não** são comparações (REV-006, REV-042): só literatura na Contexto. Explicabilidade, calibração e *dashboard* estão fora do mínimo atual.
- `latex/proposta_IAHC_DINIS_ROSA.pdf` **não se altera**. Toda a alteração ao `.tex` leva cor `\revtext{revNNN}`, igual à do `REVISION_LOG.md`. Próximo ID livre: **REV-045**.
- Cores no `.tex` ainda em uso: rev021 `#D500F9`, rev023 `#0277BD`, rev040 `#7F0000`, rev041 `#FF1744`, rev042 `#0A3D62`. Outras definidas, sem uso: rev013 `#808000`, rev018 `#5C6BC0`, rev020 `#607D8B`, rev022 `#00897B`, rev024 `#6D4C41`, rev025 `#6A1B9A`, rev026 `#2E7D32`, rev027 `#AFB42B`, rev028 `#00ACC1`, rev030 `#FF6F00`, rev031 `#006064`, rev032 `#D81B60`, rev035 `#6200EA`, rev036 `#00C853`. Só marcadores Markdown: REV-029 `#BF360C`, REV-033 `#3E2723`, REV-034 `#7CB342`, REV-037 `#FFAB00`, REV-038 `#304FFE`, REV-039 `#1DE9B6`, REV-044 `#9E9E9E`.

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, este `handoff.md` |
| Documentação | `docs/00_projeto_e_decisoes`, `docs/01_dados_e_preparacao`, `docs/02_cnn_viagem_completa` (tabela do que está feito), `docs/03_cnn_janelamento` (contratos do Marco 4, por implementar) |
| Biblioteca (`src/ais/phase1/`) | `data.py`, `model.py`, `training.py`, `checks.py`, `utils.py`, `artifacts.py`, `config.py`, `metrics.py`, `inference.py`, `reserved.py` (acesso reservado), `selection.py`, `segments.py` |
| Programas (`src/ais/cli/`), treino e resultados | `run_phase1_training.py`, `select_on_test.py`, `freeze_baseline.py`, `build_final_results.py`, `segment_metrics.py`, `plot_phase1_run.py`, `benchmark_training_speed.py` |
| Programas, preparação | `create_split_manifest.py`, `check_units_train.py`, `verify_trip_count.py`, `build_clean_dataset.py --split train\|validation\|test`, `count_anomalies_train.py`, `count_shared_vessels.py` |
| Programas do ensaio antigo (sem uso) | `diagnostic_fit_3_trips.py`, `plot_diagnostic_3trips.py` |
| Configuração | `configs/phase1_select.json` (baseline), `selection_protocol.json`, `authorizations/test_selection.json`; históricos: `phase1_run1.json`, `phase1_final.json` |
| Testes | `tests/` (o `pyproject.toml` põe `src/` no path do pytest) |
| Dados (não versionados) | `data/123_fishing_trajs_clean_{train,validation,test}.parquet`; manifesto versionado `manifests/split_manifest_seed42.csv` |
| Resultados (não versionados) | `results/phase1_select/` (checkpoints por época, `selection_test.json`), `results/baseline_frozen/` (baseline e `final_results.json`), `results/access_log.jsonl`; históricos: `phase1_run1/`, `phase1_final/`, `diagnostic_3trips/` |
| Proposta | `latex/proposta_pt.tex`, `latex/references.bib`, `latex/figures/`, `latex/generated/resultados.tex` (macros geradas) |

## Comandos úteis (a partir da raiz do projeto)

```bash
iach-ais-venv-4/bin/python -m pytest tests/                                       # testes
iach-ais-venv-4/bin/python -m ais.cli.run_phase1_training configs/phase1_select.json   # treino (um checkpoint por época)
iach-ais-venv-4/bin/python -m ais.cli.select_on_test results/phase1_select             # seleção no test: UMA só ronda, já feita
iach-ais-venv-4/bin/python -m ais.cli.freeze_baseline                                  # congelar a baseline, já feito
iach-ais-venv-4/bin/python -m ais.cli.build_final_results                              # regenera final_results.json, macros e figuras
iach-ais-venv-4/bin/python -m ais.cli.segment_metrics CAMINHO_PREVISOES.csv            # métricas por segmento
```

**Não voltar a correr** `select_on_test` (a autorização era de uma ronda e o programa recusa a segunda). Compilar o LaTeX à mão **sem colidir com o vigilante** (a partir de `latex/`): `-output-directory=build/check`, duas passagens de `pdflatex` e `bibtex` com `BIBINPUTS`/`BSTINPUTS` a apontar para `latex/`.

## Resultados e ensaios (histórico)

- **Baseline (REV-038, REV-040):** ver «Estado atual». A curva de perda no `test` é ruidosa (por exemplo, 0,185 na época escolhida e até 0,342 desde a época 100); no treino a perda desce de forma mais regular.
- **Treino de 100 épocas (REV-035) e execução 1 com monitorização de 15 % (REV-032):** superados. Os números estão no `REVISION_LOG.md`, já sem uso no LaTeX.
- **Ensaio de 3 viagens (REV-027, REV-028):** retirado do LaTeX em REV-035; os programas e as PNG `latex/figures/diag3_*` continuam no repositório, sem uso.
- **Velocidade (CPU, 10 threads):** o custo cresce com os **pontos**, não com as viagens: cerca de 2,4 a 3,7 µs por ponto em treino e 1,0 a 1,6 µs em avaliação; pico de memória cerca de 822 MB. O treino de 300 épocas levou cerca de 2,8 s por época (muito mais lento se houver outros programas a competir pelo CPU).
- **Métricas por segmento:** só validadas em dados sintéticos (valores calculados à mão) e sobre previsões do **treino**, conferidas por uma reimplementação independente. Ainda **não** aplicadas à baseline.

## O que falhou ou exigiu correção

- `torch.__version__` impedia carregar o checkpoint com `weights_only=True`; corrigido com `str()`.
- Testes e subagentes a correr em paralelo abrandaram muito o treino de 300 épocas; evitar CPU em paralelo durante treinos.
- A expetativa de um teste sobre o limiar estava errada e foi corrigida (não o código).
- Um primeiro `git add` falhou e o commit saiu incompleto; foi emendado antes de qualquer push.
- LaTeX: caracteres `«»` não existem na codificação do modelo (usar `` `` ''); o vigilante e compilações manuais em `latex/build/` corromperam o `.aux` (compilar em `build/check/`).
- Smoke test estrito: exige gradiente não nulo em todos os tensores; pode ter de ser relaxado.
- `class_metrics` está duplicada (`ais/phase1/metrics.py` e `ais/cli/diagnostic_fit_3_trips.py`), por unificar.
- Os programas de treino, de figuras e de geração de resultados **não têm teste automático** (só as funções de formatação e de acesso).

## O que fazer a seguir

1. **Perguntar ao utilizador, antes do Marco 4:**
   - se a sobreposição se aplica no treino, na inferência ou em ambos;
   - o orçamento de treino (a mesma quantidade de épocas não dá o mesmo número de passos);
   - usar para as janelas **o mesmo critério de seleção da baseline** (menor perda por ponto no `test`, limiar pelo F1 médio), para a comparação ser justa;
   - **autorização** para medir a baseline por segmento no `test` (uso novo desse conjunto), com âmbito declarado.
2. **Marco 4:** implementar o janelamento (`docs/03`), treinar J0 e J50 com L = 64, selecionar no `test` com protocolo declarado antes, e comparar com a baseline por ponto e por segmento. Depois, testar outros L.
3. **LaTeX, passagens ainda abertas** (o utilizador adiou-as):
   - as quatro taxas de sobreposição e a ablação (7.1);
   - explicabilidade, calibração e *dashboard* (resumo, objetivo 5, 4.6, 7.3);
   - o título começa por «OOI» (parece resto do template) e há texto a vermelho «human-on-the-loop»;
   - a Secção 6 está no futuro («Será usado…»);
   - o texto das subsecções 5.3 a 5.6 e 6.1 não foi relido pelo utilizador, apesar de estar a preto.
4. **Marco 5** só se o Marco 4 mostrar benefício, com unidade e largura do filtro aprovadas pelo utilizador. **Marcos 6 e 7** no fim.
5. Arrumação: testes dos programas de treino e de figuras; unificar `class_metrics`; apagar os restos do ensaio de 3 viagens e das execuções antigas, se o utilizador quiser.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. Validação e teste só com autorização explícita; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado e executável (AGENTS §10); no LaTeX, só por macros geradas. Não afirmar o que não foi medido; distinguir feito, validado e pendente.
- **Nunca `git push`** sem autorização explícita **nova** do utilizador (as autorizações anteriores foram pontuais). Commits após explicação; alterações substanciais com mensagem completa (O quê, Porquê, Como, Impacto, Validação, Pendente) e a linha de coautoria. Selecionar ficheiros explicitamente.
- No fim de cada interação que altere ficheiros: atualizar `PROGRESS.md` e `REVISION_LOG.md` (REV novo, cor nova, marcador `[REV-NNN | cor #HEX]`) e confirmar que `README.md`, `docs/` e o LaTeX não se contradizem.
- Explicar comandos e alterações antes de os executar. Pedir autorização para alterações metodológicas, execuções prolongadas e instalações.
- **Subagentes:** só com contrato fechado, regras explícitas no prompt e ficheiros distintos; nunca confiar só no relatório: rever o código, conferir à mão e correr os testes. (Nesta sessão: Sonnet para as métricas por segmento e Haiku para a contagem de navios.)
- Comunicar em português europeu; funções e variáveis em inglês.

## Preferências do utilizador observadas

- Quer um **plano** e uma explicação antes de avançar, e que as dúvidas lhe sejam colocadas **antes** de o trabalho autónomo começar.
- Prefere resultados em **imagens e tabelas** e um resumo final claro.
- Decide depressa e deixa decisões claras («está fechado», «desconsidera»): registá-las como estão, sem as reabrir.
- Quer commits **divididos por tema**, com mensagens completas, e o push só quando o autoriza.
- Quer o LaTeX sempre coerente e com valores **gerados por código**; aceitou reorganizar secções e usar preto para o que está fechado.
- Aceita valores recomendados em bloco quando vêm numa tabela com valor proposto e justificação.
