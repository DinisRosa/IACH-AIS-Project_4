# 02 — CNN 1D sobre a viagem completa (Marco 3)

[REV-033 | cor #3E2723] Documento fundido a partir de `02_cnn_viagem_completa` (workflow) e `05_funcoes_documentos_cnn_viagem_completa` (contratos). É a **baseline**: recebe a viagem inteira e devolve uma probabilidade de pesca por ponto, sem janelas, sem sobreposição e sem pós-processamento. Dados e entradas: `01`. Regras de acesso: `00` §6.

## 1. Contratos de dados e do modelo

- Uma viagem (ou sequência válida) entra de cada vez, sem truncar nem janelar. Se não couber em memória, parar e reportar; não introduzir janelas, truncagem ou reamostragem em silêncio.
- Forma de uma sequência: `X [7, N]`, `y [1, N]`; em lote (batch 1): `X [1, 7, N]`, `y [1, 1, N]`. Os 7 canais estão descritos em `01` §6.
- O modelo devolve **logits** `[B, 1, N]`. A perda é `BCEWithLogitsLoss` (sem sigmoide dentro do modelo); a sigmoide aplica-se uma só vez, para obter probabilidades.
- `id`, `point_id` e `t` são metadados, nunca entradas.
- Entrada completa não significa contexto global: o contexto de cada previsão é o campo recetivo da rede.

## 2. Arquitetura (valores iniciais, não validados)

```text
[7, N] → Conv1D 32 (k5, same) → ReLU → Conv1D 64 (k5, same) → ReLU
       → Conv1D 32 (k5, same) → ReLU → Conv1D 1 (k1) → logits [1, N]
```

Campo recetivo de **13 pontos** (três kernels 5, stride 1, sem dilatação) e 21 761 parâmetros. Sem pooling global nem saída única por viagem. Implementada em `src/ais/phase1/model.py` (`build_cnn`, `receptive_field`, `count_parameters`).

## 3. Treino (execução 1: REV-032, `configs/phase1_run1.json`; treino final: REV-035, `configs/phase1_final.json`)

| Elemento | Valor inicial |
|---|---|
| Perda | `BCEWithLogitsLoss`, sem pesos de classe nem reamostragem |
| Otimizador | Adam, lr 1e-3, sem procura |
| Lote | Uma viagem por passo |
| Monitorização interna | 15 % das viagens do treino (13 de 87), por ID, seed 42, aleatória, sem estratificar |
| Paragem | Perda por ponto da monitorização; paciência 10; guarda o melhor checkpoint |
| Limites | 100 épocas; orçamento de 15 minutos |
| Limiar | 0,5 (sem escolha a partir de resultados) |
| Dispositivo | CPU |

Todos são valores iniciais, não validados. No **treino final** (REV-035) usam-se as 87 viagens sem monitorização interna (`internal_monitor_fraction = 0`), paciência 30 e a paragem e o melhor modelo decididos pela perda por ponto avaliada sobre o próprio treino (`stop_criterion = "treino"`). Qualquer alteração do critério de paragem, do lr ou da arquitetura é uma escolha metodológica a aprovar. A monitorização são viagens do treino: **não é a validação oficial**, e a normalização ajustada só no treino interno é a que preserva essa independência.

Registar sempre: seed, características por ordem, configuração, versões, manifesto da divisão, épocas, passos e histórico. Com uma atualização por viagem, viagens longas pesam de modo diferente; declarar se a média é por ponto ou por sequência.

## 4. O que está implementado

| Função (contrato) | Onde | Estado |
|---|---|---|
| `load_phase1_config` | `src/ais/phase1/config.py` | Feito; só aceita `stage=development` e ficheiro de treino |
| `load_training_data`, `validate_training_data` | `src/ais/phase1/data.py` | Feito |
| `build_full_sequences`, `fit_scaler`, `apply_scaler`, `save_scaler`, `load_scaler` | `src/ais/phase1/data.py` | Feito |
| `create_internal_training_split` | `src/ais/phase1/data.py` | Feito (por ID completo) |
| `build_sequence_loader` | `src/ais/phase1/data.py` | Feito (batch 1) |
| `set_reproducibility`, `select_device` | `src/ais/phase1/utils.py` | Feito |
| `build_cnn` | `src/ais/phase1/model.py` | Feito |
| `build_loss`, `build_optimizer` | `src/ais/phase1/training.py` | Feito |
| `run_training_smoke_test` | `src/ais/phase1/checks.py` | Feito (estrito: exige gradiente não nulo em todos os tensores; pode ter de relaxar) |
| `train_one_epoch`, `evaluate_training_subset`, `train_model` | `src/ais/phase1/training.py` | Feito, com paragem antecipada e orçamento |
| `save_checkpoint`, `load_checkpoint` | `src/ais/phase1/artifacts.py` | Feito |
| Métricas por classe e por ponto (`class_metrics`) | `src/ais/phase1/metrics.py` | Feito; existe duplicada em `src/ais/cli/diagnostic_fit_3_trips.py`, por unificar |
| Inferência e tabelas por ponto (`predict`, `tables_for`) | `src/ais/phase1/inference.py` | Feito (REV-038); antes estava dentro do script |
| Acesso aos conjuntos reservados (autorização, protocolo, registo, rondas, `validation` só uma vez) | `src/ais/phase1/reserved.py` | Feito (REV-038), testado só com sintéticos |
| Critérios de seleção (época por perda, limiar por F1 médio) | `src/ais/phase1/selection.py`; programa `src/ais/cli/select_on_test.py` | Feito e executado uma vez no `test` (REV-038) |
| Congelar a baseline (`freeze_phase1_run`) | `src/ais/cli/freeze_baseline.py` | Feito (REV-038): `results/baseline_frozen/` |
| Navios partilhados entre conjuntos | `src/ais/cli/count_shared_vessels.py` | Feito (REV-039), só lê o manifesto |
| Ficheiro final de resultados, macros e figuras do LaTeX | `src/ais/cli/build_final_results.py` | Feito (REV-035; reescrito em REV-040 para partir da baseline congelada): `results/baseline_frozen/final_results.json`, `latex/generated/resultados.tex`, `latex/figures/final_*.png`. Avalia a baseline nas 87 viagens de treino e lê os números do `test` de `selection_test.json`; não abre o `test` nem o `validation` |
| Figuras da execução 1 | `src/ais/cli/plot_phase1_run.py` | Script, sem teste |
| Execução | `src/ais/cli/run_phase1_training.py` | Script, sem teste |
| Segmentos (`extract_segments`), correspondência, métricas por segmento, fronteiras e fragmentação | `src/ais/phase1/segments.py`; programa `src/ais/cli/segment_metrics.py` | Feito (REV-039): ferramenta de medição, **sem suavizar**; IoU 0,5, segundos, um-para-um guloso |
| Relatórios e `save_phase1_results` | — | **Por fazer** |
| `run_authorized_validation`, `run_authorized_final_evaluation` | — | **Por fazer**; ficam fora do caminho normal de desenvolvimento e exigem autorização externa ao agente |

Comandos (a partir da raiz do projeto):

```bash
iach-ais-venv-4/bin/python -m pytest tests/
iach-ais-venv-4/bin/python -m ais.cli.run_phase1_training configs/phase1_select.json   # treino, um checkpoint por época
iach-ais-venv-4/bin/python -m ais.cli.select_on_test results/phase1_select              # UMA ronda no test, com autorização
iach-ais-venv-4/bin/python -m ais.cli.freeze_baseline
iach-ais-venv-4/bin/python -m ais.cli.build_final_results   # final_results.json, macros e figuras do LaTeX
iach-ais-venv-4/bin/python -m ais.cli.plot_phase1_run
```

Saídas do treino em `results/phase1_run1/` (não versionadas): checkpoint, histórico, tabelas, previsões da monitorização, scaler, divisão interna, manifesto e figuras. Os resultados numéricos da execução estão em `PROGRESS.md` e `REVISION_LOG.md` (REV-032), não aqui, para não duplicar números.

## 5. Testes

Todos com dados sintéticos ou treino; um teste lê 3 viagens reais do treino.

- **Feitos** (`tests/`): comprimentos diferentes mantêm N saídas; nada se mistura entre viagens; alinhamento de `point_id` e tempo; perda finita, gradientes e passo de otimização; carregador de desenvolvimento rejeita IDs e ficheiros reservados; checkpoint recarregado reproduz as previsões; ciclo de treino com paragem antecipada; ausência de dupla sigmoide.
- **Feitos depois (REV-038, REV-039):** acesso reservado (autorização, protocolo, uma só ronda, `validation` recusado), critérios de seleção, congelação, extração de segmentos e métricas por segmento com valores calculados à mão, e navios partilhados. Conferido ainda por uma reimplementação independente sobre as previsões do treino.
- **Por fazer:** testes automáticos dos programas de treino e de figuras, e a medição por segmento sobre a baseline congelada (precisa de autorização, por usar o `test`).
- O sobreajuste de poucas viagens (ensaio de 3 viagens, REV-027/028) é um teste diagnóstico, não prova de generalização.

## 6. Estado do Marco 3 e próximos passos

**Feito (REV-038):** treino de seleção (300 épocas, um checkpoint por época, só treino), seleção da época e do limiar no `test` numa só ronda, e baseline congelada em `results/baseline_frozen/` (época 162, limiar 0,65). O `validation` **não** foi aberto. Os números estão em `results/phase1_select/selection_test.json` e em `results/baseline_frozen/baseline_frozen.json`.

**Cuidado:** a perda no `test` é muito ruidosa de época para época, e a época escolhida é um mínimo estreito; a seleção pode ter seguido parte desse ruído. A ronda autorizada era uma só, por isso não se repete sem nova decisão do utilizador.

**Próximos passos:**
1. O utilizador decide como lidar com o ruído da seleção (ver o relatório da sessão).
2. Marco 4: janelas J0 e J50 (L = 64) com a mesma CNN, comparadas com a baseline congelada, por ponto e por segmento (`segments.py`).
3. Só no fim do projeto, com todas as variantes congeladas e nova autorização, a medição final única no `validation`; ver `00` §6.

## 7. Critérios de aceitação

- Uma probabilidade por ponto válido, sem cortes ocultos.
- Testes só em treino ou sintéticos; nenhum acesso a conjuntos reservados.
- Rastreabilidade das características e dos pontos; checkpoints reproduzíveis dentro das limitações do ambiente.
- Métricas com definições e casos-limite explícitos, preparadas para a mesma comparação com `03`.
