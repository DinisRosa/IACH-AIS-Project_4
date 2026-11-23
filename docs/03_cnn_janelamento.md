# 03 — CNN 1D com janelamento e sobreposição (Marco 4)

[REV-033 | cor #3E2723] Documento fundido a partir de `03_cnn_janelamento_sobreposicao` (workflow) e `06_funcoes_documentos_cnn_janelamento_sobreposicao` (contratos). [REV-046 | cor #00B0FF] **O janelamento está implementado** em `src/ais/phase1/windows.py` e as duas variantes (J0 e J50) foram treinadas e selecionadas; o estado e os resultados estão em `PROGRESS.md` e, por código, em `results/windows_final/final_results_windows.json`. Este documento descreve as decisões e os contratos tal como foram implementados.

## 1. Objetivo

Medir o efeito de dividir as viagens em janelas e de adicionar sobreposição, comparando com a baseline de `02` (RQ1). Reutiliza a divisão por ID, as características, as unidades, o normalizador e a CNN da baseline, para alterar uma coisa de cada vez. Sem pós-processamento: a **média das previsões sobrepostas é reconstrução**, não suavização, e fica separada de um futuro ramo de pós-processamento (Marco 5).

## 2. Regras que se herdam e decisões do Marco 4

- Acesso: só treino ou sintéticos em desenvolvimento. Validação e teste exigem autorização explícita (`00` §6). A seleção no `test` fez-se **numa só abertura**, com `configs/authorizations/test_selection_windows.json` e o protocolo `configs/selection_protocol_windows.json`, ambos novos (os da baseline não se alteraram).
- Nunca atravessar IDs nem conjuntos. [REV-046 | cor #00B0FF] **Intervalos de tempo dentro de uma viagem não cortam a sequência**: a baseline trata a viagem inteira como uma só sequência (o `time_gap` é uma característica) e as janelas fazem o mesmo, para a única diferença ser o janelamento. Decisão do utilizador (REV-046); a regra «não atravessar gaps» do `AGENTS.md` §5 aplica-se, nesta fase, às viagens e não aos intervalos de tempo dentro de uma viagem.
- Entrada `[B, 7, L]` e logits `[B, 1, L]`; um rótulo por ponto.
- `BCEWithLogitsLoss` mascarada; a sigmoide só dá probabilidades, aplicada uma só vez (float64 na reconstrução).
- Avalia-se **depois** de reconstruir uma previsão por ponto original, sem contar repetições sobrepostas como pontos novos.
- Cada experiência treina de raiz, com a mesma seed (42), os mesmos pesos iniciais e o mesmo normalizador da baseline (verificado contra o checkpoint congelado). Sem monitorização interna, como a baseline.

## 3. Protocolo das experiências (decidido, REV-046)

Comprimento: **L = 64 pontos**. A CNN é exatamente a de referência, que continua fechada (REV-041) e não se treina de novo. O comprimento em pontos não corresponde a uma duração fixa.

| Variante | Entrada | Sobreposição | Passo | Estado |
|---|---|---|---|---|
| Baseline | Viagem completa | n/a | n/a | Referência (`02`) |
| J0 | Janela 64 | 0 % | 64 | **Feita** (controlo do janelamento) |
| J50 | Janela 64 | 50 % | 32 | **Feita** |
| J25, J75 | Janela 64 | 25 %, 75 % | 48, 16 | Fora do âmbito; por estudar |
| Outros L | — | — | — | Fora do âmbito; por estudar |

- **Sobreposição no treino e na inferência:** a mesma nas duas fases (decisão do utilizador). O efeito medido é, por isso, o combinado. Treinar com J0 e prever com J50 ficou fora do projeto.
- **Orçamento:** as mesmas **300 épocas** da baseline, Adam com lr 1e-3, sem pesos de classe nem reamostragem, um checkpoint por época e **45 minutos** por treino (se não terminar, o treino pára e informa-se o utilizador, sem seleção). Com **lotes de 32 janelas**, J50 tem cerca do dobro das janelas e dos passos de otimização de J0 no mesmo número de épocas; reporta-se épocas, passos e tempo. Por isso a diferença entre J0 e J50 mede «sobreposição mais mais passos».
- **Lote:** janelas de viagens diferentes misturam-se no lote, com a ordem baralhada em cada época (seed + época).
- **Perda:** soma das posições reais dividida pelo seu número, por lote; cada ocorrência de um ponto conta (um ponto em duas janelas pesa duas vezes). Sem pesos por cobertura.
- **Seleção** (no `test`, igual à da baseline): época pela menor perda por ponto **depois da reconstrução** (BCE sobre a probabilidade média de cada ponto, com recorte de 1e-12) e limiar pelo F1 médio das duas classes (grelha 0,05 a 0,95). Se a época escolhida for ≥ 291 regista-se que possivelmente não convergiu e não se prolonga o treino.

## 4. Janelas, cauda e reconstrução

1. Cada viagem começa no índice 0 e avança pelo passo.
2. Pára-se depois da primeira janela que alcança o fim (`início + L ≥ N`).
3. [REV-046 | cor #00B0FF] **A última janela é mais curta quando N não é múltiplo do passo, sem pontos falsos.** Uma viagem com N ≤ L dá uma só janela com N pontos. Uma cauda curta tem menos contexto (o campo recetivo é 13 pontos) e, em J0, os seus pontos têm uma única previsão; em J50 estão normalmente também na janela anterior.
4. Um lote de janelas de comprimentos diferentes é empilhado com enchimento **só para empilhar**: a máscara tira-o da perda e da média e `FullTripCNN.forward(x, mask)` põe a zero as posições de enchimento depois de cada ReLU. A previsão de uma janela curta num lote é assim igual à da janela sozinha (testado). Sem máscara, a baseline não muda.
5. Todos os pontos reais aparecem pelo menos uma vez; a probabilidade final de cada ponto é a **média simples** das probabilidades das janelas que o cobrem (`prediction_count` = `n_windows`); o limiar aplica-se só depois da média.

Não se acrescenta uma janela final alinhada à direita: criaria sobreposição também em J0.

## 5. O que está implementado

| Contrato | Onde | Estado |
|---|---|---|
| `calculate_stride`, `window_starts`, `WindowSet` (índice, extração sob pedido, tabela janela↔ponto, cobertura) | `src/ais/phase1/windows.py` | Feito |
| `validate_window_coverage` | idem | Feito |
| `masked_bce`, `train_window_epoch` | idem | Feito |
| `predict_window_probabilities`, `predict_window_table`, `reconstructed_loss_per_point` | idem | Feito |
| Máscara opcional no modelo | `src/ais/phase1/model.py` (`FullTripCNN.forward`) | Feito |
| Configuração e treino | `src/ais/phase1/windows.py` (`load_window_config`), `src/ais/cli/run_window_training.py`, `configs/windows_j0.json`, `configs/windows_j50.json` | Feito |
| Seleção no `test` (uma abertura) e medição por segmento da baseline, J0 e J50; congelação | `src/ais/cli/select_windows_on_test.py` | Feito |
| Resultados, macros do LaTeX e figuras | `src/ais/cli/build_window_results.py` | Feito |
| Pós-processamento (Marco 5) e medição final no `validation` (Marco 7) | — | Por fazer |

O modelo reutiliza `build_cnn`; não se duplica a arquitetura. Não se criaram os módulos `windowing`, `reconstruction`, `experiments`, etc. previstos no desenho inicial: agruparam-se em `windows.py`, mantendo as responsabilidades (o AGENTS.md pede marcos executáveis, não módulos vazios).

Comandos (a partir da raiz do projeto):

```bash
iach-ais-venv-4/bin/python -m ais.cli.run_window_training configs/windows_j0.json    # treino de J0 (só treino)
iach-ais-venv-4/bin/python -m ais.cli.run_window_training configs/windows_j50.json   # treino de J50
iach-ais-venv-4/bin/python -m ais.cli.select_windows_on_test                         # UMA abertura do test, já feita; não repetir
iach-ais-venv-4/bin/python -m ais.cli.build_window_results                           # final_results_windows.json, macros e figuras
```

## 6. Testes (sintéticos)

`tests/test_windows.py` (passo e sobreposições inválidas; N < L, N = L, N > L e cauda; nenhuma janela atravessa viagens; cobertura; lote e máscara; equivalência do lote com enchimento e da janela isolada; modo sem máscara igual à baseline; perda sem efeito do enchimento; reconstrução com valores conhecidos em J0 e J50; ordem, IDs, tempos e alvos da tabela; um passo de treino finito e reprodutível; configuração recusa teste e validação) e `tests/test_select_windows.py` (seleção de ponta a ponta num projeto sintético: uma só abertura do `test`, segunda abertura recusada, e bloqueio antes de abrir se um treino estiver incompleto, faltarem checkpoints ou a baseline não conferir).

## 7. Critérios de aceitação

- Um ponto reconstruído por ponto real; nenhuma janela atravessa viagens ou conjuntos.
- Enchimento fora da perda, da média e das métricas.
- Sobreposição igual no treino e na inferência, orçamento e passos explícitos.
- Mesma divisão, mesmas métricas e mesmo critério de seleção da baseline; nenhum uso reservado em desenvolvimento.
- Limitações descritas (bordas, cauda curta, mais passos em J50), sem prometer ganhos.
