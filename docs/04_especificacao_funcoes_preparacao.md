# Especificação das funções — preparação dos dados AIS

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## Objetivo
Definir o contrato de cada função antes da implementação: o que recebe, o que faz e o que devolve. Esta é uma proposta de API, não código já implementado. Alguns parâmetros opcionais foram acrescentados para tornar explícitos unidades, regras e agrupamentos.

## Decisões comuns
- A entidade é a viagem identificada pelo `id` completo.
- Viagens diferentes do mesmo navio podem pertencer a conjuntos diferentes.
- Todas as linhas, sequências e futuras janelas do mesmo ID ficam no mesmo conjunto.
- Os dados originais são preservados; colunas calculadas têm nomes distintos e unidades explícitas.
- Cada ponto recebe um `point_id` estável antes de alterações na ordenação ou exclusões.
- Funções de transformação devolvem uma cópia, sem alterar silenciosamente o DataFrame recebido.
- Diagnóstico não implica exclusão automática.
- Funções não tratam ausências, projeções ou unidades desconhecidas por adivinhação.
- Ajustes aprendidos a partir dos dados usam apenas treino.

## Bibliotecas previstas
| Biblioteca | Papel |
|---|---|
| pandas | Leitura, tabelas, datas, agrupamentos e exportação |
| numpy | Cálculos numéricos, ângulos e máscaras de validade |
| scikit-learn | Divisão de IDs e StandardScaler |
| matplotlib | Gráficos de diagnóstico |
| pyproj, opcional | Distâncias geodésicas e transformações com referencial confirmado |
| pathlib, json, logging, pickle | Caminhos, configuração, registos e persistência; biblioteca padrão |

PyTorch e funções de CNN/janelamento não fazem parte deste módulo de preparação. No KNIME, os nós Python Script podem importar e chamar estas funções.

## Estruturas usadas nos contratos
- `df`: pandas.DataFrame; uma linha por ponto.
- `issues_df`: tabela de problemas, idealmente com point_id, id, rule/check, severity e message.
- `audit_df`: tabela de ações executadas e respetivos motivos.
- `config`: dicionário com parâmetros explícitos e serializáveis sempre que possível.
- `feature_cols`: lista ordenada, decidida como speed_calc_mps, signed_turn, time_gap_calc_s e distanceToShore (REV-019).
- `split_table`: tabela com id único e split em train, validation ou test.

## 01 — `load_csv(path, read_options=None)`

**Módulo:** `data_io.py`

### Recebe
path: caminho do CSV. read_options: opções de leitura opcionais.

### Faz
Ler o CSV com pandas; preservar id como texto e os valores originais. Não limpar nem recalcular nesta função.

### Devolve
DataFrame com os dados originais.

### Cuidados
Erros de leitura ou ficheiro inexistente devem ser explícitos.

## 02 — `validate_schema(df)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame original.

### Faz
Verificar colunas obrigatórias, nomes duplicados e compatibilidade dos tipos. Tipos originais de t podem ser texto antes da conversão.

### Devolve
DataFrame de problemas com check, column, severity, count e message; pode estar vazio.

### Cuidados
Colunas obrigatórias ausentes impedem a continuação. Não modificar df.

## 03 — `parse_timestamps(df, timestamp_format=None)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame com t e formato opcional de data/hora.

### Faz
Converter t para datetime; preservar t_original. Identificar valores não interpretáveis. Não assumir um fuso horário que não esteja documentado.

### Devolve
Tuplo (df_updated, issues_df).

### Cuidados
Não eliminar automaticamente linhas com datas inválidas.

## 04 — `prepare_trip_order(df)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame com id e t interpretado.

### Faz
Criar point_id único antes de ordenar, preservando um identificador existente se já for válido. Ordenar de forma estável por id, t e point_id.

### Devolve
DataFrame ordenado, com point_id.

### Cuidados
Não misturar IDs. Assinalar empates temporais em vez de os resolver silenciosamente.

## 05 — `study_csv(df)`

**Módulo:** `data_study.py`

### Recebe
DataFrame, preferencialmente com timestamps interpretados e ordenação preparada.

### Faz
Resumir pontos, IDs, classes, valores em falta, duplicados, pontos e duração por viagem. Resumir intervalos temporais se estiverem disponíveis.

