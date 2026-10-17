# Relatório do Tester — rodada 05

## Versão testada e hashes verificados

Sem Git. Recalculei SHA-256 imediatamente antes e depois da suíte completa; os hashes coincidiram. Esta é a versão efetivamente executada:

| Arquivo | SHA-256 |
|---|---|
| `preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `site/login.css` | `E77DC9F29FC8FF06A8BE3823AF8798FA3736F81E65DFD9F5E1A7B7DBDE6BB9A3` |
| `site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `site/estilos.css` | `196AE086A120B144C44D553559BA57CC1B25DB53AFDFF7263B1F32C488FE0A13` |
| `site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `tests/test_tester_validation.py` | `86AFCFF657186178BB232D021731586C192DACAE1AEB45828516B48C2388E14F` |

## Resultados

- Comando completo, executado em `projeto-dashboard`: `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **26 testes, 0 falhas**, 18,137 s. Todos os 24 testes da rodada 03 e os dois novos testes WCAG foram executados.
- `TestWcagColorMath` confere os pares conhecidos: preto/branco = 21:1, `#767676`/branco ≈ 4,5422:1 e `#777777`/branco <4,5:1.
- Firefox real mediu foreground/background computados para **88 amostras visíveis** de texto normal no login e no painel. Todas passaram **>=4,5:1**; a menor razão observada foi **5,332:1**. Incluídos aviso/rodapé/placeholders de login, textos auxiliares, gráficos, KPIs, controls, tabela, paginação e empty state. A suíte imprime `count=88`, `minimum=5.332`, `failures=[]`.
- O teste WCAG foi executado antes da correção e reproduziu as quatro violações de login: aviso **4,463:1**, rodapé **3,022:1** e placeholders de usuário/senha **2,956:1** cada. Na versão acima corrigida, o teste e a suíte completa passaram; o limite de 4,5:1 não foi alterado.
- Também passaram os fluxos anteriores: preservação e cálculos independentes; HTTP e erros JS; login demonstrativo/rotas; busca, datas e filtros; ordenação nas nove chaves; paginação/reset; CSV filtrado e impressão; responsividade e acessibilidade.

## Limitações

- Firefox headless real limita `innerWidth` a 500 px mesmo com janela solicitada de 390 px; o breakpoint móvel é exercitado nessa largura, sem afirmar viewport CSS de 390 px literal.
- A exportação foi validada pelo Blob real e pelo link `.csv`; o arquivo não foi persistido no diretório de downloads nesta configuração. Impressão foi verificada pelo acionamento de `window.print()` e pelas regras CSS, não por PDF salvo.
- O login permanece explicitamente demonstrativo, não uma medida de segurança.
- O relatório da rodada 04 foi preservado; não houve edição do produto.

## Problemas e encaminhamentos

Nenhuma falha de contraste ou de fluxo reproduzida na versão testada. Nenhum encaminhamento pendente ao Construtor.

## Status

**APROVADO — Tester, rodada 05.**
