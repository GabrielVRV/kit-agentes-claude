"""Peças usadas pelas duas abas: cores dos estados, textos e tratamento de erro."""

import functools
from tkinter import messagebox

from painel.dominio.modelos import Estado
from painel.infraestrutura.json_config import ErroConfiguracao

TITULO = "Kit de agentes do Claude"
AVISO_REABRIR = "Feche e abra a sessão do Claude para ele carregar as mudanças."

COR_DO_ESTADO = {
    Estado.INSTALADO: "#1a7f37",
    Estado.DESATUALIZADO: "#9a6700",
    Estado.FALTANDO: "#cf222e",
    Estado.SOBRANDO: "#6e7781",
}


def com_aviso_de_erro(metodo):
    """Mostra o erro numa caixa em vez de derrubar a janela ou sumir no console."""

    @functools.wraps(metodo)
    def protegido(self, *args, **kwargs):
        try:
            return metodo(self, *args, **kwargs)
        except (OSError, ErroConfiguracao) as erro:
            messagebox.showerror(TITULO, str(erro))
            return None

    return protegido


def lista_em_texto(nomes: list[str]) -> str:
    return "\n".join(f"  • {nome}" for nome in nomes)
