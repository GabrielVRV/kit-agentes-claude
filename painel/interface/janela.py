"""Janela principal: monta as abas e liga cada uma aos casos de uso."""

import ctypes
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

from painel.aplicacao.instalacao_global import InstalacaoGlobal
from painel.aplicacao.lista_projetos import ListaProjetos
from painel.infraestrutura.kit import Kit, localizar_kit
from painel.interface.aba_projetos import AbaProjetos
from painel.interface.aba_usuario import AbaUsuario
from painel.interface.comum import TITULO

TAMANHO_INICIAL = "900x700"
TAMANHO_MINIMO = (780, 600)
LINHAS_DO_DIARIO = 6
VARIAVEL_PASTA_CLAUDE = "CLAUDE_CONFIG_DIR"
NOME_PASTA_BACKUP = "backups-kit-agentes"
NOME_PASTA_PREFERENCIAS = "kit-agentes-claude"
CAMINHO_DO_ICONE = Path("painel") / "recursos" / "icone.ico"
ID_DO_APLICATIVO = "GabrielVRV.KitAgentesClaude"


def _pasta_claude() -> Path:
    # O Claude Code aceita essa variável para trocar a pasta de configuração.
    return Path(os.environ.get(VARIAVEL_PASTA_CLAUDE) or Path.home() / ".claude")


def _arquivo_de_projetos() -> Path:
    base = Path(os.environ.get("APPDATA") or Path.home())
    return base / NOME_PASTA_PREFERENCIAS / "projetos.json"


def _texto_da_origem(kit: Kit) -> str:
    if not kit.embutido:
        return f"Kit lido de: {kit.raiz}"
    gerado = datetime.fromtimestamp(Path(sys.executable).stat().st_mtime)
    return f"Kit embutido neste executável (gerado em {gerado:%d/%m/%Y %H:%M})"


def _caminho_do_icone() -> Path:
    # No executável os recursos são extraídos para a pasta temporária do PyInstaller.
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / CAMINHO_DO_ICONE


def _identificar_na_barra_de_tarefas() -> None:
    """Sem um id próprio, o Windows agrupa a janela com o Python e mostra o ícone dele."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ID_DO_APLICATIVO)
    except (AttributeError, OSError):
        pass


def _aplicar_icone(raiz: tk.Tk) -> None:
    icone = _caminho_do_icone()
    if not icone.exists():
        return
    try:
        raiz.iconbitmap(default=str(icone))
    except tk.TclError:
        pass  # Ícone é enfeite: se o sistema recusar o arquivo, a janela abre com o padrão.


def _deixar_nitido_em_tela_de_alta_resolucao() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass  # Fora do Windows ou em Windows antigo: a janela só fica menos nítida.


class Diario(ttk.Frame):
    """Registro do que o painel fez, para você não depender de lembrar."""

    def __init__(self, pai) -> None:
        super().__init__(pai, padding=(12, 0, 12, 12))
        self._texto = tk.Text(self, height=LINHAS_DO_DIARIO, state="disabled", wrap="word", relief="flat")
        self._texto.pack(fill="both", expand=True)

    def registrar(self, mensagem: str) -> None:
        self._texto.configure(state="normal")
        self._texto.insert("end", f"{datetime.now():%H:%M:%S}  {mensagem}\n")
        self._texto.see("end")
        self._texto.configure(state="disabled")


def montar_janela(raiz: tk.Tk, kit: Kit, pasta_claude: Path, arquivo_projetos: Path) -> None:
    base_backup = pasta_claude / NOME_PASTA_BACKUP
    ttk.Label(raiz, text=_texto_da_origem(kit), padding=(12, 10, 12, 4)).pack(anchor="w")

    diario = Diario(raiz)
    abas = ttk.Notebook(raiz)
    instalacao = InstalacaoGlobal(kit, pasta_claude, base_backup)
    abas.add(AbaUsuario(abas, instalacao, diario.registrar), text="Meu usuário")
    abas.add(
        AbaProjetos(abas, kit, ListaProjetos(arquivo_projetos), base_backup, diario.registrar),
        text="Projetos",
    )
    abas.pack(fill="both", expand=True, padx=12, pady=(0, 8))
    diario.pack(fill="x")


def iniciar() -> None:
    _deixar_nitido_em_tela_de_alta_resolucao()
    _identificar_na_barra_de_tarefas()
    raiz = tk.Tk()
    raiz.title(TITULO)
    _aplicar_icone(raiz)
    kit = localizar_kit()
    if kit is None:
        raiz.withdraw()
        messagebox.showerror(TITULO, "Não encontrei a pasta claude-global do kit ao lado do programa.")
        return
    raiz.geometry(TAMANHO_INICIAL)
    raiz.minsize(*TAMANHO_MINIMO)
    montar_janela(raiz, kit, _pasta_claude(), _arquivo_de_projetos())
    raiz.mainloop()
