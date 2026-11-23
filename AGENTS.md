# AGENTS.md — Projeto AIS

## 1. Finalidade, âmbito e prioridades
Instruções comuns para qualquer agente que trabalhe no projeto. Implementação principal em Python; KNIME é apenas contingência futura mediante decisão do utilizador.

Objetivo: segmentar viagens AIS em pesca/navegação, com uma previsão por ponto. Desenvolver preparação comum, CNN com viagem completa e CNN com janelas/sobreposição; comparar também um ramo de pós-processamento simples com método aprovado. HMM, reprodução de Wu et al., dashboard, calibração e explicabilidade avançada não pertencem ao mínimo atual salvo nova instrução.

Ler este ficheiro, `docs/00_projeto_e_decisoes.md`, `docs/01_dados_e_preparacao.md` e o documento da fase em causa (`docs/02_…` ou `docs/03_…`) antes de executar. Decisões explícitas recentes do utilizador prevalecem sobre sugestões antigas, sem autorizar implicitamente dados reservados, publicação ou ações destrutivas. Perguntar quando houver conflito não resolvido.

As funções especificadas nos documentos são contratos orientadores, não obrigação de criar módulos vazios. Implementar por marcos executáveis. Nunca simular resultados, subagentes, testes ou funcionalidades concluídas.

## 2. Comunicação e autonomia
- Comunicar em português de Portugal. Funções/variáveis em inglês; documentação e commits em português por defeito.
- Antes de comandos, mostrar o comando e explicar finalidade, motivo e efeitos possíveis.
- Antes de criar/alterar ficheiros, explicar o seu papel e a alteração prevista.
- Agrupar apenas ações pequenas relacionadas; não ocultar comandos numa descrição genérica.
- Depois, resumir resultado, validação realizada, erros, limitações e próximo passo. Não despejar logs sem interpretação.
- Explicar decisões e efeitos observáveis; não é necessário expor raciocínio interno privado.
- Ações locais pequenas e reversíveis dentro do plano podem avançar após explicação, sem confirmação a cada passo.
- Pedir autorização para alterações metodológicas, exclusões destrutivas, sobrescrita de originais, instalação global, mudança relevante de backend e execuções prolongadas sem orçamento acordado.
- Não há limite de minutos aprovado: perguntar antes do primeiro treino prolongado.
- Preservar alterações existentes do utilizador. Não reverter nem reescrever trabalho alheio por conveniência.
- Investigar dúvidas resolúveis com ambiente, documentação e treino; perguntar quando faltar evidência ou houver escolha relevante. Juntar perguntas relacionadas sem bloquear tarefas independentes.

## 3. Dados: regras obrigatórias
- Há um dataset, dividido 70/15/15 pelos IDs completos das viagens, com seed 42 (confirmada pelo utilizador) e manifesto persistido em `manifests/split_manifest_seed42.csv`, gerado por `src/ais/cli/create_split_manifest.py`.
- Todas as linhas, sequências e janelas de um ID pertencem ao mesmo conjunto. Viagens diferentes do mesmo navio podem ficar em conjuntos diferentes por decisão do utilizador.
- Não afirmar generalização para navios inéditos: a divisão é por viagem.
- Dividir no início, antes da exploração, usando apenas leitura técnica mínima de IDs/encaminhamento e verificações estruturais.
- Desenvolvimento, debugging, amostras, gráficos, inspeção, benchmarks e testes de integração: EXCLUSIVAMENTE treino ou dados sintéticos.
- Não abrir pequenas amostras de validação/teste para verificar código.
- Manter conjuntos reservados isolados e fora do ponto de entrada normal.
- **Papéis dos conjuntos reservados (decisão do utilizador, REV-036):** o conjunto `test` é o de **seleção** (número de épocas, limiar, se treinar mais compensa, escolha entre variantes) e o conjunto `validation` é a **medição final**, aberta **uma só vez** com o modelo e o protocolo congelados. Os nomes dos ficheiros e do manifesto mantêm-se. Acesso ao `test` exige autorização explícita, com o âmbito das decisões declarado; acesso ao `validation` exige nova autorização para a medição final.
- Flags de configuração, delegação e decisões do agente não concedem autorização.
- Ajustar normalizadores, imputadores, limites estatísticos e outros objetos aprendidos apenas no treino correspondente.
- Monitorização interna: separar por ID dentro do treino oficial ANTES do fit de transformações e das janelas; ajustar no treino interno para independência interna.
- Preservar originais e point_id; registar exclusões, parâmetros e incertezas. Não inventar unidades, CRS, alinhamentos ou rótulos.
- Após excluir pontos, recalcular características afetadas; não combinar distância do predecessor antigo com tempo do novo.
- Qualquer exposição indevida deve ser documentada. Não afirmar que conjuntos expostos continuam intocados.

