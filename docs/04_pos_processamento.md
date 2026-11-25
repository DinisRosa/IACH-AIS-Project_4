# 04 — Pós-processamento temporal (Marco 5)

[REV-056 | cor #D84315] Plano e registo do Marco 5. Regras gerais: `AGENTS.md`; dados: `01`; modelo: `02`. Responde à **RQ2** (o pós-processamento reduz a fragmentação e melhora a concordância com os segmentos anotados?). A RQ3 (interação com a sobreposição) fica sem resposta, porque J0 e J50 não entram.

[REV-066 | cor #8E24AA] Este documento é anterior ao relatório: onde diz «proposta» e «Secção 10», refere-se à proposta retirada (etiqueta `proposta-pt-v1`). No relatório (`latex/relatorio_pt.tex`) o filtro está nas secções 4.4, 5.4, 5.6 e 6.3, e **a versão de 13 pontos é declarada** nas limitações (decisão do utilizador, REV-065), o que substitui a decisão de a deixar de fora.

[REV-058 | cor #546E7A] **Estado:** a primeira versão (janela de 13 pontos, v1) foi aplicada ao `validation` e ficou aquém do pretendido. O utilizador decidiu refazer com uma janela de **301 pontos** (v2), escolhida no `test`. A v2 vai ser aplicada uma única vez ao `validation` e substitui a v1 nos **números e figuras** da proposta; o texto da Secção 10 mantém-se. A v1 **fica registada aqui** (§3), no `PROGRESS.md` e no `REVISION_LOG.md`, mas, por decisão do utilizador, **não entra na proposta**.

## 1. Decisões comuns (v1 e v2)

| Decisão | Valor | Motivo |
|---|---|---|
| Modelo | Só a referência (época 162, limiar 0,65), congelada em `results/baseline_frozen/` | Foi o modelo escolhido e medido na medição final (REV-053) |
| Filtro | Janela **gaussiana** que desliza ponto a ponto pela viagem, sobre as **probabilidades** de pesca; depois o limiar 0,65 | Pedido do utilizador: o ponto central pesa mais, os vizinhos menos com a distância |
| Forma | σ = tamanho / 6 | O peso cai quase a zero nas pontas da janela |
| Pontas da viagem | Só os pontos existentes, pesos reajustados para somarem 1; nunca atravessa viagens | Sem pontos inventados (como no janelamento) |
| Onde se mede | Ficheiro já guardado `results/final_validation/predictions_validation.csv`, gerado na medição final (REV-053) | Comparação direta com a medição final, no mesmo conjunto |
| O que se usa desse ficheiro | `p_fishing` (probabilidade da CNN) para filtrar; `target` (classe real anotada) para medir | Ver §1.1 |
| Formalidade | Protocolo escrito e commitado antes de medir, e uma só execução registada; a confirmação do utilizador no chat vale como autorização | Não é uma reabertura dos dados (§1.1) |

### 1.1 O que é e o que não é usar o `validation` aqui

- **Não se faz:** reabrir o parquet do `validation`, voltar a passá-lo pela CNN ou ler as características. A CNN não volta a correr.
- **Faz-se:** aplicar o filtro às probabilidades **já previstas** e compará-las com as **classes reais anotadas** (`target`), que estão no mesmo ficheiro.
- **Porque conta como medição:** as anotações são as «respostas do exame». O risco é **decidir algo depois de ver os resultados**. Na v2 isto aconteceu em parte: a decisão de mudar de janela foi tomada depois de ver o resultado da v1 no `validation` (§5). O tamanho 301 foi escolhido no `test`, não no `validation`.

O filtro não é a reconstrução das janelas sobrepostas: esta junta previsões do mesmo ponto, o filtro junta previsões de pontos vizinhos.

## 2. Porque é que a janela de 13 pontos fez pouco

Análise das previsões da referência no `test` e no treino (`ais.cli.analyze_error_runs`, resultados em `results/postproc_window_analysis/`). Um **buraco** é um bloco de pontos seguidos mal classificados (com a mesma classe prevista), dentro de uma viagem.

| `test` | Valor |
|---|---|
| Buracos | 373 (5 502 pontos errados) |
| Média / mediana | 14,8 / 5 pontos |
| p75 / p90 / p95 / máximo | 16 / 37 / 55 / 286 pontos |
| Navegação prevista no meio de pesca | 79 % dos pontos errados; média 17,2, p90 47 |
| Segmentos reais mais curtos | pesca 633 pontos, navegação 127 (treino: 584 e 102) |

Com o limiar 0,65 o filtro é **assimétrico**: um ponto de navegação no meio de pesca só passa a pesca se a média pesada chegar a 0,65. Com dados ideais 0/1 e σ = tamanho/6:

| Janela | Remove pesca isolada até | Remove navegação isolada até | Buracos do `test` cobertos | Pontos de erro cobertos |
|---|---|---|---|---|
| 13 | 4 | **1** | 26 % | 3 % |
| 51 | 15 | 7 | 63 % | 16 % |
| 101 | 31 | 15 | 78 % | 29 % |
| 201 | 62 | 30 | 90 % | 50 % |
| **301** | 93 | 45 | **93 %** | **59 %** |
| 401 | 124 | 60 | 96 % | 68 % |

A janela de 13 só removia navegação isolada de 1 ponto, que era o erro mais comum. A de 301 remove a pesca isolada até 93 pontos (todos os casos do `test`) e a navegação até 45 (≈ p90), e fica abaixo do segmento real de navegação mais curto (102 a 127 pontos).

## 3. Efeito da janela no `test` (escolha da v2)

Previsões guardadas da referência no `test`, com autorização própria (`configs/authorizations/test_postproc_eval.json`), por `ais.cli.eval_postproc_test`. Resultados em `results/postproc_window_analysis/test_eval.json`. O utilizador escolheu **301**; 13, 201 e 401 são só contexto.

| `test` | Sem filtro | 13 | 201 | **301** | 401 |
|---|---|---|---|---|---|
| Exatidão por ponto | 94,7 % | 94,8 % | 95,7 % | **95,7 %** | 95,6 % |
| Erros | 5 502 | 5 393 | 4 484 | **4 422** | 4 499 |
| Segmentos de pesca previstos (reais 18) | 358 | 189 | 39 | **32** | 26 |
| F1 de segmentos, pesca | 0,032 | 0,068 | 0,526 | **0,600** | 0,682 |
| Segmentos de navegação previstos (reais 36) | 376 | 207 | 57 | **50** | 44 |
| F1 de segmentos, navegação | 0,151 | 0,263 | 0,774 | **0,814** | 0,825 |
| Erro mediano do fim da pesca (s) | 100 | 130 | 110 | **154** | 209 |

Leitura: com 301 a fragmentação quase desaparece e a exatidão sobe 1 ponto percentual (2 741 pontos corrigidos, 1 661 estragados). **Pioram 8 viagens de 18**, duas muito: `219001624-2` de 83,7 % para 48,4 % (a probabilidade de pesca da CNN fica pouco abaixo de 0,65 durante muito tempo e a janela espalha-a) e `220006000-2` de 74,0 % para 66,2 %. As fronteiras recuam um pouco. Estes números são **otimistas**: a janela foi escolhida com este conjunto.

## 4. Plano da v2 (301 pontos)

| # | Passo | Quem | Estado |
|---|---|---|---|
| 1 | Este documento atualizado | Coordenador | **Feito (REV-058)** |
| 2 | Protocolo `configs/postproc_protocol_v2.json` (301 pontos, σ = 301/6, limiar 0,65, mesma fonte e hash; uma execução; regista que a v1 existiu), commitado **antes** de medir | Coordenador (revisão da Abacus) | **Feito (REV-059)**, commit antes de medir |
| 3 | Programa: `postproc_validation` passa a aceitar a v2 (uma execução da v2, independente da v1 já feita), com saída em `results/postproc_validation_v2/` | Abacus (gera), coordenador (revê e integra) | **Feito (REV-059)** |
| 4 | Testes sintéticos da v2 (uma execução, v1 não bloqueia a v2, segunda v2 recusada, hash, tamanho) | Abacus (gera), subagente (corre e corrige os testes) | **Feito (REV-059)**: a falha era do teste |
| 5 | Revisão independente do código antes de executar | Abacus | **Feito (REV-059)**: corrigidos escrita atómica, hash fixado no código, árvore limpa obrigatória |
| 6 | Execução única da v2 no `validation` | Coordenador | **Feito (REV-059)**, 2026-11-25, `results/postproc_validation_v2/` |
| 7 | Confirmação dos números por uma segunda implementação (`verify_postproc_independent` com tamanho 301) | Abacus (adapta), coordenador (corre localmente) | **Feito (REV-059)**: 19/19 |
| 8 | Macros, figuras e números da Secção 10 atualizados para a v2; o texto mantém-se (só se ajustam o tamanho, o σ e a justificação do 301) | Coordenador | **Feito (REV-059)**: também os parágrafos de resultados cujos números deixaram de estar certos |
| 9 | `PROGRESS.md`, `REVISION_LOG.md`, handoff e commits | Coordenador | **Feito (REV-059)** |

A Abacus recebe só código, contratos e descrições, nunca dados nem linhas do `validation` ou do `test`.

## 4.1 Resultados da v2 no `validation` (REV-059)

[REV-059 | cor #8B008B] Referência antes → depois (301 pontos): exatidão 94,4 % → 94,8 % (11 662 → 10 790 erros); segmentos de pesca previstos 486 → 32 (reais 18), de navegação 502 → 49 (reais 35); F1 de segmentos de pesca 0,028 → 0,600 e de navegação 0,119 → 0,786; 4 100 pontos mudam (2 486 corrigidos, 1 614 estragados); melhoram 11 viagens e pioram 7, a pior `219020187-4` de 40,4 % para 19,7 %. Números em `results/postproc_validation_v2/postproc_validation.json`, confirmados por `verify_postproc_independent --size 301` (19/19); macros em `latex/generated/resultados_posproc.tex`. Resposta à RQ2: a fragmentação cai muito e a exatidão sobe; as viagens em que a CNN erra durante muito tempo pioram.

Reprodução (não volta a executar: `postproc_validation` recusa uma segunda execução de cada versão):
```bash
iach-ais-venv-4/bin/python -m ais.cli.verify_postproc_independent --size 301 results/final_validation/predictions_validation.csv
iach-ais-venv-4/bin/python -m ais.cli.build_postproc_results
iach-ais-venv-4/bin/python -m ais.cli.plot_postprocessing_kernel
```

## 5. Histórico: v1 (janela de 13 pontos) — registo interno, fora da proposta

[REV-057 | cor #B8860B] Protocolo `posproc_validation_v1` (commit `3359890`), execução única em 2026-11-25 (`results/postproc_validation/`, eventos `postproc_start` e `postproc_done`). No `validation`, antes → depois: exatidão 94,4 % → 94,5 %; segmentos de pesca previstos 486 → 255 (reais 18), de navegação 502 → 272 (reais 35); F1 de segmentos de pesca 0,028 → 0,066 e de navegação 0,119 → 0,221; 784 pontos mudam (514 corrigidos, 270 estragados). Confirmado por uma segunda implementação (19/19).

**Registo de integridade:** a v2 foi decidida depois de ver este resultado no `validation`. O tamanho da v2 foi escolhido no `test`, mas a decisão de procurar outra janela não é independente do `validation`. Por decisão do utilizador isto não entra na proposta; fica registado aqui, no `PROGRESS.md` e no `REVISION_LOG.md` (REV-058).

## 6. Limitações
- As anotações do `validation` são usadas pela terceira vez (medição final, v1, v2), sempre sem nova passagem pela CNN.
- A v2 foi decidida depois de ver a v1 no `validation` (§5).
- Uma janela de 301 pode apagar segmentos reais de navegação com menos de ~45 pontos e desloca as fronteiras; piora viagens em que a probabilidade de pesca fica pouco abaixo do limiar.
- Uma semente, 18 viagens, sem intervalo de incerteza; J0 e J50 não são pós-processadas.
