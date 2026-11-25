# Handoff — Projeto AIS

**Data e hora desta atualização:** 21:23 WET de 2026-11-25 (UTC+00:00). Reescrito de raiz em REV-061 (20:47 WET), depois do Marco 5 e da Secção de conclusões; atualizado em REV-062 (passagens adiadas da proposta) e REV-063 (tabela da releitura em `docs/05_releitura_proposta.md`). Versões anteriores: REV-044, REV-045, REV-046 a REV-055. Todas as horas deste ficheiro estão em WET (em novembro igual a UTC), lidas com `date`.

### Última validação (registada neste handoff)

| Verificação | Resultado | Data e hora (WET) |
|---|---|---|
| Testes (`pytest tests/`) | 243 passaram | 2026-11-25 21:22 |
| LaTeX (`pdflatex` + `bibtex` + 2 × `pdflatex`, em `latex/build/check`) | 16 páginas; 0 erros; 0 referências indefinidas | 2026-11-25 21:22 |
| Git | antes deste commit, `main` tinha 1 commit à frente de `origin/main` (`c0af577`, REV-062); este commit e esse são enviados a pedido do utilizador. Confirmar com `git status -sb` e `git log origin/main..HEAD` | 2026-11-25 21:22 |
| Pós-processamento v1 (13 pontos) no `validation` | execução única, protocolo `posproc_validation_v1`; **histórico interno, fora da proposta** | 2026-11-25 ~19:45 |
| Análise dos buracos e efeito das janelas no `test` | `postproc_window_analysis` e `postproc_test_eval` no `access_log.jsonl` | 2026-11-25 ~20:00 a 20:07 |
| Pós-processamento v2 (301 pontos) no `validation` | execução única, protocolo `posproc_validation_v2`; verificação independente 19/19 | 2026-11-25 ~20:30 |

Quem retomar deve repetir estas verificações e comparar com as horas acima: o que tiver mudado depois **não foi** validado por este handoff.

### Cronologia dos últimos commits (hora local WET)

| Commit | Data e hora | Assunto |
|---|---|---|
| `c0af577` | 2026-11-25 21:14 | Alinha as passagens adiadas da proposta com o trabalho feito e ignora docs/bibliografia (REV-062) |
| `1ab2376` | 2026-11-25 20:48 | Reescreve o handoff depois do Marco 5 e das conclusões (REV-061) |
| `c7478dc` | 2026-11-25 20:39 | Secção de conclusões na proposta: RQ1, RQ2 e porque fica a RQ3 sem resposta (REV-060) |
| `fccd79e` | 2026-11-25 20:34 | Documenta o pós-processamento v2: docs/04, PROGRESS, registo, README e handoff (REV-059) |
| `3a297a5` | 2026-11-25 20:33 | Resultados do pós-processamento v2 (301 pontos) na proposta (REV-059) |
| `e46ec58` | 2026-11-25 20:29 | Protocolo v2 (301 pontos) e programa com uma execução por versão, antes de medir (REV-059) |
| `84e0b54` | 2026-11-25 20:12 | docs/04: v1 como histórico interno, análise dos buracos, efeito no test e plano da v2 (REV-058) |
| `0299d46` | 2026-11-25 20:07 | Aplica a janela de 301 pontos às previsões do test e regista o efeito (REV-058) |
| `16f9e21` | 2026-11-25 20:00 | Análise dos buracos no test para escolher a nova janela (REV-058) |
| `10dc183` | 2026-11-25 19:55 | Exatidão por viagem antes e depois do pós-processamento (figura de diagnóstico) |
| `ab83a5f` | 2026-11-25 19:51 | Resultados do pós-processamento v1 no validation na proposta (REV-057; depois substituídos pela v2) |
| `afe1c64` | 2026-11-25 19:45 | Programa do pós-processamento no validation e testes, antes da execução (REV-057) |
| `3359890` | 2026-11-25 19:37 | Protocolo do pós-processamento v1, declarado antes de medir (REV-057) |
| `96b09c5` | 2026-11-25 19:30 | Esclarece o uso das previsões guardadas do validation (REV-056) |
| `c1cdcfe` | 2026-11-25 19:13 | Pós-processamento: método na proposta, filtro e plano do Marco 5 (REV-056) |
| `cee2e58` | 2026-11-24 00:44 | Atualiza a regra do push: só a pedido explícito do utilizador (REV-055) |

