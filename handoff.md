# Handoff — Projeto AIS

Data: 2026-11-23 (atualizado no fim da sessão do código da fase 1). Ler primeiro `AGENTS.md` (regras fixas), depois `PROGRESS.md` e `REVISION_LOG.md` (REV-001 a REV-030).

## Objetivo

Segmentação de viagens AIS de pesca com uma **CNN 1D** (uma probabilidade por ponto). Ordem de trabalho:
1. Pré-processamento (concluído).
2. CNN 1D de referência sobre a viagem completa (**Marco 3, em curso**).
3. Janelamento com sobreposição e a mesma CNN sobre janelas (Marco 4).
4. Pós-processamento temporal e explicabilidade.

Dataset: 123 viagens, 1 026 279 linhas. Divisão por ID completo, seed 42, 70/15/15 (87/18/18 viagens).

## Estado atual

- Marcos 1 e 2 fechados. **Marco 3: passos 1 a 4 feitos** (sequências, normalização, CNN, testes). Passos 5 a 7 por fazer.
- **75 testes a passar** (`iach-ais-venv-4/bin/python -m pytest tests/`): 15 anteriores e 60 novos. Só dados sintéticos, mais um teste que lê 3 viagens reais de **treino**.
- Código novo em `src/phase1/`: `data.py`, `model.py`, `training.py`, `checks.py`, `utils.py`. Ainda **não existem**: `config.py`/JSON de configuração, checkpoints (`artifacts.py`), inferência dedicada, `segments.py`, `metrics.py` por segmento, `run_phase1.py`, `reporting.py`.
- Foi feito **só um ensaio curto** (não o treino completo): ver «Ensaio curto» abaixo. Validação e teste oficiais **não foram abertos** (as bases limpas de validação e teste existem desde REV-015, só para preparação).
- Proposta LaTeX compila (7 páginas) e já tem: secção 5 «Especificação da CNN 1D de referência» (com a Figura 2, desenho da CNN) e a subsecção 7.4 «Ensaio preliminar» com duas figuras marcadoras de resultados.
- **Commits locais** desta sessão: `fa391a5` (código), `7fe7693` (LaTeX), `11a0d97` (documentação), `b4abd65` (registo). **Nenhum push foi feito por mim**: o push é do utilizador (confirmar com `git status`, o `main` está à frente de `origin/main`).
- `handoff.md` (este ficheiro) está por commitar até o utilizador pedir.

## Decisões vigentes (resumo)

