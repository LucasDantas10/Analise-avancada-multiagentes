"""Gera gráficos de valor vendido por categoria e por cidade."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


PASTA = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA / "papelaria_limpa.csv"


def formatar_reais(valor: float, casas: int = 2) -> str:
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    numero = f"{valor:,.{casas}f}"
    numero = numero.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {numero}"


def criar_grafico_barras(
    resumo: pd.Series, titulo: str, dimensao: str, destino: Path
) -> None:
    resumo = resumo.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    barras = ax.bar(resumo.index, resumo.values, color="#4C72B0", width=0.65)

    ax.set_title(titulo, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(dimensao)
    ax.set_ylabel("Valor vendido (R$)")
    ax.set_ylim(bottom=0, top=max(resumo.values) * 1.18)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda valor, _: formatar_reais(valor, casas=0))
    )
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, valor in zip(barras, resumo.values):
        ax.annotate(
            formatar_reais(valor),
            (barra.get_x() + barra.get_width() / 2, barra.get_height()),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.text(0.01, 0.01, "Fonte: papelaria_limpa.csv", fontsize=9, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(destino, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    dados = pd.read_csv(ARQUIVO_CSV)
    dados["valor_venda"] = pd.to_numeric(dados["valor_venda"], errors="raise")

    por_categoria = dados.groupby("categoria")["valor_venda"].sum()
    por_cidade = dados.groupby("cidade")["valor_venda"].sum()

    criar_grafico_barras(
        por_categoria,
        "Valor total vendido por categoria",
        "Categoria",
        PASTA / "categorias.png",
    )
    criar_grafico_barras(
        por_cidade,
        "Valor total vendido por cidade",
        "Cidade",
        PASTA / "cidades.png",
    )

    print("Totais por categoria (R$):")
    print(por_categoria.sort_values(ascending=False).to_string())
    print("\nTotais por cidade (R$):")
    print(por_cidade.sort_values(ascending=False).to_string())
    print("\nGráficos salvos em categorias.png e cidades.png")


if __name__ == "__main__":
    main()
