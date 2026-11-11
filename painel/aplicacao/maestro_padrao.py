"""Liga e desliga o maestro como agente principal das sessões."""

from pathlib import Path

from painel.dominio.configuracao import CHAVE_AGENTE_PADRAO, com_agente_padrao
from painel.infraestrutura.json_config import gravar_json, ler_json

NOME_AGENTE_MAESTRO = "maestro"


def maestro_ativo(arquivo_settings: Path) -> bool:
    return ler_json(arquivo_settings).get(CHAVE_AGENTE_PADRAO) == NOME_AGENTE_MAESTRO


def definir_maestro(arquivo_settings: Path, ativo: bool) -> None:
    atual = ler_json(arquivo_settings)
    if not ativo and CHAVE_AGENTE_PADRAO not in atual:
        return  # Evita criar um settings vazio só para "desligar" o que já está desligado.
    gravar_json(arquivo_settings, com_agente_padrao(atual, NOME_AGENTE_MAESTRO if ativo else None))
