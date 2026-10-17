# Construtor — rodada 05 (alinhamento de versão)

## Versão no disco

Sem Git. Recalculei SHA-256 dos arquivos de produto; `site/estilos.css` atual é **`196AE086A120B144C44D553559BA57CC1B25DB53AFDFF7263B1F32C488FE0A13`**, confirmando o hash do Construtor da rodada 04. Os hashes `DA869...` citados pela coordenação correspondem a uma versão anterior do CSS.

| Artefato | SHA-256 atual |
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

## Correção WCAG identificada

A correção de contraste está nesta versão dos dois CSS; não alterei produto nesta rodada. O histórico da rodada 04 registra o escurecimento dos auxiliares/placeholders e o clareamento dos textos sobre gradientes. Confirmei novamente os pares principais pela fórmula de luminância WCAG sRGB:

| Par atual | Razão |
|---|---:|
| Auxiliar e placeholder do painel `#526779` / `#ffffff` | **5,87:1** |
| Placeholder do login `#526779` / `#fcfdfd` | **5,76:1** |
| Aviso de demonstração `#526779` / `#ffffff` | **5,87:1** |
| Rodapé do login `#526779` / `#f5f7f8` | **5,47:1** |
| Acento teal do painel `#0b706e` / `#e4f3f0` | **5,17:1** |

A folha também mantém as cores de destaque ajustadas para as gradientes. O relatório da rodada 04 contém uma divergência interna de contagem: o resumo diz **80 pares, mínimo 4,70:1**, enquanto a linha de comando diz **76 pares, mínimo 4,87:1**. Recalculei a amostra de foreground/background da versão atual: **80 pares, mínimo 4,70:1**, portanto o resumo concorda com a versão final e o item da linha de comando é evidência anterior/desatualizada. A meta AA de 4,5:1 é atingida na checagem; a validação independente continua com Tester/Revisor.

## Comandos e evidências

- `Get-ChildItem projeto-dashboard\preparar_dados.py, projeto-dashboard\README.md, projeto-dashboard\site -File -Recurse | Get-FileHash -Algorithm SHA256` — **OK**; hashes acima, inclusive CSS `196AE...`.
- Recalculei os seis exemplos prioritários por Python (luminância relativa sRGB); todos ficaram acima de 4,5:1, conforme a tabela.
- Firefox headless serviu a raiz `/`, `/vendas/`, CSS, JavaScript e JSON por HTTP. `getComputedStyle` confirmou as cores renderizadas de placeholders, textos auxiliares, nota e rodapé em ambas as rotas; valores calculados coincidiram com os estilos computados.
- Não alterei CSV, JSON, código, README, testes ou relatórios existentes; nenhum teste foi editado ou executado nesta rodada de alinhamento.

## Status

**APROVADO — alinhamento de versão/hash e confirmação da correção do Construtor.** A suíte completa e a revisão independente não são aprovadas por este relatório e permanecem sob responsabilidade de Tester/Revisor.
