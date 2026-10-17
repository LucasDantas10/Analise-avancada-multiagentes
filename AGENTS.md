# Equipe de análise de dados e dashboard

## Objetivo

Após a atividade das três skills, transformar o CSV indicado pelo usuário em uma análise reproduzível e um dashboard interativo em site estático. Explicar tudo em português simples, para iniciantes usando Windows e VS Code.

Estas instruções devem ser executadas quando o usuário pedir a construção do projeto. Apenas ler ou editar este arquivo não inicia o projeto.

## Skills que devem continuar sendo usadas

- `explore-data`: conhecer a base e orientar a limpeza.
- `data-visualization`: escolher e apresentar os gráficos.
- `validate-data`: conferir cálculos e conclusões.

Leia os respectivos arquivos em `.agents/skills/NOME-DA-SKILL/SKILL.md`. Se algum estiver ausente, informe qual falta; não afirme que o utilizou.

## Organização dos agentes

O Codex principal coordena o trabalho. Use três subagentes reais com as responsabilidades abaixo, reutilizando-os nas correções. Passe a cada um o objetivo, os arquivos relevantes e o relatório da etapa anterior.

Se as ferramentas de subagentes não estiverem disponíveis, informe a limitação antes de começar. Não simule três agentes nem apresente uma execução individual como revisão independente.

| Agente | O que constrói | Relatório |
| --- | --- | --- |
| Construtor | Limpeza, análise, site e correções do produto. | `construtor.md` |
| Tester | Testes reproduzíveis dos dados e do dashboard. | `tester.md` |
| Revisor | Revisão dos resultados, código e testes; exemplos que reproduzam problemas e propostas de correção. | `revisor.md` |

Todos produzem entregas concretas. O tester pode corrigir seus testes; o revisor pode acrescentar casos de teste. Correções no produto voltam ao construtor. Não permita que dois agentes editem o mesmo arquivo ao mesmo tempo.

## Ciclo de trabalho

1. O coordenador confirma o CSV solicitado e registra os critérios de aprovação abaixo. Se houver vários CSVs e nenhum tiver sido indicado, pergunta qual usar.
2. O construtor prepara a análise e o dashboard. Enquanto isso, o tester pode planejar os testes a partir dos requisitos.
3. O construtor entrega seus arquivos e relatório. O tester executa os testes sobre essa versão e registra os resultados.
4. Se houver falhas, o tester devolve o relatório ao construtor. O construtor corrige e devolve ao tester para nova execução.
5. Quando os testes passarem, o revisor confere a entrega, os testes e suas evidências. Falta de cobertura volta ao tester; defeito no produto volta ao construtor.
6. Toda alteração exige nova execução dos testes afetados. Na versão final, execute toda a suíte e faça nova revisão.
7. Termine como **APROVADO** somente quando construtor, tester e revisor aprovarem a mesma versão, todos os testes obrigatórios passarem e não houver pendências.

Continue corrigindo enquanto houver progresso. Se faltar acesso, ferramenta ou limite de uso, registre **BLOQUEADO** e o próximo passo. Se a mesma falha persistir por três tentativas sem avanço, interrompa o ciclo e explique o impedimento. Nunca transforme um bloqueio em aprovação.

## O que construir

- Preserve o CSV original e os resultados da atividade anterior. Gere a nova entrega em `projeto-dashboard/`.
- Use Python e pandas para preparar os dados, aproveitando `.venv/Scripts/python.exe` quando disponível.
- Registre o significado de cada linha, as regras de limpeza, os campos calculados e as limitações. Não invente dados nem elimine duplicatas sem justificar.
- Crie `site/index.html`, CSS, JavaScript e dados preparados dentro de `projeto-dashboard/`. O site deve funcionar como conteúdo estático, sem servidor de aplicação ou banco de dados.
- Inclua três indicadores pertinentes à base, dois gráficos, uma tabela e dois filtros por colunas existentes. Filtros devem atualizar indicadores, gráficos e tabela juntos.
- Para vendas: use valor total vendido, quantidade de vendas e ticket médio, com a definição de venda documentada. Não chame faturamento de lucro.
- Inclua botão para limpar filtros, mensagem para resultados vazios, títulos claros e valores formatados corretamente. O dashboard deve funcionar em computador e celular.
- Entregue um `README.md` curto com os comandos reais para preparar os dados, executar os testes e abrir o site por um servidor HTTP local. Identifique `site/` como a pasta publicável em hospedagem estática. A publicação não faz parte desta etapa.

## Testes obrigatórios

O tester deve construir e executar testes que confiram:

- Preservação do original, colunas necessárias, tipos, valores ausentes e tratamento das duplicatas conforme as regras documentadas.
- Totais e agrupamentos recalculados de forma independente; use também um pequeno exemplo de resultado conhecido, sem copiar a lógica do construtor.
- Correspondência entre os dados preparados e os indicadores, gráficos e tabela apresentados.
- Cada filtro isolado, filtros combinados, seleção vazia e botão de limpar; nenhuma divisão por zero ou `NaN` na tela.
- Carregamento do site por HTTP, sem arquivos ausentes ou erros de JavaScript, e interação real no navegador, preferencialmente com testes automatizados.
- Exibição em tela pequena e grande, rótulos legíveis e filtros utilizáveis por teclado.

Teste não executado é **PENDENTE**, nunca aprovado. Se não houver acesso a navegador, registre o bloqueio dos testes de interface. Não remova testes nem enfraqueça critérios apenas para obter aprovação; uma correção legítima de teste precisa de justificativa e revisão.

## Relatórios curtos por rodada

Cada agente salva seu relatório em `projeto-dashboard/relatorios/rodada-01/`, depois `rodada-02/` e assim por diante. Preserve o histórico.

Cada relatório deve conter:

1. Versão examinada: commit, quando existir, ou hashes dos arquivos relevantes.
2. O que foi construído, alterado ou conferido.
3. Comandos executados, resultados e localização das evidências.
4. Problemas encontrados e para qual agente devem voltar.
5. Status: **APROVADO**, **REPROVADO** ou **BLOQUEADO**; verificações não realizadas ficam explicitamente **PENDENTES**.

O coordenador entrega `projeto-dashboard/relatorios/FINAL.md` com o status conjunto, a versão final, os testes executados e como abrir o dashboard. Não afirme que todos os testes passaram sem os resultados registrados.

## Referências do funcionamento do Codex

- [Instruções em AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- [Subagentes no Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents). O arquivo orienta a delegação; a execução depende dos recursos disponíveis no Codex. Subagentes consomem mais uso do que uma execução individual.