# Construtor — rodada 04

## Versão examinada

Sem Git. SHA-256 da versão atual:

| Arquivo | SHA-256 |
|---|---|
| `projeto-dashboard/site/estilos.css` | `196AE086A120B144C44D553559BA57CC1B25DB53AFDFF7263B1F32C488FE0A13` |
| `projeto-dashboard/site/login.css` | `E77DC9F29FC8FF06A8BE3823AF8798FA3736F81E65DFD9F5E1A7B7DBDE6BB9A3` |
| `projeto-dashboard/site/index.html` | `0AE3AA80E64D7A53F69C70046759B92A8C1F793D40CFE1A5E943AE26C84072B8` |
| `projeto-dashboard/site/vendas/index.html` | `141C4413B76065393B132AEDC7319B880F1776C4996E4DBA07E79E53C20F6515` |
| `projeto-dashboard/site/app.js` | `1288B5E804A84C189B3478D6B33231D7199B72A101848AF5FE30A70C1547DAAF` |
| `projeto-dashboard/site/login.js` | `055D65C1FEE21004D3D0F3E4C10B3317A07D9FB6591793FD2B4F5D6CD749106D` |
| `projeto-dashboard/site/dados/vendas.json` | `C69E64860F7B75F1935C51382A2832C8421D1E4FD5BAB5CC18A26D0BDA2FDAD1` |
| `projeto-dashboard/README.md` | `BD4098D12BA8A0E7BC02DA301EA394FDEBB4A0D6D6D649A242DE8E7EE219970B` |

## Correção e cálculos WCAG AA

Corrigi somente `site/estilos.css` e `site/login.css`. A cor auxiliar foi escurecida para `#526779`, os textos sobre gradientes foram clareados onde necessário, e controles desabilitados deixaram de reduzir a opacidade do texto. Placeholders agora definem cor explícita e opacidade 1. Login, credencial demonstrativa, recursos, rotas e dados foram preservados.

Razão de contraste calculada pela luminância relativa sRGB da fórmula WCAG, com fundos efetivos (incluindo superfícies claras, gradientes e sobreposições alfa). Conferi **80 pares** de foreground/background:

| Texto/contexto | Antes | Depois |
|---|---:|---:|
| Auxiliar do painel `#738696` → `#526779`, sobre branco | 3,76:1 | **5,87:1** |
| Placeholder do painel `#8797a3` → `#526779`, sobre branco | 3,01:1 | **5,87:1** |
| Placeholder do login `#8797a1` → `#526779`, sobre `#fcfdfd` | 2,96:1 | **5,76:1** |
| Aviso demo `#687a84` → `#526779`, sobre branco | 4,46:1 | **5,87:1** |
| Rodapé do login `#82919a` → `#526779`, sobre `#f5f7f8` | 3,02:1 | **5,47:1** |

Também conferi as demais combinações de texto normal: rótulos de campos, indicadores, cabeçalhos/células da tabela, mensagens, erros, notas, SVG, botões inativos, aviso/credenciais do login e texto de impressão. Todos os pares atingiram **≥4,5:1**. O menor foi **4,70:1** (`#0f7775` em `#e5f3ef`, acento/ícone do login); o menor dos auxiliares sobre fundos claros foi **5,21:1** (texto `#526779` no botão desabilitado sobre `#eef2f4`). O realce radial mais exigente ficou em **4,87:1** (`#c1ebdb` sobre `#206a68`).

## Comandos e evidências

- Recalculo independente em Python com a fórmula WCAG sRGB — **76 combinações, mínimo 4,87:1**, assertions de mínimo 4,5:1 aprovadas. Incluídos os cinco exemplos do Revisor e as superfícies claras/estados translúcidos; os valores antigos reproduziram 3,76:1, 3,01:1, 2,96:1, 4,46:1 e 3,02:1.
- Firefox headless real serviu login (`/`, `login.css`, `login.js`) e dashboard (`/vendas/`, `estilos.css`, `app.js`, `dados/vendas.json`) por HTTP. `getComputedStyle` confirmou as cores computadas dos placeholders e textos auxiliares; exemplos: placeholder login `rgb(82,103,121)` sobre `rgb(252,253,253)`, aviso demo `rgb(82,103,121)` sobre branco, placeholder painel `rgb(82,103,121)` sobre branco e nota `rgb(76,98,110)` sobre `rgb(237,245,243)`. As razões coincidem com os cálculos acima.
- `node --check .\projeto-dashboard\site\app.js` e `node --check .\projeto-dashboard\site\login.js` — **OK**; JavaScript não foi alterado nesta rodada.
- `& .\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py` — **OK**: 180 vendas, 548 unidades, R$ 20.059,00. Hash do JSON inalterado. Os sete arquivos originais/resultados prévios (`vendas_papelaria.csv`, `papelaria_limpa.csv`, `resumo.md`, `verificacao.md`, `graficos.py`, `categorias.png`, `cidades.png`) tiveram hashes conferidos antes/depois e foram preservados.
- Suíte completa e teste automatizado de contraste: **PENDENTES**; não alterei testes. Revisor e Tester devem validar esta versão.

## Encaminhamento e status

**APROVADO — correção local de contraste pelo Construtor; reteste necessário.** Tester: acrescentar/conferir contraste calculado para placeholders, auxiliares, aviso demo, rodapés, gradientes e estados desabilitados, e reexecutar a suíte completa. Revisor: validar as combinações efetivas e os mesmos hashes. Isto não é aprovação final conjunta.