### Devolve
Dicionário de DataFrames: overview, missing_values, class_counts, trip_summary, duplicate_summary e, quando disponível, time_gap_summary.

### Cuidados
Diagnóstico apenas: não altera dados nem escolhe limiares automaticamente.

## 06 — `plot_data_summary(df, output_dir)`

**Módulo:** `data_study.py`

### Recebe
DataFrame e diretório de destino.

### Faz
Criar gráficos de classes, pontos e duração por viagem e distribuições das variáveis disponíveis. Usar amostragem documentada se necessário.

### Devolve
Lista de caminhos dos gráficos guardados.

### Cuidados
Não executar transformações de limpeza a partir dos gráficos.

## 07 — `calculate_time_gap(df, group_cols=None)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame ordenado; group_cols indica id, ou id e sequence_id após separar sequências.

### Faz
Calcular a diferença entre t atual e anterior em segundos, apenas dentro do grupo.

### Devolve
DataFrame com time_gap_calc_s.

### Cuidados
Primeiro ponto de cada grupo: valor ausente. Intervalos não positivos ficam disponíveis para diagnóstico, não para divisão.

## 08 — `calculate_distance_gap(df, method, crs=None, group_cols=None)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame ordenado, método explícito, referencial quando aplicável e colunas de agrupamento.

### Faz
Método projected: distância euclidiana em x/y com CRS e unidade linear confirmados, convertendo para metros. Método geodesic: distância entre longitude/latitude com elipsoide confirmado. Preservar distance_gap original.

### Devolve
DataFrame com distance_gap_calc_m; registar o método e referencial na configuração.

### Cuidados
Não inferir metros apenas pelo nome x/y. Primeiro ponto do grupo sem distância. Métodos diferentes podem não reproduzir a distância original.

## 09 — `calculate_speed(df, distance_col, time_col, distance_unit)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame, coluna de distância, coluna de intervalo em segundos e unidade de distância confirmada.

### Faz
Converter distância para metros e dividir apenas por intervalos positivos e finitos. Criar também conversão para nós se solicitada na configuração.

### Devolve
Tuplo (df_updated, issues_df), com speed_calc_mps e opcionalmente speed_calc_knots.

### Cuidados
Não substituir divisões inválidas por zero. Não assumir a unidade do distance_gap original.

## 10 — `compare_original_and_calculated(df, comparisons)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame e lista de comparações, cada uma com colunas original/calculada, conversão de unidades e tolerâncias.

### Faz
Comparar apenas pares válidos referentes ao mesmo intervalo e na mesma unidade. Calcular diferenças absolutas e relativas; tratar referências zero explicitamente.

### Devolve
Dicionário com summary e differences, ambos DataFrames.

### Cuidados
Comparar time_gap, distance_gap e euc_speed apenas após confirmar a convenção de cada coluna.

## 11 — `flag_data_issues(df, rules)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame e regras explícitas, incluindo limites e respetivas unidades.

### Faz
Detetar dados em falta, duplicados exatos, empates temporais, coordenadas inválidas, intervalos não positivos e valores suspeitos definidos nas regras.

### Devolve
DataFrame longo de problemas: point_id, id, rule, severity, observed_value e message.

### Cuidados
Não apagar linhas. Limiares estatísticos devem ser estimados apenas no treino; regras fixas devem estar documentadas.

## 12 — `clean_data(df, rules)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame e regras que mapeiam cada problema para manter, excluir ou outra ação explicitamente definida.

### Faz
Aplicar decisões aprovadas usando a mesma lógica de flag_data_issues. Preservar point_id e registar exclusões ou alterações.

### Devolve
Tuplo (clean_df, audit_df). audit_df inclui point_id, rule, action e reason.

### Cuidados
Não eliminar indiscriminadamente todas as linhas com algum valor ausente. A execução repetida não deve alterar dados já limpos sem motivo.

## 13 — `assign_sequence_ids(df, max_gap_s)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame ordenado e limiar fixado/documentado em segundos, ou None se não se pretender cortar por duração.

