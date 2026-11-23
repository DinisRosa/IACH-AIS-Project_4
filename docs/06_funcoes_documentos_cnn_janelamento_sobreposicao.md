# Parte 3 — Funções e documentos para CNN com janelamento e sobreposição

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## 1. Objetivo
Especificação para o agente implementar a fase de CNN com janelas, incluindo 0% de sobreposição como controlo. Comparar com a CNN de viagem completa sem introduzir pós-processamento temporal adicional.

As funções abaixo são contratos propostos, não código implementado. Reutilizar componentes da preparação e da CNN completa em vez de duplicar lógica.

## 2. Política obrigatória de acesso
- Desenvolvimento, debugging, gráficos, benchmarks, testes de integração e ensaios usam exclusivamente treino oficial ou dados sintéticos.
- Nenhuma amostra de validação/teste pode ser aberta para verificar funcionamento do código.
- Monitorização interna, se necessária, é criada apenas a partir do treino, por ID completo e antes de gerar janelas.
- Não repartir aleatoriamente janelas da mesma viagem entre treino interno e monitorização interna.
- Validação oficial requer autorização explícita do utilizador após implementação testada e congelada; teste requer nova autorização e solução final congelada.
- Uma flag alterada pelo agente não constitui autorização. As funções reservadas ficam fora do fluxo normal de desenvolvimento.
- Erros surgidos nas etapas reservadas devem ser reproduzidos e corrigidos com treino/dados sintéticos, com exposição documentada.
- A política da preparação comum prevalece sobre instruções menos restritivas.

## 3. Contratos e decisões comuns
- Entidade de separação: ID completo da viagem, não prefixo do navio.
- Todas as sequências e janelas de um ID permanecem no mesmo conjunto.
- Não atravessar IDs, sequências separadas por gaps ou splits.
- Mesma divisão, características, unidades e normalizador da fase de viagem completa.
- Nenhum fit de transformações nos dados reservados.
- Características iniciais: speed_calc_mps, signed_turn, time_gap_calc_s, distanceToShore, na ordem do manifesto.
- Entrada da CNN: [B,F,L]; logits: [B,1,L]. Um rótulo por ponto, não rótulo maioritário da janela.
- Usar BCEWithLogitsLoss sem sigmoid prévia; sigmoid apenas para probabilidades.
- Padding não entra na perda, nas métricas nem na agregação; pode ainda afetar previsões perto da borda, o que deve ser reconhecido.
- Avaliar após reconstruir uma previsão por ponto original, nunca contando repetições sobrepostas como novos pontos.

## 4. Documentos e artefactos necessários

### Entradas da preparação comum
| Artefacto | Conteúdo |
|---|---|
| Dados preparados de treino | Características, target, id, sequence_id, point_id e t |
| Manifesto de divisão | id → split fixo para ambas as fases |
| Manifesto das características | Ordem, unidades, transformações e política de ausências |
| Normalizador e configuração | Ajustados apenas no treino |
| Relatório de preparação | Limpeza, gaps, exclusões e decisões |

### Referências da fase de viagem completa
| Artefacto | Finalidade |
|---|---|
| Configuração/implementação da CNN | Reutilizar a arquitetura como ponto de partida |
| Protocolo de métricas | Mesmas definições de IoU, matching e fronteiras |
| Manifesto e resultados da baseline | Comparação no mesmo conjunto autorizado |
| Funções de segmentos e métricas | Evitar diferenças metodológicas acidentais |

Não é obrigatório inicializar com os pesos treinados da fase 1. Por defeito, treinar cada experiência de raiz com sementes declaradas. Se for usado fine-tuning, identificá-lo como experiência diferente.

### Documentos a criar antes das experiências
| Documento sugerido | Conteúdo |
|---|---|
| phase2_config.json | Comprimento, overlap, stride, padding, máscara, arquitetura, batch, perda, seed e stage |
| experiments.csv | Lista pré-definida de variantes e experiment_id |
| phase2_protocol.md | Hipóteses, variáveis controladas, orçamento e critérios de seleção |
| windowing_protocol.md | Alinhamento, cauda, sequências curtas, correspondência e agregação |
| README_phase2.md | Execução autorizada, entradas/saídas e regras de acesso |
| environment.yml ou requirements.txt | Ambiente versionado; pode reutilizar o da fase 1 |

