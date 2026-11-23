# REVISION_LOG — Projeto AIS

Registo das revisões lógicas dos documentos (AGENTS.md §8). Cada revisão tem um ID sequencial estável e uma cor. O ID é a referência permanente; a cor é apenas auxiliar.

Regras:
- IDs sequenciais (REV-001, REV-002…) e nunca renumerados.
- Uma revisão pode abranger vários ficheiros e commits.
- Marcador no Markdown: `[REV-00N | cor #RRGGBB]`.
- Correspondência no LaTeX: `atualizado`, `não aplicável` ou `pendente` (com motivo).

## Paleta

| ID | Cor | Hexadecimal | RGB |
|---|---|---|---|
| REV-001 | Vermelho | `#C62828` | (198, 40, 40) |
| REV-002 | Azul | `#1565C0` | (21, 101, 192) |
| REV-003 | Verde | `#2E7D32` | (46, 125, 50) |
| REV-004 | Roxo | `#6A1B9A` | (106, 27, 154) |

## Revisões

### REV-001 — Confirmação da seed e das proporções da divisão

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Vermelho `#C62828`, RGB (198, 40, 40).
- **O quê:** confirmada a seed `42` e a divisão 70/15/15 por ID completo. Regra de arredondamento: validação e teste arredondados ao inteiro mais próximo; treino recebe o resto.
- **Porquê:** a divisão tem de estar fixada antes de qualquer exploração (docs/01 §2-§3).
- **Ficheiros e secções afetados:**
  - `docs/01_preparacao_comum.md` §3: proporções e seed marcadas como confirmadas.
  - `docs/00_contexto_projeto_dicionario_dados.md` §15, ponto 2.
  - `scripts/create_split_manifest.py` (novo): gera o manifesto.
  - `manifests/split_manifest_seed42.csv` (gerado, não versionado pela regra `*.csv`).
- **Correspondência no LaTeX (`latex/proposta_pt.tex`):** **pendente**. A proposta original fala em divisão por navio. Falta decidir se o texto da proposta deve refletir a divisão por viagem. Não alterado nesta revisão.
- **Validação:**
  - Manifesto: 123 IDs (87 treino, 18 validação, 18 teste). Cada ID num só conjunto; cobertura completa; soma das linhas = 1 026 279.
  - Reexecução do script dá o mesmo SHA-256 (`d56918bc65f9bebc6aa0a01a1e82213fda2404a9dfab9f39b3a1858c52733539`).
- **Pendentes:**
  - Diferença 128 (documentos) vs 123 (ficheiro e LaTeX): documentos corrigidos em REV-004. Por fechar no PDF da proposta, se o PDF ainda disser 128.
  - Decidir se o manifesto deve ser versionado.

### REV-002 — Decisões de âmbito: overlaps prioritários e fuso horário ignorado

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Azul `#1565C0`, RGB (21, 101, 192).
- **O quê:**
  - Os overlaps 0% e 50% são prioritários. Os 25% e 75% ficam para decisão posterior.
  - O fuso horário de `t` é ignorado. Não é necessário para o projeto.
- **Porquê:** decisões explícitas do utilizador.
- **Ficheiros e secções afetados:**
  - `docs/00_5_orientacoes_execucao_decisoes.md` (secção "Protocolo e dúvidas"): pergunta substituída pela decisão.
  - `docs/00_contexto_projeto_dicionario_dados.md` §18: fuso horário marcado como ignorado.
- **Correspondência no LaTeX:** **não aplicável**. A proposta não define a prioridade dos overlaps.
- **Validação:** não aplicável (decisão, não código).
- **Pendentes:**
  - Decidir mais tarde se os overlaps 25% e 75% entram no âmbito.

