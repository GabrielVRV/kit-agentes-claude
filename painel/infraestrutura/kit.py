"""Onde está o kit e onde fica cada parte dele."""

import sys
from pathlib import Path

NOME_PASTA_KIT = "claude-global"


class Kit:
    def __init__(self, raiz: Path, embutido: bool = False) -> None:
        self.raiz = raiz
        self.embutido = embutido
        self.regras = raiz / "CLAUDE.md"
        self.settings_exemplo = raiz / "settings.exemplo.json"
        self._pasta_iniciar = raiz / "skills" / "iniciar-projeto"
        self.hook_commit = self._pasta_iniciar / "modelos" / "commit-msg"

    def agentes_globais(self) -> list[Path]:
        return sorted((self.raiz / "agents").glob("*.md"))

    def agentes_de_stack(self) -> list[Path]:
        return sorted((self._pasta_iniciar / "agentes").glob("*.md"))

    def skills(self) -> list[Path]:
        return sorted(p for p in (self.raiz / "skills").iterdir() if p.is_dir())


def localizar_kit() -> Kit | None:
    """Uma pasta do kit ao lado do programa vence a cópia embutida no executável.

    Assim dá para atualizar o kit em outro PC só trocando a pasta, sem gerar o .exe de novo.
    """
    if getattr(sys, "frozen", False):
        ao_lado = Path(sys.executable).parent / NOME_PASTA_KIT
        if ao_lado.is_dir():
            return Kit(ao_lado)
        embutida = Path(getattr(sys, "_MEIPASS", "")) / NOME_PASTA_KIT
        return Kit(embutida, embutido=True) if embutida.is_dir() else None
    # Rodando pelo código-fonte: painel/infraestrutura/kit.py -> raiz do repositório.
    pasta = Path(__file__).resolve().parents[2] / NOME_PASTA_KIT
    return Kit(pasta) if pasta.is_dir() else None
