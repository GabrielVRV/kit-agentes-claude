"""Lê na pasta de um projeto os sinais que indicam a stack."""

import json
import os
from pathlib import Path

from painel.dominio.stack import SinaisProjeto

# Pastas grandes e sem código do projeto: pular evita varrer milhares de arquivos.
PASTAS_PULADAS = {".git", ".claude", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
PROFUNDIDADE_MAXIMA = 4
EXTENSOES_ABL = {".p", ".w", ".i", ".cls"}
ARQUIVOS_PYTHON = {"pyproject.toml", "requirements.txt"}
FRAMEWORKS_PYTHON = ("fastapi", "flask", "django")
CHAVES_DE_DEPENDENCIA = ("dependencies", "devDependencies")


def _dependencias_npm(arquivo: Path) -> set[str]:
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return set()
    if not isinstance(dados, dict):
        return set()
    nomes: set[str] = set()
    for chave in CHAVES_DE_DEPENDENCIA:
        bloco = dados.get(chave)
        if isinstance(bloco, dict):
            nomes.update(bloco)
    return nomes


def _usa_framework_python(arquivo: Path) -> bool:
    try:
        texto = arquivo.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    return any(nome in texto for nome in FRAMEWORKS_PYTHON)


def ler_sinais(pasta: Path) -> SinaisProjeto:
    tem_abl = tem_react = tem_angular = tem_python = tem_html = False
    for atual, subpastas, arquivos in os.walk(pasta):
        profundidade = len(Path(atual).relative_to(pasta).parts)
        # Alterar a lista no lugar é o que faz o os.walk não descer nas pastas removidas.
        subpastas[:] = (
            []
            if profundidade >= PROFUNDIDADE_MAXIMA
            else [nome for nome in subpastas if nome not in PASTAS_PULADAS]
        )
        for nome in arquivos:
            arquivo = Path(atual) / nome
            if arquivo.suffix.lower() in EXTENSOES_ABL:
                tem_abl = True
            elif nome == "package.json":
                dependencias = _dependencias_npm(arquivo)
                tem_react = tem_react or "react" in dependencias
                tem_angular = tem_angular or any(
                    d == "angular" or d.startswith("@angular/") for d in dependencias
                )
            elif nome in ARQUIVOS_PYTHON:
                tem_python = tem_python or _usa_framework_python(arquivo)
            elif nome.lower() == "index.html":
                tem_html = True
    return SinaisProjeto(
        tem_abl=tem_abl,
        tem_react=tem_react,
        tem_python_web=tem_python,
        tem_front_web=tem_react or tem_angular or tem_html,
    )
