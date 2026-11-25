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
| Onde se mede | Ficheiro já guardado `results/final_validation/predictions_validation.csv`, gerado na medição final (REV-053) | Comparação direta com a medição final, no mesmo conjunto |
| O que se usa desse ficheiro | `p_fishing` (probabilidade da CNN) para filtrar; `target` (classe real anotada) para medir | Ver §1.1 |
| Formalidade | Protocolo curto, escrito antes de medir, e uma só execução registada; a confirmação do utilizador no chat vale como autorização | Não é uma reabertura dos dados (§1.1) |

### 1.1 O que é e o que não é usar o `validation` aqui

- **Não se faz:** reabrir o parquet do `validation`, voltar a passá-lo pela CNN ou ler as características (`speed`, `turn`, etc.). A CNN não volta a correr.
- **Faz-se:** aplicar o filtro às probabilidades **já previstas** e compará-las com as **classes reais anotadas** (`target`), que estão no mesmo ficheiro.
- **Porque conta como medição:** as anotações são as «respostas do exame». Calcular exatidão, F1 ou fragmentação depois do filtro é usá-las pela segunda vez. O risco não é ler o ficheiro; é **decidir algo depois de ver os resultados** (por exemplo, trocar 13 por 21 pontos). Para evitar isso, o tamanho, a forma e o limiar ficam fixados antes, aplica-se uma única vez e reporta-se o que sair, bom ou mau.

O filtro não é a reconstrução das janelas sobrepostas: esta junta previsões do mesmo ponto, o filtro junta previsões de pontos vizinhos.

## 2. Plano de ação

| # | Passo | Estado |
|---|---|---|
| 1 | Secção 10 da proposta (método, tamanho, forma, objetivo, figura), antes dos resultados | **Feito (REV-056)** |
| 2 | Filtro em `src/ais/phase1/postprocessing.py` (`gaussian_kernel`, `smooth_trip`, `smooth_probabilities`) | **Feito (REV-056)**, 11 testes sintéticos em `tests/test_postprocessing.py` |
| 3 | Figura `latex/figures/posproc_janela.png` (pesos e exemplo sintético) por `python -m ais.cli.plot_postprocessing_kernel` | **Feito (REV-056)** |
| 4 | Protocolo curto `configs/postproc_protocol.json` (filtro fixado: 13 pontos, σ = 13/6, limiar 0,65; uma execução; métricas a reportar), escrito e commitado **antes** de medir | Por fazer; **só depois do «sim» do utilizador** |
| 5 | Programa `ais.cli.postproc_validation`: confirma por hash que o ficheiro de previsões é o da medição final, aplica o filtro uma vez, regista a execução e guarda `results/postproc_validation/` (recusa uma segunda execução) | Por fazer; testes sintéticos |
| 6 | Métricas antes e depois: por ponto (exatidão, F1 por classe, matriz de confusão) e por segmento (F1, fragmentação, erros de fronteira, IoU 0,5); figura de uma viagem antes e depois | Por fazer |
| 7 | Resultados na Secção 10 do LaTeX (macros e figuras geradas), limitações, docs, `PROGRESS.md`, `REVISION_LOG.md` e handoff | Por fazer |

## 3. Limitações já conhecidas
- As anotações do `validation` são usadas pela segunda vez para medir (sem nova passagem pela CNN): o resultado é uma medição, não uma escolha, desde que nada mude depois de o ver.
- O filtro só corrige trocas curtas (até alguns pontos); blocos de erros mais longos que a janela ficam; pode apagar segmentos reais curtos e deslocar fronteiras.
- Uma semente, 18 viagens, sem intervalo de incerteza; J0 e J50 não são pós-processadas.
