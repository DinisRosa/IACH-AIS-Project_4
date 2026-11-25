# 01 — Dados e preparação

[REV-033 | cor #3E2723] Documento fundido a partir do dicionário de `00_contexto…`, de `01_preparacao_comum` e de `04_especificacao_funcoes_preparacao`. Descreve os dados, o que foi verificado e **o que a preparação realmente faz**. As regras de acesso estão em `00` §6 e no `AGENTS.md` §3.

## 1. O dataset

- **123 viagens (IDs únicos) e 1 026 279 linhas**, verificados por `src/ais/cli/verify_trip_count.py` (REV-007). O nome do ficheiro e a página do Zenodo dizem 128; o ficheiro local tem 123. O PDF entregue ao professor diz 128 e não se altera; o relatório (`latex/relatorio_pt.tex`) usa 123 e indica a diferença.
- Divisão por ID completo, seed 42: treino 87 viagens (713 854 linhas), validação 18 (209 016), teste 18 (103 409).
- O `id` é uma string composta (navio + `-` + viagem). Não se converte para número, não é entrada da CNN e não se assume que o sufixo seja um contador diário.
- Todas as linhas, sequências e janelas de um ID ficam no mesmo conjunto.

Cabeçalho do ficheiro original (13 colunas, 12 além do rótulo) e linha de exemplo:

```csv
id,t,longitude,latitude,x,y,signed_turn,bearing,time_gap,distance_gap,euc_speed,distanceToShore,label
211477000-2,2021-11-14 15:00:10,12.31017,56.127777,705723.070725276,6225237.28619866,-1.234665653,309.501333116,4,2.979796558,1.448065282,6.726539723,01-sailing
```

## 2. Colunas originais

| Coluna | Tipo lógico | Significado e unidade (estado) | Papel |
|---|---|---|---|
| `id` | string | Navio + viagem | Agrupar e dividir; nunca feature |
| `t` | datetime | Data e hora, resolução de segundos; fuso ignorado por decisão (REV-002) | Ordenação e intervalos; não é valor absoluto de entrada |
| `longitude`, `latitude` | float64 | Graus decimais; CRS não indicado, hipótese WGS84 (por confirmar) | Mapas e verificação |
| `x`, `y` | float64 | Metros num referencial plano; SRID 25832 (ETRS89/UTM 32N) segundo o README do Zenodo | Distâncias e rumo; **fora das entradas** da CNN (REV-019) |
| `signed_turn` | float64 | Graus; diferença de `bearing` entre pontos consecutivos, em (-180, 180] (REV-003) | Substituída pela versão recalculada |
| `bearing` | float64 | Graus a partir do norte; azimute do ponto anterior para o atual (REV-003) | Fora das entradas (é função de x e y) |
| `time_gap` | float64 | Segundos entre pontos consecutivos (REV-003) | Comparação com o recálculo |
| `distance_gap` | float64 | Metros entre pontos consecutivos (REV-003) | Comparação com o recálculo |
| `euc_speed` | float64 | Nós: `distance_gap / time_gap × 1,94384` (REV-003) | Comparação com o recálculo |
| `distanceToShore` | float64 | Metros, à costa da Dinamarca (README do Zenodo, REV-008); método de cálculo não documentado, aceite como correto (REV-011) | Entrada da CNN |
| `label` | string | Cinco categorias, ver §4 | Resposta; nunca entrada |

As verificações de unidades foram feitas só com o treino (87 IDs, 713 767 pares consecutivos) por `src/ais/cli/check_units_train.py`, que escreve `results/units_check_train/summary.json` (não versionado).

## 3. Cuidados com tipos e ausências

- Preservar `id` como texto; não truncar casas decimais; guardar `t` como datetime.
- Uma ausência não é um zero físico: mantém-se ausente até aplicar a política da §6.
- Converter para `float32` só nas entradas do modelo, depois de todos os cálculos.
- Latitude/longitude e x/y representam a mesma posição em referenciais diferentes. Nunca tratar graus como metros.
- As variáveis originais ficam preservadas; as calculadas têm nome próprio e unidade explícita.

## 4. Rótulos

```text
01-sailing, 03-sailing, 05-sailing → target 0 (navegação)
02-fishing, 04-fishing             → target 1 (pesca)
```

Preserva-se `label` e cria-se `target` à parte. O prefixo numérico não é intensidade. Uma categoria desconhecida dá erro, nunca é convertida para 0. Mantém-se o desequilíbrio natural: sem reamostragem nem pesos de classe na configuração inicial.

## 5. Variáveis recalculadas

Criadas por `src/ais/cli/build_clean_dataset.py` dentro de cada viagem (sem diferenças através de IDs):

| Coluna | Definição |
|---|---|
| `time_gap_calc_s` | `t[i] − t[i−1]` em segundos |
| `distance_gap_calc_m` | Distância euclidiana plana em x/y, em metros |
| `bearing_calc_deg` | Azimute a partir do norte, pela grelha UTM |
| `signed_turn_calc_deg` | Diferença de `bearing_calc_deg`, normalizada para (-180, 180] |
| `speed_calc_mps` | `distance_gap_calc_m / time_gap_calc_s`, só com intervalo positivo |

Se algum dia se excluírem pontos, recalcula-se tudo o que depende do predecessor; nunca se combina a distância do predecessor antigo com o tempo do novo. Até agora **nenhuma linha foi removida**. Intervalos não positivos não ocorrem nos dados (REV-009).

## 6. Entradas da CNN e valores em falta

Características, por ordem (REV-019): `speed_calc_mps`, `signed_turn_calc_deg`, `time_gap_calc_s`, `distanceToShore`. A decisão é do utilizador, não uma conclusão sobre a inutilidade das restantes colunas; pode rever-se com evidência.

- O 1.º ponto de cada viagem não tem `time_gap`, `speed` nem `signed_turn`; o 2.º não tem `signed_turn`.
- Política (REV-022): nenhuma linha removida; preenchimento com **zero depois de normalizar**, mais uma **máscara de ausência** por característica (`speed`, `signed_turn`, `time_gap`). Não se inventa `bearing` para o 1.º ponto. Os pontos iniciais entram na perda.
- Entrada final: **7 canais** (4 características normalizadas + 3 máscaras), definidos em `src/ais/phase1/data.py`.
- Normalizador: média e desvio-padrão populacional por característica, ignorando ausentes, ajustado só com o treino (ou só com o treino interno).

## 7. Como a preparação é feita

A preparação faz-se com scripts, não com os 25 módulos que as primeiras especificações previam (`data_io`, `preprocessing`, `trajectory`, `scaling`, `run_preparation`…). Foram abandonados no Marco 1 (REV-019). Pela ordem de execução:

| Passo | Ponto de entrada | Resultado |
|---|---|---|
| Divisão por ID | `src/ais/cli/create_split_manifest.py` | `manifests/split_manifest_seed42.csv` (versionado) |
| Contagem de viagens | `src/ais/cli/verify_trip_count.py` | 123 viagens e coincidência com o manifesto |
| Unidades (só treino) | `src/ais/cli/check_units_train.py` | `results/units_check_train/` |
| Base limpa | `src/ais/cli/build_clean_dataset.py --split train\|validation\|test` | `data/123_fishing_trajs_clean_{train,validation,test}.parquet` |
| Anomalias (só treino) | `src/ais/cli/count_anomalies_train.py` | `results/anomalies_train/` |
| Leitura, validação, sequências e normalização | `src/ais/phase1/data.py` | ver `02` |

Princípios mantidos: preservar originais e `point_id`; transformações devolvem cópias; diagnóstico não implica exclusão; nada de unidades ou referenciais por adivinhação; qualquer valor aprendido só no treino; versões físicas e normalizadas distinguidas. `point_id` é um inteiro estável atribuído antes de qualquer ordenação.

A base limpa de validação e de teste existe desde REV-015, só para preparação, e não há registo de análise dos seus valores.

## 8. Anomalias (só treino)

Quantificadas por `src/ais/cli/count_anomalies_train.py` (REV-017): 55 saltos acima de 30 nós em 4 viagens; 3 717 inversões de rumo acima de 170° em 70 viagens, 68 % delas em duas viagens. Mantidas tal como estão (REV-012); a limpeza por IQR foi retirada (REV-019). Assinalar uma anomalia não prova erro nem autoriza exclusão. Robustez a anomalias não é estudo próprio.

## 9. Dúvidas ainda abertas

- CRS de longitude e latitude (hipótese WGS84).
- Anotações: [REV-066 | cor #8E24AA] o artigo de Wu et al. (2022) descreve anotação manual de 128 trajetórias (1 080 220 pontos) de uma semana de AIS dinamarquês (`docs/06` §8); falta explicar a diferença para as 123 do ficheiro, a fiabilidade das anotações e a convenção dos intervalos.
- Alinhamento do rumo em tempo real: a análise é offline; uma aplicação em tempo real teria de especificar causalidade à parte.

Nenhuma destas incertezas autoriza abrir validação ou teste.
