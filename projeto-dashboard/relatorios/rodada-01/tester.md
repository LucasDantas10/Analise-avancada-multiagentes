# Relatório do Tester — rodada 01

## Versão examinada

Não há repositório Git no workspace. Hashes SHA-256 da versão testada:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/site/index.html` | `980B34C00181ADD2C2606722AB4688013FC52BC12A540F5F204BB9823C2B0EC0` |
| `projeto-dashboard/site/app.js` | `F7954EDFB0C748D5DD4E88C0F7971F50359AA147884BE99463989DD36C81237C` |
| `projeto-dashboard/site/estilos.css` | `0C165327C011A49F8603BBFC707EF5335E6DFC8A6139600006510AF8B8B69D59` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `5FB583BE52B38E057F324F1AC8F8ACDF36D54745F72F42EB4180D60B04D4DE75` |
| `projeto-dashboard/tests/test_tester_validation.py` | `6F2EDF7181C5941976810376DA501124F0A83DEAE75BE2EC244237702B8AAF88` |

## O que foi testado

- Criada a suíte independente `tests/test_tester_validation.py`. A suíte existente também foi executada.
- Conferidos CSV original e base limpa, duplicatas, schema, tipos, nulos, valores monetários, IDs, preservação byte a byte do JSON preparado e hashes das fontes/resultados prévios.
- Totais e agrupamentos foram recalculados independentemente: 180 vendas, 548 unidades, 2.005.900 centavos; Acessórios 1.051.700, Livros 743.800, Papelaria 210.400; Campinas 857.800, Santos 693.750, Sorocaba 454.350. Um fixture conhecido de duas vendas conferiu 880 centavos e 5 unidades no preparador.
- No Firefox real, verificados indicadores, gráficos por categoria/mês e IDs/linhas da tabela, com filtros cidade e categoria isolados e combinados, seleção sem resultados, valores finitos e botão limpar. As séries dos gráficos foram comparadas novamente nos estados filtrados.
- Verificados HTTP 200 dos recursos estáticos, sintaxe JS com Node, erros JavaScript capturados durante a execução no navegador, teclado, rótulos legíveis e viewports 1280×900 e 390×844.

## Comandos e evidências

- `python -m unittest discover -s tests -v` (executado em `projeto-dashboard`) — **OK: 16 testes, 0 falhas**, incluindo Firefox headless real. Última execução após todas as alterações dos testes.
- A saída detalhada do comando contém cada caso aprovado; os testes são reproduzíveis pelo mesmo comando. O navegador não foi simulado.
- Na primeira execução surgiu uma asserção incorreta na suíte existente: o teste esperava o total da cidade como se fosse uma barra do gráfico de categorias. A verificação foi corrigida para conferir a soma das barras filtradas, conforme a granularidade real do gráfico. Também foi corrigida a expectativa de arredondamento do ticket médio para centavos. A suíte completa foi executada novamente e passou.
- O preparador preservou os hashes dos arquivos de origem/resultados prévios e reproduziu o JSON sem alteração de bytes.

## Problemas e encaminhamentos

Não foram encontrados defeitos reproduzíveis no produto. Nenhum encaminhamento ao Construtor. Verificações obrigatórias executadas; sem pendências.

## Status

**APROVADO — Tester, rodada 01.**
