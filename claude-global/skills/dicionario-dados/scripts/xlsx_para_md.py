#!/usr/bin/env python3
"""Converte uma planilha .xlsx em Markdown (uma tabela por aba).

Por que existe: o Claude Code nao le .xlsx diretamente. Convertida, a planilha
do dicionario de dados (campos, tipos, tamanhos, formatos e indices) vira texto
que o agente consegue ler.

Uso:
    python xlsx_para_md.py <planilha.xlsx> [pasta_de_saida]

Saida:
    <nome_da_planilha>.md, na pasta da planilha (ou na pasta de saida informada).

Requisito:
    pip install openpyxl
"""
import sys
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit("Falta a biblioteca openpyxl. Instale com: pip install openpyxl")


def formatar_celula(valor):
    """Converte o valor da celula em texto seguro para uma celula de tabela Markdown."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)  # 10.0 vira 10
    if hasattr(valor, "isoformat"):
        valor = valor.isoformat()  # datas no formato ISO
    texto = str(valor).replace("\r", " ").replace("\n", " ").strip()
    return texto.replace("|", "\\|")  # o pipe separa colunas no Markdown


def ler_linhas(aba):
    """Le as linhas da aba, sem linhas vazias e sem colunas vazias no final."""
    linhas = [[formatar_celula(c) for c in linha] for linha in aba.iter_rows(values_only=True)]
    linhas = [linha for linha in linhas if any(linha)]
    if not linhas:
        return []
    # Largura = posicao da ultima coluna preenchida em qualquer linha.
    largura = max(max(i for i, c in enumerate(linha) if c) for linha in linhas) + 1
    return [(linha + [""] * largura)[:largura] for linha in linhas]


def aba_para_markdown(nome, linhas):
    """Monta o texto Markdown de uma aba: titulo e tabela (a 1a linha vira o cabecalho)."""
    saida = [f"## {nome}", ""]
    if not linhas:
        return saida + ["(aba vazia)", ""]
    cabecalho, corpo = linhas[0], linhas[1:]
    saida.append("| " + " | ".join(cabecalho) + " |")
    saida.append("|" + "|".join([" --- "] * len(cabecalho)) + "|")
    saida.extend("| " + " | ".join(linha) + " |" for linha in corpo)
    saida.append("")
    return saida


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    origem = Path(sys.argv[1])
    if not origem.is_file():
        sys.exit(f"Arquivo nao encontrado: {origem}")
    if origem.suffix.lower() not in (".xlsx", ".xlsm"):
        sys.exit("Use um arquivo .xlsx (no Excel: Salvar como, Pasta de Trabalho do Excel).")
    pasta = Path(sys.argv[2]) if len(sys.argv) > 2 else origem.parent
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / (origem.stem + ".md")

    try:
        # data_only=True traz o valor calculado das formulas, e nao a formula.
        pasta_de_trabalho = load_workbook(origem, data_only=True)
    except Exception as erro:
        sys.exit(f"Nao consegui abrir a planilha: {erro}")

    texto = [f"# {origem.stem}", ""]
    abas = 0
    total_linhas = 0
    for aba in pasta_de_trabalho.worksheets:
        if aba.sheet_state != "visible":
            continue  # ignora abas ocultas
        linhas = ler_linhas(aba)
        texto.extend(aba_para_markdown(aba.title, linhas))
        abas += 1
        total_linhas += len(linhas)

    destino.write_text("\n".join(texto), encoding="utf-8")
    print(f"{destino}: {abas} aba(s), {total_linhas} linha(s) no total")


if __name__ == "__main__":
    main()