## 4. Ambiente e recursos
Hardware informado: Intel Core i7 de 12.ª geração, 16 GB de RAM e GPU integrada. Começar em CPU; não assumir CUDA ou aceleração disponível. Medir custo no treino antes de prometer viabilidade.

Verificar SO, Python e ambientes existentes. Conda não é requisito. Se não estiver instalado, NÃO instalar por iniciativa própria: usar normalmente venv/pip sem alterar Python global. Se Conda existir, não migrar automaticamente.

Nome do ambiente do projeto: `iach-ais-venv-4` (indicado pelo utilizador). Está na raiz do projeto e fica ignorado pelo git.

Exemplos a explicar e adaptar antes de executar:
```sh
python --version
python -m venv iach-ais-venv-4
# Linux/macOS, após rever requirements.txt:
iach-ais-venv-4/bin/python -m pip install -r requirements.txt
# Windows, após rever requirements.txt:
iach-ais-venv-4\Scripts\python.exe -m pip install -r requirements.txt
```
No Windows pode ser necessário `py -m venv iach-ais-venv-4`. Se falhar, diagnosticar antes de instalar ferramentas no sistema.

Manter dependências mínimas e versões registadas. Não materializar todas as janelas em RAM sem necessidade; preferir extração sob pedido e agregação incremental. Evitar buscas extensas e treinos simultâneos sem orçamento.

Se uma viagem não couber em memória, parar e reportar. Não truncar, excluir viagens longas, reamostrar ou introduzir janelas na baseline silenciosamente.

## 5. Implementação, testes e continuidade
- Testar diferenças temporais, gaps, máscaras, cobertura, alinhamento, segmentos e métricas com dados sintéticos/treino.
- CNN devolve logits para BCEWithLogitsLoss; sigmoid na inferência para probabilidades. Não aplicar sigmoid duas vezes.
- Uma previsão por ponto original. Não atravessar IDs/gaps; padding não participa na perda, agregação ou métricas.
- Agregação das janelas não é o mesmo que suavização temporal. Preservar probabilidades brutas e comparar pós-processamento num ramo identificado e aprovado.
- Registar se a sobreposição varia no treino, na inferência ou em ambos; épocas iguais não garantem igual número de passos/custo.
- Entrada completa não significa contexto global. A arquitetura ilustrativa de três kernels 5, stride 1 e sem dilatação tem campo recetivo de 13 pontos.
- Registar seed, features em ordem, configurações, versões, manifesto da divisão e proveniência.
- Atualizar documentação afetada, sem inventar resultados no Markdown/LaTeX.
- Atualizar PROGRESS.md após marcos/sessões: feito, validado, problemas, decisões, pendentes e próximo passo.
- **Atualização automática no fim de cada interação (obrigatória, sem pedido do utilizador):** no fim de cada resposta que altere ficheiros, decisões, validações ou pendentes, o agente atualiza `PROGRESS.md` e `REVISION_LOG.md` antes de terminar. Regras:
  - `REVISION_LOG.md`: uma revisão por alteração lógica de documentos, com novo ID sequencial e cor (§8). Nunca renumerar.
  - `PROGRESS.md`: uma entrada datada com feito, validado, problemas, decisões e pendentes. Atualizar também o "Estado atual", o "Decisões vigentes", os pendentes dos marcos e a tabela de artefactos, para que nenhuma informação fique desatualizada.
  - Se a interação não alterar nada (só perguntas ou leituras), não se criam entradas vazias; verifica-se apenas que os documentos continuam corretos.
  - Antes de terminar, confirmar que `PROGRESS.md`, `REVISION_LOG.md` e `README.md` não contradizem o estado real do repositório. Commits locais seguem §6.

## 6. Git: commits e publicação
### Commits locais
Commits pequenos estão autorizados sem nova confirmação, após explicação. Verificar status/diff, selecionar ficheiros explicitamente e não incluir alterações alheias. Evitar git add . automático. Alterações substanciais/metodológicas requerem confirmação. Não configurar identidade global, remoto ou repositório externo sem autorização.

Pequena correção: título curto mas específico, como `Corrige máscara na perda das janelas`. Evitar mensagens vagas. Não declarar testes inexistentes.

