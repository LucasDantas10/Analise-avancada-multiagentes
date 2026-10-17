# Construtor — rodada 03

## Versão examinada

Sem Git; SHA-256 da versão entregue (sem alterações nos testes):

| Arquivo | SHA-256 |
|---|---|
| `preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `site/index.html` (login) | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `site/login.css` | `6065561C3A531572CA4FE51255B0135F5F68AA61C009C7FC139BF6BD21C99E35` |
| `site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `site/estilos.css` | `C3F5B2BA5AE507558F0B07D4D1C30DD7B954D3B02BC9129B8D760DCEA06701ED` |
| `site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |

## Alterações e contrato

- Modernizei a identidade visual do painel e da tela de entrada, com layout responsivo e sem dependências externas; acrescentei KPI de unidades.
- A rota raiz `site/index.html` agora é o login; após credenciais válidas, navega para `site/vendas/`. Essa página exige a marca `papelaria-demo-auth=ok` em `sessionStorage` antes de exibir o painel; “Sair” remove a marca e retorna à raiz. Credenciais públicas de demonstração: `admin` / `papelaria2026`.
- A autenticação é somente demonstrativa, **não oferece segurança**: credencial e JSON são públicos em site estático. O README documenta a necessidade de backend para dados privados.
- O dashboard preserva busca por texto, datas inclusivas, filtros de cidade/categoria, ordenação acessível nas nove colunas, paginação/tamanho de página, exportação CSV de todos os filtrados e impressão/PDF com tabela completa da seleção. Busca/filtros atualizam KPIs, gráficos e tabela; ordenar/paginar altera somente a tabela.
- IDs acordados com o Tester mantidos: `busca-venda`, `data-inicio`, `data-fim`, `registros-por-pagina`, `pagina-anterior`, `pagina-proxima`, `pagina-atual`, `exportar-csv`, `imprimir-painel`, mais os filtros/KPIs existentes. Ordenação segue `button[data-ordenar]` com as nove chaves acordadas. CSS/JS do painel usam caminhos `../`; o JSON permanece em `site/dados/vendas.json`.
- Corrigi o achado do Tester: campos de filtro, busca, datas e tamanho de página agora calculam 16 px (`1rem`), acima do mínimo 14 px; o critério não foi reduzido.
- Não editei testes, relatórios do Tester/Revisor nem `FINAL.md`. CSVs e resultados anteriores preservados.

## Comandos e resultados

- `node --check .\projeto-dashboard\site\app.js` e `node --check .\projeto-dashboard\site\login.js` — **OK**.
- `& .\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py` — **OK**: 180 vendas, 548 unidades, R$ 20.059,00. SHA-256 do JSON continua igual.
- Conferência de hashes antes/depois do preparo para `vendas_papelaria.csv`, `papelaria_limpa.csv`, `resumo.md`, `verificacao.md`, `graficos.py`, `categorias.png` e `cidades.png` — **OK**, sem alteração.
- Firefox headless real: fluxo anterior confirmou login incorreto com mensagem, login `admin`/`papelaria2026` para `/vendas/`, carregamento de 180 vendas/548 unidades, Sair limpando a marca e redirecionamento de rota direta sem sessão.
- Firefox headless após correção do Tester: `getComputedStyle` mediu `#filtro-cidade` **16 px**, `#filtro-categoria` **16 px** e `#registros-por-pagina` **16 px**. Sem overflow horizontal (`scrollWidth == clientWidth == 500 px`). O Firefox deste ambiente limita a viewport solicitada de 390 px a 500 px; não afirmo que `innerWidth=390` foi medido.
- O relatório do Tester registra, na versão imediatamente anterior a este ajuste tipográfico, 6 testes direcionados de funcionalidades e 3 verificações de rota/login aprovados; também registra o Blob CSV completo lido no Firefox. O único achado encaminhado foi o tamanho 13,4375 px, corrigido aqui para 16 px. **A suíte completa após esta correção permanece PENDENTE**, a ser reexecutada pelo Tester com estes hashes.

## Encaminhamento e status

**APROVADO — entrega do Construtor para reteste.** Tester: repetir a suíte completa (`python -m unittest discover -s tests -v`) nesta versão, em especial a asserção de fonte mínima 14 px, rotas/autenticação, recursos HTTP e os testes de filtros, ordenação, paginação, CSV e impressão. Não considerar esta aprovação do Construtor como aprovação final; a suíte e a revisão final continuam pendentes.