Há ainda dois commits de correção de hora (`076aa09`, `4ecaf43`). O commit deste handoff vem a seguir e não está na tabela.

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas. O `CLAUDE.md` manda lê-lo antes de qualquer ação.
2. Este ficheiro.
3. `docs/04_pos_processamento.md` (Marco 5, incluindo o histórico interno da v1) e, se for preciso, `docs/00` a `docs/03`.
4. `PROGRESS.md` (estado vivo no topo; histórico termina em 2026-11-25i) e `REVISION_LOG.md` (REV-001 a REV-063).
6. **`docs/05_releitura_proposta.md`**: tabela das passagens da proposta ainda por corrigir (A a H), com a recomendação para cada uma.
5. Antes de qualquer ação: `git status`, `git log` e `iach-ais-venv-4/bin/python -m pytest tests/` (243 testes a passar).

Mensagem sugerida para abrir a nova sessão: «Lê o AGENTS.md e o handoff.md e continua de onde ficámos. Qual é o ponto de situação e o próximo passo?»

## Objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma **CNN 1D**:
1. Pré-processamento (feito).
2. CNN de referência sobre a viagem completa (feita, Marco 3).
3. A mesma CNN sobre janelas: J0 (0 %) e J50 (50 %), L = 64 (feito, Marco 4; RQ1).
4. Pós-processamento temporal (feito, Marco 5; RQ2).
5. Medição final no `validation` (feita, Marcos 6 e 7).
6. **Conclusões** (Secção 11 da proposta; RQ3 sem resposta, com as razões).

Dataset: 123 viagens, 1 026 279 linhas. Divisão por viagem, seed 42, 70/15/15: treino 87 (713 854 linhas), validação 18 (209 016), teste 18 (103 409). Fonte: Zenodo (Song Wu, CC BY 4.0).

## O que se fez nesta sessão (2026-11-25)

- **Arranque:** leitura completa; ponto de situação. A pedido do utilizador, retiradas as menções ao «OOI» (sem REV próprio).
- **Método do pós-processamento na proposta (REV-056):** nova Secção 10 com o filtro gaussiano (média pesada das probabilidades, depois o limiar 0,65), figura e plano em `docs/04`. Esclarecido com o utilizador: o pós-processamento usa as previsões **já guardadas** do `validation`, sem reabrir os dados nem correr a CNN; só as anotações contam como reutilização.
- **v1, 13 pontos (REV-057):** protocolo commitado antes; programa gerado com revisão da Abacus e testes de um subagente (encontraram um erro em viagens curtas, corrigido antes de executar); execução única; verificação independente 19/19. Resultado fraco: segmentos de pesca previstos 486 → 255, exatidão 94,4 % → 94,5 %.
- **Decisão do utilizador:** refazer com outra janela, tratando a v1 como se não tivesse existido **na proposta** (fica registada em `docs/04` §5, `PROGRESS.md` e `REVISION_LOG.md`).
- **Análise no `test` (REV-058), com autorizações próprias:** comprimento dos «buracos» (blocos de erro): média 14,8, mediana 5, p90 37 pontos. Com o limiar 0,65 o filtro é assimétrico: com 13 pontos só removia navegação isolada de 1 ponto. A janela de 301 aplicada ao `test`: exatidão 94,7 % → 95,7 %, segmentos de pesca 358 → 32. O utilizador escolheu 301.
- **v2, 301 pontos (REV-059):** protocolo v2 commitado antes; programa, testes e verificação gerados pela Abacus e revistos; execução única. Resultado no `validation`: ver «Estado atual». Secção 10 atualizada (números, figuras e os parágrafos que dependiam dos 13 pontos).
- **Conclusões (REV-060):** Secção 11 com RQ1, RQ2, RQ3 (sem resposta, quatro razões e o desenho fatorial necessário), critérios de sucesso e trabalho futuro.
- **Este handoff (REV-061)** e push a pedido do utilizador.
- **Passagens adiadas da proposta (REV-062):** «*human-on-the-loop*» sem vermelho; explicabilidade, calibração e *dashboard* como «previstos, não concluídos nesta fase» (resumo, objetivo 5, 4.6, 7.3, trabalho futuro); objetivo 3 «aplicado ao melhor dos modelos testados»; caixa «Explicabilidade / decisão humana» a tracejado na figura; contribuições reais; 7.1 sem o estudo de ablação. «(Kaggle)» mantido: os PDFs de `docs/bibliografia/` (fora do git) não referem o Zenodo.
- **Releitura (REV-063):** tabela A a H em `docs/05_releitura_proposta.md`, por aplicar.

