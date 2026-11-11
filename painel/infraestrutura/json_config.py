"""Leitura e gravação dos arquivos JSON de configuração."""

import json
from pathlib import Path


class ErroConfiguracao(Exception):
    """O arquivo existe, mas não dá para alterá-lo com segurança."""


def ler_json(caminho: Path) -> dict:
    if not caminho.exists():
        return {}
    try:
        # utf-8-sig: o PowerShell 5.1 grava com BOM e o json puro rejeitaria o arquivo.
        dados = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as erro:
        raise ErroConfiguracao(
            f"{caminho} não é um JSON válido ({erro}). Corrija o arquivo; nada foi alterado."
        ) from erro
    if not isinstance(dados, dict):
        raise ErroConfiguracao(f"{caminho} não contém um objeto JSON. Nada foi alterado.")
    return dados


def gravar_json(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    caminho.write_text(texto, encoding="utf-8")
