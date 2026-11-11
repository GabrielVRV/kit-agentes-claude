"""Lembra os projetos que você já adicionou ao painel."""

from pathlib import Path

from painel.infraestrutura.json_config import gravar_json, ler_json

CHAVE_PROJETOS = "projetos"


class ListaProjetos:
    def __init__(self, arquivo: Path) -> None:
        self._arquivo = arquivo

    def todos(self) -> list[Path]:
        return [Path(p) for p in ler_json(self._arquivo).get(CHAVE_PROJETOS, [])]

    def adicionar(self, pasta: Path) -> None:
        projetos = self.todos()
        if pasta not in projetos:
            self._salvar([*projetos, pasta])

    def remover(self, pasta: Path) -> None:
        self._salvar([p for p in self.todos() if p != pasta])

    def _salvar(self, projetos: list[Path]) -> None:
        gravar_json(self._arquivo, {CHAVE_PROJETOS: [str(p) for p in projetos]})