## Estado atual

| Marco | Estado |
|---|---|
| 1 Ambiente e divisão | Fechado |
| 2 Preparação auditável | Fechado |
| 3 CNN de referência (viagem completa) | Fechado (REV-041) |
| 4 Janelamento (J0 e J50) | Feito (REV-046, REV-047) |
| 5 Pós-processamento | **Feito (REV-056 a REV-059)**: v2, janela gaussiana de 301 pontos |
| 6 e 7 Medição final no `validation` | Feito (REV-053), só a referência |
| Conclusões na proposta | **Feito (REV-060)** |

- **Referência:** época 162, limiar 0,65 (`results/baseline_frozen/`). `test` 94,7 %; `validation` 94,4 % (11 662 erros).
- **J0 e J50:** épocas 8 e 4, limiares 0,60 e 0,75; `test` 93,4 % e 93,7 %; J50 fragmenta menos. Não medidas no `validation`.
- **Pós-processamento v2 no `validation`** (`results/postproc_validation_v2/`): exatidão 94,4 % → 94,8 % (11 662 → 10 790 erros); segmentos de pesca previstos 486 → 32 (reais 18), navegação 502 → 49 (reais 35); F1 de segmentos de pesca 0,028 → 0,600 e de navegação 0,119 → 0,786; 4 100 pontos mudam (2 486 corrigidos, 1 614 estragados); melhoram 11 viagens e pioram 7; a pior, `219020187-4`, cai de 40,4 % para 19,7 %.
- **Respostas:** RQ1 — o janelamento não supera a referência; J50 reduz a fragmentação face a J0 (só no `test`). RQ2 — sim, o filtro reduz muito a fragmentação e a exatidão sobe um pouco. RQ3 — sem resposta (só a referência foi filtrada; não há conjunto limpo; modelos pouco comparáveis; efeitos sobrepostos).
- **Conjuntos reservados (`results/access_log.jsonl`):** `test` aberto para seleção da baseline, das janelas, duas leituras de diagnóstico, análise dos buracos e efeito das janelas no pós-processamento. **As anotações do `validation` foram usadas três vezes:** medição final (REV-053), v1 e v2, sempre sem nova passagem pela CNN nas duas últimas. A decisão de mudar para a v2 foi tomada depois de ver a v1.
- **Testes:** 243, sintéticos (mais um que lê 3 viagens de treino).
- **LaTeX** (`latex/proposta_pt.tex`): 15 páginas. Secções 8 (resultados), 9 (medição final), 10 (pós-processamento, v2), 11 (conclusões) e Anexo A. O utilizador disse que o número de páginas se trata depois.
- **Git:** remoto `origin` (`git@github.com:DinisRosa/IACH-AIS-Project_4.git`), branch `main`. Confirmar com `git status -sb`.

## Decisões vigentes

**Dados e preparação**
- Características: `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`; 7 canais (4 normalizadas e 3 máscaras). Valores em falta a zero depois de normalizar, mais máscara. Anomalias mantidas. Divisão por viagem; questão dos navios partilhados desconsiderada pelo utilizador.

**Modelos**
- CNN Conv1D 32/64/32 (kernel 5), cabeça de kernel 1, logits, `BCEWithLogitsLoss`, Adam lr 1e-3; campo recetivo 13; 21 761 parâmetros. J0/J50: L = 64, lote de 32 janelas, mesma sobreposição no treino e na inferência, média das janelas para reconstruir.

**Conjuntos reservados**
- `test` seleciona, `validation` mede (REV-036). Só com autorização escrita em `configs/authorizations/`, protocolo antes e registo de acesso. **Não voltar a correr** `select_on_test`, `select_windows_on_test`, `final_validation` nem `postproc_validation` (as duas versões já executaram; o programa recusa).

**Pós-processamento (REV-056 a REV-059)**
- Filtro gaussiano sobre `p_fishing`, σ = tamanho/6, limiar 0,65 depois do filtro, pesos reajustados nas pontas, nunca atravessa viagens. **v2: 301 pontos** (escolhida no `test`); só a referência. A v1 (13 pontos) **não entra na proposta** por decisão do utilizador; está registada em `docs/04` §5.

