# 06 — Plano de reescrita da proposta

[REV-064 | cor #33691E] Plano de 2026-11-25 para reescrever a proposta como **relatório do trabalho feito**. O utilizador aprovou o género e a estrutura base e, às 22:36 WET, **aceitou todas as recomendações da §2** («Aceito podes avançar»); a execução é a REV-065. Este plano absorve os pontos A a H de `docs/05_releitura_proposta.md`. Revisto às 22:25 WET: acrescentadas D7 (onde escrever) e D8 (versão de segurança), por proposta do utilizador.

## 1. Princípios

- As perguntas de investigação, os objetivos e os critérios de sucesso **não mudam depois dos resultados**. Diz-se o que ficou cumprido e o que não ficou.
- Cada assunto aparece uma só vez: método na §4, protocolo na §5, resultados na §6, limitações na §7.
- Nenhum resultado novo, nenhuma nova abertura de dados e nenhum treino. Os números empíricos entram só por macros geradas (AGENTS §10).
- A versão atual tem de poder ser recuperada exatamente (D7 e D8). O PDF entregue ao professor não se altera.

## 2. Decisões do utilizador (tomadas: vale a coluna «Recomendação», e em D3 a frase A)

| # | Decisão | Recomendação | Alternativa |
|---|---|---|---|
| D7 | Onde escrever | Ficheiro novo `latex/relatorio_pt.tex`; `latex/proposta_pt.tex` não se altera. Autoriza mudar a frase do AGENTS §8 «Não criar um relatório substituto» | Reescrever `proposta_pt.tex` e voltar atrás pela D8 (outro nome possível para o novo: `documento_pt.tex`) |
| D8 | Versão de segurança | Etiqueta git `proposta-pt-v1` no commit `7d60861`, mais uma secção no `README.md` (§2.1) | Só o número do commit no `README.md` |
| D1 | Limite de páginas (os registos falam em 15, sem indicar a origem) | Teto de 15, alvo de 13 ou menos | Outro limite |
| D2 | Cores da revisão | Texto a preto, registado como REV-065 (exceção ao AGENTS §8, precisa de autorização) | Colorir todo o texto novo |
| D3 | Dependência do resultado do filtro | Frase **A** nas limitações | Frase **B**, sem mencionar a versão de 13 pontos |
| D4 | Figuras com a legenda «baseline» | Autorizar a regeneração a partir das previsões **já guardadas** do `test` (sem parquet nem CNN sobre o `test`) | Manter a legenda e explicá-la na legenda do LaTeX |
| D5 | Título | Manter (nomeia o que foi estudado) | Mudar «usando» para «estudo de» |
| D6 | Modelo IJCAI | «Figura» e «Tabela» em português; números de linha até à versão final | Deixar como está |

- **Frase A:** «Antes desta versão, foi medido no conjunto de validação um filtro com uma janela de 13 pontos; a decisão de procurar outra janela foi tomada depois de ver esse resultado. O valor obtido com 301 pontos não é, por isso, uma medição final independente.»
- **Frase B:** «O resultado do filtro no conjunto de validação não é uma medição final independente: as anotações já tinham sido usadas para avaliar o pós-processamento, e a escolha da janela não é independente delas.»

Em qualquer dos casos saem as frases «uma única vez» e «nada é escolhido com estes resultados» aplicadas ao pós-processamento (hoje na 10.3). A frase A revê a decisão anterior de deixar a primeira versão fora da proposta.

### 2.1 Versão de segurança (D8)

A última alteração a `proposta_pt.tex` é o commit `c0af577` (REV-062). O commit `7d60861` (REV-063, handoff atualizado) tem esse mesmo `.tex`, já está em `origin/main` e é o ponto proposto. O commit anterior de handoff (`1ab2376`) **não serve**: o `.tex` ainda não tem as alterações de REV-062.

Uma cópia em disco não chega: o ficheiro antigo e o novo partilham `latex/generated/`, `latex/figures/` e `references.bib`. Por isso, ficheiros partilhados só se **acrescentam**; uma figura que mude ganha nome novo. A etiqueta guarda o conjunto exato.

Texto a pôr no `README.md`, depois de aprovado:

```bash
# ver a versão antiga numa pasta à parte, sem mexer no trabalho atual
git worktree add ../proposta-pt-v1 proposta-pt-v1
# recuperar os ficheiros antigos para o projeto (fazer commit do trabalho em curso antes);
# --overlay repõe sem apagar os ficheiros novos
git restore --overlay --source=proposta-pt-v1 -- latex/
```

O comando de recuperação foi ensaiado num clone temporário, com o número do commit: repôs `proposta_pt.tex` e manteve um ficheiro novo.

## 3. Estrutura nova

As páginas são estimativas, a confirmar na compilação.

| § | Secção | Conteúdo | Vem de (secções atuais) | Figuras e tabelas | Pág. |
|---|---|---|---|---|---|
| — | Resumo | Problema, método, resultados de RQ1 e RQ2 com macros, RQ3 sem resposta | Resumo (novo texto) | — | 0,3 |
| 1 | Introdução | Problema e motivação; objetivos (com o 5.º marcado como não concluído, uma vez); RQ1 a RQ3; critérios de sucesso; contribuições | 1, 3 | — | 1,0 |
| 2 | Trabalho relacionado | HMM em VMS; esforço de pesca com AIS; segmentação e deteção; aprendizagem profunda; HCAI; o que este trabalho estuda | 2 | — | 0,6 |
| 3 | Dados e preparação | Conjunto, classes, anomalias, grandezas recalculadas, entradas e ausências | 6, 6.1, parte de 5.1 | — | 0,6 |
| 4 | Método | 4.1 visão geral; 4.2 CNN (entrada, arquitetura, campo recetivo, perda); 4.3 janelas e reconstrução; 4.4 filtro gaussiano | 4, 5.1 a 5.5, 10.1, parte de 10.2 | Pipeline (redesenhada), CNN, janela do filtro | 2,2 |
| 5 | Protocolo experimental | Divisão e papéis dos conjuntos; treino; seleção no `test`; escolha dos 301 pontos; métricas; medições no `validation`; reprodutibilidade e testes | 4.3, 5.6, 5.7, 7, 9.1, 10.2, 10.3 | Tabela do treino | 1,2 |
| 6 | Resultados e discussão | 6.1 janelas (RQ1, `test`); 6.2 medição final da referência (`validation`); 6.3 filtro (RQ2); 6.4 interação (RQ3) | 8, 9, 10.4, parte de 11 | Ver §4 | 4,0 |
| 7 | Limitações, ética e dimensão humana | Uma só lista de limitações; ética; explicabilidade, calibração e *dashboard* como não concluídos | 6 (ética), 7.3, 8.4, 9.3, 10.5 | — | 0,6 |
| 8 | Conclusões e trabalho futuro | Respostas curtas, critérios (i) a (iii), trabalho futuro | 11 | — | 0,4 |
| A | Anexo | Pormenores das janelas e métricas por classe | A | Tabela por classe | 0,5 |
| — | Referências | | | | 0,9 |

Total estimado: 12 a 13 páginas (hoje 16).

## 4. Figuras e tabelas

| Atual | Destino |
|---|---|
| Fig. 1, *pipeline* | Redesenhar: o filtro recebe o melhor dos modelos |
| Fig. 2, CNN | Manter, mais baixa |
| Tab. 2, arquitetura | Cortar; o total de parâmetros fica no texto |
| Tab. 1, protocolo do treino | Passa para a §5 |
| Tab. 3 e Fig. 3, resumo por ponto e perda | Manter em 6.1 |
| Fig. 4, matrizes e exatidão por viagem | Só a exatidão por viagem (`janelas_viagens.png`); as matrizes repetem a tabela por classe |
| Tab. 4, segmentos no `test` | Manter em 6.1 |
| Fig. 5, métricas e linha temporal | Só a linha temporal; as barras repetem a Tab. 4 e o erro de fronteira da pesca assenta em 5 ou 6 pares |
| Tab. 5, escolha do modelo | Passa a uma frase na §5, com macros |
| Tab. 6 e Fig. 6, medição final | Manter em 6.2 |
| Tab. 7 e Tab. 8, segmentos e filtro | Uma tabela «antes e depois» no `validation`, por ponto e por segmento, **com erros de fronteira**; as linhas do `test` repetem a Tab. 4 |
| Fig. 7, janela do filtro | Manter em 4.4, mais baixa |
| Fig. 8, efeito do filtro | Manter em 6.3 |
| Tab. 9, métricas por classe | Anexo |

Paginação: retirar a opção `section` do pacote `placeins` (provável causa das páginas quase vazias) e pôr `\FloatBarrier` só onde for preciso.

## 5. Correções obrigatórias

| # | Problema | Como fica |
|---|---|---|
| A a H | Ver `docs/05_releitura_proposta.md` | Aplicados nas secções novas |
| I | 9.2: o pós-processamento «ainda não foi estudado» | Cortar |
| J | 4.2, 4.4 e contribuições: a única diferença é o janelamento; «comparação controlada» | Mesma rede, dados e critério de seleção; o lote e o número de passos também diferem |
| K | 10.3 promete erros de fronteira que a 10.4 não mostra | Entram na tabela antes/depois. As medianas calculam-se sobre os pares correspondidos, que mudam (na pesca, de 7 para 15): dizê-lo |
| K2 | 10.5: «a janela grande desloca as fronteiras» apoia-se em valores do `test` que não estão na proposta | Separar o que se vê no `validation` do que se viu no `test` (este só com macros geradas) |
| L | 10.3 e 10.5 sugerem uma medição independente | D3 |
| M | 10.2 a 10.4: «mais curto/comprido do que a janela» | Usar o limite que o filtro remove (com dados ideais, diferente para pesca e navegação) |
| N | RQ1: J50 «não melhora a exatidão», mas fica um pouco acima de J0 | Dizer: acima de J0 por pouco, abaixo da referência; uma só semente |
| O | Contexto: Cheng classifica **tipos de navio**; Hu trata padrões de comportamento e previsão de trajetória; Wang, quatro estados operacionais. O FishNET (`arasteh2020`, CNN por segmento) está no `.bib` e não é citado | Descrever cada trabalho pelo que faz; citar o FishNET; confirmar cada afirmação no PDF, incluindo os valores sobre pesca IUU (o artigo de Agnew não está na pasta) |
| P | «Os modelos atuais produzem resultados ruidosos», sem fonte | Citar uma fonte ou apresentar como hipótese |
| Q | Frases geradas: «em 0 viagens», «em 1 viagem», «-0,2» | Reescrever à volta das macros; sinal de menos correto |
| R | Figuras com «baseline» e texto com «referência» | D4 |

## 6. Fases

| Fase | O que se faz | Paragem |
|---|---|---|
| 0 | Decisões D1 a D8 | Resposta do utilizador |
| 1 | Commit dos documentos do plano; etiqueta local (D8) e secção no `README.md`. Se D7 for o ficheiro novo: ajustar o AGENTS §8, criar o esqueleto de `relatorio_pt.tex` (preâmbulo e títulos), compilar e apontar o `watch_latex.sh` para ele | Confirmar que a recuperação funciona com a etiqueta |
| 2 | Programa novo que gera as macros dos blocos de erro a partir de `results/postproc_window_analysis/{test,train}.json` (já gerados), com testes sintéticos. Se D4: mudar a legenda, gravar as figuras com nomes novos e confirmar que nenhum número mudou | Mostrar o diff das macros |
| 3 | Confirmar na bibliografia cada frase do trabalho relacionado e da motivação | Mostrar o que não se confirma |
| 4 | Escrever por esta ordem: §4, §5, §6, §3, §2, §7, §1, §8, resumo | Mostrar o PDF depois da §6 |
| 5 | Compilar; contar páginas; verificar A a R; procurar números soltos; confrontar cada afirmação com código ou resultados; `pytest`; revisão independente (subagente) | Lista do que falhar |
| 6 | `PROGRESS.md`, `REVISION_LOG.md`, `README.md`, `handoff.md`; linhas do Marco 5 desatualizadas em `docs/00` e `docs/03`; fechar `docs/05`; commits por tema | Push (e envio da etiqueta) só a pedido |

## 7. Critérios de conclusão

- Compila sem erros nem referências indefinidas, dentro do limite de D1.
- Os pontos A a R estão fechados ou registados como não aplicados, com o motivo.
- Nenhum número empírico escrito à mão.
- Nenhum conjunto reservado aberto.
- A versão `proposta-pt-v1` recupera-se com os comandos da §2.1; se D7 for o ficheiro novo, `proposta_pt.tex` fica igual ao dessa versão.
