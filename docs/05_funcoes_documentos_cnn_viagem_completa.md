# Fase 1 — Funções e documentos para a CNN com viagem completa

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## 1. Objetivo e âmbito
Guia para o agente implementar a segunda parte do projeto: a primeira fase de modelação, CNN com viagem completa. A saída é uma probabilidade de pesca por ponto, sem janelamento externo, sobreposição ou pós-processamento temporal.

Este documento especifica uma API proposta. Estado (REV-024): implementadas e testadas as funções 02 a 06, 07, 08, 09, 10, 11, 12 (smoke test), 13 e 14; as restantes (config, inferência, segmentos, métricas, relatórios, checkpoints, congelamento e execução) **não** estão implementadas. A política de acesso definida na preparação comum é obrigatória e prevalece sobre exemplos de execução.

## 2. Regra de acesso aos dados
- Durante desenvolvimento, usar exclusivamente treino oficial ou dados sintéticos independentes.
- Não abrir, inspecionar, testar código ou fazer benchmarks em validação/teste oficiais, nem com pequenas amostras.
- Se for necessária monitorização interna, subdividir apenas treino oficial, mantendo cada ID inteiro numa partição interna.
- A validação oficial só pode ser acedida com autorização explícita do utilizador, na seleção formal após implementação testada e congelada.
- O teste oficial exige nova autorização e serve apenas para avaliação final.
- Alterar uma flag no código não equivale a autorização. O agente não se pode autorizar a si mesmo.
- Se surgir um erro numa execução reservada, reproduzir/corrigir com treino ou dados sintéticos e documentar a exposição; não usar esse conjunto para debugging.

## 3. Contratos dos dados e do modelo
- Entidade: id completo da viagem. Viagens do mesmo navio podem ficar em conjuntos diferentes, conforme a decisão do projeto.
- Sequências válidas separadas por gaps continuam ligadas à viagem original e ao mesmo split.
- Entradas iniciais: speed_calc_mps, signed_turn, time_gap_calc_s, distanceToShore, na ordem guardada na preparação.
- X de uma sequência: [F,N]; lote inicial: [1,F,N].
- y: [1,N]; lote: [1,1,N], com rótulos 0/1.
- O modelo devolve logits [B,1,N]. BCEWithLogitsLoss recebe logits; sigmoid é aplicada na inferência, sem duplicação.
- Manter comprimento temporal; não reduzir a uma classe por viagem.
- Uma viagem inteira entra de cada vez, salvo quebras de qualidade previamente documentadas. Se não couber em memória, parar e reportar; não introduzir janelas ou truncamento silenciosamente.
- ID, point_id e t são metadados, não entradas preditivas.
- Normalizador e política de ausências vêm da preparação comum; não os reajustar nesta fase.

## 4. Bibliotecas previstas
| Biblioteca | Utilização |
|---|---|
| torch | CNN, Dataset/DataLoader, perda, otimizador, treino e inferência |
| pandas | Tabelas de pontos, previsões, segmentos e relatórios |
| numpy | Operações numéricas, máscaras e reprodutibilidade |
| scikit-learn | Métricas por ponto; não reajustar o normalizador da preparação |
| matplotlib | Curvas e gráficos diagnósticos |
| pathlib, json, logging, random, time, hashlib | Caminhos, configuração, registos, sementes, tempos e identificação de artefactos |

Fixar versões no ambiente e registar as versões efetivamente utilizadas. No KNIME, os nós Python Script chamam estas funções; o workflow de desenvolvimento não deve executar ramos reservados.

## 5. Documentos e artefactos necessários

### Recebidos da preparação comum
| Artefacto | Conteúdo obrigatório |
|---|---|
| Dados preparados de treino | Características, target, IDs, timestamps e point_id; sequence_id quando aplicável |
| Manifesto de divisão | id → split fixo e seed; sem abrir os valores dos conjuntos reservados |
| Manifesto de características | Ordem, unidades, tipos e transformações |
| Normalizador guardado | Objeto ajustado só no treino, acompanhado da respetiva configuração |
| Relatório da preparação | Limpeza, exclusões, gaps e política de ausências |