### Resultados gerados no desenvolvimento
| Artefacto | Conteúdo |
|---|---|
| window_index_train.csv | Janelas, inícios, comprimentos válidos e viagens |
| coverage_train.csv | Número de contribuições por ponto |
| training_history.csv | Épocas, passos, perda, tempo e diagnóstico |
| checkpoint.pt | Pesos e metadados de cada experiência |
| point_predictions_train.csv | Uma probabilidade agregada por ponto |
| segments_train.csv | Segmentos sem suavização extra |
| metrics_train.json | Métricas diagnósticas, não avaliação final |
| comparison_train.csv | Comparação com baseline e entre variantes no treino |
| run_report.md e run_manifest.json | Decisões, limitações, versões e proveniência |

Previsões por janela e tabela completa de correspondência podem ser volumosas: permitir gravação opcional ou em lotes, mantendo a possibilidade de reconstrução auditável. Não alterar a semântica para poupar memória sem documentar.

## 5. Bibliotecas previstas
- torch: CNN, Dataset/DataLoader, treino, perda mascarada e inferência.
- pandas: índices de janelas, correspondências, resultados e relatórios.
- numpy: índices, máscaras e operações numéricas.
- scikit-learn: métricas comuns quando aplicável.
- matplotlib: gráficos diagnósticos.
- pathlib, json, logging, random, time, hashlib: configuração, execução e proveniência.

Reutilizar o ambiente versionado da fase 1 sempre que possível. No KNIME, importar estas funções em nós Python Script; evitar Execute All sobre ramos reservados.

## 6. Funções propostas
### 01 — `load_phase2_config(path)`

- Módulo: `config.py`.
- Recebe: Configuração JSON.
- Faz: Validar comprimento, sobreposição, estratégia de treino/inferência, orçamento, caminhos e stage.
- Devolve: Configuração validada.

### 02 — `load_phase2_training_data(path, split_manifest)`

- Módulo: `data.py`.
- Recebe: Treino preparado e manifesto fixo da preparação comum.
- Faz: Carregar apenas treino e verificar os IDs. Não carregar conjuntos reservados.
- Devolve: DataFrame de treino.

### 03 — `validate_phase2_inputs(df, feature_manifest)`

- Módulo: `data.py`.
- Recebe: Treino e ordem/unidades das características.
- Faz: Verificar unicidade de point_id, tipos, ausências resolvidas, target e pertença ao treino.
- Devolve: Relatório de validação; falha em erros obrigatórios.

### 04 — `build_training_sequences(df, feature_cols)`

- Módulo: `data.py`.
- Recebe: Treino ordenado e características.
- Faz: Construir sequências por ID e sequence_id, preservando point_id, tempo e rótulos. Não unir gaps.
- Devolve: Registos com X [F,N], y [1,N] e metadados.

### 05 — `create_internal_training_split(sequences, fraction, seed)`

- Módulo: `data.py`.
- Recebe: Apenas sequências do treino oficial.
- Faz: Separar opcionalmente por ID completo para monitorização interna; nunca separar janelas aleatoriamente.
- Devolve: Treino interno, monitorização interna e manifesto interno.

### 06 — `build_experiment_grid(config)`

- Módulo: `experiments.py`.
- Recebe: Lista pré-definida de comprimentos, sobreposições e sementes.
- Faz: Criar configurações identificadas por experiment_id, sem escolher variantes a partir de resultados de teste.
- Devolve: Tabela de experiências.

### 07 — `calculate_stride(window_length, overlap)`

- Módulo: `windowing.py`.
- Recebe: L inteiro positivo e fração de sobreposição.
- Faz: Validar 0 <= overlap < 1 e calcular passo inteiro pela política declarada. Preferir combinações que deem passo exato.
- Devolve: Stride inteiro >= 1 e sobreposição efetiva.

### 08 — `generate_window_index(sequences, window_length, stride)`

- Módulo: `windowing.py`.
- Recebe: Metadados das sequências e parâmetros.
- Faz: Gerar inícios 0, stride, 2*stride, ... enquanto o início for menor que N; terminar após a primeira janela que alcançar o fim. Preencher apenas a última janela se necessário.
- Devolve: Tabela window_id, id, sequence_id, start_index, valid_length e window_length.

