# Relatório do Revisor — rodada 03

## Versão examinada

Sem Git. SHA-256 recalculados da versão revisada (após a execução dos testes):

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `projeto-dashboard/site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `projeto-dashboard/site/login.css` | `6065561C3A531572CA4FE51255B0135F5F68AA61C009C7FC139BF6BD21C99E35` |
| `projeto-dashboard/site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `projeto-dashboard/site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `projeto-dashboard/site/estilos.css` | `C3F5B2BA5AE507558F0B07D4D1C30DD7B954D3B02BC9129B8D760DCEA06701ED` |
| `projeto-dashboard/site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `projeto-dashboard/tests/test_tester_validation.py` | `5DACC5CE6D809AB7C09A574A8A078D5A57FA6AE27BC37E251B9DF5D82E9CE881` |

Os hashes do produto e dos testes coincidem com os relatórios de Construtor e Tester da rodada 03.

## O que revisei

- Li os relatórios de revisão das rodadas 01 e 02, os relatórios de Construtor e Tester da rodada 03, README, preparação, produto e testes atuais. As correções anteriores de SVG responsivo e uso por teclado permanecem no código/testes.
- Recalculei com Python padrão (`csv` + `Decimal`) diretamente de `papelaria_limpa.csv`, usando quantidade × preço unitário: 180 linhas/IDs, 548 unidades e 2.005.900 centavos (R$ 20.059,00). Categorias: Acessórios 1.051.700, Livros 743.800, Papelaria 210.400 centavos; cidades: Campinas 857.800, Santos 693.750, Sorocaba 454.350 centavos; meses: jan/2026 623.500, fev/2026 618.100 e mar/2026 764.300 centavos. Os agregados conciliam com o total e com o JSON. Ticket médio independente: R$ 111,438…; arredondado a centavos, R$ 111,44. Também confirmei 182 linhas no original e duas duplicatas exatas, contra 180 linhas na cópia limpa/JSON.
- Revisei busca sem distinção de acentos, datas inclusivas e intervalo inválido, atualização dos KPIs/gráficos/tabela, ordenação estável, paginação e reset, CSV de todos os resultados filtrados (não só página visível) e impressão da tabela filtrada completa. Código e testes cobrem esses fluxos, inclusive ordenação de todas as nove colunas e cenários combinados. O escopo e a definição de venda/valor bruto continuam documentados; não encontrei divergências metodológicas ou aritméticas.
- A autenticação está corretamente descrita como demonstração pública, não como segurança: credenciais aparecem no HTML/JS, os dados estáticos são acessíveis e a marca em `sessionStorage` é contornável. README e página de login dizem para não usar isso para dados privados e indicam backend para autenticação real. Não encontrei alegação de proteção real.
- **Defeito de acessibilidade: contraste de textos abaixo de WCAG AA.** Recalculei a razão de contraste pela fórmula de luminância relativa WCAG a partir das cores e fundos declarados nos CSS. Para texto normal, a referência AA é 4,5:1. Exemplos reproduzíveis: painel, `--ink-faint #738696` sobre branco (`#fff`) = **3,76:1**, usado em descrições dos gráficos e notas dos indicadores; placeholder do painel `#8797a3` sobre branco = **3,01:1**. Na tela de login, placeholder `#8797a1` sobre `#fcfdfd` = **2,96:1**; texto do aviso de demonstração `#687a84` sobre branco = **4,46:1**; rodapé `#82919a` sobre `#f5f7f8` = **3,02:1**. São textos informativos/auxiliares legíveis visualmente, mas não atingem contraste AA para texto normal. A suíte atual não calcula contraste, logo os 24 testes passam sem cobrir essa falha.

## Comando e evidências

- Em `projeto-dashboard`, executei `..\.venv\Scripts\python.exe -m unittest discover -s tests -v`: **24 testes, 0 falhas**, em 17,621 s. Firefox headless real foi executado; a saída inclui busca, datas, login/rotas, ordenação, paginação, exportação CSV, impressão, HTTP e cálculos. Os testes do CSV leram o Blob real, mas o Firefox não salvou o arquivo no diretório de downloads nesta execução. Impressão foi verificada pela chamada `window.print()` e pelas regras CSS, não por um PDF persistido.
- A saída móvel informa janela solicitada de 390 px e `innerWidth=500px`. O painel permanece sob o breakpoint móvel (560 px); os textos SVG medidos tiveram altura mínima de DOMRect 18 px. **Não afirmo medição de viewport CSS de 390 px literal.** O teste valida a largura disponível de 500 px desta instalação, não a de 390 px.
- Recalculei hashes SHA-256 no Python após os testes e os resultados numéricos acima por código independente do preparador. O cálculo de contraste foi conferido por script Python avulso, usando os valores CSS identificados; nenhum arquivo de produto ou teste foi alterado.

## Problemas e encaminhamentos

1. **Construtor — corrigir contraste de texto.** Escurecer cores de texto auxiliar e placeholders no painel e no login, incluindo aviso/rodapé da tela de entrada, para alcançar no mínimo 4,5:1 sobre os fundos efetivos (ou ajustar fundo e cor em conjunto), preservando foco e estados. Recalcular cada combinação após a alteração.
2. **Tester — acrescentar cobertura objetiva de contraste.** Validar combinações foreground/background efetivamente usadas para texto normal na tela de login e no painel, incluindo placeholders, texto auxiliar, aviso demonstrativo e rodapé; não basta medir font-size. Retestar após correção do Construtor.

Limitações explicitamente observadas: o mecanismo de login não autentica nem protege dados; o browser desta instalação não entrega `innerWidth=390`; o teste valida CSV pelo Blob quando não há arquivo em disco, e impressão pelo acionamento/CSS, não por arquivo PDF gerado. A publicação/servidor não transforma o login estático em proteção.

## Pendências

- Contraste AA nos textos listados: **PENDENTE de correção pelo Construtor e reteste**.
- Teste automatizado de contraste: **PENDENTE para o Tester**.
- A viewport exata de 390 px, persistência do download CSV em disco e artefato PDF não foram verificados; permanecem limitações de evidência/ambiente, não alegações aprovadas nesta revisão.

## Status

**REPROVADO — Revisor, rodada 03.** A suíte completa passou e os números estão corretos, mas há falhas objetivas de contraste acessível não cobertas pelos testes. Encaminhei correção ao Construtor e nova cobertura ao Tester; esta versão não está aprovada para entrega final.