Alterações substanciais e alterações ao LaTeX usam título e corpo com:
```text
Título específico

O quê:
- Alterações realizadas.

Porquê:
- Motivo.

Como:
- Abordagem.

Impacto:
- Efeitos no código, dados ou documentação.

Validação:
- Testes/revisão/compilação realmente realizados; indicar o não executado.

Pendente:
- Tarefas reais ou Nenhum.
```
Incluir ID da revisão documental quando aplicável. Um commit pequeno não autoriza uma mudança científica sem aprovação.

### Push é exclusivo do utilizador
O agente NUNCA executa git push, incluindo force/force-with-lease, sincronização por interface, publicação por API, merge remoto ou automação equivalente.

Pode verificar branch/upstream/remoto por comandos de leitura e indicar ao utilizador o comando exato adequado, sem executar. Não assumir main/master/origin. Não sugerir force por rotina; explicar risco e contexto antes de o discutir.

Não reescrever histórico, executar reset destrutivo/rebase arriscado ou apagar branches sem autorização. Preferir branch de trabalho quando apropriado sem mudar trabalho existente inadvertidamente.

Não versionar datasets, credenciais, `iach-ais-venv-4/` (nem outros ambientes), checkpoints e resultados volumosos sem aprovação. Os CSV ficam fora do git por defeito (`*.csv` no `.gitignore`). Exceção: o manifesto da divisão `manifests/split_manifest_seed42.csv`, versionado por decisão do utilizador (REV-006). Manter gitignore; não remover rastreamento existente sem discutir. Se houver segredo exposto, avisar sem o repetir.

## 7. Compatibilidade de ferramentas
AGENTS.md é a fonte única das regras. Confirmar leitura na ferramenta/versão real; nenhum adaptador garante carregamento automático.
- OpenCode/Codex e outros agentes compatíveis: ler este ficheiro e instruções herdadas.
- Claude Code: CLAUDE.md pode mandar ler AGENTS.md; confirmar leitura.
- VS Code: identificar extensão/modo; sem ponte própria no repositório, ler explicitamente este ficheiro (as pontes .github/copilot-instructions.md e GEMINI.md foram removidas).
- Antigravity/Gemini: sem ponte no repositório; ler explicitamente este ficheiro e verificar o mecanismo da versão instalada.
- Cursor/outras extensões: leitura explícita deste ficheiro; adaptador nativo só quando necessário.
Não alterar configurações globais dos agentes. Se referências não forem seguidas, abrir/anexar explicitamente AGENTS.md. Nenhuma ferramenta está definitivamente escolhida.

## 8. Revisões por cor entre Markdown e LaTeX
### Regra
Cada revisão lógica dos documentos recebe um ID e uma cor. Se originar alteração no .tex, usar EXATAMENTE a mesma cor e o mesmo ID. Toda a alteração ao `.tex` (texto novo ou substituído) é colorida com a cor do seu ID, usando a macro `\revtext`; não há alteração ao `.tex` sem cor. Cada revisão tem cor atribuída antes de terminar a interação, nunca "a atribuir". Cor pertence à revisão lógica, não a cada comando/commit; uma revisão pode abranger vários ficheiros e commits. Correções para concluir a mesma revisão mantêm ID/cor salvo decisão diferente.

### Antes de editar
Ler os documentos de acompanhamento e o .tex real quando fornecido. Identificar macros, cores, pacotes e convenções existentes; não recolorir revisões anteriores. Se o significado das cores não for claro, perguntar. Não reconstruir cronologia/autoria por adivinhação.

O ficheiro da proposta está em `latex/proposta_pt.tex` (a base original é `latex/proposta_IAHC_DINIS_ROSA.pdf`). Não criar um relatório substituto nem afirmar que foi atualizado. Registar atualização pendente quando aplicável. O estado atual de revisão do `.tex` está em `PROGRESS.md`, secção "LaTeX (`latex/proposta_pt.tex`)".

### Registo
Criar/manter REVISION_LOG.md com:
- ID sequencial estável (REV-001, REV-002...), sem renumerar passado.
- Data/hora e fuso quando conhecido.
- Nome da cor, hexadecimal e RGB exatos.
- O quê, porquê e ficheiros/secções afetados.
- Estado de correspondência no LaTeX: atualizado, não aplicável ou pendente, com motivo.
- Validação e pendentes.

Usar convenção existente. Se não houver, propor paleta legível e registar antes de editar. Nova revisão lógica usa nova cor distinguível; se a paleta ficar ambígua, perguntar em vez de reciclar silenciosamente. O ID é a referência permanente, não apenas a perceção da cor.