### 09 — `build_window_mapping(window_index, sequences)`

- Módulo: `windowing.py`.
- Recebe: Índice de janelas e correspondência dos pontos.
- Faz: Mapear posições válidas para point_id e position_in_window. Representar padding com is_valid=false e sem point_id real.
- Devolve: Tabela de correspondência janela ↔ ponto.

### 10 — `create_window_dataset(sequences, window_index, feature_cols)`

- Módulo: `data.py`.
- Recebe: Sequências, índice e lista de entradas.
- Faz: Criar Dataset PyTorch com extração sob pedido, preservando rótulos por ponto. Aplicar padding de valor fixo, com máscara.
- Devolve: Dataset; cada item contém X [F,L], y [1,L], mask [1,L], window_id e metadados.

### 11 — `create_window_loader(dataset, batch_size, shuffle, seed)`

- Módulo: `data.py`.
- Recebe: Dataset e parâmetros de carregamento.
- Faz: Criar lotes sem misturar pertença aos conjuntos e sem perder metadados.
- Devolve: DataLoader com X [B,F,L], y/mask [B,1,L].

### 12 — `validate_window_coverage(mapping, sequences)`

- Módulo: `checks.py`.
- Recebe: Correspondência e pontos originais.
- Faz: Verificar cobertura de todos os pontos válidos, ausência de cruzamento de IDs/gaps e padding sem associação indevida.
- Devolve: Relatório com cobertura e número de previsões esperado por ponto.

### 13 — `build_phase2_cnn(model_config, n_features)`

- Módulo: `model.py`.
- Recebe: Configuração arquitetural e número de entradas.
- Faz: Reutilizar preferencialmente a implementação totalmente convolucional da fase 1. Preservar L.
- Devolve: Modelo que devolve logits [B,1,L].

### 14 — `masked_binary_loss(logits, targets, mask)`

- Módulo: `training.py`.
- Recebe: Logits, rótulos e máscara de posições válidas.
- Faz: Calcular BCEWithLogitsLoss com reduction=none; somar só posições válidas e dividir pelo seu número. Rejeitar lote sem posições válidas.
- Devolve: Perda escalar diferenciável.

### 15 — `train_window_epoch(model, loader, optimizer, device)`

- Módulo: `training.py`.
- Recebe: Modelo, janelas exclusivamente de treino e otimizador.
- Faz: Treinar com perda mascarada. Registar passos, pontos válidos e posições repetidas pela sobreposição.
- Devolve: Estatísticas por época.

### 16 — `predict_windows(model, loader, device)`

- Módulo: `inference.py`.
- Recebe: Modelo e janelas de um conjunto autorizado, só treino no desenvolvimento.
- Faz: Usar eval/no_grad e sigmoid nos logits. Preservar window_id e posição.
- Devolve: Previsões por janela e posição; padding identificado.

### 17 — `aggregate_point_predictions(window_predictions, mapping, method="mean")`

- Módulo: `reconstruction.py`.
- Recebe: Probabilidades por janela, correspondência e agregação fixa.
- Faz: Ignorar padding e calcular média das probabilidades associadas a cada ponto. Registar número de contribuições.
- Devolve: Tabela com uma linha por point_id, p_fishing e prediction_count.

### 18 — `restore_sequence_predictions(point_predictions, original_metadata)`

- Módulo: `reconstruction.py`.
- Recebe: Probabilidades agregadas e metadados autorizados.
- Faz: Repor ID, sequência, timestamps, target e ordem. Verificar correspondência um-para-um sem perda ou duplicação de pontos.
- Devolve: Tabela reconstruída por ponto original.

### 19 — `evaluate_internal_monitor(model, loader, mapping, metadata, threshold)`

- Módulo: `training.py`.
- Recebe: Apenas monitorização interna proveniente do treino oficial.
- Faz: Inferir, agregar por ponto, reconstruir e usar métricas comuns. Não avaliar pontos sobrepostos como amostras independentes.
- Devolve: Métricas diagnósticas por ponto/segmento e previsões reconstruídas.

### 20 — `train_window_model(model, train_loader, config, internal_monitor=None)`

