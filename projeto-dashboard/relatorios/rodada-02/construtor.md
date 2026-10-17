# Construtor — rodada 02

## Versão examinada

Sem Git. Hashes SHA-256 dos artefatos relevantes desta versão:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/site/index.html` | `980B34C00181ADD2C2606722AB4688013FC52BC12A540F5F204BB9823C2B0EC0` |
| `projeto-dashboard/site/estilos.css` | `61C7EA5C6ED975DD986537CE8851C5FEF898229481DC27BAB355D8C5CBC24C84` |
| `projeto-dashboard/site/app.js` | `069097BF5F4EB3B7BDF14A9BC4C1D45086902F1812FCF33DFD776F731E7C66BF` |
| `projeto-dashboard/README.md` | `310A78D53A8330D9FEB45320854DC24480216DA016443F9CB9586D8A80127667` |

## Correção

- **Item 1 do Revisor:** SVGs agora definem o `viewBox` pelas dimensões CSS efetivas, em escala 1:1, e redesenham ao redimensionar. Tipografia de eixos, categorias e valores permanece em 12 px renderizados também em telas estreitas. Eixos usam valores monetários abreviados onde necessário; rótulos dos dados mantêm os valores integrais para preservar precisão e validação. Rótulos dos gráficos ganharam descrições acessíveis com seus valores. Corrigido ainda o posicionamento dos valores das barras para não saírem da área do SVG.
- Alterados apenas `site/app.js` e `site/estilos.css`; CSVs, dados preparados, HTML, script de preparo, README, testes e relatórios de outras funções não foram editados.

## Comandos e resultados

- `node --check .\projeto-dashboard\site\app.js` — **OK**.
- `& .\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py` — **OK**; 180 vendas, 548 unidades, R$ 20.059,00. SHA do JSON permaneceu igual.
- Recalculei hashes antes/depois do preparo para `vendas_papelaria.csv`, `papelaria_limpa.csv`, `resumo.md`, `verificacao.md`, `graficos.py`, `categorias.png` e `cidades.png` — **OK**, os sete foram preservados.
- Firefox headless real via Marionette (servidor HTTP local): após estreitar o conteúdo para 370 px — largura correspondente ao conteúdo em viewport de 390 px — os SVGs mediram 339,2 × 220 px. Medi cada rótulo com `getScreenCTM()`; tamanho renderizado mínimo **12 px**, todos dentro do SVG, sem erro JavaScript. Valores mensais foram conferidos sem abreviação: R$ 6.235,00, R$ 6.181,00 e R$ 7.643,00. O conteúdo permaneceu dentro da largura simulada.
- Limitação da medição: Firefox desta instalação restringe `SetWindowRect` a viewport CSS mínima de 500 px. Portanto, não foi possível medir `documentElement.clientWidth == 390` diretamente. A geometria do conteúdo em 370 px (viewport de 390 menos margens responsivas) foi medida no Firefox real; o Tester deve repetir a suíte e conferir a viewport móvel na configuração disponível.
- Suíte completa do Tester após esta alteração: **PENDENTE**, para execução pelo Tester sobre os hashes acima. Testes não foram modificados nem declarados aprovados.

## Encaminhamento e status

**APROVADO — correção do item 1 pelo Construtor.** Tester: executar a suíte completa nesta versão, verificar novamente o tamanho/legibilidade dos textos do SVG em viewport pequeno e teclado nos dois filtros. Retornar ao Construtor se encontrar regressão. Aprovação conjunta permanece pendente.
