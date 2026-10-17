# Relatório do Tester — rodada 04

## Versão testada

Sem Git. SHA-256 dos arquivos efetivamente testados:

| Arquivo | SHA-256 |
|---|---|
| `preparar_dados.py` | `68827E0FDD001F80C1143E63B4325F5A5360681BCAF904464C4B6552A061214F` |
| `README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |
| `site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `site/login.css` | `E77DC9F29FC8FF06A8BE3823AF8798FA3736F81E65DFD9F5E1A7B7DBDE6BB9A3` |
| `site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `site/estilos.css` | `DA869561BF07814F370A3B962698640C4854825EE661470B24A22900A3109AD0` |
| `site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `tests/test_dashboard.py` | `4454DDDC01CBFBE66B1C6CB3C208EDA52993E61E66EDD83FD713AAE927537974` |
| `tests/test_tester_validation.py` | `86AFCFF657186178BB232D021731586C192DACAE1AEB45828516B48C2388E14F` |

## Cobertura e evidências

- Adicionados `TestWcagColorMath.test_known_wcag_srgb_pairs` e `TestIndependentFirefox.test_wcag_aa_normal_text_contrast_on_login_and_dashboard`. A função implementa luminância relativa WCAG sRGB e razão `(Lmaior + 0,05)/(Lmenor + 0,05)`. Pares de referência conferidos: preto/branco = 21:1; `#767676`/branco ≈ 4,5422:1; `#777777`/branco < 4,5:1.
- No Firefox real, as cores foreground computadas e o fundo opaco efetivo (subindo os ancestrais DOM quando necessário) foram medidos para 88 amostras visíveis de texto normal: aviso e destaque demonstrativos, rodapé e textos/labels/placeholders do login; descrições dos gráficos, notas e rótulos dos KPIs, resumo, rodapé, placeholder da busca, labels, campos, botões, cabeçalhos/células da tabela, paginação, textos SVG e empty state. Limite estrito mantido: **>=4,5:1**.
- A nova verificação falhou inicialmente nas quatro combinações de login relatadas pelo Revisor: aviso 4,463:1; rodapé 3,022:1; placeholders de usuário e senha 2,956:1 cada. Esse resultado foi encaminhado ao Construtor. Após a atualização dos estilos, a medição direcionada passou: **88 amostras, menor razão 5,332:1, zero violações**. A regra mínima não foi reduzida.
- `python -m unittest discover -s tests -k wcag_aa_normal_text_contrast -k known_wcag_srgb_pairs -v` — **2 testes, OK** na versão corrigida.
- Comando completo final, em `projeto-dashboard`: `..\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **26 testes, 0 falhas**, 18,709 s. Permaneceram executando os 24 testes anteriores da rodada 03, além dos dois novos testes de contraste; a saída confirma dados/preservação, HTTP, Firefox, login/rotas, busca, datas, ordenação, paginação, CSV e impressão.

## Limitações de evidência

- Firefox real: janela solicitada de 390 px resulta em `innerWidth=500px`; o breakpoint móvel foi medido nessa largura, sem alegar viewport CSS de 390 px.
- O CSV foi validado pelo Blob real e pela tentativa de download; não foi persistido em disco nesta configuração. Impressão foi validada por `window.print()` e CSS de impressão, não por PDF salvo.
- O login segue sendo demonstrativo e público, não uma barreira de segurança.

## Problemas e encaminhamentos

Nenhuma violação de contraste permaneceu na versão testada; nenhum encaminhamento pendente ao Construtor.

## Status

**APROVADO — Tester, rodada 04.**