- Módulo: `training.py`.
- Recebe: Modelo, treino e monitorização interna opcional.
- Faz: Coordenar treino, checkpoints e histórico conforme orçamento explícito. Não aceder a validação/teste oficiais.
- Devolve: Modelo, histórico e manifesto do treino.

### 21 — `evaluate_reconstructed_predictions(predictions, metrics_config)`

- Módulo: `evaluation.py`.
- Recebe: Previsões reconstruídas com target de conjunto autorizado.
- Faz: Reutilizar funções de classes, segmentos e métricas da fase 1, sem suavização adicional.
- Devolve: Métricas por ponto/segmento, fragmentação e erros de fronteira.

### 22 — `compare_experiments(results, baseline_manifest, comparison_config)`

- Módulo: `experiments.py`.
- Recebe: Resultados autorizados, referência da fase 1 e regras de comparação.
- Faz: Verificar mesma divisão, características, unidades e métricas; comparar qualidade e custo no mesmo split.
- Devolve: Tabela comparativa com limitações e configurações.

### 23 — `plot_phase2_results(history, predictions, coverage, output_dir)`

- Módulo: `reporting.py`.
- Recebe: Resultados e metadados apenas de treino no desenvolvimento.
- Faz: Criar curvas, cobertura de janelas, probabilidades reconstruídas e exemplos de fronteiras.
- Devolve: Caminhos dos gráficos.

### 24 — `save_phase2_artifacts(model, config, results, output_dir)`

- Módulo: `artifacts.py`.
- Recebe: Modelo, configuração, resultados e destino.
- Faz: Guardar pesos, histórico, índices, previsões, segmentos, métricas e proveniência. Correspondência completa pode ser regenerável e opcional em disco, mas deve ser auditável.
- Devolve: Manifesto dos artefactos.

### 25 — `freeze_phase2_experiments(experiments, manifests)`

- Módulo: `artifacts.py`.
- Recebe: Lista de variantes e manifestos finalizados.
- Faz: Congelar modelos, regras, agregação e protocolo antes de pedir acesso reservado.
- Devolve: Manifesto versionado; não concede acesso.

### 26 — `run_phase2_development(config)`

- Módulo: `run_phase2.py`.
- Recebe: Configuração de desenvolvimento com treino apenas.
- Faz: Coordenar dados, janelas, testes, treino, reconstrução e comparação diagnóstica. Parar antes das etapas oficiais.
- Devolve: Relatório e caminhos dos artefactos.

### 27 — `run_phase2_authorized_validation(frozen_experiments, authorization)`

- Módulo: `reserved_evaluation.py`.
- Recebe: Variantes congeladas e autorização explícita externa do utilizador.
- Faz: Executar seleção formal na validação com preparação já aprendida no treino. Não usar como debugging.
- Devolve: Relatório de seleção e decisões versionadas.

### 28 — `run_phase2_authorized_final_evaluation(frozen_protocol, authorization)`

- Módulo: `reserved_evaluation.py`.
- Recebe: Protocolo/modelos finais e nova autorização explícita.
- Faz: Avaliar no teste a lista pré-registada de variantes e baseline, sem alterar decisões a partir dos resultados.
- Devolve: Relatório final comparativo.

## 7. Protocolo inicial das experiências
Comprimento inicial proposto: L=64 pontos, ainda não validado.

| Variante | Entrada | Overlap | Stride | Pós-processamento |
|---|---|---|---|---|
| Baseline | Viagem completa | Não aplicável | Não aplicável | Não |
| J0 | Janela 64 | 0% | 64 | Não |
| J25 | Janela 64 | 25% | 48 | Não |
| J50 | Janela 64 | 50% | 32 | Não |
| J75 | Janela 64 | 75% | 16 | Não |

Definir antes de executar se o overlap varia no treino, na inferência ou em ambos. Na comparação inicial pode variar em ambos; nesse caso o efeito combina treino e inferência e deve ser descrito assim. Uma análise posterior pode fixar o modelo e variar só as janelas de inferência para isolar a agregação.

Manter as restantes escolhas tão constantes quanto possível. Registar diferenças inevitáveis de batch e memória em relação à viagem completa.