### Documentos a criar antes do treino
| Documento sugerido | Conteúdo |
|---|---|
| phase1_config.json | Arquitetura, seed, dispositivo, épocas, otimizador, perda, limiar e caminhos autorizados |
| phase1_protocol.md | Objetivo, dados permitidos, orçamento experimental, critérios de checkpoint e regras de comparação |
| metrics_protocol.md | Fórmulas, agregação, IoU temporal, matching um-para-um e convenções das fronteiras |
| environment.yml ou requirements.txt | Dependências e versões fixadas |
| README_phase1.md | Como executar desenvolvimento e testes, entradas, saídas e proibição de acesso reservado |

### Gerados durante a execução
| Artefacto | Conteúdo |
|---|---|
| training_history.csv | Perdas, métricas diagnósticas, épocas, passos e tempos |
| checkpoint.pt | Pesos, estado necessário para retoma e metadados |
| point_predictions_train.csv | Probabilidades e classes por ponto do treino |
| segments_train.csv | Segmentos diagnósticos previstos e referências |
| metrics_train.json | Métricas identificadas como treino ou monitorização interna |
| run_report.md | Configuração, limitações, verificações e resultados diagnósticos |
| run_manifest.json | Referências aos artefactos, versões e identificação da execução |
| access_log.json | Registo das autorizações e acessos reservados, quando existirem |

Resultados oficiais de validação/teste não são entregáveis da execução de desenvolvimento. Só serão gerados nas etapas autorizadas.

## 6. Funções propostas
### 01 — `load_phase1_config(path)`

- Módulo: `config.py`.
- Recebe: Configuração JSON e caminho de origem.
- Faz: Validar parâmetros, características, stage e caminhos; rejeitar acesso reservado sem autorização externa.
- Devolve: Dicionário validado.

### 02 — `load_training_data(data_path, split_manifest)`

- Módulo: `data.py`.
- Recebe: Caminho dos dados preparados de treino e manifesto fixo.
- Faz: Carregar só treino; verificar que todos os IDs constam como train. Não abrir validação/teste.
- Devolve: DataFrame de treino.

### 03 — `validate_training_data(df, feature_cols)`

- Módulo: `data.py`.
- Recebe: Treino e lista ordenada de características.
- Faz: Verificar point_id único, target binário, tipos, valores finitos, ordem temporal e correspondência com o manifesto. Não reaprender transformações.
- Devolve: Relatório de verificações; erro se existirem falhas obrigatórias.

### 04 — `build_full_sequences(df, feature_cols)`

- Módulo: `data.py`.
- Recebe: Treino tratado com id, sequence_id quando aplicável, point_id, t e target.
- Faz: Agrupar por viagem ou sequência válida, sem janelamento; preservar alinhamento de entradas e resposta.
- Devolve: Lista de registos com X [F,N] float32, y [1,N] float32, point_ids, timestamps e id.

### 05 — `create_internal_training_split(sequences, fraction, seed)`

- Módulo: `data.py`.
- Recebe: Sequências exclusivamente do treino oficial, fração interna e seed.
- Faz: Opcionalmente separar treino interno e monitorização interna por ID completo; todas as sequências do mesmo ID ficam juntas.
- Devolve: Duas listas de sequências e manifesto interno. Se desativado, não inventar avaliação independente.

### 06 — `build_sequence_loader(sequences, shuffle, seed)`

- Módulo: `data.py`.
- Recebe: Lista de sequências e configuração.
- Faz: Criar Dataset/DataLoader PyTorch com batch_size=1 inicialmente, sem truncar, reamostrar ou criar janelas silenciosamente.
- Devolve: DataLoader que devolve X [1,F,N], y [1,1,N] e metadados.

### 07 — `set_reproducibility(seed, deterministic)`

- Módulo: `utils.py`.
- Recebe: Semente e política de determinismo.
- Faz: Configurar random, NumPy e PyTorch; registar restrições e ambiente.
- Devolve: Metadados de reprodutibilidade; não prometer identidade entre hardwares.

### 08 — `select_device(requested_device)`

