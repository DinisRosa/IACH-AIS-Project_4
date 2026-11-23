# Fase 1 — CNN com a viagem completa

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## Objetivo
Construir uma baseline que recebe a sequência completa de cada viagem e devolve uma probabilidade de pesca por ponto, sem janelamento externo, sobreposição ou pós-processamento temporal.

## Pré-requisitos
Usar os dados e a divisão por ID produzidos na preparação comum. Se uma viagem tiver quebras temporais identificadas na limpeza, processar as sequências válidas separadamente, sem alterar o conjunto atribuído à viagem.

## Workflow
```text
Sequências completas → CNN 1D → Treino → Validação
→ Predição no teste → Classes e segmentos → Avaliação → Exportação
```

## 10 — Preparação das sequências
Para cada viagem ou sequência válida, preparar:
- Entrada: matriz com N pontos e F características.
- Resposta: N rótulos de pesca/navegação.
- Metadados: ID, identificadores dos pontos e timestamps.

Começar por processar uma sequência de cada vez para simplificar o tratamento de comprimentos diferentes. Confirmar a viabilidade de memória com as sequências mais longas antes do treino completo.

## 11 — Construção da CNN 1D
A CNN deve preservar o comprimento temporal e produzir uma previsão por ponto, não um único rótulo para toda a viagem.

Arquitetura inicial proposta, ainda por validar:
```text
N pontos × F características
→ Conv1D: 32 filtros, kernel 5, padding same
→ ReLU
→ Conv1D: 64 filtros, kernel 5, padding same
→ ReLU
→ Conv1D: 32 filtros, kernel 5, padding same
→ ReLU
→ Conv1D: 1 filtro, kernel 1
→ Logits (usados na perda)
→ Sigmoid apenas na inferência
→ N probabilidades de pesca
```

A trajetória entra inteira, mas o contexto usado por cada previsão depende do campo recetivo da arquitetura. Não usar uma operação final que reduza toda a sequência a uma única classe.

## 12 — Treino
Aprender os parâmetros apenas com as viagens de treino. Usar inicialmente a política da proposta: sem reamostragem nem pesos de classe.

Guardar semente, arquitetura, otimizador, taxa de aprendizagem, épocas, passos de otimização e histórico do treino.

## 13 — Validação
Usar a validação para escolher parâmetros, checkpoint e limiar de classificação. Não ajustar decisões com base no teste.

## 14 — Predição no teste
Aplicar o modelo escolhido às sequências completas de teste. Guardar uma probabilidade por ponto original e preservar a correspondência com ID e timestamp.

## 15 — Classes e segmentos
Converter probabilidades em classes com o limiar escolhido na validação.

Agrupar pontos consecutivos da mesma classe em segmentos, sem suavizar ou eliminar segmentos curtos. A extração de segmentos é apenas uma mudança de representação das previsões.

## 16 — Avaliação
Calcular:
- Precisão, sensibilidade, F1 e IoU por ponto.
- Métricas por segmento, com regras de correspondência previamente definidas.
- Fragmentação e erro de fronteira.
- Tempo de treino e inferência.

Definir explicitamente convenções temporais, limiar de IoU e correspondência um-para-um entre segmentos. Usar as mesmas regras na fase 2.

## 17 — Exportação
Guardar modelo, configuração, normalizador associado, previsões por ponto, segmentos e métricas.

## Integração futura opcional com KNIME
```text
Dados preparados
→ Python Script: preparação das sequências
→ Python Script: treino e validação da CNN
→ Python Script: inferência
→ Classes e extração dos segmentos
→ Avaliação e exportação
```

## Entregável principal
Baseline de viagem completa, sem janelas externas e sem pós-processamento temporal, para comparação com a fase 2.
