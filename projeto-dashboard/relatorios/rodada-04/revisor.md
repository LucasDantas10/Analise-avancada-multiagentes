# Relatório do Revisor — rodada 04

## Versão examinada

Sem Git. SHA-256 recalculados após a execução da suíte:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `projeto-dashboard/site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `projeto-dashboard/site/login.css` | `E77DC9F29FC8FF06A8BE3823AF8798FA3736F81E65DFD9F5E1A7B7DBDE6BB9A3` |
| `projeto-dashboard/site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `projeto-dashboard/site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `projeto-dashboard/site/estilos.css` | `DA869561BF07814F370A3B962698640C4854825EE661470B24A22900A3109AD0` |
| `projeto-dashboard/site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `projeto-dashboard/tests/test_tester_validation.py` | `86AFCFF657186178BB232D021731586C192DACAE1AEB45828516B48C2388E14F` |

Os hashes correspondem à versão indicada nos relatórios de Construtor e Tester da rodada 04.

## Verificações

- Revisei o relatório do Revisor da rodada 03, os relatórios de Construtor e Tester da rodada 04, README, CSS de login/painel, HTML/JS, dados e testes. O login continua explicitamente demonstrativo: as credenciais e os dados são públicos, `sessionStorage` é contornável e README/tela dizem que isso não protege dados nem substitui autenticação no servidor. Não há alegação de segurança real.
- Recalculei os valores independentemente de `papelaria_limpa.csv` com `csv` e `Decimal`, somando quantidade × preço unitário. Confirmei 180 linhas/IDs, 548 unidades e R$ 20.059,00 (2.005.900 centavos); categorias: Acessórios R$ 10.517,00, Livros R$ 7.438,00 e Papelaria R$ 2.104,00; cidades: Campinas R$ 8.578,00, Santos R$ 6.937,50, Sorocaba R$ 4.543,50; meses: jan R$ 6.235,00, fev R$ 6.181,00, mar R$ 7.643,00. Ticket: R$ 111,438… (R$ 111,44 arredondado). O original contém 182 linhas e 2 repetições exatas; base tratada/JSON têm 180. O total e as unidades do JSON conciliam com o recálculo.
- **Contraste da reprovação anterior — resolvido.** Revisei as novas cores e recalculei pela luminância relativa WCAG sRGB e razão `(Lmais claro + 0,05)/(Lmais escuro + 0,05)`. As combinações que falharam na rodada 03 agora resultam em: auxiliar/placeholder do painel `#526779` sobre branco **5,874:1**; placeholder do login `#526779` sobre `#fcfdfd` **5,764:1**; aviso de demonstração sobre branco **5,874:1**; rodapé sobre `#f5f7f8` **5,466:1**. Todas excedem 4,5:1 para texto normal. Também recalculei o contexto de texto claro no gradiente do hero reportado pelo Construtor (`#c1ebdb` sobre `#206a68`): **4,867:1**. Os CSS corrigem a paleta auxiliar e dão opacidade explícita aos placeholders.
- A suíte executa no Firefox real um teste de cores conhecido (preto/branco 21:1, cinza 118/branco ≈4,542:1 e cinza 119 abaixo de 4,5) e a verificação de elementos visíveis do login, painel e estado vazio. Nesta execução observei a evidência de **88 amostras, mínimo 5,332:1, zero violações**. Isso, combinado à minha recálculo independente das combinações que motivaram a reprovação, confirma a correção.
- Revisei também a lógica de busca textual sem acento, limites inclusivos de data, erro de intervalo invertido, composição de filtros, KPIs/unidades, agregações SVG, ordenação nas nove colunas, paginação/reset, CSV de todos os resultados filtrados e tabela completa de impressão. HTML mantém labels, estados e foco; os filtros/ordenação são operáveis por teclado. Os relatórios indicam que a geometria móvel permanece sob o breakpoint em 500 px. Não encontrei nova divergência de dados ou defeito funcional nos fluxos cobertos.

## Comando e evidências

- No diretório `projeto-dashboard`, executei `..\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **26 testes, 0 falhas**, em 20,352 s. A saída incluiu testes de dados/preservação, HTTP, Firefox real, login/rotas, busca, datas, ordenação, paginação, CSV, impressão e os dois testes WCAG; também imprimiu `count=88 minimum=5.332 failures=[]`.
- Recálculo independente dos agregados e dos quatro contextos de contraste da rodada 03 executado em Python padrão. Os hashes acima foram calculados da versão atual após o teste.

## Limitações explícitas

- **Viewport:** Firefox recebe pedido de janela 390 px, mas reporta `innerWidth=500px`; esse valor segue no breakpoint móvel. Não afirmo ter medido viewport CSS exato de 390 px.
- **CSV:** o conteúdo real do Blob e a tentativa de download são validados, mas o Firefox desta execução não persistiu o arquivo no diretório de downloads.
- **Impressão/PDF:** o teste confirma `window.print()` e as regras `@media print`; não há PDF salvo como evidência. “Salvar como PDF” depende do diálogo do navegador.
- **Login:** continua público e demonstrativo, sem proteção dos dados. Para dados privados é necessário backend com autenticação/autorização; essa limitação está visível no README e na tela inicial.

Não resta pendência de contraste ou funcional obrigatória nesta versão. As limitações de viewport/artefatos acima ficam registradas e não são tratadas como verificações realizadas.

## Status

**APROVADO — Revisor, rodada 04.** As falhas de contraste que motivaram a reprovação da rodada 03 foram recalculadas e estão resolvidas; os 26 testes passaram na versão identificada pelos hashes acima, e números, fluxos e transparência do acesso demonstrativo foram conferidos.
