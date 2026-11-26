# Handoff — Projeto AIS

**Atualizado em 2026-11-26 01:03 WET (UTC+00:00).** Reescrito de raiz em REV-066, para continuar numa nova conversa; atualizado em REV-067 a REV-079 (a REV-072 foi aplicada depois da 073). As horas são WET, lidas com `date` ou do `git log`.

## Ponto de situação em quatro linhas

- O trabalho técnico está **feito**: preparação, CNN baseline, janelas (J0, J50), medição final no `validation` e filtro temporal.
- O documento ativo é o **relatório** `latex/relatorio_pt.tex` (completo, 10 páginas, a preto), que substituiu a proposta.
- **Galeria (REV-073)** em `viagens/`, ligada ao `README.md` e enviada; **REV-072** aplicada: o modelo da viagem completa chama-se **baseline** e o relatório está todo a preto.
- **REV-074** a **REV-077** enviadas. **REV-078** (Anexo B do relatório com a ligação para `viagens/galeria_viagens.pdf` no GitHub; não mover esse ficheiro) e **REV-079** (e-mail do autor, alterado pelo utilizador) em commits locais, **por enviar**. **Por fazer:** a leitura do relatório pelo utilizador (REV-080).
- Não há treinos, medições nem acessos a dados pendentes.

Mensagem sugerida para abrir a nova conversa: «Lê o AGENTS.md e o handoff.md e diz-me o ponto de situação. Quero continuar o relatório.»

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas (o `CLAUDE.md` manda lê-lo antes de qualquer ação).
2. Este ficheiro.
3. O topo do `PROGRESS.md` (estado, decisões, pendências).
4. `latex/relatorio_pt.tex` ou o PDF em `latex/build/relatorio_pt.pdf`.
5. Só se for preciso: `docs/00` (modelos, protocolos, acesso e referências verificadas), `docs/01` (dados) e `REVISION_LOG.md`.
6. Antes de agir: `git status -sb`, `git log --oneline -10` e os testes.

## Última validação

| Verificação | Resultado | Hora (WET; 2026-11-25 salvo indicação) |
|---|---|---|
| `pytest tests/` | 256 passaram; 2026-11-26 | 00:50 |
| Relatório (vigilante) | 10 páginas, sem referências em falta; 662 números de linha nas margens; 2026-11-26 | 01:03 |
| GitHub (`git push` da REV-077) | `main` local e remoto em `ce81668` antes da REV-078; 2026-11-26 | 00:52 |
| Vigilante do LaTeX | um a correr, com a versão nova (reiniciado às 00:00 de 2026-11-26) | 00:03 |
| Recuperação da proposta antiga (num clone temporário) | os dois comandos do `README.md` funcionaram e a proposta compilou | 23:12 |
| Revisão independente do relatório (subagente Opus, só leitura; anterior à REV-068) | sem erros graves; achados aplicados | 23:00 |

O que mudar depois destas horas **não foi** validado por este handoff.

## Cronologia dos commits recentes

