"""Conceitos do painel: o que é um item do kit e em que estado ele está."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Impressão digital do conteúdo: caminho relativo do arquivo -> hash.
Impressoes = dict[str, str]


class Estado(Enum):
    INSTALADO = "Instalado"
    DESATUALIZADO = "Desatualizado"
    FALTANDO = "Faltando"
    SOBRANDO = "Sobrando"


class Tipo(Enum):
    AGENTE = "Agente"
    SKILL = "Skill"
    REGRAS = "Regras"
    CONFIGURACAO = "Configuração"
    HOOK = "Hook"


@dataclass(frozen=True)
class ItemKit:
    nome: str
    tipo: Tipo
    origem: Path | None  # None quando o item só existe no destino (sobrando)
    destino: Path


@dataclass(frozen=True)
class Situacao:
    item: ItemKit
    estado: Estado

    @property
    def pendente(self) -> bool:
        return self.estado in (Estado.FALTANDO, Estado.DESATUALIZADO)


def estado_por_conteudo(origem: Impressoes, destino: Impressoes) -> Estado:
    """Compara pelo conteúdo, não pela data: copiar um arquivo muda a data sem mudar nada."""
    if not destino:
        return Estado.FALTANDO
    # Arquivos a mais no destino não contam: podem ser coisas suas, fora do kit.
    em_dia = all(destino.get(caminho) == marca for caminho, marca in origem.items())
    return Estado.INSTALADO if em_dia else Estado.DESATUALIZADO