### Orçamento e ponderação
- A mesma quantidade de épocas não implica o mesmo número de atualizações quando o overlap muda.
- Fixar a política de comparação: épocas, passos, orçamento temporal ou outra estratégia explícita; reportar também as outras contagens.
- A perda mascarada padrão conta cada ocorrência válida em janela. Pontos repetidos podem contribuir várias vezes no treino; não afirmar que todos os pontos têm peso idêntico.
- Não introduzir pesos por cobertura sem os declarar como alteração experimental. A configuração inicial continua sem pesos de classe nem reamostragem.
- Para monitorização interna verdadeiramente independente, transformações aprendidas devem ser ajustadas apenas no treino interno. Um normalizador aprendido no treino oficial inteiro torna essa monitorização apenas diagnóstica, salvo reajuste correto.

## 8. Janela final, sequências curtas e agregação
Proposta determinística:
1. Começar no índice zero de cada sequência.
2. Avançar pelo stride escolhido.
3. Parar depois da primeira janela que atinja o fim.
4. Preencher a cauda se necessário e criar máscara.
5. Uma sequência mais curta que L produz uma única janela preenchida.
6. Confirmar que todos os pontos reais aparecem pelo menos uma vez.
7. Calcular a média simples das probabilidades válidas por point_id.
8. Aplicar o limiar de classificação só depois dessa média.

Não adicionar uma janela final alinhada à direita por conveniência sem a declarar: pode criar sobreposição também na variante nominalmente 0%. Não confundir o padding externo das janelas com o padding interno das convoluções.

## 9. Testes técnicos obrigatórios
Só treino ou dados sintéticos:
- Cálculo de stride e rejeição de configurações inválidas.
- Sequências com N<L, N=L, N>L e cauda incompleta.
- Sequências curtas e múltiplas sequências da mesma viagem.
- Ausência de janelas que atravessem viagens ou gaps.
- Máscara correta e padding sem point_id válido.
- Alterar logits em posições mascaradas não muda a perda diretamente calculada nessas posições.
- Cobertura completa dos pontos e ausência de duplicações após agregação.
- Média por ponto validada com probabilidades artificiais e resultado esperado conhecido.
- Reconstrução com ordem, timestamps e target preservados.
- Métricas reutilizadas da fase 1, com exemplos de referência.
- Forward/backward finitos e checkpoint com previsões equivalentes após recarga.
- Teste de permissões: desenvolvimento rejeita dados e IDs reservados.

## 10. Organização dos módulos
```text
src/phase2/
├── config.py
├── data.py
├── windowing.py
├── model.py                 # preferir importar modelo comum
├── training.py
├── inference.py
├── reconstruction.py
├── evaluation.py            # reutiliza métricas/segmentos da fase 1
├── experiments.py
├── checks.py
├── reporting.py
├── artifacts.py
├── run_phase2.py
└── reserved_evaluation.py

tests/
├── test_window_index.py
├── test_padding_masks.py
├── test_window_coverage.py
├── test_masked_loss.py
├── test_point_reconstruction.py
└── test_phase2_access_policy.py
```

## 11. Fluxo de desenvolvimento
```text
Configuração e manifesto de treino
→ carregar apenas treino preparado
→ validar dados e criar sequências
→ partição interna opcional por ID, apenas dentro do treino
→ gerar configurações de experiências
→ gerar índices e correspondência das janelas
→ validar máscaras e cobertura com testes sintéticos/treino
→ criar Dataset/DataLoader e CNN
→ treinar com perda mascarada
→ inferir nas janelas autorizadas
→ agregar probabilidades por ponto
→ reconstruir viagens
→ classes e segmentos sem suavização extra
→ métricas diagnósticas e comparação no mesmo split
→ guardar e congelar configurações/modelos
→ PARAR e pedir autorização para seleção formal
```

## 12. Critérios de aceitação
- Um ponto reconstruído por ponto real válido.
- Nenhuma janela atravessa IDs, gaps ou splits.
- Padding excluído da perda, agregação e métricas.
- Protocolo do overlap, treino/inferência e orçamento explícitos.
- Mesma divisão e definições de métricas da baseline.
- Nenhum uso reservado para desenvolvimento, escolha informal ou debugging.
- Nenhuma suavização temporal adicional nesta fase.
- Limitações e efeitos das bordas das janelas descritos, sem prometer ganhos antes de os medir.