### Faz
Criar uma nova sequência no início de cada viagem e após uma lacuna superior ao limiar. Assumir que timestamps inválidos e não crescentes já foram resolvidos.

### Devolve
DataFrame com sequence_id único ou combinado com id.

### Cuidados
Não une viagens nem muda o split. Todas as sequências de um ID permanecem no mesmo conjunto.

## 14 — `recalculate_sequence_features(df, feature_config)`

**Módulo:** `trajectory.py`

### Recebe
DataFrame limpo com sequence_id e configuração das variáveis, unidades e métodos.

### Faz
Reexecutar time gap, distâncias e velocidade dentro de cada sequência após exclusões. Recalcular também bearing/signed_turn se essa opção estiver implementada e as suas definições confirmadas.

### Devolve
Tuplo (df_updated, issues_df).

### Cuidados
Se forem removidos pontos, a distância original pode deixar de corresponder ao novo predecessor: não a reutilizar cegamente. Preservar originais e identificar variáveis desatualizadas.

## 15 — `encode_labels(df)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame com label original.

### Faz
Criar target: 02-fishing e 04-fishing para 1; 01-sailing, 03-sailing e 05-sailing para 0. Manter label.

### Devolve
Tuplo (df_updated, issues_df).

### Cuidados
Rótulos desconhecidos ficam assinalados; nunca convertê-los silenciosamente em navegação.

## 16 — `split_trip_ids(df, ratios=(0.70, 0.15, 0.15), seed=42)`

**Módulo:** `splitting.py`

### Recebe
DataFrame com id, três proporções e semente.

### Faz
Dividir a lista de IDs completos únicos, não as linhas. Criar treino, validação e teste de forma reprodutível.

### Devolve
DataFrame com uma linha por id e coluna split: train, validation ou test.

### Cuidados
Validar soma das proporções e número suficiente de IDs. As percentagens referem-se a viagens, não a pontos. Viagens do mesmo navio podem ficar em conjuntos diferentes, conforme a decisão do projeto.

## 17 — `apply_split(df, split_table)`

**Módulo:** `splitting.py`

### Recebe
DataFrame de pontos e tabela id → split.

### Faz
Associar o conjunto a cada ponto por junção muitos-para-um, preservando a ordem e point_id.

### Devolve
DataFrame com split.

### Cuidados
Falhar se houver IDs em falta ou duplicados na tabela de divisão. Não multiplicar linhas na junção.

## 18 — `validate_splits(df)`

**Módulo:** `splitting.py`

### Recebe
DataFrame com id, point_id e split.

### Faz
Verificar que cada ID aparece em exatamente um conjunto, que todos os pontos têm split e que os conjuntos esperados existem. Resumir pontos, viagens e classes por conjunto.

### Devolve
DataFrame de resumo; lançar ValueError se alguma invariável obrigatória falhar.

### Cuidados
Não impor separação pelo prefixo do navio: a decisão atual é separar pelo ID completo.

## 19 — `select_features(df, feature_cols)`

**Módulo:** `preprocessing.py`

### Recebe
DataFrame e lista ordenada de características.

### Faz
Confirmar existência, tipos numéricos e política para valores não finitos. Separar entradas, resposta e metadados sem perder o alinhamento.

### Devolve
Dicionário com X (DataFrame), y (Series target) e metadata (DataFrame), com índices alinhados.

### Cuidados
Proibir label, target, id e point_id como características. Preservar ordem explícita das entradas. Política de ausentes deve ser resolvida antes de alimentar a CNN.

## 20 — `fit_scaler(train_df, feature_cols)`

**Módulo:** `scaling.py`

### Recebe
Apenas os dados de treino e a lista ordenada de características.

### Faz
Ajustar StandardScaler nas características. Não normalizar target, IDs ou timestamps.

### Devolve
StandardScaler ajustado.

### Cuidados
Verificar entradas e ordem das características. Qualquer imputação aprendida também deve ser ajustada só no treino.

## 21 — `transform_features(df, scaler, feature_cols)`

**Módulo:** `scaling.py`

### Recebe
Dados de qualquer split, normalizador já ajustado e lista ordenada de características.

### Faz
Aplicar apenas transform, sem fit. Manter metadados, rótulos e correspondência dos pontos; preservar as versões físicas não normalizadas no dataset tratado.

