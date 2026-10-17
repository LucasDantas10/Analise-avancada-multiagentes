# Relatório do Tester — rodada 03

## Versão testada

Sem Git; hashes SHA-256 dos arquivos efetivamente testados:

| Arquivo | SHA-256 |
|---|---|
| `preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `site/login.css` | `6065561C3A531572CA4FE51255B0135F5F68AA61C009C7FC139BF6BD21C99E35` |
| `site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `site/estilos.css` | `C3F5B2BA5AE507558F0B07D4D1C30DD7B954D3B02BC9129B8D760DCEA06701ED` |
| `site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `tests/test_tester_validation.py` | `5DACC5CE6D809AB7C09A574A8A078D5A57FA6AE27BC37E251B9DF5D82E9CE881` |

## Cobertura verificada

- Suite anterior preservada: origem e resultados prévios, schema/tipos/nulos/duplicatas, recálculo independente e fixture conhecido, KPIs/gráficos/tabela, filtros, vazio/limpar, HTTP, JavaScript, teclado e responsividade. A tabela completa é conferida escolhendo “Todas”; labels e rota foram atualizados ao novo formulário e a `/vendas/`.
- Firefox real + HTTP: login em `/`, senha incorreta com alerta sem navegar, credenciais demo válidas para `/vendas/`, guarda da rota sem sessão e Sair limpando a sessão e voltando ao login. A autenticação é conveniência demonstrativa, não é tratada como segurança.
- Busca parcial pelos cinco campos textuais e datas inicial/final/combinadas: KPIs, gráficos e todas as páginas da tabela conferidos contra os dados. Ordenação em ambas as direções para as nove chaves; páginas 1/2, tamanhos e reset completo verificados.
- Exportação: o Firefox acionou o link `.csv`; o arquivo foi conferido no Blob real do produto (IDs de todos os filtrados, mesmo exportando a partir da página 2, e soma dos valores igual ao total independente). O Firefox desta configuração não persistiu o arquivo no diretório de downloads; o conteúdo do Blob e a tentativa de download foram verificáveis.
- Impressão: botão acionou `window.print()` no Firefox e regras `@media print` carregadas foram conferidas, incluindo ocultação dos filtros e exibição da tabela de impressão.
- Correção do Construtor confirmada no navegador: fonte computada de `#filtro-cidade` e demais controles de filtro é 16 px, acima do mínimo preservado de 14 px.

## Comandos e evidências

- Comando final solicitado, em `projeto-dashboard`: `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **24 testes, 0 falhas**, 17,610 s. A saída lista todos os testes anteriores e novos; incluiu Firefox headless real e os estados de login/rotas, busca, datas, ordenação, paginação, CSV e impressão.
- Também passaram antes da execução final: `python -m unittest discover -s tests -p test_tester_validation.py -k partial_search -k date_filters -k pagination_page_sizes -k each_sort_button -k csv_export -k print_button -v` (6 testes) e `python -m unittest discover -s tests -k test_http_carrega_site_scripts_css_e_json -k demo_login_error_success_route_guard_logout_and_relogin -v` (3 testes).
- Uma execução completa anterior ao resultado final encontrou dois seletores de layout antigos (`.campos-filtro`) que já não existem após o redesenho. Os testes foram atualizados para `.grade-filtros`, mantendo a checagem de empilhamento; a suíte completa foi então executada novamente e passou.
- Limitações registradas: Firefox aceita janela solicitada de 390 px, mas entrega `innerWidth=500px`; o breakpoint móvel é exercitado nessa largura. A exportação foi validada pelo Blob do Firefox, sem arquivo persistido no diretório de downloads. Não se declara viewport CSS de 390 px nem arquivo baixado em disco.

## Problemas e encaminhamentos

Não há falhas reproduzíveis pendentes no produto. Nenhum encaminhamento ao Construtor.

## Status

**APROVADO — Tester, rodada 03.**
