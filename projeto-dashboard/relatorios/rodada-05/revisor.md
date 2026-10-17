# Relatório do Revisor — rodada 05

## Versão examinada

Sem Git. Recalculei os hashes SHA-256 do produto e testes atuais:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `projeto-dashboard/site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `projeto-dashboard/site/login.css` | `E77DC9F29FC8FF06A8BE3823AF8798FA3736F81E65DFD9F5E1A7B7DBDE6BB9A3` |
| `projeto-dashboard/site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `projeto-dashboard/site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `projeto-dashboard/site/estilos.css` | `196AE086A120B144C44D553559BA57CC1B25DB53AFDFF7263B1F32C488FE0A13` |
| `projeto-dashboard/site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `projeto-dashboard/tests/test_tester_validation.py` | `86AFCFF657186178BB232D021731586C192DACAE1AEB45828516B48C2388E14F` |

O CSS atual confere exatamente com o hash exigido: **`196AE086A120B144C44D553559BA57CC1B25DB53AFDFF7263B1F32C488FE0A13`**. Também coincide com os relatórios de Construtor e Tester da rodada 05. O hash `DA869…` do relatório do Revisor da rodada 04 refere-se a versão anterior e não é o CSS testado nesta rodada.

## Revisão independente

- Li os relatórios de Construtor e Tester da rodada 05, o relatório do Revisor da rodada 04, README, CSS atual, produto e suíte. Os hashes de `app.js`, HTML, dados e testes permanecem iguais aos da versão anterior revisada; a alteração relevante é o alinhamento/atualização do CSS.
- **Contraste:** recalculei pela luminância sRGB WCAG as combinações que motivaram a reprovação da rodada 03: auxiliar/placeholder do painel `#526779` sobre branco = **5,874:1**; placeholder do login `#526779` sobre `#fcfdfd` = **5,764:1**; aviso demo sobre branco = **5,874:1**; rodapé do login sobre `#f5f7f8` = **5,466:1**. Todos excedem o critério AA de 4,5:1 para texto normal. Acento teal `#0b706e` sobre `#e4f3f0` = **5,166:1**. O contexto de texto claro no gradiente (`#c1ebdb` / `#206a68`) fica em **4,867:1**. Portanto, considero resolvido o achado de contraste anterior.
- A suíte usa Firefox real para contrastes calculados de texto visível no login, painel e estado vazio. Minha execução reproduziu `count=88`, `minimum=5.332`, `failures=[]`. O Construtor relata uma checagem complementar de 80 pares com mínimo 4,70:1; esse escopo inclui combinações/fundos diferentes da amostra DOM de 88 textos. Ambos excedem 4,5:1. O relatório do Revisor da rodada 04 tinha hash CSS anterior (`DA869…`); o relatório atual de alinhamento e a hash local concordam em `196AE…`.
- Recalculei diretamente de `papelaria_limpa.csv`, com `csv` e `Decimal`, quantidade × preço unitário: 180 linhas/IDs, 548 unidades e 2.005.900 centavos (R$ 20.059,00). Categorias: Acessórios 1.051.700, Livros 743.800, Papelaria 210.400 centavos; cidades: Campinas 857.800, Santos 693.750, Sorocaba 454.350 centavos; meses: jan 623.500, fev 618.100, mar 764.300 centavos. Ticket médio R$ 111,438… (exibido como R$ 111,44). JSON e CSV limpo conciliam; original 182 linhas com duas duplicatas exatas, base limpa/JSON 180.
- A metodologia continua definindo linha como venda, valor bruto como quantidade × preço, e explicita que não é lucro. Revisei busca e filtros de data/cidade/categoria, KPIs/gráficos/tabela, ordenação, paginação, reset, exportação dos filtrados e impressão. Os testes cobrem busca/datas/filtros combinados, ordenação nas nove colunas, paginação, CSV e print. A tela e README descrevem o login como demonstração pública com credenciais e dados públicos; `sessionStorage` não protege acesso. Não fazem alegação de segurança real.

## Comando e evidências

- Em `projeto-dashboard`, executei `..\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **26 testes, 0 falhas**, em 19,816 s. A saída detalhada inclui Firefox real, HTTP, login/rotas, dados/preservação, filtros, busca, datas, ordenação, paginação, CSV, impressão, altura de textos SVG e WCAG: `count=88 minimum=5.332 failures=[]`.
- Recalculei os hashes após a execução, agregados da base e razões WCAG acima com Python padrão; os resultados e a versão CSS coincidem com os relatórios da rodada 05.

## Limitações explícitas

- Firefox recebe solicitação de janela de 390 px, mas informa `innerWidth=500px`; a largura observada continua sob o breakpoint móvel. Não afirmo que viewport CSS de 390 px tenha sido medida.
- CSV foi verificado pelo Blob real e tentativa de download, sem persistência no diretório nesta configuração. Impressão foi verificada por `window.print()` e regras `@media print`; não foi salvo arquivo PDF.
- Login permanece público e demonstrativo, não é barreira de segurança. Não deve proteger dados privados; isso está documentado no README e na tela.

Não encontrei divergência funcional, numérica ou de contraste pendente nesta versão.

## Status

**APROVADO — Revisor, rodada 05.** Hash local do CSS corresponde ao `196AE…` solicitado; a suíte completa passou e a correção de contraste foi confirmada por recálculo próprio e pela medição Firefox de 88 amostras. Limitações de viewport, download, PDF e autenticação demo estão explicitadas e não são tratadas como testes realizados.
