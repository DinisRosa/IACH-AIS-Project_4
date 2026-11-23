# 00 — Contexto do projeto e dicionário dos dados AIS

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## 1. Para que serve este documento
Ponto de entrada para o agente de implementação. Resume a proposta PDF e regista as decisões posteriores do utilizador. Não confundir objetivos futuros da proposta com funcionalidades já implementadas.

Fontes deste resumo: proposta «Segmentação semântica de trajetórias AIS para deteção de atividade de pesca usando janelas sobrepostas e pós-processamento temporal», de Dinis Soveral Botelho Rosa; esclarecimentos do utilizador nesta conversa; cabeçalho e linha real de CSV fornecidos pelo utilizador.

As unidades não documentadas são apresentadas como hipóteses, nunca como factos confirmados. Não assumir que existe acesso ao CSV completo apenas por conhecer uma linha.

## 2. Resumo rápido para o agente
- Problema: identificar intervalos de pesca e navegação em trajetórias AIS anotadas.
- Tipo de tarefa: segmentação temporal binária supervisionada, com uma previsão por ponto e posterior agrupamento em segmentos.
- Entidade operacional: viagem identificada pelo id completo, por exemplo 211477000-2.
- Dataset: **123 IDs únicos** e **1 026 279 linhas**, verificados no ficheiro (REV-001, confirmados por `scripts/verify_trip_count.py`, REV-007). O nome e a página do Zenodo indicam 128 (`128_fishing_trajs.csv`), mas o ficheiro local tem 123 IDs. O `latex/proposta_IAHC_DINIS_ROSA.pdf` (versão entregue ao professor, não se altera) diz 128; o `latex/proposta_pt.tex` diz 123.
- Esquema observado: 13 colunas no total, incluindo label; portanto, 12 colunas além do rótulo, não 13 mais o rótulo.
- Implementação: Python; KNIME pode servir como orquestrador dos componentes e nós Python Script.
- Modelo atual: CNN 1D totalmente convolucional que devolve uma probabilidade por ponto.
- Ordem: preparação comum → CNN com viagem completa → CNN com janelamento/sobreposição.
- Durante desenvolvimento: apenas treino oficial ou dados sintéticos. Validação e teste ficam isolados até autorização explícita do utilizador. Exceção autorizada (REV-015, 2026-11-23): validação e teste foram processados só para preparação (bases limpas e contagens de linhas e viagens), sem análise de resultados nem uso para escolher modelos ou regras.

## 3. Contexto e objetivo principal
A proposta enquadra o trabalho no apoio à monitorização da atividade de pesca e à fiscalização, motivado pelo problema da pesca ilegal, não declarada e não regulamentada (IUU).

O objetivo técnico é desenvolver segmentações robustas e interpretáveis que identifiquem, ao longo de cada viagem, onde começam e acabam períodos de pesca e navegação. A investigação pretende avaliar se janelas sobrepostas e pós-processamento temporal melhoram a qualidade, as fronteiras e a estabilidade dessas segmentações.

Detetar comportamento compatível com pesca não demonstra ilegalidade. O modelo não verifica, por si só, licenças, quotas, zonas autorizadas ou infrações. A decisão de fiscalização continua humana.

## 4. Proposta original versus decisões atuais
| Aspeto | Proposta PDF | Plano atual acordado |
|---|---|---|
| Modelo principal | Rede recorrente ou convolucional, possivelmente com atenção; arquitetura em aberto | Começar com CNN 1D |
| Unidade da divisão | Navio: todas as suas viagens no mesmo conjunto | ID completo: cada viagem é uma entidade independente |
| Primeira experiência | Foco em janelas e pós-processamento | Baseline com viagem completa, sem janelamento externo |
| Segunda experiência | Janelas sobrepostas | Janelas com 0%, 25%, 50% e 75% de sobreposição |
| Saída do modelo | Texto refere classificação de janelas, com objetivo de segmentação | Probabilidade de pesca por ponto, incluindo dentro de cada janela |
| Pós-processamento | Objetivo central da proposta | Adiado; não incluir suavização adicional nas duas fases iniciais |
| HMM e Wu et al. (2022) | Baselines previstas | Âmbito posterior; não estão implicitamente implementados pela CNN |
| Explicabilidade, calibração e dashboard | Objetivos previstos | Extensões posteriores, ainda não implementadas |
| Acesso reservado | Treino/validação/teste | Desenvolvimento estritamente em treino; acesso formal reservado depende de autorização |

