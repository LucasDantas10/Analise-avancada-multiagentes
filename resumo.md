# Análise e tratamento — `vendas_papelaria.csv`

## Visão geral

- **Original preservado:** `vendas_papelaria.csv` não foi alterado.
- **Granularidade:** uma linha por venda; `id_venda` identifica a venda.
- **Original:** 182 linhas e 8 colunas.
- **Cópia tratada:** 180 linhas e 9 colunas, incluindo `valor_venda`.
- **Período observado:** 2026-01-01 a 2026-03-31.
- **Colunas:** identificador (`id_venda`), data (`data`), dimensões (`cidade`, `categoria`, `produto`, `forma_pagamento`), métricas de origem (`quantidade`, `preco_unitario`) e métrica derivada (`valor_venda`).

## Problemas encontrados

- **Duplicatas exatas:** 2 linhas excedentes, uma repetição de `V0010` e outra de `V0020`. Não havia IDs associados a registros distintos conflitantes.
- **Espaços extras:** 6 valores de `cidade` tinham espaços no início ou no fim.
- **Categoria inconsistente:** `acessórios` aparecia 3 vezes em minúsculas, em vez de `Acessórios`.
- **Pagamento vazio:** 4 células em `forma_pagamento` estavam vazias.
- **Outras verificações:** não foram encontrados campos vazios nas demais colunas, datas inválidas, valores não numéricos nem quantidades ou preços negativos.

## Tratamento aplicado

1. Removidas apenas duplicatas exatas da linha inteira; não foi feita deduplicação somente por `id_venda`.
2. Removidos espaços no início e no fim de `cidade`.
3. Categorias padronizadas para `Livros`, `Papelaria` e `Acessórios`.
4. Pagamentos vazios preenchidos com `Não informado`.
5. Adicionada `valor_venda`, calculada como `quantidade × preco_unitario` com precisão decimal.

Após o tratamento, há **180 vendas** (180 `id_venda` distintos) e 548 unidades vendidas. As categorias têm 54 vendas de `Livros`, 61 de `Papelaria` e 65 de `Acessórios`. O total de `valor_venda` na cópia é **R$ 20.059,00**. Esse valor representa vendas brutas calculadas a partir de quantidade × preço unitário, **não lucro** (custos e despesas não foram considerados). O resultado está em `papelaria_limpa.csv`; os demais campos de origem foram mantidos.