- Módulo: `utils.py`.
- Recebe: cpu, cuda ou auto.
- Faz: Selecionar dispositivo disponível e registar a escolha.
- Devolve: torch.device.

### 09 — `build_cnn(model_config, n_features)`

- Módulo: `model.py`.
- Recebe: Arquitetura e número de características.
- Faz: Construir CNN 1D totalmente convolucional com padding que preserve N e cabeça Conv1D de um canal. Sem pooling global nem saída única por viagem.
- Devolve: torch.nn.Module que recebe [B,F,N] e devolve logits [B,1,N].

### 10 — `build_loss(loss_config)`

- Módulo: `training.py`.
- Recebe: Configuração da perda e política de ponderação.
- Faz: Usar inicialmente BCEWithLogitsLoss sem pesos de classe. Não pôr Sigmoid dentro do modelo usado com esta perda.
- Devolve: Objeto de perda. Aplicar sigmoid aos logits apenas para probabilidades.

### 11 — `build_optimizer(model, optimizer_config)`

- Módulo: `training.py`.
- Recebe: Parâmetros do modelo e hiperparâmetros.
- Faz: Criar otimizador, inicialmente Adam, com valores declarados na configuração.
- Devolve: Otimizador PyTorch.

### 12 — `run_training_smoke_test(model, train_batch, loss_fn, device)`

- Módulo: `checks.py`.
- Recebe: Modelo temporário ou cópia e lote sintético ou do treino.
- Faz: Verificar forward, forma da saída, perda finita e backward; não usar o modelo alterado inadvertidamente no treino oficial.
- Devolve: Relatório de testes técnicos.

### 13 — `train_one_epoch(model, loader, optimizer, loss_fn, device)`

- Módulo: `training.py`.
- Recebe: Modelo e loader exclusivamente de treino interno ou treino oficial.
- Faz: Ativar train, calcular logits e perda, backward e atualização. Registar agregação por ponto e por sequência explicitamente.
- Devolve: Estatísticas da época e número de passos/pontos.

### 14 — `evaluate_training_subset(model, loader, loss_fn, device, threshold)`

- Módulo: `training.py`.
- Recebe: Subconjunto pertencente exclusivamente ao treino oficial.
- Faz: Usar eval e no_grad; calcular métricas diagnósticas, sem atualizar pesos. A monitorização interna não é a validação oficial.
- Devolve: Perda e métricas identificadas como treino ou monitorização interna.

### 15 — `train_model(model, train_loader, config, internal_monitor_loader=None)`

- Módulo: `training.py`.
- Recebe: Modelo, treino e monitorização interna opcional.
- Faz: Coordenar épocas e checkpoints; usar early stopping apenas com critério declarado e dados permitidos. Nunca carregar conjuntos oficiais reservados.
- Devolve: Modelo, histórico e metadados do checkpoint selecionado.

### 16 — `predict_full_sequences(model, loader, device)`

- Módulo: `inference.py`.
- Recebe: Modelo e sequências autorizadas: só treino durante desenvolvimento.
- Faz: Executar sequência completa sem gradientes; aplicar sigmoid aos logits; restaurar a correspondência ponto a ponto.
- Devolve: DataFrame com id, sequence_id, point_id, t, target quando disponível e p_fishing.

### 17 — `probabilities_to_classes(predictions, threshold)`

- Módulo: `inference.py`.
- Recebe: Tabela de probabilidades e limiar fixado.
- Faz: Criar predicted_class por comparação explícita com threshold. Começar com 0.5, sem o escolher olhando para teste.
- Devolve: Tabela com predicted_class; preservar p_fishing.

### 18 — `extract_segments(point_predictions, class_col, interval_convention)`

- Módulo: `segments.py`.
- Recebe: Pontos ordenados, coluna de classe e convenção temporal.
- Faz: Agrupar classes consecutivas dentro da mesma sequência. Não suavizar nem eliminar segmentos curtos. Aplicar a mesma convenção a previsões e target.
- Devolve: Tabela com segment_id, id, sequência, classe, início/fim, pontos, duração e estatísticas da probabilidade.

### 19 — `compute_point_metrics(predictions, positive_class=1)`