As decisões posteriores do utilizador prevalecem sobre os pontos do PDF que alteram. A divisão atual mede generalização entre viagens e não garante independência entre navios de treino e teste. Não afirmar que o risco de dependência entre viagens do mesmo navio desapareceu por tratar IDs completos como entidades distintas.

## 5. Perguntas de investigação da proposta
- RQ1: em que medida a sobreposição reduz a instabilidade das fronteiras face a janelas sem sobreposição?
- RQ2: em que medida o pós-processamento reduz fragmentação e melhora a concordância com os segmentos anotados?
- RQ3: qual a interação entre sobreposição e pós-processamento?

As fases atuais começam pela baseline e pela análise do janelamento/sobreposição. Não respondem integralmente a RQ2 e RQ3 enquanto o pós-processamento não for estudado.

Um resultado sem melhoria também é um resultado válido: o agente não deve modificar o protocolo para fabricar ganhos.

## 6. Unidade dos dados e identificadores
Cada linha é um ponto de uma viagem, com posição, instante, variáveis de movimento/contexto e uma anotação.

Exemplo informado pelo utilizador:
```text
id = 211477000-2
prefixo 211477000 = identificador do navio
sufixo 2 = identificador da viagem desse navio
```

O id completo é uma string composta. O projeto não o trata como número contínuo nem como entrada da CNN. Não assumir que o sufixo é um contador diário nem reconstruir viagens com um limiar não documentado: a origem exata da numeração não foi demonstrada.

Viagens do mesmo navio podem estar em treino, validação e teste distintos, por decisão explícita do utilizador. Todas as linhas, sequências e janelas do mesmo id completo ficam sempre no mesmo conjunto.

## 7. Cabeçalho e linha real fornecidos
```csv
id,t,longitude,latitude,x,y,signed_turn,bearing,time_gap,distance_gap,euc_speed,distanceToShore,label
211477000-2,2021-11-14 15:00:10,12.31017,56.127777,705723.070725276,6225237.28619866,-1.234665653,309.501333116,4,2.979796558,1.448065282,6.726539723,01-sailing
```

## 8. Dicionário completo das colunas originais
Nota de leitura: um CSV armazena texto; os tipos abaixo são os tipos lógicos recomendados depois da leitura e conversão. Uma única linha não comprova a ausência de valores em falta ou a mesma representação em todo o ficheiro.

| Coluna | Tipo lógico recomendado | Significado | Unidade/escala e estado | Exemplo | Papel no projeto |
|---|---|---|---|---|---|
| id | string composta | Navio + separador + viagem | Sem unidade; composição explicada pelo utilizador | 211477000-2 | Agrupar viagens e definir split; não usar como feature |
| t | datetime após conversão de string | Data e hora do ponto | Formato observado YYYY-MM-DD HH:MM:SS; resolução aparente de segundos; fuso não especificado | 2021-11-14 15:00:10 | Ordenação, intervalos e alinhamento; não usar como valor absoluto na configuração inicial |
| longitude | float64 | Longitude geográfica | Graus decimais; datum/CRS a confirmar | 12.31017 | Mapa e verificação geográfica |
| latitude | float64 | Latitude geográfica | Graus decimais; datum/CRS a confirmar | 56.127777 | Mapa e verificação geográfica |
| x | float64 | Coordenada X de outra representação da posição | Metros num referencial plano (verificado no treino, REV-003); CRS exato por confirmar | 705723.070725276 | Guardar; distância euclidiana só com referencial conhecido |
| y | float64 | Coordenada Y da mesma representação de x | Mesma unidade de x (verificado, REV-003); CRS exato por confirmar; não inferir EPSG/UTM apenas pelos valores | 6225237.28619866 | Guardar; usar em conjunto com x após confirmação |
| signed_turn | float64 | Mudança angular com sinal, associada ao movimento | Graus; diferença de bearing entre pontos consecutivos, normalizada para (-180, 180] (verificado, REV-003); anomalias por quantificar | -1.234665653 | Feature inicial proposta; pode ser negativa |
| bearing | float64 | Direção/azimute do deslocamento | Graus a partir do norte; azimute inicial do ponto anterior para o atual (verificado, REV-003) | 309.501333116 | Feature opcional; não confundir com mudança de direção |
| time_gap | float64, mesmo que haja valores inteiros | Intervalo temporal entre pontos, segundo a definição original | Segundos; igual à diferença de t entre pontos consecutivos (verificado, REV-003); anomalia com razão 1/3 por quantificar | 4 | Preservar original e comparar com recálculo |
| distance_gap | float64 | Distância associada a um intervalo entre pontos | Metros (verificado, REV-003); coincide com a distância plana entre pontos consecutivos | 2.979796558 | Calcular velocidade apenas após confirmar unidade e alinhamento |
| euc_speed | float64 | Velocidade calculada segundo a definição original | Nós: euc_speed = (distance_gap / time_gap) × 1,94384 (verificado, REV-003) | 1.448065282 | Comparação com velocidade recalculada |
| distanceToShore | float64 | Distância à costa | **Metros**, distância à costa da Dinamarca (confirmado pelo README oficial do Zenodo, REV-008) | 6.726539723 | Feature inicial proposta; preservar nome original na leitura |
| label | string categórica | Anotação original do estado nesse ponto da viagem | Cinco categorias descritas na proposta; sem unidade | 01-sailing | Resposta supervisionada; nunca entrada preditiva |