### Markdown
Incluir marcador textual, mesmo que a cor não seja renderizada:
```text
[REV-001 | cor #C62828]
```
HTML inline pode ser usado onde suportado:
```html
<span style="color:#C62828">[REV-001] Texto desta revisão.</span>
```
Não garantir cor em todos os visualizadores/GitHub. Manter conteúdo legível se estilos forem ignorados; não quebrar tabelas, listas ou código para o colorir.

Acrescentar entradas cronológicas em PROGRESS.md, distinguindo feito/validado/pendente. Não recolorir todo o documento. Preservar histórico no registo e Git.

### LaTeX
Respeitar macros existentes. Se for necessário adicionar marcação, uma implementação ilustrativa, não substituição automática, é:
```tex
% No preâmbulo, apenas se necessário/compatível:
\usepackage{xcolor}
\definecolor{rev001}{HTML}{C62828}
\newcommand{\revtext}[2]{{\color{#1}#2}}
% REV-001 — mesma cor do registo Markdown:
Texto existente. \revtext{rev001}{Texto novo.}
```
Mesmos valores RGB/hex do registo. Não duplicar pacotes nem redefinir macros inadvertidamente. Colorir apenas conteúdo novo/substituído; não alterar cores antigas. Escolher marcação compatível com matemática, títulos, tabelas e citações.

Texto eliminado fica rastreável no registo/diff. Se uma revisão substituir texto antes colorido, o novo texto recebe nova cor/ID e o passado permanece no histórico, não em camadas de cores sobrepostas.

### Sincronização
Após cada marco, verificar impacto real no relatório: metodologia, implementação concluída, resultados e limitações podem exigir atualização; correções cosméticas podem não exigir. Não transformar intenções em trabalho concluído.

Atualizar Markdown/.tex na mesma revisão quando aplicável. Se o .tex faltar ou houver bloqueio/aprovação pendente, registar pendência; não simular sincronização. Resultados só entram com evidência reproduzível.

Rever diff, IDs e cores. Compilar LaTeX com procedimento existente quando possível. Se não houver compilador, dizer explicitamente; não instalar distribuição pesada sem autorização. Reportar ID, cor, secções e pendentes. Só produzir versão final sem cores por instrução do utilizador.

## 9. Delegação por modelo e subagentes
Quando a ferramenta suportar escolha de modelo por subagente:
- Sonnet: coordenador, integração e implementação principal.
- Haiku: tarefas delimitadas, funções com contrato fechado, testes sintéticos e correções simples.
- Opus: diagnóstico complexo, revisão metodológica e implementação difícil com objetivo bem definido.

É uma política de encaminhamento, não garantia de disponibilidade/poupança. Usar nomes/IDs reais disponíveis; não inventar resolução de aliases. Não é obrigatório criar uma skill adicional se a ferramenta já suportar subagentes.

O coordenador deve:
1. Explicar tarefa, modelo, motivo, ficheiros e critério de conclusão antes de delegar.
2. Fornecer explicitamente regras, interfaces e contexto relevantes. Não assumir que o subagente herdou a conversa ou leu este ficheiro.
3. Garantir que ferramentas e acesso efetivo respeitam restrições. Nunca ampliar permissões para contornar bloqueios.
4. Exigir resumo, alterações, comandos, testes, resultados e pendentes, com evidência.
5. Rever integração e validar a evidência; a declaração “feito” não prova correção.
6. Manter um responsável por ficheiro, evitando alterações concorrentes e treinos paralelos.

Todos os subagentes têm as mesmas proibições: só treino/sintéticos no desenvolvimento, sem push, sem acesso reservado autónomo e sem experiências fora do plano/orçamento. Podem propor commits; integração e commit seguem o fluxo do coordenador para evitar conflitos.

Não delegar microtarefas cujo custo de explicar/rever exceda o benefício. A delegação também consome tokens/tempo; Sonnet continua a coordenar e rever. Não prometer que deixa de consumir contexto. Evitar cadeias recursivas ou proliferação de subagentes sem justificação.

Se a ferramenta não suportar encaminhamento, explicar e executar sequencialmente. Nunca simular uma chamada a outro modelo. Registar papéis/modelos e utilização quando disponível. Não usar modos que ignorem permissões.

