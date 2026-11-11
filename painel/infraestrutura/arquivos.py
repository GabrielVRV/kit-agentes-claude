"""Leitura de impressões digitais, cópia e backup de arquivos e pastas."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from painel.dominio.modelos import Impressoes

PASTAS_IGNORADAS = ("__pycache__",)
FORMATO_PASTA_BACKUP = "%Y-%m-%d_%H%M%S"


def _impressao(arquivo: Path) -> str:
    # Fim de linha normalizado: o mesmo texto em CRLF e em LF não é "desatualizado".
    conteudo = arquivo.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(conteudo).hexdigest()


def impressoes_de(caminho: Path) -> Impressoes:
    """Aceita arquivo ou pasta; devolve vazio se o caminho não existir."""
    if caminho.is_file():
        return {caminho.name: _impressao(caminho)}
    if not caminho.is_dir():
        return {}
    return {
        arquivo.relative_to(caminho).as_posix(): _impressao(arquivo)
        for arquivo in caminho.rglob("*")
        if arquivo.is_file() and not set(PASTAS_IGNORADAS) & set(arquivo.parts)
    }


def copiar(origem: Path, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origem.is_dir():
        shutil.copytree(
            origem,
            destino,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(*PASTAS_IGNORADAS),
        )
    else:
        shutil.copyfile(origem, destino)


def copiar_script_shell(origem: Path, destino: Path) -> None:
    """Grava com LF: o sh do Git para Windows falha com CRLF na linha do interpretador."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(origem.read_bytes().replace(b"\r\n", b"\n"))


def remover(alvo: Path) -> None:
    if alvo.is_dir():
        shutil.rmtree(alvo)
    elif alvo.exists():
        alvo.unlink()


class Backup:
    """Pasta de backup de uma operação. Só aparece no disco se algo for guardado."""

    def __init__(self, base: Path) -> None:
        self.pasta = base / datetime.now().strftime(FORMATO_PASTA_BACKUP)

    def guardar(self, alvo: Path) -> None:
        if not alvo.exists():
            return
        # A pasta-mãe entra no caminho para "agents/x.md" e "skills/x" não colidirem.
        copia = self.pasta / alvo.parent.name / alvo.name
        copiar(alvo, copia)