### Notas sobre tipos
- Não converter id para int nem perder o sufixo.
- signed_turn e bearing têm casas decimais no exemplo: não truncar para inteiros.
- t não é um mero índice inteiro no ficheiro exemplificado.
- Diferenças temporais podem ser calculadas como timedelta e convertidas em segundos float.
- Ausências numéricas devem manter um estado ausente até aplicar a política documentada; zero não é sinónimo de ausente.
- Só converter float64 para float32 nas entradas do modelo, depois dos cálculos de preparação apropriados.

## 9. Relação entre posição e movimento
Latitude/longitude e x/y podem codificar a mesma localização em referenciais diferentes; não são necessariamente os mesmos números nem usam as mesmas unidades.

Guardar ambas as representações para rastreabilidade. Não usar distância euclidiana em graus como se fossem metros. Se for escolhido cálculo geodésico, confirmar referencial e elipsoide; se for escolhido cálculo plano, confirmar projeção e unidade.

bearing indica direção; signed_turn indica uma mudança de direção. Não são automaticamente intercambiáveis. Para inclusão futura de bearing, considerar seno e cosseno depois de confirmar a unidade.

As fórmulas e convenções das variáveis originais devem ser verificadas antes de declarar que foram reproduzidas, incluindo se usam pontos futuros. A configuração atual é análise offline; uma eventual aplicação em tempo real precisaria de especificar causalidade separadamente.

## 10. Variáveis recalculadas e unidades explícitas

### Time gap
```text
time_gap_calc_s[i] = (t[i] - t[i-1]).total_seconds()
```
Calcular dentro da mesma viagem ou sequência válida. Primeiro ponto sem predecessor: ausente, com tratamento documentado. Não dividir por intervalos nulos ou negativos.

### Distância
```text
distance_gap_calc_m
```
Só criar com este nome quando a saída em metros estiver assegurada. Escolher e registar método; uma distância geodésica não é necessariamente idêntica à distância euclidiana original.

### Velocidade
```text
speed_calc_mps = distância_em_metros / time_gap_calc_s
speed_calc_knots = speed_calc_mps * 1.94384449
```

