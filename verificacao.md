# Verificação da análise de vendas da papelaria

## Resultado geral

**A análise está correta para compartilhar, com a ressalva de que valor vendido não é lucro.** Conferi os arquivos locais `vendas_papelaria.csv`, `papelaria_limpa.csv`, `resumo.md` e `graficos.py`. Recalculei os valores a partir de `quantidade × preco_unitario`, sem usar `valor_venda` como fonte do recálculo.

## Contagem e total recalculados

| Base | Linhas/registros | `id_venda` distintos | Total vendido recalculado |
|---|---:|---:|---:|
| Original, incluindo repetições | 182 | 180 | R$ 20.066,00 |
| Cópia limpa | 180 | 180 | R$ 20.059,00 |

O original contém duas repetições exatas (`V0010` e `V0020`). Cada uma soma R$ 3,50; removê-las reduz o total em R$ 7,00. Na cópia limpa há 180 linhas para 180 vendas distintas. A soma de `quantidade` nessa cópia é **548 unidades** — diferente da contagem de vendas.

## Conferências de agregação

Valores recalculados da cópia limpa, em reais:

| Categoria | Valor vendido |
|---|---:|
| Acessórios | R$ 10.517,00 |
| Livros | R$ 7.438,00 |
| Papelaria | R$ 2.104,00 |
| **Soma das categorias** | **R$ 20.059,00** |

A soma das categorias coincide exatamente com o total geral recalculado de R$ 20.059,00.

| Cidade | Valor vendido |
|---|---:|
| Campinas | R$ 8.578,00 |
| Santos | R$ 6.937,50 |
| Sorocaba | R$ 4.543,50 |
| **Soma das cidades** | **R$ 20.059,00** |

A soma por cidade também coincide com o total geral. Além disso, confirmei que os 180 `valor_venda` da cópia correspondem a `quantidade × preco_unitario` e que a cópia corresponde ao tratamento descrito no resumo.

## Código e conclusões

- `graficos.py` lê `papelaria_limpa.csv` a partir da pasta do próprio script, converte `valor_venda` para número e agrega essa coluna por `categoria` e `cidade`. Portanto, usa a base e o campo corretos para os gráficos.
- Reexecutei o script com `.venv/Scripts/python.exe`; ele gerou `categorias.png` e `cidades.png` com os totais acima.
- Os gráficos usam barras com eixo iniciado em zero e títulos/unidades coerentes com valor vendido.
- As conclusões comparativas estão corretas: Acessórios tem o maior valor entre as categorias e Campinas entre as cidades. Esses números descrevem **valor bruto vendido**, não lucro; não há dados de custos ou despesas nesta análise.

## Ajuste documental

Não encontrei divergências numéricas na análise ou no código. Para deixar a leitura menos ambígua, atualizei o último parágrafo de `resumo.md` para explicitar as 180 vendas distintas, as 548 unidades, a moeda e que o total vendido não é lucro.

**Escopo/limitação:** a verificação foi feita exclusivamente com os arquivos locais fornecidos; não houve comparação com fonte financeira ou externa.
