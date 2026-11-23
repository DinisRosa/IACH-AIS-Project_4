# Preparação comum às duas fases — política obrigatória contra leakage

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## Estado e âmbito
Versão revista para orientar o agente que vai implementar o projeto. Este documento atualiza a preparação comum e estabelece regras de acesso aos dados que prevalecem sobre instruções menos restritivas nos restantes documentos do projeto.

A palavra “testes” neste documento inclui experiências de desenvolvimento, execuções exploratórias, debugging, smoke tests, testes de integração com dados reais, benchmarks, inspeções manuais e ensaios de modelos. Não deve ser confundida com a avaliação final no conjunto de teste.

## 1. Regra obrigatória para o agente
Durante a implementação e o desenvolvimento, usar EXCLUSIVAMENTE o conjunto de treino ou dados sintéticos independentes para executar testes e experiências.

É proibido usar validação ou teste, mesmo em pequenas amostras, para:
- Verificar se o código funciona ou depurar erros.
- Escolher ou alterar características, regras de limpeza, imputação ou limites de outliers.
- Inspecionar distribuições, exemplos, trajetórias, rótulos ou previsões.
- Escolher arquitetura, hiperparâmetros, janelamento, agregação ou limiares.
- Ajustar normalizadores, imputadores, calibradores ou qualquer transformação aprendida.
- Fazer benchmarks de desempenho ou consumo de memória durante o desenvolvimento.
- Decidir mudanças a partir de erros ou métricas observados nesses conjuntos.

O agente não pode ativar acesso a validação ou teste por iniciativa própria. O acesso exige autorização explícita do utilizador e a passagem para a etapa apropriada, descrita na secção 8.

## 2. Divisão antecipada e exceção estritamente estrutural
A divisão por ID completo deve acontecer antes do estudo exploratório, limpeza informada pelos dados, recálculo exploratório de variáveis ou qualquer treino.

Antes de separar os dados, só é permitido o mínimo técnico necessário para ler e dividir o ficheiro:
1. Confirmar que o ficheiro é legível e contém a coluna id.
2. Ler id como texto e recolher os IDs completos únicos.
3. Rejeitar IDs ausentes ou inválidos para atribuição de conjunto, sem analisar outras características.
4. Atribuir os IDs aos conjuntos usando proporções e semente previamente fixadas, sem usar rótulos, métricas ou características.
5. Encaminhar todas as linhas de cada ID para o seu conjunto.
6. Verificar invariantes estruturais: IDs sem interseção, atribuição única e conservação do número de linhas.

Não executar study_csv no dataset completo. Não mostrar exemplos, estatísticas por classe ou distribuições dos conjuntos reservados. A verificação de cabeçalhos e invariantes de separação não autoriza análise dos valores reservados.

## 3. Entidade e divisão fixa
- Cada id completo representa uma viagem independente.
- Viagens diferentes do mesmo navio podem pertencer a conjuntos diferentes, por decisão do projeto.
- Todas as linhas, sequências e futuras janelas do mesmo ID ficam no mesmo conjunto.
- Proporções propostas: aproximadamente 70% dos IDs para treino, 15% para validação e 15% para teste.
- A semente e as proporções devem ser fixadas antes de analisar os resultados.
- Guardar a tabela id → split e reutilizá-la em todas as fases e experiências.
- Não refazer a divisão porque um resultado não agradou ou porque um conjunto ficou mais difícil.

Esta divisão avalia generalização entre viagens e não garante generalização para navios nunca observados. Não apresentar os resultados como avaliação por navio independente.