**Âmbito e LaTeX**
- HMM e Wu et al. não são comparações. Explicabilidade, calibração e *dashboard* fora do mínimo atual.
- `latex/proposta_IAHC_DINIS_ROSA.pdf` não se altera. Toda a alteração ao `.tex` leva `\revtext{revNNN}` com a cor do `REVISION_LOG.md`. **Próximo ID livre: REV-064.** Confirmar no `REVISION_LOG.md` que uma cor nova não foi usada.
- Cores no `.tex` em uso: rev021 `#D500F9`, rev023 `#0277BD`, rev040 `#7F0000`, rev041 `#FF1744`, rev042 `#0A3D62`, rev046 `#00B0FF`, rev047 `#4A148C`, rev048 `#1B5E20`, rev052 `#880E4F`, rev053 `#0D47A1`, rev056 `#D84315`, rev057 `#B8860B`, rev059 `#8B008B`, rev060 `#C71585`, rev062 `#4682B4`. Só marcadores Markdown, entre outros: REV-054 `#00BFA5`, REV-055 `#F06292`, REV-058 `#546E7A`, REV-061 `#26C6DA`, REV-063 `#FF7043`.

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, este `handoff.md` |
| Documentação | `docs/00` a `docs/03`, **`docs/04_pos_processamento.md`** (Marco 5; §5 com o histórico interno da v1), **`docs/05_releitura_proposta.md`** (passagens da proposta por corrigir) |
| Biblioteca (`src/ais/phase1/`) | `data.py`, `model.py`, `training.py`, `checks.py`, `utils.py`, `artifacts.py`, `config.py`, `metrics.py`, `inference.py`, `reserved.py`, `selection.py`, `segments.py`, `windows.py`, **`postprocessing.py`** (filtro, buracos, `max_removable_island`) |
| Programas do pós-processamento | `postproc_validation.py --version v1\|v2` (já executados), `build_postproc_results.py`, `verify_postproc_independent.py [--size N]` (escrito pela Abacus), `plot_postprocessing_kernel.py`, `analyze_error_runs.py --split test\|train`, `eval_postproc_test.py` |
| Outros programas | preparação, baseline, janelas, diagnóstico e medição final: ver `README.md` |
| Configuração | `postproc_protocol.json` (v1), `postproc_protocol_v2.json`; autorizações `test_postproc_window.json`, `test_postproc_eval.json`; os anteriores (`selection_protocol*.json`, `validation_final.json`…) |
| Testes | `tests/` (243); novos: `test_postprocessing.py`, `test_postproc_validation.py` |
| Resultados (não versionados) | `results/postproc_validation/` (v1), `results/postproc_validation_v2/` (v2, com `verificacao_independente.json`), `results/postproc_window_analysis/` (buracos e `test_eval.json`), e os anteriores (`baseline_frozen/`, `windows_*`, `final_validation/`, `access_log.jsonl`) |
| Proposta | `latex/proposta_pt.tex`; macros geradas em `latex/generated/` (`resultados_posproc.tex` é da v2); figuras `posproc_janela.png`, `posproc_resultados.png`, `posproc_viagem.png` (v2) e `posproc_viagens.png` (diagnóstico, fora da proposta) |

## Comandos úteis (a partir da raiz do projeto)

```bash
iach-ais-venv-4/bin/python -m pytest tests/                                     # testes
iach-ais-venv-4/bin/python -m ais.cli.build_postproc_results                    # macros e figuras da Secção 10 (v2; não volta a medir)
iach-ais-venv-4/bin/python -m ais.cli.plot_postprocessing_kernel                # figura da janela (sintética)
iach-ais-venv-4/bin/python -m ais.cli.verify_postproc_independent --size 301 results/final_validation/predictions_validation.csv
iach-ais-venv-4/bin/python -m ais.cli.build_final_results                       # números da baseline
iach-ais-venv-4/bin/python -m ais.cli.build_window_results                      # números de J0 e J50
iach-ais-venv-4/bin/python -m ais.cli.build_validation_results                  # Secção 9
```

Compilar o LaTeX à mão (a partir de `latex/`), sem colidir com o vigilante: `pdflatex -interaction=nonstopmode -output-directory=build/check proposta_pt.tex`, depois `bibtex` dentro de `build/check` com `BIBINPUTS=../..` e `BSTINPUTS=../..`, e mais duas passagens de `pdflatex`.

**Delegação na Abacus (skill `delegate-terminal`):** o script `delegate.sh` da skill não existe na pasta do plugin; usou-se `abacusai -p "<tarefa>" < contexto.txt` a partir do scratchpad (para não lhe dar acesso ao projeto), só com código, contratos e descrições, **nunca dados**. O utilizador pediu para não usar o OpenCode e para dar o máximo de trabalho à Abacus.