| Commit | Data e hora | Assunto |
|---|---|---|
| `6f94ec1` | 2026-11-26 01:01 | Acrescenta ao relatório o anexo com a ligação para a galeria (REV-078) |
| `ce81668` | 2026-11-26 00:51 | Regista o pedido de envio da REV-077 |
| `11ce248` | 2026-11-26 00:50 | Corrige uma frase do AGENTS sobre os documentos LaTeX (REV-077) |
| `e2a9907` | 2026-11-26 00:50 | Acrescenta a galeria de viagens em LaTeX e PDF (REV-077) |
| `3b3be87` | 2026-11-26 00:45 | Legenda da Tabela 6 explica porque o teste é otimista (REV-076) |
| `c1dfe83` | 2026-11-26 00:40 | Regista o pedido de envio das REV-074 e REV-075 |
| `0ad4837` | 2026-11-26 00:38 | Legendas das Figuras 3 e 8 deixam de tapar o gráfico (REV-075) |
| `3171028` | 2026-11-26 00:38 | Legendas das Figuras 3 e 8 fora das barras e curvas, no código (REV-075) |
| `122a4d8` | 2026-11-26 00:31 | Figura 7 com «baseline» em vez de «previsto» (REV-074) |
| `d68d595` | 2026-11-26 00:30 | A Figura 7 passa a dizer «baseline» no código (REV-074) |
| `81ad42b` | 2026-11-26 00:27 | Troca «referência» por «baseline» e põe o relatório todo a preto (REV-072) |
| `e2bed4b` | 2026-11-26 00:25 | Figuras e galeria passam a dizer «baseline» no código (REV-072) |
| `f707939` | 2026-11-26 00:22 | Acrescenta a galeria de viagens ao repositório (REV-073) |
| `abd8cab` | 2026-11-26 00:21 | Cria o programa da galeria de viagens e grava as autorizações (REV-073) |
| `ff050a8` | 2026-11-26 00:04 | Regista o pedido de envio das REV-069 a REV-071 |
| `442a19f` | 2026-11-26 00:03 | Preenche a página 8 do relatório com o início do anexo (REV-071) |
| `2b91f35` | 2026-11-25 23:59 | Documenta como compilar com os números de linha nas margens (REV-070) |
| `7cef3e2` | 2026-11-25 23:56 | Acrescenta um commit em falta à cronologia do handoff (REV-069) |
| `0760bec` | 2026-11-25 23:56 | Conta no relatório as duas janelas do filtro (REV-069) |
| `aa918ae` | 2026-11-25 23:39 | Prepara o handoff para uma nova conversa (REV-068) |
| `6249d54` | 2026-11-25 23:37 | Regista o pedido de envio da REV-068 |
| `5ee8117` | 2026-11-25 23:35 | Retira do resumo a ressalva sobre o filtro (REV-068) |
| `d750eb1` | 2026-11-25 23:24 | Regista que nenhum vigilante fica a correr (REV-067) |
| `79eca07` | 2026-11-25 23:23 | Regista que o vigilante antigo foi parado (REV-067) |
| `552c0fc` | 2026-11-25 23:22 | Atualiza o handoff e os registos depois de confirmar o GitHub (REV-067) |
| `7b9005a` | 2026-11-25 23:18 | Regista o arquivo dos documentos e atualiza o handoff (REV-067) |
| `463606e` | 2026-11-25 23:18 | Arquiva os documentos concluídos e reescreve docs/00 (REV-067) |
| `b8580b5` | 2026-11-25 23:13 | Reescreve o handoff para uma nova conversa (REV-066) |
| `edc3dda` | 2026-11-25 23:12 | Atualiza o estado e o registo de revisões (REV-066) |
| `8950471` | 2026-11-25 23:12 | Atualiza regras, README e docs depois de retirar a proposta (REV-066) |
| `100e2b2` | 2026-11-25 23:12 | Retira a proposta em LaTeX e guarda o seu PDF (REV-066) |
| `661da35` | 2026-11-25 23:03 | Regista o envio do main e da etiqueta para o GitHub (REV-065) |
| `280459d` | 2026-11-25 23:01 | Fecha os registos da REV-065 |
| `ace6b2b` | 2026-11-25 23:01 | Aplica a revisão independente ao relatório (REV-065) |
| `08682a4` | 2026-11-25 22:55 | Alinha o Marco 5 e fecha a releitura nos documentos (REV-065) |
| `fd81dc8` | 2026-11-25 22:55 | Relatório: introdução, trabalho relacionado, dados, ética, conclusões e resumo (REV-065) |
| `219f471` | 2026-11-25 22:44 | Corrige a hora das entradas da REV-065 |
| `d993734` | 2026-11-25 22:44 | Registos da REV-065 e verificação bibliográfica |
| `4b799bd` | 2026-11-25 22:44 | Relatório: método, protocolo, resultados, anexo e limitações (REV-065) |
| `ea972d5` | 2026-11-25 22:39 | Gera as macros dos blocos de erro e as duas figuras do relatório (REV-065) |
| `b06dddc` | 2026-11-25 22:38 | Macros dos blocos de erro e figuras do relatório com «referência» (REV-065) |
| `c6cbf83` | 2026-11-25 22:37 | Versão de segurança e esqueleto do relatório (REV-065) |
| `38f2857` | 2026-11-25 22:37 | Plano de reescrita da proposta como relatório (REV-064) |
| `7d60861` | 2026-11-25 21:24 | Última versão da proposta (REV-063; etiqueta `proposta-pt-v1`) |

