# Dashboard de vendas da papelaria

Site estático em português com uma tela de login demonstrativa e um painel para explorar as vendas de janeiro a março de 2026. O painel inclui busca, filtros de cidade/categoria/período, indicadores, gráficos, tabela ordenável e paginada, exportação CSV e impressão/Salvar como PDF. Requer Python com `pandas` instalado (o ambiente recomendado do projeto já contém pandas).

## Preparar os dados

No PowerShell do VS Code, entre na pasta `projeto-dashboard` e execute:

```powershell
& ..\.venv\Scripts\python.exe .\preparar_dados.py
```

O script lê `papelaria_limpa.csv` na pasta principal, valida colunas, identificadores, tipos e a conta quantidade × preço, e grava `site/dados/vendas.json`. Ele não modifica nem limpa novamente o CSV.

## Executar os testes

Depois que a suíte do Tester estiver em `tests/`, execute na pasta `projeto-dashboard`:

```powershell
& ..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Abrir o site localmente

Na pasta `projeto-dashboard`, inicie um servidor HTTP:

```powershell
& ..\.venv\Scripts\python.exe -m http.server 8000 --directory site
```

Abra <http://localhost:8000> no navegador. Entre com o usuário **`admin`** e senha **`papelaria2026`** para abrir o painel em `/vendas/`. “Sair” encerra a sessão demonstrativa e volta à página inicial. Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`. Não abra as páginas HTML diretamente: o navegador precisa carregar arquivos e JSON por HTTP.

## Publicação estática

A pasta publicável é `site/`. Execute o preparo antes de publicar, para que `site/dados/vendas.json` esteja presente. Não é necessário servidor de aplicação nem banco de dados.

## Definições e limites

- Cada linha é uma venda, identificada por `id_venda`; a quantidade de vendas conta linhas/IDs, enquanto unidades vendidas é a soma de `quantidade`.
- Valor vendido é a soma de `valor_venda` (quantidade × preço unitário). É valor bruto, não lucro; custos e despesas não estão na base.
- Ticket médio = valor vendido ÷ número de vendas. Com filtros sem resultados, o painel mostra zero sem divisão por zero e informa que não há registros.
- A busca procura texto em ID, produto, cidade, categoria e forma de pagamento. Datas inicial/final são inclusivas; os dois filtros afetam KPIs, gráficos e tabela.
- Ordenar os cabeçalhos e mudar o tamanho da página afeta somente a tabela. O CSV inclui todas as vendas que correspondem aos filtros, não apenas a página visível. “Imprimir / PDF” prepara a tabela completa filtrada para impressão ou para Salvar como PDF no diálogo do navegador.
- “Limpar tudo” remove busca e filtros de cidade, categoria e data e volta à primeira página. O painel inclui também o indicador de unidades vendidas, separado da quantidade de vendas.
- A base limpa herdou o tratamento documentado em `resumo.md`: foram removidas apenas duas duplicatas exatas, aparados espaços em `cidade`, padronizadas categorias e preenchidos quatro pagamentos vazios como “Não informado”. Este projeto não reaplica essas regras nem altera os arquivos de origem.
- A análise cobre somente os registros disponíveis entre 2026-01-01 e 2026-03-31; não permite concluir sobre custos, lucro ou períodos fora desse intervalo.

## Acesso demonstrativo — importante

A credencial de demonstração `admin` / `papelaria2026` está no JavaScript público do site e também é exibida na tela de login. A marca de acesso usa apenas `sessionStorage` no navegador e serve para demonstrar a navegação, **não é autenticação nem proteção real**. Qualquer pessoa pode ler o código/JSON ou contornar a tela de login. Não publique dados privados com este mecanismo; para restringir acesso de verdade, é necessário um backend que autentique usuários e autorize as requisições aos dados.