- **Entrada da CNN: 7 canais**, nesta ordem: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore` (normalizados) e 3 máscaras de ausência (`speed`, `signed_turn`, `time_gap`). `x` e `y` ficam de fora. (decisão do utilizador, REV-024)
- **Valores em falta:** nenhuma linha removida. 1.º ponto de cada viagem sem `time_gap`, `speed` e `signed_turn`; 2.º ponto só sem `signed_turn`. Preenchimento com **zero depois de normalizar** (decisão do utilizador, REV-024) e máscara. Os pontos iniciais entram na perda (REV-022).
- **Normalizador:** média e desvio-padrão populacional por característica, só valores observados, só treino (ou treino interno, se houver partição interna).
- **Anomalias** mantidas, sem limpeza IQR (REV-012, REV-019). `bearing` pela grelha UTM; `distanceToShore` aceite (REV-011).
- **CNN:** Conv1D 32/64/32 com kernel 5 (ReLU, padding same) e cabeça Conv1D de kernel 1; logits; `BCEWithLogitsLoss` sem pesos de classe; Adam. Campo recetivo de **13 pontos**. 21 761 parâmetros. Uma viagem por passo (batch 1), sem janelas, sem truncar.
- **Valores NÃO validados** (declarados assim no LaTeX): 32/64/32, kernel 5, Adam, **lr 1e-3** (só valor por omissão), 200 épocas do ensaio. Vêm da arquitetura inicial de `docs/02`, não de experiências.
- `latex/proposta_IAHC_DINIS_ROSA.pdf` **não se altera**. HMM e Wu et al. como baselines ficam fora por agora.
- Toda a alteração ao `.tex` leva cor com `\revtext{revNNN}`, igual à do `REVISION_LOG.md` (rev013 a rev030 definidas no preâmbulo; as cores estão no registo).

## Ficheiros principais

- Regras e registo: `AGENTS.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`.
- Código da fase 1: `src/phase1/` (ver acima). Testes: `tests/test_sequences.py`, `test_point_alignment.py`, `test_access_policy.py`, `test_model_shapes.py`, `test_loss_and_gradients.py`, `test_integration_phase1.py`, `conftest.py` (põe `src/` no path), mais os dois testes da preparação.
- Scripts: `scripts/create_split_manifest.py`, `check_units_train.py`, `verify_trip_count.py`, `build_clean_dataset.py --split train|validation|test`, `count_anomalies_train.py`, **`diagnostic_fit_3_trips.py`** (ensaio curto) e **`plot_diagnostic_3trips.py`** (figuras e tabelas). Os dois últimos **não têm teste automático**.
- Resultados do ensaio (não versionados): `results/diagnostic_3trips/` (`predictions.csv`, `tables.json`, `run_manifest.json`, `training_history.csv`, `figures/`).
- Docs: `docs/00` a `docs/06` (CNN em `docs/02`, `docs/05`, janelas em `docs/03`, `docs/06`). `docs/05` indica quais funções já existem.
- Proposta: `latex/proposta_pt.tex`, `latex/references.bib`, imagens em `latex/figures/`.

## Ensaio curto (REV-027, REV-028), só treino oficial

- `scripts/diagnostic_fit_3_trips.py`: 200 épocas (600 passos de Adam), lr 1e-3, seed 42, limiar 0,5, CPU, cerca de 11 s. Ajuste em 3 viagens (`211477000-3`, `211477000-4`, `219001039-2`; 17 844 pontos) e avaliação nessas e em outras 3 (`219001125-3`, `219001149-2`, `219001522-2`; 35 290 pontos). Scaler ajustado só com as 3 de ajuste.
- Resultados (dos artefactos, ilustrativos, **sem valor estatístico, não é validação oficial**): accuracy 95,71 % no ajuste e **93,01 %** fora da amostra (maioritária 75,21 %). Fora da amostra a navegação tem sensibilidade 0,736 (2 310 erros, muitos previstos como pesca) e a pesca 0,994. Por viagem: 86,15 %, 98,28 % e 80,17 %.
- Observação **não quantificada**, só da leitura visual das figuras: nas viagens mais difíceis os erros parecem formar blocos junto às fronteiras do segmento de pesca (pesca prevista começa antes e acaba depois da real). Medir com código antes de a usar como evidência.

## O que falhou ou exigiu correção nesta sessão

- Dois testes do agente B falharam no desenvolvimento e foram corrigidos (ordem da verificação de forma no smoke test; teste de ausência de sigmoide).
- `\mathbb` falhou no LaTeX (falta `amssymb`): usado `\mathbf{R}`. Quatro parágrafos movidos em REV-023 começavam com minúscula: corrigido.
- Bug no script das figuras: uma variável do ciclo sobrepunha o parâmetro `name` e gravava `previsto.png`; corrigido.
- Nome errado do script no `.tex` (`3_trips` em vez de `3trips`): corrigido.
- **Corrida de compilação:** o `watch_latex.sh` (se estiver ativo) e compilações manuais em `latex/build/` corrompem o `.aux`. Compilar manualmente em `latex/build/check/` com `-output-directory=build/check` (ignorada pelo git). Se o PDF de `build/` ficar corrompido: apagar `latex/build/proposta_pt.aux` e gravar o `.tex`.
- Smoke test estrito: exige gradiente não nulo em todos os tensores; pode ter de ser relaxado com dados reais.

## O que fazer a seguir

**Decisões em aberto do utilizador (antes do treino a sério):** proporção da partição interna de monitorização (por ID completo, dentro do treino), taxa de aprendizagem, número de épocas, critério de paragem e orçamento de tempo. Não correr treinos longos sem elas.

Marco 3:
5. Treino de ensaio só com o treino oficial, com partição interna por ID **antes** de ajustar o normalizador.
6. Medir o custo em CPU (tempo e memória das 87 viagens de treino; a maior viagem do ensaio tem 23 151 pontos) e registar métricas internas de referência.
7. Pedir revisão do Marco 3.

Antes ou durante:
- Medir com código o desfasamento nas fronteiras do segmento de pesca (verificar a observação das figuras).
- Escrever testes para os dois scripts de ensaio.
- Implementar o que falta da API de `docs/05`: configuração JSON, checkpoints, inferência, segmentos e métricas por segmento, `run_phase1`.
- Substituir as figuras marcadoras do LaTeX pelos resultados reais e rever a paginação (a Figura 4 ficou sozinha numa página).
- Decidir se `latex/figures/` e figuras entram definitivamente no repositório.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. Validação e teste só com autorização explícita para análise ou seleção. As bases limpas de validação e teste só foram usadas para preparação.
- Nunca `git push` sem autorização explícita do utilizador. Commits pequenos locais autorizados após explicação; alterações substanciais com mensagem completa (O quê/Porquê/Como/Impacto/Validação/Pendente) e trailer de coautoria da sessão.
- Todo o número usado como evidência vem de código versionado e executável (AGENTS §10). Não afirmar resultados que não foram medidos.
- Comunicar em português europeu. Pedir autorização para alterações metodológicas e para o primeiro treino prolongado.
- No fim de cada interação com alterações, atualizar `PROGRESS.md` e `REVISION_LOG.md`.
- Delegação a subagentes: Sonnet para `data.py`, Haiku para modelo e treino nesta sessão; rever sempre a integração e correr os testes, não aceitar só o relatório deles.
