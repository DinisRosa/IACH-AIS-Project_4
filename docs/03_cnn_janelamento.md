# 03 — CNN 1D com janelamento e sobreposição (Marco 4)

[REV-033 | cor #3E2723] Documento fundido a partir de `03_cnn_janelamento_sobreposicao` (workflow) e `06_funcoes_documentos_cnn_janelamento_sobreposicao` (contratos). **Nada disto está implementado**: não existe `src/phase2/` nem código de janelamento. Os contratos abaixo são propostas a rever quando o Marco 4 começar.

## 1. Objetivo

Medir o efeito de dividir as viagens em janelas e de adicionar sobreposição, comparando com a baseline de `02` (RQ1). Reutiliza a divisão por ID, as características, as unidades, o normalizador e a CNN da baseline, para alterar uma coisa de cada vez. Sem pós-processamento: a **média das previsões sobrepostas é reconstrução**, não suavização, e fica separada de um futuro ramo de pós-processamento (Marco 5).

## 2. Regras que se herdam

- Acesso: só treino ou sintéticos; a monitorização interna cria-se por ID completo, **antes** de gerar janelas (nunca repartir janelas da mesma viagem entre treino interno e monitorização). Validação e teste exigem autorização explícita (`00` §6).
- Nunca atravessar IDs, sequências separadas por gaps ou conjuntos.
- Entrada `[B, 7, L]` e logits `[B, 1, L]`; um rótulo por ponto (não o rótulo maioritário da janela).
- `BCEWithLogitsLoss` mascarada; sigmoide só para probabilidades.
- Padding não entra na perda, na agregação nem nas métricas (pode ainda afetar previsões perto da borda).
- Avalia-se **depois** de reconstruir uma previsão por ponto original, sem contar repetições sobrepostas como pontos novos.
- Treinar cada experiência de raiz, com seeds declaradas. Fine-tuning a partir da baseline seria outra experiência e teria de ser identificado.

## 3. Protocolo das experiências

Comprimento inicial proposto: **L = 64 pontos**, não validado. O comprimento em pontos não corresponde a uma duração fixa; manter a amostragem original e declará-lo.

| Variante | Entrada | Sobreposição | Passo | Prioridade |
|---|---|---|---|---|
| Baseline | Viagem completa | n/a | n/a | Referência (`02`) |
| J0 | Janela 64 | 0 % | 64 | **Prioritária** (controlo do janelamento) |
| J50 | Janela 64 | 50 % | 32 | **Prioritária** |
| J25 | Janela 64 | 25 % | 48 | A decidir depois (REV-002) |
| J75 | Janela 64 | 75 % | 16 | A decidir depois (REV-002) |

Todas sem pós-processamento. A comparação com J0 separa o efeito do janelamento do efeito da sobreposição.

**Decisões a fixar antes de executar:**

- Se a sobreposição varia no treino, na inferência ou em ambos. Na comparação inicial pode variar em ambos, descrevendo o efeito como combinado; uma análise posterior pode fixar o modelo e variar só as janelas de inferência.
- Orçamento: a mesma quantidade de épocas **não** dá o mesmo número de passos quando a sobreposição muda. Fixar a política (épocas, passos ou tempo) e reportar as outras contagens. Perguntar ao utilizador antes de execuções prolongadas.
- A perda mascarada conta cada ocorrência válida numa janela; pontos repetidos pesam várias vezes no treino. Não introduzir pesos por cobertura sem declará-lo como alteração experimental. Continua sem pesos de classe nem reamostragem.
- Monitorização realmente independente exige normalizador ajustado só no treino interno; com o normalizador do treino inteiro é apenas diagnóstica.

## 4. Janelas, cauda e agregação

Proposta determinística:

1. Começar no índice 0 de cada sequência e avançar pelo passo.
2. Parar depois da primeira janela que alcance o fim.
3. Preencher a cauda com valor fixo e máscara (`is_valid=false`, sem `point_id` real).
4. Uma sequência com menos de L pontos dá uma única janela preenchida.
5. Todos os pontos reais têm de aparecer pelo menos uma vez.
6. A probabilidade final de cada ponto é a **média simples** das probabilidades válidas; o limiar aplica-se só depois da média.

Não acrescentar uma janela final alinhada à direita por conveniência: criaria sobreposição também na variante nominal de 0 %. O padding externo das janelas não é o padding interno das convoluções.

Tabela de correspondência: `window_id`, `id`, `sequence_id`, `point_id`, `position_in_window`, `is_valid`. Pode ser regenerável em vez de gravada, mas tem de ser auditável.

## 5. Contratos propostos

| Módulo | Funções | Responsabilidade |
|---|---|---|
| `windowing` | `calculate_stride`, `generate_window_index`, `build_window_mapping` | Passo inteiro (rejeitar sobreposições sem passo exato), inícios e validade, correspondência janela↔ponto |
| `data` | `create_window_dataset`, `create_window_loader` | Extração sob pedido (sem materializar tudo em RAM); `X [F,L]`, `y [1,L]`, `mask [1,L]` |
| `training` | `masked_binary_loss`, `train_window_epoch`, `train_window_model`, `evaluate_internal_monitor` | Soma só posições válidas e divide pelo seu número; rejeita lote sem posições válidas; regista passos, pontos válidos e repetições |
| `inference` | `predict_windows` | `eval`, `no_grad`, sigmoide; preserva `window_id` e posição |
| `reconstruction` | `aggregate_point_predictions`, `restore_sequence_predictions` | Média por `point_id` com `prediction_count`; uma linha por ponto original, com ID, tempo, alvo e ordem |
| `checks` | `validate_window_coverage` | Cobertura completa, sem cruzar IDs/gaps, padding sem associação indevida |
| `experiments` | `build_experiment_grid`, `compare_experiments` | Variantes pré-definidas; comparação no mesmo conjunto, com as mesmas métricas da baseline |
| `evaluation` | `evaluate_reconstructed_predictions` | Reutiliza classes, segmentos e métricas de `02` |
| `artifacts` / `reserved_evaluation` | congelar experiências; validação e teste autorizados | Fora do caminho normal de desenvolvimento |

O modelo reutiliza `build_cnn` de `src/ais/phase1/model.py`; não se duplica a arquitetura. Os módulos não são obrigatórios um a um: agrupar mantendo responsabilidades claras.

## 6. Testes obrigatórios (sintéticos ou treino)

- Cálculo do passo e rejeição de configurações inválidas.
- N < L, N = L, N > L, cauda incompleta, sequências curtas e várias sequências da mesma viagem.
- Nenhuma janela atravessa viagens ou gaps; máscara correta; padding sem `point_id` válido.
- Alterar logits em posições mascaradas não muda a perda.
- Cobertura completa e sem duplicações após agregar; média validada com probabilidades artificiais de resultado conhecido.
- Reconstrução com ordem, tempos e alvo preservados.
- Métricas reutilizadas de `02` com exemplos de referência; forward/backward finitos; checkpoint com previsões equivalentes após recarga.
- Desenvolvimento rejeita dados e IDs reservados.

## 7. Fluxo e critérios de aceitação

```text
treino preparado → sequências → partição interna por ID → grelha de experiências
→ índice e correspondência das janelas → validar máscaras e cobertura
→ treinar com perda mascarada → inferir → agregar por ponto → reconstruir
→ classes e segmentos (sem suavização) → métricas e comparação com a baseline
→ congelar → PARAR e pedir autorização para seleção formal
```

- Um ponto reconstruído por ponto real válido; nenhuma janela atravessa IDs, gaps ou conjuntos.
- Padding fora da perda, da agregação e das métricas.
- Protocolo de sobreposição (treino/inferência) e orçamento explícitos.
- Mesma divisão e mesmas métricas da baseline; nenhum uso reservado em desenvolvimento.
- Limitações das bordas descritas, sem prometer ganhos antes de os medir.