### Devolve
DataFrame com as características transformadas e restantes colunas preservadas, ou uma cópia de modelagem explicitamente identificada.

### Cuidados
Validar ordem e número de características. Guardar separadamente o dataset físico e o normalizado para evitar normalização dupla.

## 22 — `save_prepared_data(datasets, output_dir)`

**Módulo:** `data_io.py`

### Recebe
Dicionário com dados físicos, dados para modelagem por split e tabela de divisão; diretório de saída.

### Faz
Exportar tabelas sem índices artificiais, preservando colunas de identificação. CSV é o formato inicial; Parquet pode ser opcional com dependência apropriada.

### Devolve
Dicionário que associa cada artefacto ao caminho guardado.

### Cuidados
Confirmar diretório, escrita e nomes claros. Não sobrescrever o CSV de origem.

## 23 — `save_preparation_report(reports, output_dir)`

**Módulo:** `data_io.py`

### Recebe
Dicionário de resumos, problemas, comparações e auditoria de limpeza.

### Faz
Exportar tabelas e um resumo legível das decisões, contagens e avisos.

### Devolve
Dicionário de caminhos dos relatórios.

### Cuidados
Incluir contagens antes/depois, exclusões por motivo e unidades ainda por confirmar.

## 24 — `save_preprocessing_artifacts(scaler, config, output_dir)`

**Módulo:** `data_io.py`

### Recebe
Normalizador ajustado, configuração e diretório de saída.

### Faz
Guardar o normalizador e a configuração: características em ordem, unidades, regras, seed, métodos e versões das bibliotecas.

### Devolve
Dicionário de caminhos dos artefactos.

### Cuidados
Se usar pickle, carregar apenas ficheiros de origem confiável. A tabela de divisão é guardada por save_prepared_data.

## 25 — `run_preparation(config)`

**Módulo:** `prepare_data.py`

### Recebe
Configuração completa com caminhos, regras, métodos, características, divisão e seed.

### Faz
Coordenar leitura, diagnóstico, limpeza, recálculo, divisão, seleção, normalização e exportação. Interromper em erros obrigatórios e agregar avisos.

### Devolve
Dicionário com datasets, split_table, scaler, reports e paths.

### Cuidados
Não conter toda a lógica de cálculo: chamar as funções especializadas. Não estimar parâmetros com validação ou teste.

## Ordem geral de execução revista
```text
manifesto de IDs → separação técnica e isolamento → carregar só treino
→ verificar esquema → datas/ordenação → estudo exclusivo do treino
→ recálculos → limpeza auditável → sequências → recálculo pós-limpeza
→ rótulos → partição interna opcional → seleção → fit só no treino adequado
→ transformação de dados autorizados → exportação → parar antes dos reservados
```

## Política para pontos iniciais e ausências
O primeiro ponto de cada sequência não tem diferenças anteriores calculáveis. O segundo não tem signed_turn, porque depende do rumo do primeiro intervalo. Política de ausências (REV-022): nenhuma linha é removida. Os valores em falta nas entradas são preenchidos com zero e marcados por um indicador de ausência (máscara) por característica, para distinguir ausência de um valor físico zero. O primeiro ponto de cada viagem mantém-se, com time_gap, speed e signed_turn ausentes. O segundo mantém-se, com signed_turn ausente. Se os pontos iniciais entram ou não na função de perda fica por confirmar pelo utilizador.

## Condições mínimas antes de exportar para a CNN
- IDs sem sobreposição entre conjuntos.
- Rótulos reconhecidos e entradas numéricas com política de ausências resolvida.
- Uma correspondência inequívoca entre cada linha e point_id.
- Características alinhadas com o ponto/intervalo a que se referem.
- Nenhuma diferença calculada através de viagens ou quebras temporais.
- Unidades documentadas e comparação entre originais e calculados revista.
- Normalizador aprendido apenas no treino.
- Mesma ordem de características em todos os conjuntos.
- Versões físicas e normalizadas claramente distinguidas.

## Organização dos módulos
```text
src/
├── data_io.py
├── data_study.py
├── preprocessing.py
├── trajectory.py
├── splitting.py
├── scaling.py
└── prepare_data.py
```
