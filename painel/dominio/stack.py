"""Quais agentes de stack um projeto precisa (mesma regra da skill iniciar-projeto)."""

from dataclasses import dataclass

AGENTE_ABL_API = "implementador-abl"
AGENTE_ABL_PROGRAMA = "implementador-abl-programa"
AGENTE_PYTHON = "implementador-python"
AGENTE_REACT = "implementador-react"
AGENTE_CONFERIDOR = "conferidor-visual"


@dataclass(frozen=True)
class SinaisProjeto:
    tem_abl: bool = False
    tem_react: bool = False
    tem_python_web: bool = False
    tem_front_web: bool = False


def agentes_sugeridos(sinais: SinaisProjeto) -> set[str]:
    sugeridos: set[str] = set()
    if sinais.tem_react:
        sugeridos.add(AGENTE_REACT)
    if sinais.tem_python_web:
        sugeridos.add(AGENTE_PYTHON)
    if sinais.tem_front_web:
        sugeridos.add(AGENTE_CONFERIDOR)
    # ABL sem React fica sem sugestão: API e programa direto usam agentes
    # diferentes e os arquivos não dizem qual é o caso.
    if sinais.tem_abl and sinais.tem_react:
        sugeridos.add(AGENTE_ABL_API)
    return sugeridos


def descricao_da_stack(sinais: SinaisProjeto) -> str:
    partes = [
        nome
        for nome, presente in (
            ("Progress ABL", sinais.tem_abl),
            ("React", sinais.tem_react),
            ("Python web", sinais.tem_python_web),
            ("front web", sinais.tem_front_web and not sinais.tem_react),
        )
        if presente
    ]
    if not partes:
        return (
            "Nenhuma stack detectada. O implementador-geral, que já fica no seu "
            "usuário, cobre este projeto."
        )
    texto = "Detectado: " + ", ".join(partes) + "."
    if sinais.tem_abl and not sinais.tem_react:
        texto += (
            f" ABL sem front React: marque {AGENTE_ABL_API} se for API para outro "
            f"sistema consumir, ou {AGENTE_ABL_PROGRAMA} se for tela .w, batch ou Datasul."
        )
    return texto
