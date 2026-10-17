# Relatório do Construtor — rodada 01

## Versão examinada

Não há repositório Git neste workspace; versão identificada pelos hashes SHA-256 dos artefatos entregues:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/site/index.html` | `980B34C00181ADD2C2606722AB4688013FC52BC12A540F5F204BB9823C2B0EC0` |
| `projeto-dashboard/site/estilos.css` | `0C165327C011A49F8603BBFC707EF5335E6DFC8A6139600006510AF8B8B69D59` |
| `projeto-dashboard/site/app.js` | `F7954EDFB0C748D5DD4E88C0F7971F50359AA147884BE99463989DD36C81237C` |
| `projeto-dashboard/README.md` | `310A78D53A8330D9FEB45320854DC24480216DA016443F9CB9586D8A80127667` |

## Construído e conferido

- `preparar_dados.py` lê `papelaria_limpa.csv` sem alterá-lo, valida esquema, vazios, IDs únicos, datas, quantidades, valores monetários e a igualdade entre `valor_venda` e quantidade × preço. Exporta os preços e valores em centavos inteiros para evitar erros de ponto flutuante no navegador.
- Dashboard estático acessível, com filtros de cidade e categoria, três indicadores, barras por categoria, linha mensal, tabela detalhada, botão para limpar, estados vazios e layout responsivo. Todos os componentes usam o mesmo conjunto filtrado.
- README documenta comandos PowerShell, definições, tratamento herdado e limitações; indica `site/` como pasta publicável.
- Foram preservados os arquivos de origem e resultados prévios; o preparo só lê `papelaria_limpa.csv` e grava `projeto-dashboard/site/dados/vendas.json`.

## Comandos executados e resultados

1. `& .\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py` — **OK**. Gerou 180 registros e 548 unidades; total de R$ 20.059,00.
2. Conferência independente com pandas/JSON — **OK**. Confirmados 180 IDs distintos, total de 2.005.900 centavos, 548 unidades e `valor_venda_centavos = quantidade × preco_unitario_centavos` em todas as linhas. Agregados: Acessórios 1.051.700 centavos; Livros 743.800; Papelaria 210.400.
3. `node --check .\projeto-dashboard\site\app.js` — **OK**, sem erro de sintaxe.
4. Servidor HTTP temporário do Python e requisições HTTP para `index.html`, `app.js`, `estilos.css` e `dados/vendas.json` — **OK**, todos responderam HTTP 200 com conteúdo conferido. A evidência foi a saída no terminal; o servidor foi encerrado ao fim da verificação.
5. Suíte de testes — **PENDENTE**, ainda será criada/executada pelo Tester. Interação real no navegador, filtros, teclado e inspeção visual responsiva também **PENDENTES**; não foram localizados Playwright, Selenium ou executáveis de navegador disponíveis neste ambiente.

## Problemas e encaminhamento

Não foram identificados defeitos nos checks locais de construção. **Tester:** executar a suíte obrigatória e conferir filtros isolados/combinados, seleção vazia, limpar, tabela, KPIs, gráficos, teclado e telas pequena/grande. Se houver defeito de produto, devolver ao Construtor com reprodução. A falta de navegador neste ambiente não é registrada como teste aprovado.

## Status

**APROVADO — entrega do Construtor nesta rodada.** Testes de sistema e interação do navegador permanecem **PENDENTES**; este status não representa aprovação conjunta do projeto.
