# Fase 2 — CNN com janelamento e sobreposição

## Atualização normativa do pacote
Ler AGENTS.md e 00_5_orientacoes_execucao_decisoes.md antes dos passos abaixo. Implementação principal em Python; KNIME só futuro opcional. Desenvolvimento APENAS no treino/sintéticos; validação/teste apenas depois de autorização separada. Divisão por ID no início, antes da exploração. Pós-processamento simples é ramo adicional a aprovar, preservando saídas brutas; não confundir com média de janelas. Os contratos antigos ficam subordinados a estas correções.


## Objetivo
Avaliar o efeito de dividir as viagens em janelas e de adicionar sobreposição, comparando com a baseline de viagem completa.

## Pré-requisitos
Reutilizar a divisão dos IDs, as características, as unidades e a normalização da preparação comum. Manter inicialmente a arquitetura da CNN da fase 1 para reduzir alterações simultâneas.

## Workflow
```text
Configuração → Construção das janelas → Preparação dos dados
→ Treino da CNN → Validação → Predição por janela
→ Reconstrução por ponto → Classes e segmentos
→ Avaliação → Comparação e exportação
```

## 10 — Configuração das janelas
Definir comprimento L e sobreposição r. Exemplo inicial: L = 64 pontos.

```text
Sobreposição 0%  → passo 64
Sobreposição 25% → passo 48
Sobreposição 50% → passo 32
Sobreposição 75% → passo 16
```

O comprimento em pontos não corresponde necessariamente a uma duração fixa. Documentar a decisão de manter a amostragem original ou reamostrar antes desta fase.

## 11 — Construção das janelas
Criar janelas dentro de cada viagem ou sequência válida, sem atravessar IDs, quebras temporais ou conjuntos de dados.

Guardar uma tabela de correspondência:
```text
window_id
id
sequence_id
point_id
position_in_window
is_valid
```

## 12 — Preparação das entradas
Cada janela contém L pontos e F características, acompanhados de L rótulos. A CNN deve devolver uma probabilidade por ponto da janela.

Não atribuir a todos os pontos o rótulo maioritário da janela. Manter as transições pesca/navegação.

Para as janelas finais incompletas, definir uma estratégia comum às experiências. Proposta: preenchimento artificial com máscara, ignorando o preenchimento na função de perda e na avaliação. Garantir cobertura de todos os pontos válidos, incluindo sequências curtas.

## 13 — Treino
Usar apenas janelas das viagens de treino. Registar as mesmas informações de treino da fase 1.

Documentar se a sobreposição é aplicada no treino, na inferência ou em ambos. Na comparação inicial, pode ser aplicada em ambos; uma análise posterior pode separar esses efeitos.

Registar épocas e passos de otimização, porque a sobreposição altera o número de janelas.

## 14 — Validação
Selecionar comprimento, sobreposição e restantes parâmetros com a validação. Manter o teste reservado para a avaliação final.

Para reconstruir as viagens de validação, usar o mesmo processo de agregação que será aplicado ao teste.

## 15 — Predição por janela
Aplicar a CNN às janelas de teste. Cada posição válida recebe uma probabilidade de pesca.

## 16 — Reconstrução das viagens
Associar cada previsão ao ponto original através da tabela de correspondência.

Se o mesmo ponto surgir em várias janelas, combinar as probabilidades pela média como estratégia inicial. Ignorar posições de preenchimento.

A saída deve ter exatamente uma linha por ponto válido original, com ID, timestamp, rótulo real e probabilidade agregada.

## 17 — Classes e segmentos
Converter a probabilidade agregada em classe com o limiar escolhido na validação. Extrair segmentos contíguos usando as mesmas regras da fase 1.

Não aplicar suavização temporal adicional nesta fase: a agregação das previsões sobrepostas fica separada de um futuro pós-processamento.

## 18 — Avaliação
Usar as mesmas viagens de teste e definições de métricas da fase 1:
- Precisão, sensibilidade, F1 e IoU por ponto.
- Qualidade por segmento.
- Fragmentação e erro de fronteira.
- Tempo de treino e inferência.

## 19 — Comparação e exportação
Experiências previstas:

| Experiência | Entrada | Sobreposição | Pós-processamento |
|---|---|---|---|
| Fase 1 | Viagem completa | Não aplicável | Não |
| Fase 2A | Janelas fixas | 0% | Não |
| Fase 2B | Janelas fixas | 25% | Não |
| Fase 2C | Janelas fixas | 50% | Não |
| Fase 2D | Janelas fixas | 75% | Não |

A comparação com janelas a 0% ajuda a distinguir o efeito do janelamento do efeito da sobreposição.

Guardar configurações, modelos, previsões reconstruídas, segmentos e métricas por experiência.

## Integração futura opcional com KNIME
```text
Dados preparados + tabela de configurações
→ Python Script: construção das janelas
→ Python Script: treino e validação
→ Python Script: inferência nas janelas
→ Python Script: agregação por ponto
→ Extração dos segmentos
→ Avaliação comum e comparação
```

## Entregável principal
Tabela comparativa entre viagem completa e janelas com diferentes sobreposições, mantendo a divisão dos dados e as regras de avaliação.
