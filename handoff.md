# Handoff — Projeto AIS

**Atualizado em 2026-11-26 01:27 WET (UTC+00:00).** Reescrito de raiz em REV-083, para continuar numa nova conversa. As horas são WET, lidas com `date` ou do `git log`. Versões anteriores estão no histórico do git (REV-044 a REV-082).

## Ponto de situação

- O trabalho técnico está **feito**: preparação, CNN baseline, janelas (J0, J50), medição final no `validation` e filtro temporal.
- O **relatório** `latex/relatorio_pt.tex` está completo: 10 páginas, todo a preto, com os anexos **depois** das referências.
- A **galeria de viagens** está em `viagens/` (página, 36 imagens, PDF e `.tex`), ligada ao `README.md` e ao Anexo B do relatório.
- O GitHub é **público**. O utilizador pediu o envio desta atualização (REV-083); confirmar com `git status -sb` que o `main` local e o remoto estão iguais.
- **Próximo passo:** a leitura do relatório pelo utilizador e os ajustes que dela saírem (REV-084).
- Não há treinos, medições nem acessos a dados pendentes.

Mensagem sugerida para abrir a nova conversa: «Lê o AGENTS.md e o handoff.md e diz-me o ponto de situação. Quero continuar o relatório.»

## Como retomar (ler por esta ordem)

1. `AGENTS.md`: regras fixas (o `CLAUDE.md` manda lê-lo antes de qualquer ação).
2. Este ficheiro.
3. O topo do `PROGRESS.md` (estado, decisões, pendências).
4. `latex/relatorio_pt.tex` ou o PDF em `latex/build/relatorio_pt.pdf`.
5. Só se for preciso: `docs/00` (modelos, protocolos, acesso e referências verificadas), `docs/01` (dados) e `REVISION_LOG.md`.
6. Antes de agir: `git status -sb`, `git log --oneline -10`, os testes e ver se há um vigilante do LaTeX a correr (o utilizador pode ter alterado o `.tex`).

## Última validação (2026-11-26)

| Verificação | Resultado | Hora (WET) |
|---|---|---|
| `pytest tests/` | 256 passaram | 01:26 |
| Relatório, compilado do zero (`watch_latex.sh --once`) | 10 páginas, sem referências em falta; 662 números de linha, todos nas margens; ligação da galeria presente | 01:26 |
| Galeria | `galeria_viagens.tex` igual ao que o programa gera da página; 36 imagens iguais às de `proveniencia.json`; PDF com 12 páginas | 01:26 |
| GitHub (`git fetch`, `git ls-remote`) | `main` local e remoto em `a6d8796` antes desta revisão; etiquetas `proposta-pt-v1` e `docs-historico-v1` presentes | 01:26 |
| Ligação do Anexo B, sem sessão iniciada | respondeu 200 | 01:26 |
| Vigilante do LaTeX | um a correr no terminal do utilizador (versão que compila até estabilizar) | 01:22 |

Não repetido nesta atualização: a recuperação da proposta antiga num clone (2026-11-25, 23:12) e a revisão independente do relatório (2026-11-25, 23:00, anterior à REV-068; o texto mudou depois). O que mudar depois destas horas **não foi** validado por este handoff.

## Cronologia dos commits desta conversa

| Commit | Data e hora | Assunto |
|---|---|---|
| `a6d8796` | 2026-11-26 01:23 | Regista o pedido de envio das REV-081 e REV-082 |
| `7b9317a` | 2026-11-26 01:22 | Põe os anexos depois das referências (REV-082) |
| `da2d2aa` | 2026-11-26 01:16 | Alivia a página 6 do relatório (REV-081) |
| `3672387` | 2026-11-26 01:09 | Regista o pedido de envio das REV-078 a REV-080 |
| `880c146` | 2026-11-26 01:08 | Põe a Figura 8 antes dos anexos (REV-080) |
| `4d8512b` | 2026-11-26 01:04 | Passa o Anexo B a preto (REV-078) |
| `bc210da` | 2026-11-26 01:03 | Muda o e-mail do autor no relatório para o institucional (REV-079) |
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

O commit desta atualização do handoff vem a seguir e não está na tabela. Os anteriores veem-se com `git log`.

## O que se fez nesta conversa (2026-11-25, 23:40, a 2026-11-26)

