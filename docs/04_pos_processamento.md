# 04 — Pós-processamento temporal (Marco 5)

[REV-056 | cor #D84315] Plano de ação do Marco 5, decidido pelo utilizador em 2026-11-25. Regras gerais: `AGENTS.md`; dados: `01`; modelo: `02`. Responde à **RQ2** (o pós-processamento reduz a fragmentação e melhora a concordância com os segmentos anotados?). A RQ3 (interação com a sobreposição) fica sem resposta, porque J0 e J50 não entram.

## 1. Decisões do utilizador

| Decisão | Valor | Motivo |
|---|---|---|
| Modelo | Só a referência (época 162, limiar 0,65), congelada em `results/baseline_frozen/` | Foi o modelo escolhido e medido na medição final (REV-053) |
| Filtro | Janela **gaussiana** que desliza ponto a ponto pela viagem, sobre as **probabilidades** de pesca; depois o limiar 0,65 | Pedido do utilizador: o ponto central pesa mais, os vizinhos menos com a distância |
| Tamanho | **13 pontos** (−6 a +6) | É o campo recetivo da CNN; fixado antes de qualquer medição, sem escolha em dados |
| Forma | σ = 13 / 6 ≈ 2,17 pontos | O peso cai quase a zero nas pontas da janela |
| Pontas da viagem | Só os pontos existentes, pesos reajustados para somarem 1; nunca atravessa viagens | Sem pontos inventados (como no janelamento) |
| Onde se mede | **Previsões já guardadas do `validation`** (`results/final_validation/predictions_validation.csv`), uma só aplicação | Comparação direta com a medição final, no mesmo conjunto |
| Reutilização do `validation` | **Decisão do utilizador**: segunda utilização, depois de declarado gasto (REV-053) | Aceitável porque o filtro está totalmente fixado antes; nada se escolhe com estes resultados |

O filtro não é a reconstrução das janelas sobrepostas: esta junta previsões do mesmo ponto, o filtro junta previsões de pontos vizinhos.

## 2. Plano de ação

| # | Passo | Estado |
|---|---|---|
| 1 | Secção 10 da proposta (método, tamanho, forma, objetivo, figura), antes dos resultados | **Feito (REV-056)** |
| 2 | Filtro em `src/ais/phase1/postprocessing.py` (`gaussian_kernel`, `smooth_trip`, `smooth_probabilities`) | **Feito (REV-056)**, 11 testes sintéticos em `tests/test_postprocessing.py` |
| 3 | Figura `latex/figures/posproc_janela.png` (pesos e exemplo sintético) por `python -m ais.cli.plot_postprocessing_kernel` | **Feito (REV-056)** |
| 4 | Protocolo `configs/selection_protocol_postproc.json` e autorização `configs/authorizations/validation_postproc.json` (declarados antes) | Por fazer; **parar e pedir autorização escrita ao utilizador** |
| 5 | Programa que lê as previsões guardadas do `validation` (verificando hash e o acesso no `access_log.jsonl`), aplica o filtro uma vez e guarda `results/postproc_validation/` | Por fazer, depois da autorização; testes sintéticos da recusa da segunda aplicação |
| 6 | Métricas antes e depois: por ponto (exatidão, F1 por classe, matriz de confusão) e por segmento (F1, fragmentação, erros de fronteira, IoU 0,5); figura de uma viagem antes e depois | Por fazer |
| 7 | Resultados na Secção 10 do LaTeX (macros e figuras geradas), limitações, docs, `PROGRESS.md`, `REVISION_LOG.md` e handoff | Por fazer |

## 3. Limitações já conhecidas
- Segunda utilização do `validation`: o resultado é uma medição, não uma escolha, mas deixa de ser a primeira e única leitura desse conjunto.
- O filtro só corrige trocas curtas (até alguns pontos); blocos de erros mais longos que a janela ficam; pode apagar segmentos reais curtos e deslocar fronteiras.
- Uma semente, 18 viagens, sem intervalo de incerteza; J0 e J50 não são pós-processadas.
