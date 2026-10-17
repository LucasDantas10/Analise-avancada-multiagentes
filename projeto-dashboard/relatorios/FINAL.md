# Relatório final — Dashboard de vendas da papelaria

## Status conjunto: **APROVADO**

Construtor, Tester e Revisor aprovaram a versão final identificada na rodada 05. O histórico das rodadas anteriores foi preservado em `projeto-dashboard/relatorios/`.

## Entrega

- Login demonstrativo na página inicial e painel de vendas separado em `/vendas/`.
- Painel responsivo com quatro indicadores (valor vendido, quantidade de vendas, ticket médio e unidades), dois gráficos e tabela.
- Funções: busca por texto, filtros por cidade/categoria/período, ordenação, paginação, exportação CSV dos resultados filtrados, impressão/Salvar como PDF e limpar filtros.
- Paleta verificada por contraste WCAG AA: 88 amostras de texto computadas passaram, com mínimo de **5,332:1** para o limite de 4,5:1.
- Base: 180 vendas, 548 unidades, R$ 20.059,00 em valor bruto vendido e ticket médio de R$ 111,44. Valor vendido não é lucro. Originais e resultados anteriores preservados.

## Versão final

Não há Git neste workspace; os hashes SHA-256 identificam a mesma versão aprovada por Construtor, Tester e Revisor:

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

## Verificações e limitações

- Suíte completa executada pelo Tester, Revisor e coordenador: **26 testes, 0 falhas**, incluindo Firefox real, HTTP, rotas/login, busca, datas, ordenação, paginação, CSV, impressão, responsividade e contraste.
- Totais e agregações recalculados independentemente; hashes confirmados antes e depois dos testes. Contrastes reprovados na rodada 03 foram corrigidos e recalculados na rodada 05.
- Firefox disponível informa `innerWidth=500px` quando se solicita uma janela de 390 px; não se afirma que a viewport CSS exata de 390 px foi medida.
- CSV foi conferido pelo Blob real, mas não persistido na pasta de downloads. Impressão e CSS para impressão foram verificados, mas nenhum PDF foi salvo como evidência.
- Credenciais demonstrativas: **admin / papelaria2026**. Como o site é estático, credenciais e JSON são públicos e `sessionStorage` pode ser contornado. O login não protege dados privados; autenticação real requer backend. Essa limitação está documentada na tela e no README.

Relatórios de aprovação final: `rodada-05/construtor.md`, `rodada-05/tester.md` e `rodada-05/revisor.md`.

## Como preparar, testar e abrir

No PowerShell do VS Code, entre em `projeto-dashboard` e execute:

```powershell
& ..\.venv\Scripts\python.exe .\preparar_dados.py
& ..\.venv\Scripts\python.exe -m unittest discover -s tests -v
& ..\.venv\Scripts\python.exe -m http.server 8000 --directory site
```

Abra <http://localhost:8000> e entre com `admin` / `papelaria2026`. A pasta publicável é `projeto-dashboard/site/`; publicação não faz parte desta etapa.