- Módulo: `metrics.py`.
- Recebe: Previsões e target de um conjunto autorizado.
- Faz: Calcular matriz de confusão, precisão, sensibilidade, F1 e IoU; declarar política de divisões por zero e agregação global/por viagem.
- Devolve: Dicionário de métricas e DataFrames por viagem.

### 20 — `match_segments(predicted_segments, reference_segments, matching_config)`

- Módulo: `metrics.py`.
- Recebe: Segmentos previstos/reais e regras fixadas de IoU temporal.
- Faz: Calcular sobreposições dentro da mesma sequência e classe; correspondência um-para-um com algoritmo e limiar explícitos.
- Devolve: Tabela de pares, previstos sem correspondência e reais sem correspondência.

### 21 — `compute_segment_metrics(matches, predicted_segments, reference_segments)`

- Módulo: `metrics.py`.
- Recebe: Correspondências e tabelas de segmentos.
- Faz: Calcular precisão, sensibilidade e F1 por segmento, IoU dos pares e erro de início/fim; contar fragmentação. Definir casos sem pesca e segmentos de duração zero.
- Devolve: Métricas e tabelas detalhadas, com unidades e denominadores.

### 22 — `plot_training_results(history, predictions, output_dir)`

- Módulo: `reporting.py`.
- Recebe: Histórico e previsões exclusivamente de treino durante desenvolvimento.
- Faz: Criar curvas, exemplos temporais e matriz de confusão; identificar claramente o conjunto usado.
- Devolve: Lista de caminhos dos gráficos.

### 23 — `save_checkpoint(model, optimizer, config, epoch, path)`

- Módulo: `artifacts.py`.
- Recebe: Estado do treino, configuração e destino.
- Faz: Guardar state_dict, estado do otimizador se necessário, ordem das entradas, versões e proveniência dos artefactos.
- Devolve: Caminho do checkpoint e metadados.

### 24 — `load_checkpoint(path, model_config, device)`

- Módulo: `artifacts.py`.
- Recebe: Checkpoint confiável e arquitetura correspondente.
- Faz: Reconstruir modelo e validar compatibilidade das características e versão. Carregar apenas artefactos confiáveis.
- Devolve: Modelo restaurado e metadados.

### 25 — `save_phase1_results(results, output_dir)`

- Módulo: `artifacts.py`.
- Recebe: Métricas, tabelas, histórico e configuração da execução.
- Faz: Persistir CSV/JSON, gráficos referenciados e relatório de execução, com stage e split explícitos.
- Devolve: Manifesto de artefactos com caminhos.

### 26 — `freeze_phase1_run(config, checkpoint, preprocessing_manifest)`

- Módulo: `artifacts.py`.
- Recebe: Configuração final, checkpoint e referência à preparação.
- Faz: Guardar versão imutável identificável e registar características, divisão, regras e decisões antes de pedir acesso reservado.
- Devolve: Manifesto da execução congelada. Não concede autorização.

### 27 — `run_phase1_development(config)`

- Módulo: `run_phase1.py`.
- Recebe: Configuração de desenvolvimento e caminhos apenas de treino.
- Faz: Coordenar verificações, sequências, testes técnicos, treino, inferência diagnóstica e exportação. Parar antes de validação/teste oficiais.
- Devolve: Manifesto, histórico, métricas diagnósticas e caminhos.

### 28 — `run_authorized_validation(frozen_run, authorization)`

- Módulo: `reserved_evaluation.py`.
- Recebe: Execução congelada e autorização explícita do utilizador, externa ao agente.
- Faz: Só na etapa formal: aplicar preparação congelada e inferência à validação para decisões previstas no protocolo; sem debugging nem fit de normalizadores.
- Devolve: Relatório de seleção e decisões versionadas.

### 29 — `run_authorized_final_evaluation(frozen_run, authorization)`

- Módulo: `reserved_evaluation.py`.
- Recebe: Solução final congelada e nova autorização explícita.
- Faz: Avaliar teste com pipeline congelada e protocolo aprovado. Não selecionar modelos nem alterar solução a partir destes resultados.
- Devolve: Relatório final de métricas e artefactos.