### REV-003 — Verificação de unidades e convenções no treino

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Verde `#2E7D32`, RGB (46, 125, 50).
- **O quê:** registados os resultados de `scripts/check_units_train.py` sobre o conjunto de treino. Confirmadas as unidades de `x`, `y`, `distance_gap`, `time_gap`, `euc_speed`, `bearing` e `signed_turn`. `distanceToShore` ficou por confirmar.
- **Porquê:** as unidades têm de estar confirmadas antes de recalcular variáveis (docs/01 §5).
- **Ficheiros e secções afetados:**
  - `scripts/check_units_train.py` (novo).
  - `docs/00_contexto_projeto_dicionario_dados.md` §18: subsecção "Estado das dúvidas".
  - `requirements.txt`: `matplotlib==3.10.9` (necessário para gerar os gráficos).
  - `results/units_check_train/` (gráficos e `summary.json`, gerados, não versionados).
- **Correspondência no LaTeX:** **pendente**. Não há impacto metodológico na proposta, mas as unidades devem ser refletidas no texto quando a proposta for revista.
- **Validação:**
  - Execução apenas sobre o treino: 713 854 linhas e 713 767 pares consecutivos. Validação e teste não foram lidos além do `id`.
  - Reexecução e hashes registados em `summary.json`.
- **Resultados (medianas):**
  - `x`/`y` vs haversine ≈ 1,002. `distance_gap` / distância plana = 1,0000. Logo, x/y e `distance_gap` em metros num referencial plano.
  - `time_gap` / Δt = 1,0. Logo, segundos.
  - `euc_speed` / (`distance_gap`/`time_gap`) = 1,94384. Logo, nós.
  - `bearing` = azimute inicial do ponto anterior para o atual. Logo, graus a partir do norte.
  - `signed_turn` = variação de `bearing`, normalizada para (-180, 180]. Logo, graus.
- **Anomalias não quantificadas:** `distance_gap` com razão mínima ~0,48; `time_gap` com razão mínima 1/3; `signed_turn` com diferença máxima ~175°.
- **Pendentes:**
  - Quantificar e tratar as anomalias no marco 2 (limpeza).
  - `distanceToShore`: unidade não confirmada. Metros é a hipótese mais plausível.
  - CRS exato de x/y e de longitude/latitude.

### REV-004 — Coerência documental após REV-001 a REV-003

- **Data:** 2026-11-23 (hora não registada).
- **Cor:** Roxo `#6A1B9A`, RGB (106, 27, 154).
- **O quê:** alinhamento de todos os Markdown com o estado real do projeto.
  - `PROGRESS.md`: reescrito com estado atual, artefactos e pendentes. Removido "REVISION_LOG por criar".
  - `AGENTS.md`: exemplos de ambiente trocados de `.venv` para `iach-ais-venv-4`; referência à seed 42 e ao manifesto; referência ao `latex/proposta_pt.tex` existente.
  - `README.md`: estrutura completa (scripts, manifests, requirements, REVISION_LOG, PROGRESS, results).
  - `docs/00`: número de viagens corrigido (123 IDs no ficheiro); tabela de unidades atualizada com os resultados de REV-003; dúvidas atualizadas.
  - `docs/00_5`: estado do código atualizado (executado sobre treino; modelos ainda não).
  - `docs/01`: regra de arredondamento definida (REV-001).
- **Porquê:** a documentação tinha afirmações que já não correspondiam ao estado do projeto, como "ainda não existe" e "hipótese" para unidades já verificadas.
- **Ficheiros afetados:** `PROGRESS.md`, `REVISION_LOG.md`, `AGENTS.md`, `README.md`, `docs/00_contexto_projeto_dicionario_dados.md`, `docs/00_5_orientacoes_execucao_decisoes.md`, `docs/01_preparacao_comum.md`.
- **Correspondência no LaTeX (`latex/proposta_pt.tex`):** **pendente**. O ficheiro não foi alterado. Há contagens diferentes (86/19/18 vs 87/18/18), descrições de implementações que não existem e uma lista de características diferente. Ver `PROGRESS.md`, secção "Inconsistências do LaTeX".
- **Validação:** pesquisa por texto desatualizado (`.venv`, "ainda por criar", "128", "70/15/15", "hipótese" nas unidades) em todos os MDs, e revisão dos resultados.
- **Pendentes:**
  - Decidir como tratar o LaTeX (rever ou manter a versão atual).
  - Esclarecer a discrepância 86/19/18 vs 87/18/18.