## 10. Todos os cálculos usados devem ser reproduzíveis
### Regra central
Qualquer valor calculado a partir dos dados e usado em decisões, gráficos, relatórios, mensagens, limpeza ou avaliação deve resultar de código versionado e executável do projeto. Não usar cálculos informais do agente como evidência empírica.

Inclui: médias, medianas, quantis, IQR, limites de outliers, contagens de pontos/viagens/classes, durações, ausências, comparações, métricas e sumários de execução.

Fluxo obrigatório:
```text
Pergunta quantitativa
→ procurar função existente
→ criar/estender função testável se necessário
→ testar com sintéticos/treino
→ executar por ponto de entrada documentado em dados autorizados
→ guardar resultados e proveniência
→ usar/reportar o valor
```

Scripts temporários, python -c e notebooks podem chamar funções do projeto. Não podem ser a única implementação de uma fórmula/regra que produza números usados na análise. Se uma exploração ad hoc for útil, integrar a lógica e recalcular antes de apresentar a conclusão como evidência.

Não é preciso uma função por número ou operação pandas/NumPy. Funções reutilizáveis podem devolver tabelas inteiras e usar bibliotecas internamente. O utilizador deve conseguir repetir a operação com a API/CLI documentada. Evitar duplicar lógica entre notebooks, scripts e relatórios.

### APIs sugeridas, sem duplicação obrigatória
| Função | Recebe | Devolve |
|---|---|---|
| summarize_dataset | df autorizado e configuração | Contagens e tabelas globais de diagnóstico |
| summarize_trips | df e agrupamento | Pontos, durações e resumos por viagem |
| describe_features | df, colunas e convenções | Contagem válida, média, mediana, dispersão e quantis |
| fit_outlier_limits | Treino correspondente e método/configuração | Limites aprendidos, parâmetros e estatísticas |
| flag_outliers | df autorizado e limites congelados | Máscaras/tabela de ocorrências sem reaprender |
| compare_feature_versions | df, pares, unidades e tolerâncias | Diferenças e sumários |
| export_analysis_results | Resultados e proveniência | CSV/JSON/relatório e manifesto |

Reutilizar study_csv, flag_data_issues e compare_original_and_calculated quando já cobrirem esses contratos. Os nomes sugeridos não justificam duplicar APIs.

### Outliers e IQR
Se aprovado método IQR, guardar Q1, Q3, IQR=Q3-Q1, multiplicador k e limites Q1-k*IQR e Q3+k*IQR. Declarar quantis/interpolação, agrupamento, ausências/não finitos e caso IQR=0. k=1.5 é exemplo de proposta, não decisão aprovada por este ficheiro.

Assinalar outlier não prova erro nem autoriza exclusão. Método estatístico e ação de limpeza são decisões distintas. Aprender limites só no treino correspondente e persistir; não recalcular em conjuntos reservados.

### Proveniência mínima
Para resultados utilizados, guardar:
- Função e versão de código/commit quando disponível.
- Comando/ponto de entrada para reprodução.
- Dataset/split e identificação/hash do ficheiro ou manifesto conforme viável.
- Colunas, unidades, filtros, agrupamentos e parâmetros.
- Ausências, denominadores e convenções estatísticas relevantes.
- Seed quando aplicável, versões, data/hora.
- Caminho do resultado e arredondamento de apresentação.

Guardar precisão útil; arredondar apenas na apresentação. Não copiar valores para Markdown/LaTeX sem origem rastreável; preferir tabelas/templates gerados a partir dos artefactos. Aplicar também IDs/cores de revisão.

### Configuração não é estatística aprendida
Seed, janela, multiplicador k aprovado e limiar inicial podem ser constantes de configuração. Não precisam de uma função para os “descobrir”: são escolhas declaradas. Valores externos exigem fonte e não devem ser apresentados como medidos no CSV.

A regra vale igualmente para subagentes. O coordenador rejeita números sem caminho reproduzível. A existência de uma função nunca autoriza executá-la em validação/teste antes de aprovação.

## 11. Fecho e aceitação
Ao terminar um marco, informar ficheiros e motivos, revisão/cor, validação efetiva, resultados/limitações, commits e pendentes. Parar antes de acesso reservado, publicação ou expansão de âmbito.

Critérios obrigatórios:
- Nenhum número empírico usado como evidência depende só de uma sessão do agente.
- Resultados regeneráveis com dados autorizados e comandos documentados.
- Transformações aprendidas separadas da aplicação.
- Subagentes entregam evidência verificável e não ampliam permissões.
- Código, documentação, histórico de revisões e relatório não se contradizem sobre o que foi efetivamente feito.
