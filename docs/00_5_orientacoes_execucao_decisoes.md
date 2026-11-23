# 0.5 — Orientações consolidadas de execução

## Prioridade
Ler AGENTS.md, depois 00, este documento e 01. As regras atuais aqui e no AGENTS.md prevalecem sobre passos antigos que indiquem acesso direto a conjuntos reservados ou KNIME como obrigação. Não são autorização para usar validação/teste.

## Decisões atuais
Python é o ambiente principal; KNIME apenas contingência futura. Máquina: i7 de 12.ª geração, 16 GB de RAM e GPU integrada. Começar em CPU, medir no treino, não assumir CUDA. Conda não é requisito; preferir venv/pip se não existir.

Existe um só dataset. Dividir por ID completo antes da exploração e manter manifesto fixo. Viagens do mesmo navio podem estar em conjuntos distintos; não alegar generalização por navio inédito.

Âmbito mínimo: CNN completa e CNN com janelas/sobreposição, com ramo separado de pós-processamento simples ainda a aprovar. HMM, Wu, dashboard, explicabilidade avançada e calibração ficam fora do mínimo atual.

## Protocolo e dúvidas
A média de probabilidades de janelas é reconstrução; não equivale ao ramo de suavização temporal. Preservar previsões brutas. Propor filtro simples e pedir aprovação da unidade/largura, bordas e protocolo. Aplicar depois da reconstrução e sem atravessar gaps.

Perguntar prazo/orçamento antes de execuções longas. Perguntar se 0% e 50% devem ser prioritários ou se os quatro overlaps são obrigatórios. Não bloquear estudo do treino com essas dúvidas.

Campo recetivo da arquitetura ilustrativa de três kernels 5, stride 1, sem dilatação: 13 pontos. Entrada completa não implica contexto global. Registar orçamento, passos, épocas e diferenças de batch; overlap no treino e na inferência são decisões distintas.

## Marcos
1. Ambiente, consolidação, divisão mínima e isolamento.
2. Preparação auditável e testes só no treino/sintéticos; pedir revisão.
3. CNN completa mínima, forward/backward e alinhamento; medir custo.
4. Janelas, máscaras, cobertura, reconstrução e treino conforme orçamento.
5. Pós-processamento simples depois de aprovado, em ramo separado.
6. Congelar implementação/protocolo e pedir autorização para seleção formal na validação.
7. Congelar modelos/lista de variantes e pedir nova autorização para avaliação final no teste.

Monitorização interna é criada só no treino, por ID e antes do fit de transformações. Não abrir reservados para debugging. Reportar erros reproduzindo-os no treino/sintéticos e documentar qualquer exposição.

## Correções obrigatórias aos contratos antigos
- Ordem da preparação: manifesto por IDs → separação/isolamento → carregar treino → estudo/limpeza/recálculo → normalização → exportação.
- validate_splits na separação inicial só verifica IDs/contagens técnicas, não classes reservadas.
- run_preparation não devolve DataFrames reservados no desenvolvimento.
- fit_scaler só aprende no treino; partição interna independente exige fit no treino interno.
- CNN devolve logits para BCEWithLogitsLoss; sigmoid apenas para probabilidades.
- Não aplicar suavização no ramo principal: comparar ramo bruto com ramo pós-processado aprovado.
- Funções são contratos orientadores, não obrigação de criar dezenas de ficheiros vazios.

## Estado deste pacote
Pacote reconstituído a partir dos sete Markdowns fornecidos, com aviso normativo comum e correções direcionadas, mais este consolidado e AGENTS.md. Não é uma reprodução byte a byte do ZIP gerado anteriormente. O código e as experiências ainda não foram executados.