Na linha fornecida:
```text
2.979796558 / 4 ≈ 0.74494914
0.74494914 * 1.94384449 ≈ 1.44807
```
Isto é compatível com distance_gap em metros, time_gap em segundos e euc_speed em nós, mas não prova a definição global nem a fórmula da distância. [REV-003 | cor #2E7D32] Verificado no treino: distance_gap em metros e euc_speed em nós (ver §18).

Após excluir pontos, recalcular as características dependentes do predecessor. Não dividir uma distância original ligada ao predecessor antigo pelo intervalo até um novo predecessor.

### Outras colunas internas
| Coluna | Tipo | Função |
|---|---|---|
| point_id | string ou identificador inteiro único estável | Rastreabilidade de cada ponto; preservar após ordenação/exclusões |
| sequence_id | string ou inteiro com unicidade explicitada | Sequência contínua dentro da viagem, se houver quebras |
| split | categoria string | train, validation ou test |
| target | inteiro binário | 0 navegação; 1 pesca |
| window_id | string ou inteiro único | Identificação da janela na fase de janelamento |
| position_in_window | inteiro não negativo | Posição temporal local |
| is_valid / mask | bool | Distinguir ponto real de preenchimento |
| p_fishing | float em [0,1] | Probabilidade prevista; não é automaticamente confiança calibrada |
| predicted_class | inteiro binário | Classe obtida após limiar definido |

## 11. Rótulos e problema binário
```text
01-sailing → 0
02-fishing → 1
03-sailing → 0
04-fishing → 1
05-sailing → 0
```
Preservar label e criar target separado. Não interpretar os prefixos numéricos como intensidade ou magnitude ordinal. Categorias desconhecidas geram erro/aviso explícito, nunca conversão automática para 0.

A proposta prevê manter o desequilíbrio natural, sem reamostragem nem pesos de classe na configuração inicial.

## 12. Entradas iniciais da CNN
```text
speed_calc_mps
signed_turn
time_gap_calc_s
distanceToShore
```
Seleção decidida pelo utilizador (REV-019), não uma conclusão científica sobre a inutilidade das restantes colunas. Unidades verificadas: speed em nós, signed_turn em graus (REV-003), time_gap em segundos e distanceToShore em metros (REV-008). Ausências: o primeiro ponto de cada viagem fica sem valor em time_gap, speed e signed_turn; a política para a CNN fica para o Marco 3.

ID, target, label, timestamps absolutos e identificadores auxiliares não são features. x e y ficam fora das entradas por decisão do utilizador (REV-019), e bearing fica fora por ser função de x e y. Podem ser revistos se houver evidência de que ajudam ou de que o modelo aprende a posição absoluta.

## 13. Etapas atuais de implementação

### Parte 1 — Preparação comum
Dividir cedo por ID, isolar conjuntos reservados, explorar apenas treino, confirmar unidades, recalcular diferenças, limpar, definir sequências e ajustar transformações exclusivamente no treino.

### Parte 2 — CNN com viagem completa
Entrada de uma viagem ou sequência válida de cada vez; saída com N probabilidades para N pontos. Sem janelas externas nem suavização temporal. Uma CNN totalmente convolucional não implica que cada saída use contexto de toda a viagem: o campo recetivo depende da arquitetura.

### Parte 3 — CNN com janelas e sobreposição
Criar janelas de L pontos dentro das sequências. Incluir controlo a 0% e variantes a 25%, 50% e 75%. Para L=64, strides 64, 48, 32 e 16. Máscaras excluem padding da perda e avaliação.

Cada janela produz uma probabilidade por ponto. Agregar probabilidades repetidas por point_id, inicialmente pela média, e só depois converter em classes. Avaliar uma previsão por ponto real, sem contar duplicados da sobreposição.

### Âmbito posterior da proposta
Pós-processamento temporal, HMM e Wu et al. como comparações, calibração, explicabilidade e dashboard humano-IA. Não declarar estes objetivos cumpridos só por implementar as duas CNN.

## 14. Avaliação prevista
- Por ponto: precisão, sensibilidade, F1, IoU e matriz de confusão.
- Por segmento: correspondência um-para-um definida por protocolo, com limiar de IoU temporal declarado.
- Fronteiras: desvios de início/fim em unidade temporal explícita.
- Fragmentação: número de segmentos e relação com a anotação; menos segmentos não significa automaticamente melhor.
- Estabilidade: resposta a pequenas alterações de parâmetros/janelas; não confundir apenas com baixa fragmentação.
- Custos: tempo, passos de treino, memória quando medida e custo de inferência.

Manter os mesmos IDs, características e definições de métricas entre comparações. Especificar se a sobreposição varia no treino, na inferência ou em ambos e documentar o orçamento de otimização. Não escolher variantes a partir do teste.

## 15. Política de treino, validação e teste
1. Antes de analisar valores, ler só o mínimo necessário para dividir pelos IDs completos.
2. [REV-001 | cor #C62828] Criar manifesto fixo de 70/15/15 dos IDs, com seed **42** (confirmada pelo utilizador), sem usar rótulos para escolher a divisão.
3. Durante desenvolvimento, só treino ou dados sintéticos: inclui debugging, gráficos, benchmarks e inspeção de exemplos.
4. Não ajustar normalizadores, imputadores, regras estatísticas ou outros parâmetros em dados reservados.
5. Se necessário, criar monitorização interna apenas dentro do treino, por ID. Para independência interna, ajustar pré-processamento apenas no treino interno; caso contrário, identificar a monitorização como diagnóstica.
6. Congelar implementação e pedir autorização explícita antes da seleção formal na validação.
7. Congelar solução/protocolo e pedir nova autorização antes da avaliação final no teste.
8. Nunca usar teste para refinar a solução. Se houver exposição, documentar; não alegar que ficou intocado.

O teste estrutural dos IDs é a exceção mínima para executar e verificar a divisão, não uma licença para explorar os valores reservados.

## 16. Dimensão humana e limites
A proposta prevê apoiar o inspetor com mapas, segmentos, probabilidades e justificações. Uma probabilidade bruta não deve ser apresentada como confiança calibrada sem avaliação específica.

O sistema deve permitir revisão humana, assinalar lacunas e limitações e não fundamentar sanções de forma autónoma. Uma prova de conceito sem estudo com inspetores não comprova utilidade operacional validada.

## 17. Ordem de leitura dos restantes documentos
1. Preparação comum revista e política de acesso aos dados.
2. Especificação das funções de preparação.
3. Workflow da CNN com viagem completa.
4. Funções e documentos da CNN com viagem completa.
5. Workflow de janelamento/sobreposição.
6. Funções e documentos da CNN com janelamento/sobreposição.

Em caso de contradição, aplicar as decisões mais recentes do utilizador e a política restritiva de acesso. Não implementar a divisão antiga por navio do PDF. Não antecipar acesso reservado porque um workflow antigo menciona validação/teste.

## 18. Lista de dúvidas a resolver apenas com treino ou documentação
- CRS de longitude/latitude e de x/y. (Unidades de x/y verificadas em metros, REV-003.)
- Definição exata de distance_gap. (Unidade verificada em metros, REV-003.)
- Unidade de distanceToShore: **metros**, confirmada pelo README oficial (REV-008). Método de cálculo: não documentado; aceite como correto, sem verificação externa (REV-011).
- x e y: **SRID 25832** segundo o README oficial (ETRS89 / UTM zona 32N, EPSG:25832). Longitude e latitude: CRS não indicado; hipótese WGS84 (EPSG:4326), por confirmar.
- Alinhamento temporal de signed_turn e bearing. (Unidades e convenção verificadas, REV-003.)
- Hipótese de euc_speed em nós: verificada (REV-003).
- Tratamento dos primeiros pontos, lacunas e valores ausentes.
- Proveniência das anotações e convenções dos intervalos.

Nenhuma destas incertezas autoriza abrir validação ou teste durante desenvolvimento.

### Estado das dúvidas (atualizado por REV-002 e REV-003)
- [REV-002 | cor #1565C0] **Fuso horário de `t`:** ignorado por decisão do utilizador. Não é necessário para o projeto.
- [REV-003 | cor #2E7D32] **Verificado no treino (87 IDs, 713 767 pares consecutivos)**, com `scripts/check_units_train.py` e `results/units_check_train/summary.json` (gerado, não versionado):
  - `x`, `y` e `distance_gap` estão na mesma unidade. A distância plana entre pontos consecutivos é igual a `distance_gap` (mediana da razão = 1,0000). A distância plana é ≈1,002 vezes a haversine de lat/lon, pelo que x/y estão **em metros** num referencial plano. O CRS exato continua por confirmar.
  - `distance_gap` está **em metros**: mediana da razão com a haversine = 1,0022, mesma escala que x/y.
  - `time_gap` está **em segundos**: mediana da razão com a diferença de `t` = 1,0.
  - `euc_speed` está **em nós**: `euc_speed` = (distance_gap / time_gap) × 1,94384 (mediana e percentis 5 a 95 praticamente iguais a 1,94384).
  - `bearing` está **em graus**, azimute a partir do norte, e corresponde ao azimute inicial entre o ponto anterior e o ponto atual (diferença mediana ~3·10⁻¹⁰ °).
  - `signed_turn` está **em graus** e é a diferença de `bearing` entre pontos consecutivos, normalizada para (-180, 180]. Mediana e percentil 95 da diferença absoluta são ~0.
  - `distanceToShore`: **metros**, confirmado pelo README oficial do Zenodo (`128_fishing_trajs_README.txt`: "distance (in meters) to the Denmark Coast"), REV-008. Mediana ~18,7 mil; máximo ~79 mil. Coerente com a leitura no treino.
- **Anomalias quantificadas no treino (REV-017):** 55 saltos acima de 30 nós em 4 viagens; 3 717 inversões de rumo acima de 170° em 70 viagens, 68 % delas em duas viagens. Mantidas tal como estão (REV-012). A limpeza IQR foi retirada (REV-019).
- Ainda por confirmar: CRS de longitude/latitude; política de valores ausentes na CNN (Marco 3); proveniência das anotações.

## 19. Referências de contexto do PDF
As referências abaixo são identificadas na proposta; esta síntese não constitui verificação bibliográfica independente:
- Wu et al. (2022), Semantic segmentation of AIS trajectories for detecting complete fishing activities: referência central de segmentação de atividades completas.
- Peel e Good (2011): baseline HMM para atividade de embarcações.
- Soares Júnior et al. (2018): segmentação semântica de trajetórias.
- Kroodsma et al. (2018) e Natale et al. (2015): monitorização do esforço de pesca com AIS.
- Shneiderman (2020): enquadramento HCAI.
- Guo et al. (2017): calibração.
- Lundberg e Lee (2017): atribuições de importância.

O resumo não valida automaticamente implementações desses métodos nem resultados futuros.