| Revisão | O quê |
|---|---|
| REV-069 | O relatório conta as duas janelas do filtro: 13 pontos (ganho pequeno) e 301; mais valores e tipos de janela em trabalho futuro |
| REV-070, 071 | Números de linha nas margens (o vigilante compila até estabilizar); página sem coluna vazia |
| REV-072 | O modelo da viagem completa passa a chamar-se **baseline** (era «referência»); todo o texto a preto |
| REV-073, 077 | Galeria de viagens em `viagens/` e a sua versão em LaTeX e PDF |
| REV-074, 075 | Figura 7 com «baseline»; legendas das Figuras 3 e 8 fora das barras e curvas |
| REV-076 | Legenda da Tabela 6 explica porque os valores do teste são otimistas |
| REV-078 | Anexo B com a ligação para a galeria no GitHub |
| REV-079 | E-mail do autor passou ao institucional (alteração do próprio utilizador) |
| REV-080, 081 | Figura 8 antes dos anexos; página 6 com mais texto |
| REV-082 | Anexos depois das referências |
| REV-083 | Esta atualização do handoff e dos documentos |

## Estado e resultados

Dataset: 123 viagens, 1 026 279 pontos; divisão por viagem, seed 42: treino 87 (713 854), teste 18 (103 409), validação 18 (209 016). Fonte: Zenodo (Song Wu, CC BY 4.0).

| Resultado | Valor | Conjunto |
|---|---|---|
| Baseline (época 162, limiar 0,65) | exatidão 94,7 % | `test` (otimista) |
| Baseline, medição final | exatidão 94,4 % (classe maioritária: 83,2 %) | `validation` |
| J0 (época 8, limiar 0,60) e J50 (época 4, limiar 0,75) | 93,4 % e 93,7 %; J50 fragmenta menos | `test` |
| Filtro de 301 pontos (só a baseline) | 94,4 % → 94,8 %; segmentos de pesca previstos 486 → 32 (reais 18); piora 7 de 18 viagens | `validation`, **não independente** |

RQ1: as janelas não superam a viagem completa. RQ2: o filtro reduz muito a fragmentação. RQ3: sem resposta. Critérios de sucesso: (i) cumprido com ressalvas, (ii) em parte, (iii) não.

## O relatório

**Ordem:** resumo; 1 Introdução; 2 Trabalho relacionado; 3 Dados e preparação; 4 Método; 5 Protocolo experimental; 6 Resultados e discussão; 7 Limitações, ética e dimensão humana; 8 Conclusões e trabalho futuro; referências (página 9); Anexo A, pormenores do janelamento e Tabela 6; Anexo B, galeria de viagens (página 10).

**Onde estão os elementos:** p. 3 Figura 1; p. 4 Figuras 2 e 3 e Tabela 1; p. 6 Tabela 2 e Figuras 4 e 5; p. 7 Figuras 6 e 7 e Tabelas 3 e 4; p. 8 Figura 8 e Tabela 5; p. 10 Tabela 6.

**Compilar:** `bash latex/watch_latex.sh` (local, não versionado; recompila para `latex/build/relatorio_pt.pdf`) ou os comandos do `README.md`. O vigilante só reage a `relatorio_pt.tex` e `references.bib`: depois de gerar macros ou figuras, correr `bash latex/watch_latex.sh --once` ou reiniciá-lo. Com um vigilante a correr, **não** compilar à mão para `latex/build/`.

**Disposição (frágil; rever depois de mexer em texto ou figuras):**
- No preâmbulo, `\dbltopfraction` 0,95, `\textfraction` 0,25 e contadores de flutuantes (REV-080, 081).
- O bloco da Figura 8 está no ficheiro **antes** da subsecção que a cita, de propósito.
- A Tabela 6 e a legenda estão numa `minipage`, para não se separarem.
- Os anexos vêm depois de `\bibliography`, com `\clearpage`.
- Verificar: 10 páginas, sem `??`, e números de linha fora das colunas (com `pdftotext -bbox`, a posição horizontal fica antes de 53 pt ou depois de 559 pt). Para comparar disposições, usar uma cópia de `latex/` numa pasta temporária.

**Números e figuras** (nunca escrever à mão um número empírico):

| Ficheiro em `latex/` | Gerado por (`ais.cli.…`) |
|---|---|
| `generated/resultados.tex` | `build_final_results` |
| `generated/resultados_janelas.tex` | `build_window_results` |
| `figures/janelas_viagens_baseline.png`, `janelas_linha_temporal_baseline.png`, `janelas_perda.png` | `build_window_results --report-figures-only` |
| `generated/resultados_validacao.tex`, `figures/validacao_resumo.png` | `build_validation_results` |
| `figures/validacao_pior_viagem.png` | `build_validation_results --worst-trip-figure-only` |
| `generated/resultados_posproc.tex`, `figures/posproc_viagem.png` | `build_postproc_results` |
| `figures/posproc_resultados.png` | `build_postproc_results --results-figure-only` (não lê previsões) |
| `generated/resultados_posproc_v1.tex` | `build_postproc_results --first-version-only` |
| `generated/resultados_buracos.tex` | `build_window_analysis_macros` |
| `figures/posproc_janela.png` | `plot_postprocessing_kernel` (dados sintéticos) |