## 4. Workflow de desenvolvimento autorizado
```text
01 — Leitura técnica mínima do CSV e dos IDs
                         ↓
02 — Divisão por ID completo, com semente fixa
                         ↓
03 — Persistência da divisão e isolamento de validação/teste
                         ↓
04 — Carregamento exclusivo do treino para desenvolvimento
                         ↓
05 — Estudo estrutural e exploratório do treino
                         ↓
06 — Interpretação de t e ordenação dentro de cada viagem
                         ↓
07 — Recálculo de time gap, distância e velocidade no treino
                         ↓
08 — Comparação entre valores originais e recalculados no treino
                         ↓
09 — Definição e teste das regras de limpeza no treino
                         ↓
10 — Identificação de sequências válidas e recálculo após limpeza
                         ↓
11 — Conversão dos rótulos e seleção das características
                         ↓
12 — Ajuste de transformações apenas no treino
                         ↓
13 — Testes da CNN, janelas e reconstrução apenas no treino
                         ↓
14 — Congelamento da implementação e das regras
                         ↓
15 — Paragem obrigatória: pedir autorização para seleção formal
```

## 5. Preparação detalhada — apenas treino nesta etapa

### Importação e estudo
Usar load_csv, validate_schema, parse_timestamps, prepare_trip_order, study_csv e plot_data_summary apenas no ficheiro de treino após a separação.

Preservar os valores originais. Criar point_id estável; pode ser composto pelo ID da viagem e posição original da linha. Nunca usar IDs como entradas da CNN.

### Recálculo
- time_gap_calc_s: diferença em segundos entre instantes consecutivos do mesmo ID ou sequência válida.
- speed_calc_mps: distância convertida para metros dividida pelo intervalo em segundos.
- distance_gap_calc_m: calcular apenas depois de confirmar método, referencial e unidades.
- Não assumir unidades nem sistema de coordenadas pelo nome das colunas.
- Não calcular diferenças entre viagens ou através de quebras temporais.
- Confirmar no treino a relação entre euc_speed original e velocidade calculada.

### Limpeza
Separar deteção de problemas de exclusão de linhas. Guardar auditoria das ações. Estimar limites estatísticos apenas no treino.

Após remover pontos, recalcular variáveis dependentes do predecessor. Não reutilizar uma distância original se já não corresponder ao novo intervalo.

Definir no treino a política para primeiros pontos de sequência, ausências e intervalos não positivos. Não transformar automaticamente uma ausência num zero físico.

### Rótulos
```text
02-fishing e 04-fishing → 1
01-sailing, 03-sailing e 05-sailing → 0
```
Preservar label original. Rótulos desconhecidos geram um problema explícito.

### Características iniciais propostas
```text
speed_calc_mps
signed_turn
time_gap_calc_s
distanceToShore
```
Guardar coordenadas, timestamps e IDs como metadados. Escolhas ou alterações durante desenvolvimento só podem usar treino.

### Transformações aprendidas
Ajustar StandardScaler, imputadores, limites estatísticos e quaisquer outros objetos aprendidos apenas no treino. Guardar parâmetros e ordem das características.

Não calcular estatísticas conjuntas de treino, validação e teste, mesmo que os rótulos estejam ocultos.

## 6. Testes automatizados
- Preferir dados sintéticos para testar diferenças temporais, duplicados, gaps, janelas, máscaras e reconstrução.
- Usar apenas treino quando forem necessários dados reais.
- Criar amostras pequenas e casos de integração exclusivamente a partir do treino.
- Se for necessária avaliação interna durante desenvolvimento, criar partições internas apenas dentro do treino, mantendo cada ID inteiro numa partição. Os conjuntos oficiais de validação e teste continuam bloqueados.
- Métricas obtidas no treino são diagnósticas e não uma estimativa independente do desempenho final.
- Testar invariantes: nenhuma janela atravessa IDs; não há diferenças através de gaps; padding não conta na perda ou métricas; cada ponto válido recebe uma previsão reconstruída.

## 7. Contratos das funções e proteção de acesso
Ordem obrigatória de alto nível:
```text
create_split_manifest_from_ids()
→ materialize_raw_splits()
→ validate_split_manifest()
→ load_training_data()
→ funções de estudo, recálculo, limpeza e normalização
→ testes de desenvolvimento
→ freeze_preprocessing_artifacts()
→ aguardar autorização
```

Estas funções de isolamento complementam a API anterior:

| Função | Recebe | Devolve / responsabilidade |
|---|---|---|
| create_split_manifest_from_ids | Caminho, proporções e seed | Tabela id → split; ler apenas o necessário para a divisão |
| materialize_raw_splits | Caminho do CSV, manifesto e destino | Ficheiros separados, sem estudo exploratório |
| validate_split_manifest | Manifesto e contagens técnicas | Confirma atribuição única e IDs sem interseção |
| load_training_data | Caminho do treino | DataFrame de treino; é o carregador padrão do desenvolvimento |
| freeze_preprocessing_artifacts | Configuração, regras e objetos aprendidos | Versão identificável e persistida dos artefactos |

Regras para a API já definida:
- split_trip_ids e apply_split passam para o início do processo.
- study_csv, gráficos e comparações recebem apenas treino durante desenvolvimento.
- fit_scaler recebe apenas treino e deve verificar a origem do conjunto sempre que possível.
- transform_features em validação/teste fica bloqueada até autorização para a etapa respetiva.
- run_preparation usa por defeito stage="development" e allowed_splits=["train"].
- Ativar selection ou final_evaluation exige decisão explícita do utilizador; não basta o agente mudar uma flag.
- Não devolver dados reservados como DataFrames acessíveis no resultado normal da execução de desenvolvimento; devolver apenas referências aos ficheiros isolados.

No KNIME, manter os ramos reservados desconectados ou não executáveis no workflow de desenvolvimento. Não deixar um Execute All carregar automaticamente validação e teste. O isolamento por permissões, quando disponível, é preferível a depender apenas de convenções no código.

## 8. Etapas posteriores: validação e teste não são a mesma coisa

### Etapa A — Desenvolvimento: autorizada agora
Apenas treino ou dados sintéticos. Implementação, debugging, testes e ensaios são feitos nesta etapa.

### Etapa B — Seleção formal: requer autorização explícita
Depois de testar e congelar a implementação, a validação pode ser usada exclusivamente para as decisões experimentais previstas, como seleção de hiperparâmetros, checkpoint, limiar ou calibração, conforme um protocolo previamente definido.

Aplicar aos dados reservados as regras e transformações já definidas, sem reajustar normalizadores ou limiares estatísticos nesses dados. A análise de validação não é uma autorização para usá-la como conjunto de debugging.

Se surgir um erro de código, voltar a reproduzi-lo e corrigi-lo com treino ou dados sintéticos; documentar qualquer exposição a dados reservados. Não afirmar que o conjunto continua totalmente intocado se já foi inspecionado.

### Etapa C — Avaliação final: requer nova autorização explícita
Executar apenas depois de congelar modelos, parâmetros, regras de preparação e protocolo de comparação.

O teste serve para medir e reportar resultados finais, não para escolher modelos, características ou corrigir decisões. Se houver várias variantes previstas, congelar a lista antes de avaliar todas; não adicionar variantes em resposta às métricas do teste.

Se os resultados do teste forem usados para mudar a solução, esse conjunto deixou de ser uma avaliação final intocada. Documentar o ocorrido e não ocultar essa limitação.

## 9. Artefactos a guardar
- Manifesto fixo da divisão por ID.
- Dados originais separados e isolados por conjunto.
- Dados de treino tratados e versão física não normalizada.
- Relatórios de estudo e limpeza do treino.
- Unidades, fórmulas, regras, limiares e decisões.
- Lista ordenada de características e objetos ajustados no treino.
- Seed, versões das bibliotecas e identificação da versão de código/configuração.
- Registo de autorizações para acesso às etapas reservadas.

## 10. Critérios de aceitação para o agente
- [ ] A divisão foi criada antes de qualquer estudo exploratório.
- [ ] Não há ID completo em mais de um conjunto.
- [ ] Todos os testes de desenvolvimento usam treino ou dados sintéticos.
- [ ] Nenhuma amostra de validação/teste foi usada para debugging.
- [ ] Os artefactos aprendidos usam apenas treino.
- [ ] A mesma divisão será usada na CNN completa e na CNN com janelas.
- [ ] Validação e teste permanecem bloqueados até autorização explícita.
- [ ] Relatórios distinguem diagnóstico no treino, seleção na validação e avaliação final.