## O que falhou ou exigiu correção (nesta sessão)

- `np.convolve(mode="same")` devolve `max(n, tamanho)` valores: em viagens mais curtas do que a janela o filtro rebentaria. Encontrado pelo subagente e pela Abacus antes da execução; `smooth_trip` passou a um ciclo explícito.
- A primeira versão registava o início da execução antes de gravar: uma falha a meio gastaria a execução única. Corrigido: cálculo em memória, escrita numa pasta temporária, registo só no fim.
- Testes gerados com dados sintéticos irrealistas (segmento real mais curto do que o mínimo real; dois protocolos a reescrever o mesmo CSV): o erro era do teste, não do código.
- Horas escritas à frente do relógio em duas entradas do `PROGRESS.md`/`REVISION_LOG.md`; corrigidas em commits próprios. **Usar sempre `date`.**
- Um `}` a mais ao substituir parágrafos coloridos no `.tex` partiu a compilação; corrigido. Ao trocar texto dentro de um `\revtext{...}{...}`, conferir as chavetas.
- Dos anteriores: não correr testes ou subagentes durante treinos (abrandam muito); `«»` e `%` nu em `\texorpdfstring` partem o LaTeX; `class_metrics` duplicada; programas de treino e de figuras sem testes.

## O que fazer a seguir

1. [REV-064 | cor #33691E] (2026-11-25 21:59 WET) **Reescrever a proposta** segundo `docs/06_plano_reescrita.md`, depois de o utilizador decidir D1 a D8 (inclui ficheiro novo ou o mesmo, e a versão de segurança no commit `7d60861`); a reescrita é a REV-065 e absorve a tabela A a H de `docs/05`. Próximo ID livre: **REV-065** (substitui a indicação de REV-064 mais acima).
   - [REV-065 | cor #01579B] (2026-11-25 22:44 WET) **Em curso:** D1 a D8 aceites. O documento ativo é `latex/relatorio_pt.tex` (secções 4 a 6, anexo e limitações escritas, 7 páginas; 247 testes). `proposta_pt.tex` não se altera (etiqueta local `proposta-pt-v1`). À espera da revisão do utilizador para escrever o resto (`docs/06` §6 e §8). Próximo ID livre: **REV-066**.
2. **Versão final sem cores** só quando o utilizador o pedir.
3. **Arrumação técnica:** testes dos programas de treino e de figuras; unificar `class_metrics`; apagar restos do ensaio de 3 viagens e execuções antigas, se o utilizador quiser.
4. **Dúvidas de dados (limitações):** CRS (hipótese WGS84), proveniência das anotações, cálculo de `distanceToShore`.
5. **Push:** só a pedido do utilizador; quando pede, enviar sem mais perguntas.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. `test` e `validation` só com autorização explícita do utilizador, registada em `configs/authorizations/`; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado (AGENTS §10); no LaTeX, só por macros geradas.
- **Push (REV-055):** se o utilizador pede, o agente faz push sem pedir confirmação; por iniciativa própria, nunca. Sem `--force`.
- Commits divididos por tema, com mensagem completa (O quê, Porquê, Como, Impacto, Validação, Pendente) e a linha de coautoria.
- No fim de cada interação que altere ficheiros: atualizar `PROGRESS.md` e `REVISION_LOG.md` (REV novo e cor nova) e confirmar que `README.md`, `docs/` e o LaTeX não se contradizem.
- **Integridade:** a v1 do pós-processamento não aparece na proposta por decisão do utilizador, mas **não se apaga** dos registos internos nem se escreve na proposta nada que a contradiga (por exemplo, «fixado antes de qualquer medição»).
- Subagentes e Abacus: contrato fechado, regras explícitas, ficheiros distintos, nunca dados reservados; rever e testar tudo o que devolvem.
- Comunicar em português europeu; funções e variáveis em inglês.

## Preferências do utilizador observadas

- Quer um **plano** antes de avançar e espera pelo seu sinal; depois dá autonomia, incluindo subagentes e a Abacus (prefere dar-lhe o máximo de trabalho).
- Prefere resultados em **imagens e tabelas** e explicações de porquê (por exemplo, porque é que um valor quase não mudou).
- Decide depressa e deixa decisões claras; registá-las como estão.
- Quer o LaTeX coerente, com valores gerados por código e a cor da revisão em todo o texto novo; o tamanho trata-se no fim.
- Quer commits divididos por tema e mensagens explícitas; push só quando pede.