As figuras do esquema e da CNN são TikZ no próprio `.tex`. Os programas que leem previsões guardadas dos conjuntos reservados pedem autorização em `configs/authorizations/` e registam a leitura: não os correr sem pedido do utilizador. Os ficheiros `*_ref.png` e outras figuras antigas ficaram sem uso (o utilizador preferiu manter).

**Decisões sobre o texto (não mudar sem pedido):**
- **Resumo (REV-068):** sem «este resultado não vem de uma medição independente»; a ressalva mantém-se no corpo.
- **Filtro (REV-069):** 13 pontos primeiro (ganho pequeno, não piorou no total) e depois 301; a frase do resumo começa por «Sobre as previsões dessa medição».
- **Nome (REV-072):** «baseline», nunca «referência», para o modelo da viagem completa.
- **Anexos (REV-082):** depois das referências, por escolha do utilizador, sabendo que as instruções do IJCAI os põem antes.

**Não reintroduzir** (corrigido em REV-065):
- o resultado do filtro como medição independente, ou «medido uma única vez»;
- que a janela de 301 foi escolhida comparando várias dimensões (o efeito no `test` só se mediu **depois** da escolha, sem regra declarada antes);
- o critério da medição final como declarado antes de se conhecerem os resultados do `test`;
- a menor fragmentação de J50 como efeito só da sobreposição (limiar, época e passos também diferem);
- «até cerca de 20 % da captura mundial» (não está em Agnew) ou o artigo de Cheng como deteção de pesca.

**Bibliografia:** verificação em `docs/00` §9. `ferreira2022full` é a entrada que o relatório usa. Shneiderman, Guo e Lundberg só foram confirmados pelos resumos no arXiv.

## A galeria de viagens

| Ficheiro em `viagens/` | Gerado por |
|---|---|
| `README.md`, `teste/*.png`, `validacao/*.png`, `proveniencia.json` | `build_trip_gallery` (lê previsões guardadas do `test` e do `validation`; precisa das autorizações `*_trip_gallery.json`) |
| `galeria_viagens.tex`, `galeria_viagens.pdf` | `build_trip_gallery_pdf` (só a partir da página; correr depois do anterior) |

- Teste: real, baseline, J0, J50 e baseline + pós-processamento. Validação: real, baseline e baseline + pós-processamento. O filtro aplica-se só à baseline.
- Por ordem crescente de exatidão da baseline.
- O Anexo B liga a `viagens/galeria_viagens.pdf` no ramo `main`: **não mover nem renomear** esse ficheiro.

## Proposta anterior

`latex/proposta_pt.tex` já não existe na pasta. PDF em `latex/proposta_pt.pdf`; versão completa na etiqueta `proposta-pt-v1` (comandos no `README.md`). Não repor a pasta `latex/` inteira a partir da etiqueta. `latex/proposta_IAHC_DINIS_ROSA.pdf` é a entregue ao professor e não se altera.

## Decisões vigentes

A lista completa está no topo do `PROGRESS.md`. As que mais pesam:

- `test` seleciona, `validation` mede; o `validation` está gasto. **Não voltar a correr** `select_on_test`, `select_windows_on_test`, `final_validation` nem `postproc_validation`.
- Baseline, J0 e J50 fechadas. Sem novos treinos sem decisão do utilizador.
- Relatório: máximo 15 páginas (alvo 13 ou menos); título mantido; «Figura» e «Tabela» em português; números de linha até à versão final.
- Perguntas de investigação, objetivos e critérios de sucesso não mudam depois dos resultados (na REV-072 mudou só o nome do modelo).
- Explicabilidade, calibração e *dashboard*: «previstos, não concluídos nesta fase».
- Documentação: ficam só `docs/00` e `docs/01`.
- **Cores:** a regra (AGENTS §8) manda marcar a cor, com `\revtext{revNNN}{…}`, o texto novo ou substituído no `.tex`. O utilizador mandou usar preto na REV-072 e na REV-076 («só desta vez») e passou a preto o texto da REV-078; o relatório está todo a preto. Antes da próxima alteração de texto, **perguntar** se quer cor ou preto. Mudanças só de disposição não têm texto para colorir. **Próximo ID livre: REV-084.**

## Em aberto (nada disto bloqueia)

