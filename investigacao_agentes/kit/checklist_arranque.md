# Checklist de arranque de um projeto com agentes de IA

<!-- REV-084. Destilado das quatro tentativas do projeto AIS. -->

## Antes da primeira sessão com o agente
- [ ] Escrever, à mão ou com um LLM de chat, uma especificação curta: objetivo, entregável,
      critério de "feito", perguntas de investigação, o que fica fora do âmbito.
- [ ] Dividir o trabalho em marcos executáveis; o marco 2 é um resultado ponta a ponta simples.
- [ ] Escolher UMA ferramenta de agente principal para o projeto (as outras só para tarefas
      delimitadas, registadas).
- [ ] Criar o repositório com a estrutura final logo no início (`src/`, `tests/`, `docs/`,
      `configs/`, `latex/`), `.gitignore` para dados, ambientes e resultados.
- [ ] Copiar e preencher `AGENTS_modelo.md` (≈100 linhas) e uma ponte de 3–5 linhas para a
      ferramenta (`CLAUDE.md`, `GEMINI.md`, ...) que só manda ler o AGENTS.md e o handoff.
- [ ] Criar `handoff.md` e `PROGRESS.md` a partir dos modelos.
- [ ] Bibliografia e PDFs grandes fora do git (ou numa pasta ignorada).

## Primeira sessão
- [ ] Pedir ao agente que leia o AGENTS.md e confirme as regras por palavras suas.
- [ ] Ambiente: venv + `requirements.txt` com versões fixas; registar a versão de Python.
- [ ] Se houver conjuntos reservados: divisão por ID com seed, manifesto versionado, papéis
      dos conjuntos escritos, protocolo de autorização (JSON + registo de acessos) com testes.
- [ ] Primeiros testes sintéticos a correr.

## Em cada sessão
- [ ] Abrir com: «Lê o AGENTS.md e o handoff.md e diz-me o ponto de situação.»
- [ ] Um objetivo por sessão; pedir plano curto antes de execução grande.
- [ ] Exigir que cada número venha de código versionado.
- [ ] Recusar exploração sem pergunta e critério de paragem ("muito por pouco").
- [ ] No fim: handoff reescrito, entrada no PROGRESS, testes a passar, commits explícitos.

## Antes de entregar
- [ ] Revisão independente só de leitura (outro modelo/subagente).
- [ ] Conjunto final aberto uma só vez; qualquer reutilização declarada no resumo.
- [ ] Relatório gerado a partir de macros/tabelas produzidas por código.
- [ ] Ajustes cosméticos do relatório agrupados numa só revisão.
- [ ] Push só quando o utilizador o pedir.