## 7. Organização dos ficheiros
```text
src/phase1/
├── config.py
├── data.py
├── model.py
├── training.py
├── inference.py
├── segments.py
├── metrics.py
├── reporting.py
├── artifacts.py
├── checks.py
├── utils.py
├── run_phase1.py
└── reserved_evaluation.py

tests/
├── test_sequences.py
├── test_model_shapes.py
├── test_loss_and_gradients.py
├── test_point_alignment.py
├── test_segments_and_metrics.py
└── test_access_policy.py
```

Não é obrigatório criar um ficheiro por pequeno conceito no primeiro dia; podem ser agrupados mantendo responsabilidades claras. As funções reservadas devem ficar fora do caminho normal de desenvolvimento.

## 8. Testes técnicos obrigatórios
Todos com dados sintéticos ou treino:
1. Sequências com comprimentos diferentes mantêm N probabilidades na saída.
2. Nenhum ponto se mistura com outra viagem ou sequência.
3. Target e previsão mantêm o alinhamento de point_id e tempo.
4. A perda é finita, há gradientes e um passo de otimização funciona.
5. O modelo consegue sobreajustar um exemplo sintético simples ou pequena amostra de treino como teste diagnóstico; não apresentar isto como generalização.
6. Guardar/carregar o checkpoint preserva as previsões em modo de avaliação dentro da tolerância definida.
7. A extração de segmentos funciona com uma só classe, alternâncias e sequências mínimas.
8. As métricas têm testes com valores esperados conhecidos, incluindo casos sem positivos.
9. O carregador de desenvolvimento rejeita IDs de validação/teste e não abre esses ficheiros.
10. A inferência cobre todos os pontos válidos uma única vez.

## 9. Fluxo de desenvolvimento
```text
Ler configuração de desenvolvimento
→ verificar que só treino está acessível
→ carregar treino e manifestos da preparação
→ validar dados e construir sequências completas
→ criar monitorização interna opcional apenas no treino
→ criar CNN, perda e otimizador
→ executar testes sintéticos e smoke test no treino
→ treinar e registar histórico
→ gerar previsões diagnósticas no treino
→ converter classes e extrair segmentos
→ calcular métricas diagnósticas
→ guardar checkpoint, configuração e relatório
→ congelar a execução
→ PARAR e pedir autorização para a etapa seguinte
```

## 10. Decisões a fixar no protocolo
- Arquitetura inicial proposta: Conv1D 32/64/32 canais, kernels 5, ativações ReLU, padding same e cabeça Conv1D de kernel 1 com logits. Sem Sigmoid antes de BCEWithLogitsLoss.
- Batch inicial: uma sequência por passo.
- Política de perda: explicitar se a média é por sequência ou por ponto; com uma atualização por sequência, viagens de comprimentos diferentes influenciam o treino de modo distinto.
- Otimizador inicial: Adam; taxa de aprendizagem e épocas ficam na configuração, sem valores supostamente já validados.
- Sem pesos de classe ou reamostragem na configuração inicial.
- Threshold inicial: 0.5; eventual seleção formal usa validação apenas depois de autorizada.
- Sem suavização temporal, eliminação de segmentos curtos ou agregação de janelas.
- Registar que as convoluções têm campo recetivo limitado: entrada completa não implica que cada saída use toda a viagem.
- Se for usado subconjunto interno para comparar pré-processamentos, ajustar os respetivos objetos só no treino interno; um normalizador ajustado no treino oficial inteiro não dá uma avaliação interna totalmente independente. Essa monitorização deve ser descrita como diagnóstica ou o pré-processamento deve ser reajustado corretamente no treino interno.

## 11. Critérios de aceitação
- Uma probabilidade por ponto válido, sem cortes ocultos.
- Testes exclusivamente em treino ou dados sintéticos.
- Rastreabilidade completa das características e dos pontos.
- Checkpoints reproduzíveis dentro das limitações documentadas do ambiente.
- Métricas com definições e casos-limite explícitos.
- Nenhum acesso a conjuntos reservados no desenvolvimento.
- Mesmas características, divisão e regras de avaliação preparadas para a comparação com a fase de janelamento.