O commit desta atualização do handoff vem a seguir e não está na tabela; confirmar com `git status -sb` se já foi enviado.

## O que se fez nesta conversa (2026-11-25, à noite)

1. Leitura do projeto e diagnóstico da proposta (misturava proposta e relatório, repetia assuntos, tinha contradições).
2. Plano da reescrita (REV-064; arquivado, era o `docs/06`); o utilizador aceitou as decisões D1 a D8.
3. Relatório novo (REV-065): oito secções, anexo e bibliografia; macros novas dos blocos de erro; duas figuras com «referência»; referências confirmadas nos artigos; revisão independente aplicada.
4. Push do `main` e da etiqueta, a pedido.
5. Arrumação (REV-066): proposta em LaTeX retirada, PDF guardado, build do relatório direto em `latex/build/`, documentos refeitos.
6. Documentação (REV-067): ficam `docs/00` (reescrito) e `docs/01`; `docs/02` a `06` na etiqueta `docs-historico-v1`; envio para o GitHub a pedido.
7. O utilizador confirmou que a pasta `docs` fica assim (não repor o `05` nem o `06`), iniciou o vigilante novo e pediu para confirmar o GitHub, atualizar os registos e voltar a enviar.
8. Ajuste ao resumo (REV-068): retirada a ressalva sobre o filtro, PDF recompilado e enviado ao utilizador, push a pedido.
9. Handoff e registos atualizados e validados de novo, para continuar numa conversa nova.

## Estado e resultados

Dataset: 123 viagens, 1 026 279 pontos; divisão por viagem, seed 42: treino 87 (713 854), teste 18 (103 409), validação 18 (209 016). Fonte: Zenodo (Song Wu, CC BY 4.0).

| Resultado | Valor | Conjunto |
|---|---|---|
| Baseline (época 162, limiar 0,65) | exatidão 94,7 % | `test` (otimista) |
| Baseline, medição final | exatidão 94,4 % (classe maioritária: 83,2 %) | `validation` |
| J0 (época 8, limiar 0,60) e J50 (época 4, limiar 0,75) | 93,4 % e 93,7 %; J50 fragmenta menos | `test` |
| Filtro de 301 pontos | 94,4 % → 94,8 %; segmentos de pesca previstos 486 → 32 (reais 18); piora 7 de 18 viagens | `validation`, **não independente** |

RQ1: as janelas não superam a viagem completa. RQ2: o filtro reduz muito a fragmentação. RQ3: sem resposta. Critérios de sucesso: (i) cumprido com ressalvas, (ii) em parte, (iii) não.

## O relatório

Estrutura: resumo; 1 Introdução; 2 Trabalho relacionado; 3 Dados e preparação; 4 Método; 5 Protocolo experimental; 6 Resultados e discussão; 7 Limitações, ética e dimensão humana; 8 Conclusões e trabalho futuro; anexo do janelamento.

**Compilar:** `bash latex/watch_latex.sh` (local, não versionado; recompila para `latex/build/relatorio_pt.pdf`) ou os comandos do `README.md`. O vigilante só reage a `relatorio_pt.tex` e `references.bib`: depois de gerar macros ou figuras, reiniciá-lo. Desde a REV-070 compila até o `.aux` estabilizar (para os números de linha ficarem nas margens) e `--once` compila uma só vez. Depois de mudar o próprio script, reiniciar o vigilante.

**Números e figuras** (nunca escrever à mão um número empírico):

