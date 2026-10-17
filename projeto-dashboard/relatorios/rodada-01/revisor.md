# Relatório do Revisor — rodada 01

## Versão examinada

Não há repositório Git neste workspace. SHA-256 dos arquivos revisados:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/README.md` | `310A78D53A8330D9FEB45320854DC24480216DA016443F9CB9586D8A80127667` |
| `projeto-dashboard/site/index.html` | `980B34C00181ADD2C2606722AB4688013FC52BC12A540F5F204BB9823C2B0EC0` |
| `projeto-dashboard/site/estilos.css` | `0C165327C011A49F8603BBFC707EF5335E6DFC8A6139600006510AF8B8B69D59` |
| `projeto-dashboard/site/app.js` | `F7954EDFB0C748D5DD4E88C0F7971F50359AA147884BE99463989DD36C81237C` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `5FB583BE52B38E057F324F1AC8F8ACDF36D54745F72F42EB4180D60B04D4DE75` |
| `projeto-dashboard/tests/test_tester_validation.py` | `6F2EDF7181C5941976810376DA501124F0A83DEAE75BE2EC244237702B8AAF88` |

## O que conferi

- Li `AGENTS.md`, os relatórios de Construtor e Tester, o preparador, README, HTML/CSS/JS, JSON e ambos os testes. Consultei `resumo.md` e `verificacao.md` para conferir a linhagem e as regras herdadas.
- Recalculei com biblioteca padrão (`csv` + `Decimal`) diretamente de `papelaria_limpa.csv`, sem usar `valor_venda` nem o agregador do preparador. Confirmei 180 linhas, 180 IDs, 548 unidades e 2.005.900 centavos (R$ 20.059,00); categoria: Acessórios 1.051.700, Livros 743.800, Papelaria 210.400 centavos; cidade: Campinas 857.800, Santos 693.750, Sorocaba 454.350 centavos. Recalculei os meses: jan/2026 623.500, fev/2026 618.100, mar/2026 764.300 centavos. Os grupos somam o total geral. Ticket médio: R$ 111,438…, exibido em centavos como R$ 111,44.
- Confirmei que o CSV original tem 182 linhas e duas repetições exatas; a base limpa e o JSON têm 180 linhas. Os valores do JSON correspondem a quantidade × preço em cada linha. Definições de venda, valor bruto e ticket estão documentadas, sem chamar valor vendido de lucro.
- O produto contém três KPIs, dois gráficos, tabela, filtros combináveis, estado vazio, limpeza, site estático e layout móvel sem rolagem horizontal na página (a tabela tem rolagem própria). Os filtros têm labels associados, foco visível, atalho para conteúdo e são controles nativos.
- A execução real da suíte confirma Firefox headless via Marionette, não DOM simulado. A cobertura verifica KPIs, agregados gráficos, linhas/IDs, filtros, vazio, HTTP, teclado e geometria em dois viewports.

## Comandos e evidências

- Em `projeto-dashboard`: `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **16 testes, 0 falhas, 0 ignorados; OK**, em 12,882 s. A saída detalhada no terminal lista testes de dados, fixture conhecido, HTTP, Firefox, filtros, vazio, teclado e viewports. A suíte também reexecuta o preparador com fixtures e com a base do projeto; as verificações de preservação passaram.
- Recalculo independente executado em Python padrão, com `csv.DictReader` e valores monetários `Decimal`; números registrados acima. Não foi criado arquivo de evidência separado.

## Problemas e encaminhamento

1. **Legibilidade dos textos dos gráficos em celular — encaminhar ao Construtor.** Os SVG usam `viewBox` com 520 unidades de largura e encolhem ao espaço do cartão. Em viewport de 390 px, a área útil fica em torno de 340 px (escala aproximada 0,65); a regra móvel reduz eixo/rótulo/valor a 11 unidades, cerca de 7 px renderizados (texto de 12 unidades fica perto de 8 px). Valores monetários e categorias ficam pequenos para leitura confortável. A suíte verifica empilhamento e ausência de overflow, mas não essa legibilidade visual. Ajustar a composição móvel (tipografia/área, rótulos simplificados ou alternativa tabular agregada) sem introduzir overflow; depois repetir testes e revisão visual.
2. **Cobertura/evidência de acessibilidade — encaminhar ao Tester.** `test_tester_validation.py` verifica tamanho mínimo apenas dos labels e selects dos filtros (12/14 px), não dos textos renderizados dos gráficos; não mede contraste nem arquiva captura visual. O teste de teclado opera o filtro de cidade e o botão limpar, mas não exercita especificamente o filtro de categoria por teclado. Assim, a afirmação “rótulos legíveis” no relatório do Tester excede a evidência coletada. Acrescentar verificações reproduzíveis de legibilidade dos textos gráficos em viewport pequeno e teclado nos dois filtros, ou restringir a afirmação ao que foi testado.

Não achei divergência numérica, falha funcional reproduzível ou falha na suíte. O primeiro item, contudo, não atende ao critério de rótulos legíveis/responsividade em celular. A conclusão de legibilidade baseia-se na geometria CSS/SVG e tamanhos declarados; não há captura de tela arquivada.

## Pendências

- Legibilidade dos rótulos gráficos no viewport móvel: **PENDENTE de correção pelo Construtor e reteste**.
- Evidência de legibilidade gráfica e teclado nos dois filtros: **PENDENTE para o Tester**.
- Após alterações, executar novamente a suíte completa e revisar a mesma versão final. Relatório conjunto final permanece fora do escopo desta revisão.

## Status

**REPROVADO — Revisor, rodada 01.** Os testes passaram, mas permanecem a não conformidade visual em tela pequena e a lacuna de evidência descrita acima. Não constitui aprovação conjunta.
