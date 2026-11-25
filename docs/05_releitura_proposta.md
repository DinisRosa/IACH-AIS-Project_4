# 05 — Releitura da proposta: passagens a corrigir

[REV-063 | cor #FF7043] Resultado da releitura de `latex/proposta_pt.tex` feita em 2026-11-25, depois de REV-062 (passagens adiadas). Lista o que ainda contradiz o trabalho feito, com a recomendação para cada passagem. **Ainda não aplicado:** cada alteração ao `.tex` fica para uma revisão nova (próximo ID livre: REV-064), com cor própria, números só por macros geradas e o texto cortado registado no `REVISION_LOG.md`.

Critério combinado com o utilizador: o que descreve algo feito de outra forma **reescreve-se**; o que não foi feito mas faz sentido continuar passa a **trabalho futuro** (formulação: «estava previsto e não foi concluído nesta fase», sem dar motivo); o que é simplesmente falso **corta-se** ou **corrige-se**. Nada fica como está se contradisser o trabalho.

## Tabela da releitura

| # | Onde | Problema | Recomendação | Como fica |
|---|---|---|---|---|
| A | **Secção 6, Tratamento dos dados**: «velocidade (em nós)» | A preparação calcula a velocidade em m/s (`speed_calc_mps`, em `build_clean_dataset`); os nós só servem para comparar com o original (`check_units_train`) e para contar anomalias. | **Corrigir** | «velocidade (em m/s)». |
| B | **Contexto**: «Soares Júnior… MDL, e Wu et al. aplicaram-na a trajetórias AIS» | Segundo o artigo (`docs/bibliografia/`, Wu et al., IEEE MDM 2022), o método de Wu et al. é outro: classifica janelas sobrepostas e junta as janelas de pesca próximas numa atividade completa por *run-length encoding* (WBS-RLE). | **Corrigir** | Descreve o método real de Wu et al. |
| C | **Contexto**: «Wu et al.… a referência central deste projeto» | Confunde-se com a «CNN de referência», e Wu et al. não é uma comparação (REV-042). | **Reescrever** | «o trabalho em que este projeto se baseia». |
| D | **Contexto**: «o projeto acrescenta… a perspetiva de cooperação humano-IA» | A cooperação humano-IA não foi concluída. | **Reescrever** | Acrescenta a avaliação da estabilidade temporal; a cooperação humano-IA estava prevista e não foi concluída nesta fase. |
| E | **Figura da abordagem** (`fig:pipeline`): o pós-processamento vem a seguir à CNN sobre janelas | O filtro foi aplicado ao melhor modelo, a referência (REV-053, REV-059). | **Reescrever** | O pós-processamento recebe o melhor dos modelos (setas a partir das duas CNN), com a legenda ajustada. |
| F | **7.1 Métricas**: «“estável” designa uma segmentação que muda pouco sob pequenas alterações da janela ou do pós-processamento» | Essa sensibilidade nunca foi medida. | **Cortar** | Ficam só as duas medidas reais: a fragmentação e o erro de fronteira. |
| G | **7.2 Divisão dos dados e protocolo**: escolhas «(número de épocas, limiar, variantes)» e «validação… feita uma só vez» | Falta o tamanho da janela do filtro, também escolhido no `test`, e falta dizer que as previsões do `validation` voltaram a ser usadas. | **Reescrever** | Junta às escolhas feitas no `test` o tamanho da janela do pós-processamento (301 pontos), escolhido depois de medir no `test` o comprimento dos blocos de pontos mal classificados (média 14,8, mediana 5; 90 % até 37 pontos) e o segmento real mais curto (127 pontos), Secção 10.2. Diz também que as previsões já guardadas do `validation` serviram de novo, sem reabrir os dados, para medir o pós-processamento (Secção 10). Os números entram por macros geradas a partir de `results/postproc_window_analysis/`. |
| H | **5.6 Reprodutibilidade**: «os números… vêm de ficheiros `final_results`» | Também vêm dos ficheiros da medição final e do pós-processamento. | **Reescrever** | «ficheiros de resultados gerados por código». |

**Fica como está (relido, sem contradições):** 5.3 (porquê estes valores), 5.4 (campo recetivo), 5.5 (função de perda), a parte ética da Secção 6 e o requisito «fiável, explicável e concebido para cooperação humano-IA» do Problema e Motivação (é um requisito, não uma afirmação de trabalho feito).

## Notas

- Os números de G (blocos de erro e segmento real mais curto) já existem em `results/postproc_window_analysis/test.json` (`ais.cli.analyze_error_runs --split test`); para entrarem no LaTeX é preciso gerar macros a partir desse ficheiro (AGENTS §10), sem voltar a ler o `test`.
- A Secção 10.2 já usa estes números em texto (REV-059); ao gerar as macros, convém passá-la também a macros.
- O número de páginas (16) trata-se depois, por decisão do utilizador.
