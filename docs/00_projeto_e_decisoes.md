# 00 — Projeto, decisões, modelos e acesso aos dados

[REV-067 | cor #CD5C5C] Documento de referência do projeto: junta o que continua vivo dos antigos `docs/00` e `docs/02` a `docs/06`. Os originais completos estão na etiqueta git `docs-historico-v1` (§11). Ler primeiro o `AGENTS.md` (regras fixas) e o `handoff.md` (ponto de situação); os dados e a preparação estão em `01`.

## 1. Problema e objetivo

Segmentar viagens AIS de pesca em **pesca** e **navegação**, com uma previsão por ponto, usando uma CNN 1D totalmente convolucional. A entidade operacional é a viagem (`id` completo, por exemplo `211477000-2`).

Documento ativo: o relatório `latex/relatorio_pt.tex`. Dados do Zenodo (Song Wu, DOI 10.5281/zenodo.7283281, CC BY 4.0).

Detetar comportamento compatível com pesca não demonstra ilegalidade: o modelo não verifica licenças, quotas, zonas autorizadas ou infrações. A decisão de fiscalização continua humana.

## 2. Proposta original e decisões

| Aspeto | Proposta entregue (PDF) | Decisão |
|---|---|---|
| Modelo | Recorrente ou convolucional, possivelmente com atenção | CNN 1D |
| Divisão | Por navio | Por ID completo de viagem (70/15/15, seed 42) |
| 1.ª experiência | Janelas e pós-processamento | Referência com a viagem completa, sem janelas |
| 2.ª experiência | Janelas sobrepostas | A mesma CNN em janelas, 0 % e 50 %; 25 % e 75 % ficaram de fora |
| Saída | Classificação de janelas | Probabilidade de pesca por ponto |
| Pós-processamento | Objetivo central | Filtro temporal num ramo separado; a média das janelas é reconstrução, não suavização |
| HMM e Wu et al. (2022) | Comparações previstas | Só literatura (REV-006, REV-042) |
| Explicabilidade, calibração, *dashboard* | Previstos | Não concluídos nesta fase |
| Dados reservados | Treino/validação/teste | Papéis trocados (§6): `test` seleciona, `validation` mede no fim |

A divisão por viagem mede generalização entre viagens. Viagens do mesmo navio podem estar em conjuntos diferentes (decisão do utilizador), por isso **não se afirma generalização para navios inéditos**.

## 3. Perguntas de investigação e respostas

- **RQ1** (a sobreposição reduz a instabilidade das fronteiras face a janelas sem sobreposição?): no `test`, J50 fragmenta menos, sem melhorar de forma consistente o erro de fronteira; as janelas não superam a viagem completa.
- **RQ2** (o pós-processamento reduz a fragmentação e melhora a concordância com os segmentos?): sim, no `validation`, numa medição que não é independente.
- **RQ3** (como interagem?): sem resposta.

As ressalvas completas estão no relatório. Um resultado sem melhoria é válido: o protocolo não se altera para fabricar ganhos.

## 4. Marcos

| # | Marco | Estado |
|---|---|---|
| 1 | Ambiente, divisão por ID, isolamento | Fechado |
| 2 | Preparação auditável (só treino/sintéticos) | Fechado (REV-019) |
| 3 | CNN 1D de referência sobre a viagem completa | Fechado (REV-041); não se altera |
| 4 | A mesma CNN em janelas | Feito (REV-046, REV-047) |
| 5 | Pós-processamento | Feito (REV-056 a REV-059) |
| 6 e 7 | Congelar as variantes e medição final no `validation` | Feito (REV-053), só a referência |
| — | Relatório | Completo (REV-065); falta a leitura do utilizador |

## 5. Modelos e protocolos

Os números dos resultados não se repetem aqui: estão em `results/` e, no relatório, em macros geradas.

### 5.1 CNN de referência (viagem completa)

```text
[7, N] → Conv1D 32 (k5, same) → ReLU → Conv1D 64 (k5, same) → ReLU
       → Conv1D 32 (k5, same) → ReLU → Conv1D 1 (k1) → logits [1, N]
```

- Campo recetivo de 13 pontos; 21 761 parâmetros (`src/ais/phase1/model.py`). A entrada completa não dá contexto global.
- O modelo devolve logits; `BCEWithLogitsLoss` sem pesos de classe; a sigmoide aplica-se uma só vez, na inferência. `id`, `point_id` e `t` nunca são entradas.
- Adam, lr 1e-3, 300 épocas sem paragem antecipada, uma viagem por passo, seed 42, CPU, um checkpoint por época (`configs/phase1_select.json`). Valores iniciais, não otimizados.
- Seleção no `test` numa só ronda (`configs/selection_protocol.json`): época pela menor perda por ponto (162) e limiar pelo F1 médio (0,65). Congelada em `results/baseline_frozen/`.
- Limitação: a perda no `test` oscila entre épocas e a época escolhida é um mínimo estreito.

### 5.2 Janelas (J0 e J50)

- Janelas de L = 64 pontos; J0 com passo 64, J50 com passo 32; a mesma sobreposição no treino e na inferência. Mesma CNN, normalizador, seed e valores da referência, mas lote de 32 janelas e limite de 45 minutos (`configs/windows_j0.json`, `windows_j50.json`; `src/ais/phase1/windows.py`).
- Cada viagem começa no índice 0 e pára na primeira janela que alcança o fim; a última pode ficar mais curta, sem pontos falsos. Nenhuma janela atravessa viagens; os intervalos de tempo dentro de uma viagem não cortam a sequência.
- O enchimento serve só para empilhar: a máscara tira-o da perda e da média e a rede põe-no a zero depois de cada ReLU. Perda: média das posições reais do lote.
- Probabilidade por ponto: média simples das janelas que o cobrem (float64); o limiar aplica-se depois.
- Seleção no `test` numa só abertura (`configs/selection_protocol_windows.json`), com os critérios da referência sobre a probabilidade reconstruída: J0 época 8, limiar 0,60; J50 época 4, limiar 0,75. A perda no `test` sobe com o treino.

### 5.3 Filtro temporal

- Média pesada gaussiana das probabilidades de pesca, ponto a ponto, dentro de cada viagem; σ = tamanho/6; nas pontas usam-se só os pontos existentes, com pesos reajustados; depois o limiar 0,65 (`src/ais/phase1/postprocessing.py`). Só a referência.
- Aplicado às previsões **já guardadas** da medição final: não se reabriu o parquet nem se correu a CNN; as anotações foram reutilizadas para medir.
- **Registo de integridade.** A v1 (13 pontos, protocolo `posproc_validation_v1`) foi aplicada primeiro ao `validation`: exatidão 94,4 % → 94,5 %; segmentos de pesca previstos 486 → 255 (reais 18); F1 de segmentos de pesca 0,028 → 0,066. Por ter ficado aquém, decidiu-se procurar outra janela **depois de ver esse resultado**.
- [REV-069 | cor #7B68EE] O relatório conta as duas janelas, com os valores da v1 em macros (`build_postproc_results --first-version-only`).
- Escolha dos 301 pontos: a partir dos blocos de erro no `test` e do cálculo com probabilidades ideais (o limiar 0,65 torna o filtro assimétrico); o efeito no `test` (13, 201, 301 e 401 pontos) só se mediu **depois** da escolha. No `test`, 301 levou a exatidão de 94,7 % a 95,7 % e piorou 8 de 18 viagens.
- A v2 (301 pontos, `configs/postproc_protocol_v2.json`) correu uma vez no `validation`, com uma segunda implementação a confirmar 19 de 19 valores (`verify_postproc_independent --size 301 results/final_validation/predictions_validation.csv`). **O resultado não é uma medição independente** e o relatório declara-o (decisão do utilizador, REV-065, que substitui a de omitir a v1).

## 6. Política de acesso aos dados

As regras completas estão no `AGENTS.md` §3. Resumo operacional:

| Etapa | Dados permitidos | Condição |
|---|---|---|
| A — Desenvolvimento | Treino oficial ou sintéticos | Autorizada. Inclui debugging, gráficos, benchmarks, inspeção e testes de integração |
| B — Seleção | `test` | Só com autorização explícita (âmbito declarado), depois de congelar a implementação |
| C — Medição final | `validation` | Só com nova autorização, uma só vez, com tudo congelado. **Feita em REV-053 (2026-11-24 00:32 UTC); o `validation` está gasto** |

- **Nomes e papéis (REV-036):** os ficheiros mantêm os nomes `validation` e `test`, mas os papéis estão trocados face ao habitual. Os resultados no `test` são otimistas por terem servido a escolher; o número final do relatório é o do `validation`.
- A divisão foi feita antes de qualquer exploração, só com IDs e contagens; `manifests/split_manifest_seed42.csv` não se refaz.
- Normalizadores e qualquer objeto aprendido ajustam-se só no treino (ou no treino interno, separado por ID antes de transformações e janelas).
- **Mecanismo (REV-038):** autorização em `configs/authorizations/` a partir de uma instrução do utilizador, protocolo declarado antes e registo em `results/access_log.jsonl`; `ais.phase1.reserved` recusa uma segunda ronda e o `validation` sem autorização própria. É uma salvaguarda do código, não uma garantia.
- Uma flag no código ou uma decisão do agente nunca é autorização.
- **Não voltar a correr** `select_on_test`, `select_windows_on_test`, `final_validation` nem `postproc_validation`.
- Exposição já ocorrida (REV-015): validação e teste foram lidos por inteiro só para construir as bases limpas e contar linhas e viagens.
- Nenhum valor empírico usado como evidência pode depender só de um cálculo informal do agente (`AGENTS.md` §10).

## 7. Avaliação (como foi implementada)

- **Por ponto:** exatidão, precisão, sensibilidade, F1, IoU e matriz de confusão; comparação com a classe maioritária.
- **Por segmento** (`src/ais/phase1/segments.py`): blocos máximos da mesma classe por viagem, sem suavizar; IoU temporal em segundos; correspondência um-para-um, gulosa, com IoU ≥ 0,5; F1 de segmentos; fragmentação (previstos/reais); erro de fronteira (mediana do desvio absoluto nos pares).
- A estabilidade perante pequenas alterações de parâmetros **não foi medida**.

## 8. Dimensão humana e limites

O objetivo previa apoiar o inspetor. Uma probabilidade bruta não é confiança calibrada; o sistema não fundamenta sanções de forma autónoma; sem estudo com inspetores não se afirma utilidade operacional.

## 9. Referências verificadas

Confirmação das frases do relatório nos PDF de `docs/bibliografia/` (pasta local, não versionada) e, para Agnew, na página da PLOS ONE (2026-11-25). O relatório usa a entrada `ferreira2022full` (quatro autores).

| Fonte | O que o artigo diz | Consequência |
|---|---|---|
| Agnew et al. (2009) | Perdas anuais de 10 a 23,5 mil milhões de dólares, 11 a 26 milhões de toneladas (pesca ilegal e não declarada). Nas pescarias estudadas, 13 a 31 % (média 18 %) | **«Até cerca de 20 % da captura mundial» não está no artigo.** O relatório usa o intervalo de valor e de toneladas |
| Chuaysi e Kiattisin (2020) | Liga a pesca IUU à sobre-exploração e a trabalho ilegal; cita 11 a 26 milhões de toneladas | Serve para essas ligações |
| Kroodsma et al. (2018) | O AIS difunde identidade, posição, velocidade e ângulo de viragem a cada poucos segundos; 22 mil milhões de mensagens; redes convolucionais | Confirma; não diz que o AIS é a «principal» fonte |
| Natale et al. (2015) | Identifica pesca pelos perfis de velocidade (frota sueca) e mapeia o esforço | Confirma o padrão de velocidade; também os intervalos das mensagens AIS (2 s a 3 min) |
| Peel e Good (2011); Vermard et al. (2010) | Modelos de Markov escondidos sobre VMS | Confirma |
| Soares Júnior et al. (2018) | Segmentação semi-supervisionada com *Minimum Description Length* | Confirma |
| Wu et al. (2022) | Classificador (floresta aleatória) sobre janelas sobrepostas; junção das janelas de pesca próximas por *run-length encoding* (WBS-RLE) | É a descrição usada no relatório |
| Wu et al. (2022), dados | AIS da autoridade marítima dinamarquesa, navios de pesca, 14 a 20 de novembro de 2021; posições duplicadas removidas e coordenadas com o mesmo instante calculadas pela média; 128 trajetórias anotadas à mão, 1 080 220 pontos | Esclarece a proveniência das anotações. O ficheiro público tem menos trajetórias e linhas; o relatório diz-o |
| Arasteh et al. (2020), FishNET | CNN para classificar segmentos de atividade | Trabalho próximo, citado |
| Cheng et al. (2025) | Classifica cinco **tipos** de navio de pesca | Não é deteção de atividade |
| Wang et al. (2026) | Quatro estados operacionais, com atenção local e global | É a descrição usada no relatório |
| Hu et al. (2026) | Segmentação não supervisionada de subtrajetórias com campos angulares de Gram e previsão de trajetória | É a descrição usada no relatório |
| Ferreira et al. (2022) | Rótulos obtidos por agrupamento da geometria; redes recorrentes | Confirma |
| Shneiderman (2020); Guo et al. (2017); Lundberg e Lee (2017) | PDF fora da pasta | Confirmados depois só pelos resumos no arXiv |
| Ghazizadeh (2019) | PDF sem texto extraível | Não citado; não verificado |

## 10. Ambiente

Python com `venv` + `pip` (`iach-ais-venv-4/`, ignorado pelo git); versões fixas em `requirements.txt`. Intel i7 de 12.ª geração, 16 GB de RAM, GPU integrada: tudo em CPU. KNIME só como contingência por decisão do utilizador.

## 11. Documentos arquivados

Retirados da pasta em REV-067, por estarem concluídos ou desatualizados. Continuam na etiqueta git `docs-historico-v1`; os registos (`PROGRESS.md`, `REVISION_LOG.md`), os protocolos em `configs/` e comentários antigos podem citá-los pelo nome.

| Documento | Conteúdo | O essencial passou para |
|---|---|---|
| `02_cnn_viagem_completa.md` | Contratos e implementação da referência | §5.1 |
| `03_cnn_janelamento.md` | Contratos e testes do janelamento | §5.2 |
| `04_pos_processamento.md` | Plano e registo do filtro, análise no `test`, v1 e v2 | §5.3 |
| `05_releitura_proposta.md` | Passagens da proposta por corrigir (A a H), todas fechadas | — |
| `06_plano_reescrita.md` | Plano da passagem a relatório | §9 (verificação bibliográfica) |

Ler um deles sem o repor:

```bash
git show docs-historico-v1:docs/04_pos_processamento.md
```

Trazer um de volta:

```bash
git restore --source=docs-historico-v1 -- docs/04_pos_processamento.md
```
