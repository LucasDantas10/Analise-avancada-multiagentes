"""Valida o CSV já tratado e exporta os dados estáticos usados pelo dashboard."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_FONTE = PASTA_PROJETO.parent / "papelaria_limpa.csv"
ARQUIVO_SAIDA = PASTA_PROJETO / "site" / "dados" / "vendas.json"
COLUNAS = [
    "id_venda",
    "data",
    "cidade",
    "categoria",
    "produto",
    "quantidade",
    "preco_unitario",
    "forma_pagamento",
    "valor_venda",
]


def para_centavos(valor: object, coluna: str, linha: int) -> int:
    """Converte um valor monetário decimal exatamente para centavos."""
    try:
        decimal = Decimal(str(valor))
    except (InvalidOperation, ValueError) as erro:
        raise ValueError(f"Valor inválido em {coluna}, linha {linha}: {valor!r}") from erro
    centavos = decimal * 100
    if not decimal.is_finite() or centavos != centavos.to_integral_value():
        raise ValueError(f"Valor monetário com mais de 2 casas em {coluna}, linha {linha}.")
    return int(centavos)


def preparar_dados() -> dict[str, object]:
    if not ARQUIVO_FONTE.is_file():
        raise FileNotFoundError(f"CSV de entrada não encontrado: {ARQUIVO_FONTE}")

    # Strings na leitura evitam inferência ambígua em identificadores e valores monetários.
    df = pd.read_csv(ARQUIVO_FONTE, dtype=str, keep_default_na=False)
    faltantes = [coluna for coluna in COLUNAS if coluna not in df.columns]
    extras = [coluna for coluna in df.columns if coluna not in COLUNAS]
    if faltantes or extras:
        raise ValueError(f"Colunas inesperadas. Ausentes: {faltantes}; extras: {extras}")
    df = df[COLUNAS]

    if df.empty:
        raise ValueError("O CSV de entrada não contém vendas.")
    if df.isna().any().any() or (df == "").any().any():
        raise ValueError("Há valores ausentes/vazios; revise a base tratada sem alterar o original.")
    if df["id_venda"].duplicated().any():
        raise ValueError("id_venda deve identificar uma venda e não pode se repetir.")

    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="raise")
    for coluna in ("quantidade", "preco_unitario", "valor_venda"):
        df[coluna] = pd.to_numeric(df[coluna], errors="raise")

    if (df["quantidade"] <= 0).any() or (df["quantidade"] % 1 != 0).any():
        raise ValueError("quantidade deve conter inteiros positivos.")
    if (df["preco_unitario"] < 0).any() or (df["valor_venda"] < 0).any():
        raise ValueError("preco_unitario e valor_venda não podem ser negativos.")

    registros: list[dict[str, object]] = []
    for indice, linha in df.iterrows():
        numero_linha = int(indice) + 2  # cabeçalho ocupa a primeira linha do CSV
        quantidade = int(linha["quantidade"])
        preco_centavos = para_centavos(linha["preco_unitario"], "preco_unitario", numero_linha)
        venda_centavos = para_centavos(linha["valor_venda"], "valor_venda", numero_linha)
        if quantidade * preco_centavos != venda_centavos:
            raise ValueError(
                f"valor_venda não corresponde a quantidade × preco_unitario na linha {numero_linha}."
            )
        registros.append(
            {
                "id_venda": linha["id_venda"],
                "data": linha["data"].strftime("%Y-%m-%d"),
                "cidade": linha["cidade"],
                "categoria": linha["categoria"],
                "produto": linha["produto"],
                "quantidade": quantidade,
                "preco_unitario_centavos": preco_centavos,
                "forma_pagamento": linha["forma_pagamento"],
                "valor_venda_centavos": venda_centavos,
            }
        )

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_SAIDA.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    total_centavos = sum(item["valor_venda_centavos"] for item in registros)
    unidades = sum(item["quantidade"] for item in registros)
    print(f"Dados preparados: {len(registros)} vendas, {unidades} unidades.")
    reais = f"{total_centavos // 100:,}".replace(",", ".")
    print(f"Valor total vendido: R$ {reais},{total_centavos % 100:02d}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    return {"vendas": len(registros), "unidades": unidades, "total_centavos": total_centavos}


if __name__ == "__main__":
    preparar_dados()