| Ficheiro em `latex/` | Gerado por (`ais.cli.…`) |
|---|---|
| `generated/resultados.tex` | `build_final_results` |
| `generated/resultados_janelas.tex`, `figures/janelas_perda.png` (a figura também se refaz com `--report-figures-only`) | `build_window_results` |
| `figures/janelas_viagens_baseline.png`, `janelas_linha_temporal_baseline.png` | `build_window_results --report-figures-only` |
| `generated/resultados_validacao.tex`, `figures/validacao_*.png` | `build_validation_results` |
| `generated/resultados_posproc.tex`, `figures/posproc_resultados.png`, `posproc_viagem.png` | `build_postproc_results` |
| `generated/resultados_posproc_v1.tex` | `build_postproc_results --first-version-only` |
| `generated/resultados_buracos.tex` | `build_window_analysis_macros` |
| `figures/posproc_janela.png` | `plot_postprocessing_kernel` |

As figuras do esquema e da CNN são TikZ no próprio `.tex`. Alguns geradores leem previsões já guardadas dos conjuntos reservados: não os correr sem necessidade e, para o `test` ou o `validation`, pedir autorização.

**Resumo (REV-068):** o utilizador mandou retirar «este resultado não vem de uma medição independente». Não a repor no resumo; a ressalva continua no corpo e não se retira de lá sem pedido.

**Filtro (REV-069):** o relatório conta que se testou primeiro 13 pontos (ganho pequeno, não piorou no total) e depois 301; mais dimensões e tipos de janela ficam para trabalho futuro. A frase do resumo começa por «Sobre as previsões dessa medição».

**Não reintroduzir** (corrigido em REV-065, algumas coisas pela revisão independente):
- o resultado do filtro como medição independente, ou «medido uma única vez»; a versão de 13 pontos está declarada;
- que a janela de 301 foi escolhida comparando várias dimensões (o efeito no `test` só se mediu **depois** da escolha, sem regra declarada antes);
- o critério da medição final como declarado antes de se conhecerem os resultados do `test`;
- a menor fragmentação de J50 como efeito só da sobreposição (limiar, época e passos também diferem);
- «até cerca de 20 % da captura mundial» (não está em Agnew) ou o artigo de Cheng como deteção de pesca (classifica tipos de navio).

**Bibliografia:** verificação em `docs/00` §9. `ferreira2022full` é a entrada que o relatório usa (quatro autores). Shneiderman, Guo e Lundberg só foram confirmados pelos resumos no arXiv.

## Proposta anterior

`latex/proposta_pt.tex` já não existe na pasta. PDF em `latex/proposta_pt.pdf`; versão completa na etiqueta `proposta-pt-v1` (comandos no `README.md`). Não repor a pasta `latex/` inteira a partir da etiqueta. `latex/proposta_IAHC_DINIS_ROSA.pdf` é a entregue ao professor e não se altera.

## Decisões vigentes

A lista completa está no topo do `PROGRESS.md`; o registo da versão de 13 pontos do filtro está em `docs/00` §5.3. As que mais pesam:

- Documentação: ficam só `docs/00` e `docs/01` (confirmado pelo utilizador; não repor `05` nem `06`).
- `test` seleciona, `validation` mede; o `validation` está gasto. **Não voltar a correr** `select_on_test`, `select_windows_on_test`, `final_validation` nem `postproc_validation`.
- Baseline, J0 e J50 fechadas. Sem novos treinos sem decisão do utilizador.
- Relatório: máximo 15 páginas (alvo 13 ou menos); título mantido; «Figura» e «Tabela» em português; números de linha até à versão final.
- Perguntas de investigação, objetivos e critérios de sucesso não mudam depois dos resultados.
- Explicabilidade, calibração e *dashboard*: «previstos, não concluídos nesta fase».
- **Cores:** a REV-065 foi a preto por exceção autorizada. A partir da REV-068, qualquer texto novo ou substituído no `.tex` leva `\revtext{revNNN}{…}`, com `\definecolor{revNNN}` no preâmbulo (acrescentar `\usepackage{xcolor}` se faltar) e uma cor ainda não usada no `REVISION_LOG.md`. A REV-068 só eliminou texto, por isso não há cor no `.tex`. Na REV-072 o utilizador mandou usar preto e passar todo o texto a preto. A REV-076 também ficou a preto, só dessa vez. A REV-078 está a cor no `.tex`. **Próximo ID livre: REV-080.**

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, `handoff.md` |
| Relatório | `latex/relatorio_pt.tex`, `references.bib`, `figures/`, `generated/` |
| Documentação | `docs/00`, `docs/01`; arquivo na etiqueta `docs-historico-v1` (`docs/00` §11) |
| Galeria | `viagens/` (gerada por `build_trip_gallery`; PDF e `.tex` por `build_trip_gallery_pdf`; não editar à mão) |
| Código | `src/ais/phase1/` (biblioteca), `src/ais/cli/` (programas, tabela no `README.md`) |
| Configuração | `configs/` e `configs/authorizations/` |
| Só nesta máquina (não vão para o git) | `data/`, `results/` (modelos, previsões, `access_log.jsonl`), `iach-ais-venv-4/`, `docs/bibliografia/`, `latex/build/`, `latex/watch_latex.sh` |

