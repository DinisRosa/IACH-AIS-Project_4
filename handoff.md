# Handoff — Projeto AIS

Data: 2026-11-23. Documento para retomar o trabalho numa nova conversa.

## Como retomar (ler por esta ordem)

1. `AGENTS.md` (regras fixas; o `CLAUDE.md` manda lê-lo antes de qualquer ação).
2. Este ficheiro.
3. `PROGRESS.md` (histórico por entrada, termina em 2026-11-23an) e `REVISION_LOG.md` (REV-001 a REV-032).
4. Antes de qualquer ação: verificar `git status` e `git log` (ver «Estado atual»).

Mensagem sugerida para abrir a nova conversa: «Lê o AGENTS.md e o handoff.md e continua de onde ficámos. Qual é o ponto de situação e o próximo passo?»

## Objetivo

Segmentação de viagens AIS de pesca com uma **CNN 1D** (uma probabilidade por ponto). Ordem de trabalho:
1. Pré-processamento (concluído).
2. CNN 1D de referência sobre a viagem completa (**Marco 3, em curso**).
3. Janelamento com sobreposição e a mesma CNN sobre janelas (Marco 4; sobreposição 0 % e 50 % prioritárias).
4. Pós-processamento temporal e explicabilidade.

Dataset: 123 viagens, 1 026 279 linhas. Divisão por ID completo, seed 42, 70/15/15: treino 87 viagens (713 854 linhas), validação 18 (209 016), teste 18 (103 409). Os resultados não se apresentam como generalização para navios inéditos (a divisão é por viagem).

## Estado atual

- Marcos 1 e 2 fechados. **Marco 3: passos 1 a 5 feitos** (sequências, normalização, CNN, testes, primeira execução de treino). Passo 6 em parte (custo medido). Passo 7 (pedir revisão do Marco 3 ao utilizador) por fazer.
- **A CNN 1D está treinada** numa primeira execução (REV-032), só com o treino oficial. Resultados provisórios: ver «Primeira execução de treino».
- **94 testes a passar** (`iach-ais-venv-4/bin/python -m pytest tests/`): 15 da preparação, 60 da fase 1, 19 de checkpoints, configuração, métricas e ciclo de treino. Sintéticos, mais um teste que lê 3 viagens reais de **treino**.
- **Git:** todo o trabalho de REV-032 está **commitado localmente** (`2b5197c` código, `2a177ac` LaTeX, `e9fef3c` documentação, mais um commit final do handoff). `origin/main` está em `4ce5e53`, por isso há **commits por enviar**. Resultados (`results/`) estão no `.gitignore`.
- **Push:** o utilizador autorizou pontualmente dois pushes (feitos por mim). A regra continua: o push é do utilizador, e cada push precisa de nova autorização explícita.
- **LaTeX** (`latex/proposta_pt.tex`) compila sem erros, 8 páginas (verificado, mas o PDF desta revisão não foi inspecionado visualmente). O `scripts/watch_latex.sh` está ativo e, depois de cada compilação com sucesso, apaga os auxiliares de `latex/build/`, deixando só o PDF.
- Validação e teste oficiais **não foram abertos**. As bases limpas de validação e teste existem desde REV-015, só para preparação.

## Decisões vigentes

