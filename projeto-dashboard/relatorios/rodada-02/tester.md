# Relatório do Tester — rodada 02

## Versão examinada

Não há repositório Git. SHA-256 dos arquivos examinados/testados:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/README.md` | `310A78D53A8330D9FEB45320854DC24480216DA016443F9CB9586D8A80127667` |
| `projeto-dashboard/site/index.html` | `980B34C00181ADD2C2606722AB4688013FC52BC12A540F5F204BB9823C2B0EC0` |
| `projeto-dashboard/site/estilos.css` | `61C7EA5C6ED975DD986537CE8851C5FEF898229481DC27BAB355D8C5CBC24C84` |
| `projeto-dashboard/site/app.js` | `069097BF5F4EB3B7BDF14A9BC4C1D45086902F1812FCF33DFD776F731E7C66BF` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `5FB583BE52B38E057F324F1AC8F8ACDF36D54745F72F42EB4180D60B04D4DE75` |
| `projeto-dashboard/tests/test_tester_validation.py` | `8F30B38EE1EECBC31F266561C3F77AB01AB50604CB1554156461BDE6DD80F2C4` |

CSS e JavaScript diferem da versão da rodada 01 revisada, indicando que a cobertura foi executada contra a versão corrigida do produto. Os testes preexistentes foram preservados.

## Cobertura adicional e evidências

- Em `test_mobile_graph_text_has_minimum_rendered_height`, Firefox headless real solicitou janela de 390 px e mediu as caixas reais (`getBoundingClientRect().height`) dos textos `grafico-eixo`, `grafico-rotulo` e `grafico-valor` nos dois SVGs. Todos os elementos medidos passaram o mínimo de 12 px: altura mínima observada de **18 px** para cada classe presente em cada gráfico. Evidência emitida no terminal: `Firefox: window request=390px; innerWidth móvel real=500px; altura mínima DOMRect por SVG/classe=...`.
- Nota de viewport: Firefox manteve `innerWidth=500px`, apesar da janela solicitada em 390 px. 500 px está dentro do breakpoint móvel do CSS (até 520 px); o teste confere esse breakpoint e mede a dimensão efetiva, sem simular o navegador. A medição é do layout móvel efetivamente aplicado.
- `test_keyboard_labels_and_responsive_viewports` usa Firefox WebDriver para enviar teclas aos filtros nativos de cidade (**Campinas**) e categoria (**Livros**), confere os valores escolhidos e o resultado combinado, e envia Enter ao botão Limpar filtros, confirmando filtros vazios e 180 vendas restauradas.

## Comandos e resultados

- `python -m unittest discover -s tests -p test_tester_validation.py -v` — **8 testes, OK** após a inclusão das verificações; execução no Firefox real.
- `python -m unittest discover -s tests -v` — **17 testes, 0 falhas**, execução final completa após todas as alterações dos testes. Inclui dados, fixture conhecido, preservação dos arquivos, HTTP, sintaxe JavaScript, filtros, estado vazio, teclado, dimensões responsivas e legibilidade dos textos SVG.
- Não houve edição do produto nem dos relatórios de terceiros nesta rodada.

## Problemas, encaminhamentos e pendências

Não foi reproduzida falha no produto nos critérios adicionais; nenhum encaminhamento ao Construtor. Não há teste obrigatório pendente. O Firefox não entregou `innerWidth` de exatamente 390 px, mas mediu e aprovou o breakpoint móvel real em 500 px, conforme registrado acima.

## Status

**APROVADO — Tester, rodada 02.**
