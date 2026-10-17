# Relatório do Revisor — rodada 02

## Versão examinada

Não há repositório Git; identifiquei a versão pelos hashes SHA-256 recalculados após os testes:

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

Os hashes do produto coincidem com os registrados pelo Construtor e Tester na rodada 02; a suíte adicional do Tester é a versão indicada acima.

## Verificações

- Li o relatório de reprovação da rodada 01, os relatórios de Construtor e Tester da rodada 02, o preparador, README, HTML/CSS/JS, dados preparados e testes atuais. Revi especificamente as correções de SVG responsivo, descrições acessíveis e teclado dos dois filtros.
- Recalculei independentemente a partir de `papelaria_limpa.csv`, usando `csv` e `Decimal` (quantidade × preço, sem usar `valor_venda`): 180 linhas/IDs, 548 unidades, total de 2.005.900 centavos (R$ 20.059,00); categorias: Acessórios 1.051.700, Livros 743.800 e Papelaria 210.400 centavos; cidades: Campinas 857.800, Santos 693.750 e Sorocaba 454.350 centavos; meses: jan/2026 623.500, fev/2026 618.100 e mar/2026 764.300 centavos. Os agrupamentos conciliam com o total. Ticket recalculado: R$ 111,438… por venda, formatado em R$ 111,44.
- Confirmei que o CSV original tem 182 linhas, com duas repetições exatas; a base limpa e o JSON têm 180 linhas. O total e unidades do JSON coincidem com o recálculo. A metodologia continua documentando linha/venda, cálculo do valor bruto e limites (sem custos/lucro); o README fornece comandos PowerShell e indica `site/` como publicável.
- **Legibilidade móvel:** executei Firefox headless real via Marionette, sem editar os arquivos. O Firefox limita a janela solicitada de 390 px a `innerWidth=500px`; a media query móvel (até 520 px) estava ativa. Para revisar a largura correspondente ao conteúdo em viewport de 390 px, ajustei temporariamente no DOM a largura do contêiner para 370 px. Os SVG mediram 339,2 px de largura; fontes calculadas de 12 px e caixas `getBoundingClientRect()` de 18 px de altura para todos os textos de eixo, categoria e valor. Os valores monetários integrais permanecem nos rótulos; os ticks de escala são abreviados. A nova geometria `viewBox`/dimensões efetivas evita reduzir os textos quando o gráfico encolhe. Isso resolve o achado visual da rodada 01 na largura de conteúdo equivalente, embora não seja medição de `innerWidth=390` literal.
- **Teclado e acessibilidade:** na suíte, o Firefox envia teclas aos selects nativos de cidade (**Campinas**) e categoria (**Livros**), verifica o resultado combinado e aciona “Limpar filtros” por Enter, conferindo retorno aos filtros vazios e às 180 vendas. Labels estão associados, foco visível; os `aria-label` dos gráficos são atualizados com os valores agregados. A revisão da rodada 01 sobre ausência de teste de teclado no filtro de categoria foi resolvida.
- Mantêm-se os três KPIs, dois gráficos, tabela, filtros combináveis, estado vazio e limpeza. Os testes de interação/HTTP com Firefox real conferem estado filtrado, tabela/gráficos, recursos estáticos, erros JS e geometria móvel/grande; não identifiquei regressão nem divergência de totais.

## Comandos e evidências

- No diretório `projeto-dashboard`, executei exatamente `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **17 testes, 0 falhas, OK**, em 11,311 s. A saída detalhada mostrou os testes de Firefox real e: `window request=390px; innerWidth móvel real=500px; altura mínima DOMRect por SVG/classe=18px` para cada classe presente em ambos os gráficos. Evidência: saída do terminal; teste reproduzível em `tests/test_tester_validation.py`.
- Fiz uma verificação avulsa adicional com Firefox/Marionette sobre o site servido pela própria configuração de teste, reduzindo no DOM o contêiner para 370 px e medindo SVG/textos; resultado registrado acima. Não salvei script nem alterei produto/testes.
- Recálculo independente executado no Python do ambiente, diretamente sobre o CSV limpo; resultados numéricos acima. Não foi criado arquivo de evidência adicional.

## Limitação e pendências

O Firefox disponível não entrega `innerWidth=390` apesar de solicitar janela de 390 px; a suíte mede 500 px, ainda dentro do breakpoint móvel de 520 px. Para não tratar a solicitação como prova de 390 px, também medi a largura de contêiner de 370 px correspondente ao layout de conteúdo esperado em viewport de 390 px e confirmei textos legíveis no Firefox real. **Não resta pendência obrigatória**: o breakpoint móvel foi exercitado, a largura efetiva equivalente conferida e os critérios restantes foram cobertos. A limitação de viewport exato deve continuar explícita em evidências futuras; não afirmo que `innerWidth=390` tenha sido testado.

## Status

**APROVADO — Revisor, rodada 02.** A correção de legibilidade foi verificada independentemente em largura de conteúdo equivalente a 390 px, o teclado cobre cidade e categoria, os cálculos conciliam e a suíte completa passou nesta versão identificada pelos hashes acima.