- **Enunciado:** não está no projeto e não foi visto; convém confirmar se diz alguma coisa sobre a ordem dos anexos.
- Pequenas coisas de aspeto assinaladas ao utilizador ou notadas, sem decisão: a Figura 3 escreve «50.2» e «0.65» com ponto; a linha temporal da Figura 8 diz «antes» e «depois» em vez de «baseline» e «baseline + pós-processamento»; a legenda da Tabela 4 ainda diz «teste (otimista)», sem a explicação que a Tabela 6 ganhou; a página 10 fica com a coluna direita vazia.
- Versão final: traduzir «Abstract» e «References» e retirar os números de linha, quando pedido.
- Limitações dos dados: CRS (hipótese WGS84), 128 contra 123 trajetórias, fiabilidade das anotações, cálculo de `distanceToShore`.
- Arrumação técnica opcional: testes dos programas de treino e de figuras; unificar `class_metrics`.

## Ficheiros principais

| Área | Ficheiros |
|---|---|
| Regras e registo | `AGENTS.md`, `CLAUDE.md`, `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, `handoff.md` |
| Relatório | `latex/relatorio_pt.tex`, `references.bib`, `figures/`, `generated/` |
| Galeria | `viagens/` (não editar à mão) |
| Documentação | `docs/00`, `docs/01`; arquivo na etiqueta `docs-historico-v1` (`docs/00` §11) |
| Código | `src/ais/phase1/` (biblioteca), `src/ais/cli/` (programas, tabela no `README.md`) |
| Configuração | `configs/` e `configs/authorizations/` |
| Só nesta máquina (não vão para o git) | `data/`, `results/` (modelos, previsões, `access_log.jsonl`), `iach-ais-venv-4/`, `docs/bibliografia/`, `latex/build/` (o PDF do relatório), `latex/watch_latex.sh` |

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

```bash
iach-ais-venv-4/bin/python -m ais.cli.build_trip_gallery_pdf
```

## O que falhou ou exigiu correção (nesta conversa)

- PDF com números de linha entre as colunas: poucas passagens de compilação. A validação só via erros e páginas; **rever também as páginas em imagem**.
- Compilar à mão para `latex/build/` com o vigilante a correr estragou uma compilação.
- Chamei «página 7» à 8: confirmar a página com `pdftotext` antes de a nomear.
- A galeria ficou com 3,5 MB, acima do estimado.
- Pesquisas na Web apontaram para endereços errados (outros artigos): confirmar lendo a página. A regra do IJCAI sobre anexos foi confirmada nas instruções de 2019 e no kit de 2027; as de 2026 não foram lidas.
- Horas: usar sempre `date`.

## O que fazer a seguir

1. Os ajustes que vierem da leitura do utilizador (REV-084).
2. Se pedido: os pontos de «Em aberto».
3. **Push:** só a pedido. Antes de enviar, ver o que vai (`git log '@{u}..HEAD'`); depois confirmar com `git ls-remote`.

## Regras a não esquecer

- Desenvolvimento só com treino ou dados sintéticos. `test` e `validation` só com autorização explícita, escrita em `configs/authorizations/`; uma flag no código não é autorização.
- Todo o número usado como evidência vem de código versionado (AGENTS §10); no LaTeX, só por macros geradas. Valores externos levam citação.
- **Push (REV-055):** se o utilizador pede, enviar sem mais perguntas; por iniciativa própria, nunca. Sem `--force`.
- Explicar comandos e alterações antes de os fazer; comunicar em português de Portugal; funções e variáveis em inglês.
- No fim de cada interação com alterações: `PROGRESS.md` e `REVISION_LOG.md`, e confirmar que `README.md`, `docs/` e o relatório não se contradizem.
- Commits por tema, com mensagem completa e a linha de coautoria.

## Preferências do utilizador observadas

- Para uma mudança grande quer primeiro a explicação e o **plano**, e diz para esperar pelo sim; depois dá autonomia.
- Pede opinião («se for boa ideia, faz»; «se discordares, contraria-me»): responder com franqueza antes de aplicar.
- Revê o PDF visualmente e pede correções de disposição, uma de cada vez; gosta de páginas cheias e de figuras antes dos anexos.
- Costuma autorizar o envio depois de ver o PDF; pode alterar ele próprio o `.tex` e pedir para incluir no commit.
- Pode acompanhar a conversa noutro dispositivo: enviar-lhe o PDF quando mudar.
- Quer sempre uma forma de voltar atrás antes de reescrever ou apagar.
- Gosta de resultados em tabelas e imagens, com o porquê, em linguagem simples.
- Numa sessão anterior preferiu delegar trabalho pesado na Abacus (nunca o OpenCode), só com código e descrições, **nunca dados**.