## Comandos úteis (a partir da raiz)

```bash
git status -sb
```

```bash
iach-ais-venv-4/bin/python -m pytest tests/
```

```bash
bash latex/watch_latex.sh
```

## O que falhou ou exigiu correção (nesta conversa)

- Horas escritas à frente do relógio duas vezes (corrigidas): **usar sempre `date`** antes de escrever uma hora.
- Frases erradas minhas apanhadas pela revisão independente (ver «Não reintroduzir»): confirmar nos registos a ordem dos factos antes de a descrever.
- O vigilante antigo deixou um `texput.log` quando a proposta foi retirada.
- Ao retirar documentos, o utilizador esperava outra escolha: confirmar **quais** antes de apagar (desta vez aceitou como ficou).
- Dos anteriores: não correr testes nem subagentes durante treinos; ao trocar texto dentro de `\revtext{…}{…}`, conferir as chavetas; `%` nu em `\texorpdfstring` parte o LaTeX; `class_metrics` duplicada.

## O que fazer a seguir

1. Os ajustes que vierem da leitura do utilizador (REV-080).
2. Se pedido: traduzir «Abstract» e «References» (no modelo IJCAI); versão final sem números de linha.
3. **Push:** só a pedido. As REV-078 e REV-079 estão por enviar; confirmar com `git status -sb`. O repositório é público.
4. Opcional: arrumação técnica (testes dos programas de treino, figuras e resultados; unificar `class_metrics`; figuras sem uso em `latex/figures/`, que o utilizador preferiu manter).
5. Limitações em aberto: CRS (hipótese WGS84), 128 contra 123 trajetórias, fiabilidade das anotações, cálculo de `distanceToShore`.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. `test` e `validation` só com autorização explícita, escrita em `configs/authorizations/`; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado (AGENTS §10); no LaTeX, só por macros geradas. Valores externos levam citação.
- **Push (REV-055):** se o utilizador pede, enviar sem mais perguntas; por iniciativa própria, nunca. Sem `--force`.
- Explicar comandos e alterações antes de os fazer; comunicar em português de Portugal; funções e variáveis em inglês.
- No fim de cada interação com alterações: `PROGRESS.md` e `REVISION_LOG.md`, e confirmar que `README.md`, `docs/` e o relatório não se contradizem.
- Commits por tema, com mensagem completa e a linha de coautoria.

## Preferências do utilizador observadas

- Quer um **plano** antes de uma mudança grande e decide sobre ele; depois dá autonomia.
- No fim de um bloco de trabalho pede os registos atualizados, commit e push.
- Quer sempre uma forma de voltar atrás (cópia ou etiqueta) antes de reescrever ou apagar.
- Decide depressa («aceito», «sim, continua»); registar as decisões como são ditas.
- Gosta de resultados em tabelas e imagens, com o porquê, em linguagem simples.
- Numa sessão anterior preferiu delegar trabalho pesado na Abacus (nunca o OpenCode), só com código e descrições, **nunca dados**.
