# 00 — Projeto, decisões e política de acesso

[REV-033 | cor #3E2723] Documento fundido a partir de `00_contexto…`, `00_5_orientacoes…` e da política de acesso de `01_preparacao_comum`. Ler primeiro o `AGENTS.md` (regras fixas), depois este documento, depois `01`, e `02` ou `03` conforme a fase.

Este documento resume o que o projeto pretende, o que foi decidido e em que ponto está. Decisões recentes do utilizador prevalecem sobre a proposta em PDF e sobre qualquer texto antigo. Não confundir objetivos futuros com funcionalidades já implementadas.

## 1. Problema e objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma CNN 1D totalmente convolucional. A entidade operacional é a viagem (`id` completo, por exemplo `211477000-2`).

Fontes: proposta «Segmentação semântica de trajetórias AIS para deteção de atividade de pesca usando janelas sobrepostas e pós-processamento temporal» (Dinis Rosa), decisões do utilizador registadas em `PROGRESS.md` e `REVISION_LOG.md`, e dados do Zenodo (Song Wu, DOI 10.5281/zenodo.7283281, CC BY 4.0).

Detetar comportamento compatível com pesca não demonstra ilegalidade: o modelo não verifica licenças, quotas, zonas autorizadas ou infrações. A decisão de fiscalização continua humana.

## 2. Proposta original e decisões atuais

| Aspeto | Proposta PDF | Decisão atual |
|---|---|---|
| Modelo | Recorrente ou convolucional, possivelmente com atenção | CNN 1D |
| Divisão | Por navio | Por ID completo de viagem (70/15/15, seed 42) |
| 1.ª experiência | Janelas e pós-processamento | Referência com a viagem completa, sem janelas |
| 2.ª experiência | Janelas sobrepostas | Janelas com a mesma CNN; sobreposição **0 % e 50 % prioritárias**, 25 % e 75 % a decidir depois (REV-002) |
| Saída | Classificação de janelas | Probabilidade de pesca por ponto |
| Pós-processamento | Objetivo central | Ramo separado e identificado, depois de aprovado (Marco 5); a média das janelas é reconstrução, não suavização |
| HMM e Wu et al. (2022) | Baselines previstas | Fora por agora (REV-006) |
| Explicabilidade, calibração, dashboard | Previstos | Fora do mínimo atual |
| Dados reservados | Treino/validação/teste | Desenvolvimento só em treino; os conjuntos reservados só com autorização explícita e com papéis trocados face ao habitual (§6): `test` seleciona, `validation` mede no fim |

A divisão por viagem mede generalização entre viagens. Viagens do mesmo navio podem estar em conjuntos diferentes (decisão do utilizador), por isso **não se afirma generalização para navios inéditos**.

## 3. Perguntas de investigação

- **RQ1:** a sobreposição reduz a instabilidade das fronteiras face a janelas sem sobreposição?
- **RQ2:** o pós-processamento reduz a fragmentação e melhora a concordância com os segmentos anotados?
- **RQ3:** como interagem sobreposição e pós-processamento?

[REV-065 | cor #01579B] A RQ1 e a RQ2 têm resposta, com as ressalvas escritas no relatório (`latex/relatorio_pt.tex`); a RQ3 fica sem resposta. Um resultado sem melhoria também é válido: o protocolo não se altera para fabricar ganhos.

## 4. Marcos e estado

| # | Marco | Estado |
|---|---|---|
| 1 | Ambiente, divisão por ID, isolamento | Fechado |
| 2 | Preparação auditável (só treino/sintéticos) | Fechado (REV-019) |
| 3 | CNN 1D de referência sobre a viagem completa | **Fechado (REV-041)**: baseline definida por decisão do utilizador (época 162, limiar 0,65, escolhidos no `test` numa ronda). Não se altera; só volta a ser usada na comparação com as janelas |
| 4 | Janelamento com sobreposição e a mesma CNN | **Feito (REV-046, REV-047)**: J0 (0 %) e J50 (50 %), L = 64, mesma CNN e mesmos valores da baseline, lote de 32; sobreposição igual no treino e na inferência; escolhidas no `test` numa só abertura (J0 época 8, J50 época 4) e congeladas. Fora do projeto: 25 %, 75 % e outros L. Resultados em `results/windows_final/final_results_windows.json` |
| 5 | Pós-processamento simples, em ramo separado | **Feito (REV-056 a REV-059)**: filtro gaussiano sobre as previsões guardadas da referência no `validation`; a versão que vale é a de 301 pontos, depois de uma primeira de 13; ver `docs/04` (REV-065) |
| 6 | Congelar as variantes (baseline, J0 e J50; o pós-processamento só foi aplicado à referência, REV-059) | **Feito (REV-038, REV-047)**: congeladas, cada uma com hash |
| 7 | Medição final única no conjunto `validation` | **Feito (REV-053)**: por decisão do utilizador, **só o modelo escolhido** (a referência, pelo maior F1 médio por ponto no `test`, critério declarado antes) foi medido, uma só vez; J0 e J50 não foram medidas no `validation`. O `validation` está gasto |

O pós-processamento (um filtro que altera as previsões) não é o mesmo que extrair segmentos (só agrupar pontos consecutivos da mesma classe, sem suavizar): a extração é uma ferramenta de medição e vem antes. O `validation` só se abre no fim, para todas as variantes de uma vez, e não já para a baseline.

O estado detalhado, com datas e resultados, está em `PROGRESS.md`.

## 5. Ambiente

Python com `venv` + `pip` (`iach-ais-venv-4/`, ignorado pelo git); dependências com versões fixas em `requirements.txt`. Hardware informado: Intel i7 de 12.ª geração, 16 GB de RAM, GPU integrada. Começa-se em CPU e mede-se o custo no treino antes de prometer viabilidade. KNIME só entraria como contingência por decisão do utilizador.

## 6. Política de acesso aos dados

As regras completas estão no `AGENTS.md` §3. Resumo operacional:

| Etapa | Dados permitidos | Condição |
|---|---|---|
| A — Desenvolvimento | Treino oficial ou sintéticos | Autorizada. Inclui debugging, gráficos, benchmarks, inspeção e testes de integração |
| B — Seleção | `test` | Só com autorização explícita (âmbito das decisões declarado), depois de congelar a implementação; pode ser consultado mais do que uma vez dentro do âmbito autorizado |
| C — Medição final | `validation` | Só com nova autorização, **uma só vez**, depois de congelar modelo, limiar, número de épocas e lista de variantes. **Feita em REV-053 (2026-11-24 00:32 UTC); o `validation` está gasto** |

- **Nomes e papéis (REV-036):** os conjuntos mantêm os nomes `validation` e `test` nos ficheiros e no manifesto, mas os papéis estão trocados face ao habitual: `test` serve para **selecionar** (épocas, limiar, treinar mais, escolher entre variantes) e `validation` é a **medição final**, usada uma só vez com tudo congelado. Os resultados no `test` são otimistas por terem servido a escolher; o número final da proposta é o do `validation`.
- A divisão foi feita antes de qualquer exploração, só com IDs e contagens técnicas; a tabela `id → split` está em `manifests/split_manifest_seed42.csv` e não se refaz.
- Normalizadores e qualquer objeto aprendido ajustam-se só no treino (ou só no treino interno, se a monitorização tiver de ser independente).
- Monitorização interna: separar por ID dentro do treino, antes do ajuste de transformações e da criação de janelas.
- **Mecanismo (REV-038):** só se abre um conjunto reservado com um ficheiro de autorização escrito a partir de uma instrução do utilizador (`configs/authorizations/`), um protocolo declarado antes (`configs/selection_protocol.json`) e `ais.phase1.reserved`, que regista cada abertura em `results/access_log.jsonl`, recusa uma segunda ronda e recusa o `validation` sem autorização própria e execução congelada. É uma salvaguarda do código, não uma prova de que ninguém pode contornar.
- Uma flag no código ou uma decisão do agente nunca é autorização. Um erro numa execução reservada reproduz-se e corrige-se com treino ou sintéticos, e a exposição documenta-se.
- Exposição já ocorrida (REV-015): validação e teste foram lidos por inteiro só para construir as bases limpas e contar linhas e viagens, sem análise de resultados nem uso para escolher modelos ou regras.
- Nenhum valor empírico usado como evidência pode depender só de um cálculo informal do agente (`AGENTS.md` §10).

## 7. Avaliação prevista

- **Por ponto:** precisão, sensibilidade, F1, IoU e matriz de confusão.
- **Por segmento:** correspondência um-para-um com limiar de IoU temporal declarado.
- **Fronteiras:** desvios de início e fim em unidade temporal explícita.
- **Fragmentação:** número de segmentos face à anotação; menos segmentos não é automaticamente melhor.
- **Estabilidade:** resposta a pequenas alterações de parâmetros e janelas.
- **Custo:** tempo, passos de treino, memória e custo de inferência.

Mantêm-se os mesmos IDs, características e definições de métricas entre comparações. Declara-se se a sobreposição varia no treino, na inferência ou em ambos, e o orçamento de otimização. Variantes nunca se escolhem a partir do conjunto de medição final (`validation`).

## 8. Dimensão humana e limites

A proposta prevê apoiar o inspetor com mapas, segmentos e probabilidades. Uma probabilidade bruta não é confiança calibrada. O sistema não fundamenta sanções de forma autónoma, e uma prova de conceito sem estudo com inspetores não comprova utilidade operacional.

## 9. Referências da proposta

Identificadas na proposta, sem verificação bibliográfica independente aqui: Wu et al. (2022), segmentação semântica de atividades completas; Peel e Good (2011), HMM; Soares Júnior et al. (2018); Kroodsma et al. (2018) e Natale et al. (2015); Shneiderman (2020); Guo et al. (2017), calibração; Lundberg e Lee (2017). Citar esta lista não valida implementações nem resultados desses métodos.