**Dados e preparação**
- Features da CNN: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`. `x` e `y` ficam de fora.
- **Entrada de 7 canais**, por esta ordem: as 4 características normalizadas e 3 máscaras de ausência (`speed`, `signed_turn`, `time_gap`).
- Valores em falta: nenhuma linha removida. 1.º ponto de cada viagem sem `time_gap`, `speed` e `signed_turn`; 2.º ponto só sem `signed_turn`. Preenchimento com **zero depois de normalizar**, mais máscara. Não se inventa `bearing`. Os pontos iniciais entram na perda.
- Normalizador: média e desvio-padrão populacional por característica, ignorando ausentes, **só com o treino** (ou só com o treino interno).
- Anomalias mantidas, sem limpeza IQR. `bearing` pela grelha UTM; `distanceToShore` aceite como correto.
- HMM e Wu et al. como baselines ficam fora por agora.

**Modelo e treino** (valores iniciais, **não validados**; declarados assim no LaTeX)
- CNN: Conv1D 32/64/32 (kernel 5, ReLU, padding same) e cabeça Conv1D kernel 1; logits; `BCEWithLogitsLoss` sem pesos de classe nem reamostragem; Adam. Campo recetivo **13 pontos**; 21 761 parâmetros. Uma viagem por passo (batch 1), sem janelas, sem truncar.
- Treino (aceite em REV-032, config em `configs/phase1_run1.json`): partição interna 15 % (13 de 87 viagens, por ID, seed 42, aleatória, sem estratificar); lr 1e-3 sem procura; máx. 100 épocas; paragem antecipada na perda por ponto da monitorização (paciência 10, melhor checkpoint); orçamento 15 min; limiar 0,5.

**LaTeX**
- `latex/proposta_IAHC_DINIS_ROSA.pdf` **não se altera**.
- Toda a alteração ao `.tex` leva cor com `\revtext{revNNN}`, igual à do `REVISION_LOG.md`. Texto movido mantém a cor antiga. Próximo ID livre: **REV-033** (precisa de cor nova e distinta).
- Cores já usadas no `.tex`: rev013 `#808000`, rev018 `#5C6BC0`, rev020 `#607D8B`, rev021 `#D500F9`, rev022 `#00897B`, rev023 `#0277BD`, rev024 `#6D4C41`, rev025 `#6A1B9A`, rev026 `#2E7D32`, rev027 `#AFB42B`, rev028 `#00ACC1`, rev030 `#FF6F00`, rev031 `#006064`, rev032 `#D81B60` (REV-029 `#BF360C` só marcador do registo).

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md` |
| Código da fase 1 (`src/phase1/`) | `data.py` (leitura só de treino, validação, sequências, scaler, partição interna, DataLoader), `model.py`, `training.py` (perda, otimizador, época, avaliação, `train_model`), `checks.py` (smoke test), `utils.py`, `artifacts.py` (checkpoints), `config.py`, `metrics.py` (métricas por ponto) |
| Configuração | `configs/phase1_run1.json` |
| Scripts de treino e análise | `run_phase1_training.py`, `plot_phase1_run.py`, `benchmark_training_speed.py`, `diagnostic_fit_3_trips.py`, `plot_diagnostic_3trips.py` |
| Scripts de preparação | `create_split_manifest.py`, `check_units_train.py`, `verify_trip_count.py`, `build_clean_dataset.py --split train\|validation\|test`, `count_anomalies_train.py` |
| Testes | `tests/` (`conftest.py` põe `src/` no path); fase 1: `test_sequences`, `test_point_alignment`, `test_access_policy`, `test_model_shapes`, `test_loss_and_gradients`, `test_integration_phase1`, `test_checkpoint_and_training_loop` |
| Dados (não versionados) | `data/123_fishing_trajs_clean_{train,validation,test}.parquet`; manifesto versionado `manifests/split_manifest_seed42.csv` |
| Resultados (não versionados) | `results/phase1_run1/` (checkpoint, histórico, tabelas, previsões da monitorização, scaler, divisão interna, manifesto, `figures/`), `results/diagnostic_3trips/`, `results/benchmark_speed/` |
| Documentação | `docs/00` a `docs/06` (CNN em `docs/02` e `docs/05`; janelas em `docs/03` e `docs/06`); `docs/05` indica quais funções já existem |
| Proposta | `latex/proposta_pt.tex`, `latex/references.bib`, `latex/figures/` |

## Comandos úteis (a partir da raiz do projeto)

```bash
iach-ais-venv-4/bin/python -m pytest tests/                                   # testes
iach-ais-venv-4/bin/python scripts/run_phase1_training.py configs/phase1_run1.json   # treino
iach-ais-venv-4/bin/python scripts/plot_phase1_run.py                         # figuras do treino
iach-ais-venv-4/bin/python scripts/benchmark_training_speed.py                # velocidade
```

Compilar o LaTeX à mão **sem colidir com o vigilante** (a partir de `latex/`): usar `-output-directory=build/check` (pasta ignorada pelo git), duas passagens de `pdflatex`.

## Ensaio curto (REV-027, REV-028), só treino oficial

- `scripts/diagnostic_fit_3_trips.py`: 200 épocas, lr 1e-3, seed 42; ajuste em 3 viagens (`211477000-3`, `211477000-4`, `219001039-2`) e avaliação nessas e noutras 3 (`219001125-3`, `219001149-2`, `219001522-2`); scaler só do ajuste. Cerca de 11 s.
- Resultados ilustrativos, sem valor estatístico: accuracy 95,71 % no ajuste e 93,01 % fora da amostra (maioritária 75,21 %). Fora da amostra, a navegação tem sensibilidade 0,736 e a pesca 0,994.
- Estas figuras (matrizes e linhas temporais) estão no **Anexo A** do LaTeX, como marcador de resultados. Ainda são as deste ensaio, não as da primeira execução.

## Medição de velocidade (PROGRESS 2026-11-23al)

`scripts/benchmark_training_speed.py`, CPU, 10 threads: 1 viagem (5 475 pontos) 0,013 s por época; 2 viagens (10 853) 0,040 s; maior viagem do treino (`235008380-3`, 45 251 pontos) 0,151 s. Cerca de 2,4 a 3,7 µs por ponto em treino e 1,0 a 1,6 µs em avaliação. Pico de memória do processo cerca de 822 MB. O custo cresce com os **pontos**, não com as viagens.

## Primeira execução de treino (REV-032), só treino oficial

- Base de treino validada (87 viagens, 713 854 pontos; ordenação e NaN esperados). 74 viagens de ajuste (637 422 pontos) e 13 de monitorização (76 432 pontos); scaler só do ajuste.
- Parou por paragem antecipada após **16 épocas, 39,4 s** (cerca de 2,3 s por época); melhor época **6** (perda de monitorização 0,1398).
- Accuracy: **ajuste 92,15 %**, **monitorização 95,00 %** (maioritária 74,46 %). Monitorização: navegação sensibilidade 0,875 e precisão 0,925; pesca sensibilidade 0,976 e precisão 0,958.
- Por viagem de monitorização: de 69,6 % (`220006000-3`, 901 pontos) a 99,2 % (`219005956-2`). `220006000-3` e `219005909-1` não superam a classe maioritária; `219001039-2` tem 81,6 % e sensibilidade de navegação 0,59.
- **Cuidados:** a monitorização são 13 viagens do treino, **não a validação oficial**. A perda de monitorização oscila e ainda descia nas épocas 15 e 16, por isso a paragem pode ter sido cedo e o «melhor» modelo pode ser um mínimo por acaso. A accuracy no ajuste é inferior à da monitorização (possível subajuste; campo recetivo de só 13 pontos; ou monitorização mais fácil por acaso). Os dados não distinguem estas hipóteses.
- Observações **visuais, não quantificadas**: blocos longos de navegação (sobretudo no fim das viagens) previstos como pesca; pesca fragmentada em duas viagens. Medir com código antes de usar como evidência.

## O que falhou ou exigiu correção

- Dois testes do agente da CNN falharam no desenvolvimento e foram corrigidos (ordem da verificação de forma no smoke test; teste de ausência de sigmoide).
- `torch.__version__` impedia carregar o checkpoint com `weights_only=True`; corrigido com `str()`.
- LaTeX: `\mathbb` falhou (falta `amssymb`, usado `\mathbf{R}`); quatro parágrafos movidos começavam com minúscula; nome de script errado no texto; frases «ainda não houve treino» ficaram falsas e foram corrigidas em REV-027 e REV-032.
- Script das figuras gravava `previsto.png` por engano (variável do ciclo sobrepunha `name`); corrigido. Uma coluna enganadora na projeção de custo foi corrigida antes de ser apresentada.
- **Corrida de compilação:** o vigilante e compilações manuais em `latex/build/` corromperam o `.aux`. Resolvido compilando à mão em `build/check/` e fazendo o vigilante limpar o `build/`.
- Smoke test estrito: exige gradiente não nulo em todos os tensores; pode ter de ser relaxado.
- `class_metrics` está duplicada (`phase1/metrics.py` e `scripts/diagnostic_fit_3_trips.py`), por unificar.
- Os scripts (`run_phase1_training`, `diagnostic_fit_3_trips`, `plot_*`, `benchmark`) **não têm teste automático**.

## O que fazer a seguir

**Decisão imediata do utilizador:** o critério de paragem pode ter parado cedo. Repetir com paciência maior (por exemplo 30), ou outro lr? Repetir custa cerca de 40 s a 2 min. Qualquer alteração do critério ou do modelo é uma escolha metodológica a aprovar. Outras direções possíveis (também a aprovar, nenhuma decidida): mais contexto (kernels ou dilatação), pesos de classe (a política atual é sem eles), mais capacidade.

Depois:
1. Push dos commits locais, se o utilizador o autorizar (ou fazê-lo ele próprio).
2. Medir com código os tipos de erro (blocos de navegação prevista como pesca, fragmentação, desfasamento nas fronteiras).
3. Passo 6 do Marco 3: registar as métricas internas de referência da execução final; passo 7: pedir revisão do Marco 3.
4. Testes automáticos dos scripts; implementar o que falta de `docs/05` (segmentos e métricas por segmento, inferência como módulo, congelamento de execução).
5. Substituir as figuras do Anexo A pelas da primeira execução (decisão do utilizador) e rever a paginação das figuras de largura total.
6. Marco 4: janelamento com sobreposição (0 % e 50 %), mesma CNN sobre janelas.
7. Só mais tarde, e só com autorização explícita, validação oficial (seleção formal) e teste (avaliação final).

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. Validação e teste só com autorização explícita; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado e executável (AGENTS §10). Não afirmar resultados que não foram medidos; distinguir feito, validado e pendente.
- Nunca `git push` sem autorização explícita **nova** do utilizador. Commits locais após explicação; alterações substanciais com mensagem completa (O quê, Porquê, Como, Impacto, Validação, Pendente) e a linha de coautoria da sessão. Selecionar ficheiros explicitamente.
- No fim de cada interação que altere ficheiros, atualizar `PROGRESS.md` e `REVISION_LOG.md` (REV novo, cor nova, marcador `[REV-NNN | cor #HEX]`) e confirmar que `README.md`, `docs/` e o LaTeX não se contradizem.
- Explicar comandos e alterações antes de os executar. Pedir autorização para alterações metodológicas, execuções prolongadas fora do orçamento e instalações.
- Não confiar só no relatório dos subagentes: rever o código e correr os testes. Nesta fase usou-se Sonnet para `data.py` e Haiku para o modelo e o treino.
- Comunicar em português europeu; funções e variáveis em inglês.

## Preferências do utilizador observadas

- Quer updates à medida que o trabalho avança e um resumo final claro.
- Prefere ver resultados em **imagens e tabelas** em vez de texto corrido.
- Quer que as dúvidas lhe sejam colocadas **antes** de começar a trabalhar autonomamente.
- Quer o LaTeX atualizado em cada passo, com cores por revisão; aceitou reorganizar secções e mover figuras grandes para anexos.
- Aceitou valores recomendados em bloco quando apresentados numa tabela de decisão com valor proposto e justificação.
