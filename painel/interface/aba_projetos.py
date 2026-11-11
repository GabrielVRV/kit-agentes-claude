"""Aba "Projetos": agentes da stack, hook de commit, .gitignore e maestro por projeto."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from painel.aplicacao.lista_projetos import ListaProjetos
from painel.aplicacao.maestro_padrao import definir_maestro, maestro_ativo
from painel.aplicacao.projeto import NOME_ITEM_GITIGNORE, NOME_ITEM_HOOK, PreparacaoProjeto
from painel.dominio.modelos import Estado, Situacao
from painel.dominio.stack import agentes_sugeridos, descricao_da_stack
from painel.infraestrutura.kit import Kit
from painel.interface.comum import (
    AVISO_REABRIR,
    COR_DO_ESTADO,
    TITULO,
    com_aviso_de_erro,
    lista_em_texto,
)

LARGURA_TEXTO = 520
COR_TEXTO_APOIO = "#57606a"
TEXTO_SEM_PROJETO = "Adicione a pasta de um projeto e selecione-a na lista."
TEXTO_SEM_GIT = "Esta pasta não é um repositório Git: hook e .gitignore ficam de fora."
TEXTO_MAESTRO = "Ligado, as sessões abertas nesta pasta já começam com o maestro (Opus)."


class AbaProjetos(ttk.Frame):
    def __init__(self, pai, kit: Kit, lista: ListaProjetos, base_backup: Path, registrar) -> None:
        super().__init__(pai, padding=12)
        self._kit = kit
        self._lista = lista
        self._base_backup = base_backup
        self._registrar = registrar
        self._projetos: list[Path] = []
        self._preparacao: PreparacaoProjeto | None = None
        self._situacoes: list[Situacao] = []
        self._marcados: dict[str, tk.BooleanVar] = {}
        self._com_hook = tk.BooleanVar()
        self._com_gitignore = tk.BooleanVar()
        self._maestro = tk.BooleanVar()
        self._montar()
        self._recarregar_lista()

    # ---- montagem ----------------------------------------------------------

    def _montar(self) -> None:
        esquerda = ttk.Frame(self)
        esquerda.pack(side="left", fill="y", padx=(0, 12))
        self._caixa = tk.Listbox(esquerda, width=28, exportselection=False, activestyle="none")
        self._caixa.pack(fill="y", expand=True)
        self._caixa.bind("<<ListboxSelect>>", lambda _evento: self._mostrar_selecionado())
        ttk.Button(esquerda, text="Adicionar pasta...", command=self._adicionar).pack(fill="x", pady=(8, 2))
        ttk.Button(esquerda, text="Tirar da lista", command=self._tirar_da_lista).pack(fill="x")

        self._painel = ttk.Frame(self)
        self._painel.pack(side="left", fill="both", expand=True)
        self._mostrar_vazio()

    def _limpar_painel(self) -> None:
        for filho in self._painel.winfo_children():
            filho.destroy()
        self._preparacao = None

    def _mostrar_vazio(self, texto: str = TEXTO_SEM_PROJETO) -> None:
        self._limpar_painel()
        ttk.Label(self._painel, text=texto, foreground=COR_TEXTO_APOIO).pack(anchor="w")

    @com_aviso_de_erro
    def _mostrar_projeto(self, pasta: Path) -> None:
        if not pasta.is_dir():
            self._mostrar_vazio(f"A pasta {pasta} não existe mais. Tire-a da lista.")
            return
        self._limpar_painel()
        preparacao = PreparacaoProjeto(self._kit, pasta, self._base_backup)
        self._preparacao = preparacao
        sinais = preparacao.sinais()

        ttk.Label(self._painel, text=str(pasta), font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(
            self._painel, text=descricao_da_stack(sinais), wraplength=LARGURA_TEXTO, foreground=COR_TEXTO_APOIO
        ).pack(anchor="w", pady=(2, 8))

        self._montar_agentes(agentes_sugeridos(sinais))
        self._montar_git()
        ttk.Button(self._painel, text="Aplicar no projeto", command=self._aplicar).pack(anchor="w", pady=8)
        self._montar_maestro()

    def _montar_agentes(self, sugeridos: set[str]) -> None:
        quadro = ttk.LabelFrame(self._painel, text="Agentes da stack (marque os que o projeto usa)", padding=10)
        quadro.pack(fill="x")
        self._situacoes = self._preparacao.situacoes_agentes()
        self._marcados = {}
        for linha, situacao in enumerate(self._situacoes):
            nome = situacao.item.nome
            # Já vem marcado o que a stack pede e o que o projeto já tem.
            marcado = tk.BooleanVar(value=nome in sugeridos or situacao.estado is not Estado.FALTANDO)
            self._marcados[nome] = marcado
            ttk.Checkbutton(quadro, text=nome, variable=marcado).grid(row=linha, column=0, sticky="w")
            self._rotulo_estado(quadro, situacao.estado).grid(row=linha, column=1, sticky="w", padx=16)

    def _montar_git(self) -> None:
        quadro = ttk.LabelFrame(self._painel, text="Git", padding=10)
        quadro.pack(fill="x", pady=(8, 0))
        if not self._preparacao.eh_repositorio_git:
            self._com_hook.set(False)
            self._com_gitignore.set(False)
            ttk.Label(quadro, text=TEXTO_SEM_GIT, foreground=COR_TEXTO_APOIO).pack(anchor="w")
            return
        estado_hook = self._preparacao.situacao_hook().estado
        estado_ignore = Estado.INSTALADO if self._preparacao.gitignore_em_dia() else Estado.FALTANDO
        self._com_hook.set(True)
        self._com_gitignore.set(True)
        linhas = ((NOME_ITEM_HOOK, self._com_hook, estado_hook), (NOME_ITEM_GITIGNORE, self._com_gitignore, estado_ignore))
        for linha, (texto, variavel, estado) in enumerate(linhas):
            ttk.Checkbutton(quadro, text=texto, variable=variavel).grid(row=linha, column=0, sticky="w")
            self._rotulo_estado(quadro, estado).grid(row=linha, column=1, sticky="w", padx=16)

    def _montar_maestro(self) -> None:
        quadro = ttk.LabelFrame(self._painel, text="Maestro como padrão neste projeto", padding=10)
        quadro.pack(fill="x")
        self._maestro.set(maestro_ativo(self._preparacao.arquivo_settings))
        ttk.Checkbutton(
            quadro, text="Usar o maestro neste projeto", variable=self._maestro, command=self._alternar_maestro
        ).pack(anchor="w")
        ttk.Label(quadro, text=TEXTO_MAESTRO, wraplength=LARGURA_TEXTO, foreground=COR_TEXTO_APOIO).pack(anchor="w")

    @staticmethod
    def _rotulo_estado(pai, estado: Estado) -> ttk.Label:
        return ttk.Label(pai, text=estado.value, foreground=COR_DO_ESTADO[estado])

    # ---- lista de projetos -------------------------------------------------

    @com_aviso_de_erro
    def _recarregar_lista(self, selecionar: Path | None = None) -> None:
        self._projetos = self._lista.todos()
        self._caixa.delete(0, "end")
        for pasta in self._projetos:
            self._caixa.insert("end", pasta.name or str(pasta))
        if selecionar in self._projetos:
            self._caixa.selection_set(self._projetos.index(selecionar))
        self._mostrar_selecionado()

    def _selecionado(self) -> Path | None:
        indices = self._caixa.curselection()
        return self._projetos[indices[0]] if indices else None

    def _mostrar_selecionado(self) -> None:
        pasta = self._selecionado()
        if pasta is None:
            self._mostrar_vazio()
        else:
            self._mostrar_projeto(pasta)

    @com_aviso_de_erro
    def _adicionar(self) -> None:
        escolhida = filedialog.askdirectory(title="Pasta do projeto")
        if not escolhida:
            return
        pasta = Path(escolhida)
        self._lista.adicionar(pasta)
        self._recarregar_lista(selecionar=pasta)

    @com_aviso_de_erro
    def _tirar_da_lista(self) -> None:
        pasta = self._selecionado()
        if pasta is None:
            return
        # Só some da lista do painel; nada é apagado dentro do projeto.
        self._lista.remover(pasta)
        self._recarregar_lista()

    # ---- ações -------------------------------------------------------------

    @com_aviso_de_erro
    def _aplicar(self) -> None:
        preparacao = self._preparacao
        escolhidos = [s for s in self._situacoes if self._marcados[s.item.nome].get()]
        sobrescritos = [s.item.nome for s in escolhidos if s.estado is Estado.DESATUALIZADO]
        hook_diferente = (
            self._com_hook.get() and preparacao.situacao_hook().estado is Estado.DESATUALIZADO
        )
        if hook_diferente:
            sobrescritos.append("commit-msg (já existe um hook diferente neste repositório)")
        if sobrescritos and not messagebox.askyesno(
            TITULO,
            "Estes arquivos do projeto estão diferentes do kit e serão substituídos:\n\n"
            f"{lista_em_texto(sobrescritos)}\n\n"
            "A versão atual de cada um vai para a pasta de backup. Continuar?",
        ):
            return
        feitos, pasta_backup = preparacao.aplicar(escolhidos, self._com_hook.get(), self._com_gitignore.get())
        nome = preparacao.pasta.name
        if not feitos:
            self._registrar(f"{nome}: nada a fazer, já estava em dia.")
        else:
            self._registrar(f"{nome}: {', '.join(feitos)}. {AVISO_REABRIR}")
        if pasta_backup.exists():
            self._registrar(f"Backup das versões anteriores em {pasta_backup}")
        self._mostrar_projeto(preparacao.pasta)

    def _alternar_maestro(self) -> None:
        preparacao = self._preparacao
        self._gravar_maestro(preparacao)
        # Reler do disco garante que a caixa mostre o que ficou gravado, mesmo após erro.
        self._mostrar_projeto(preparacao.pasta)

    @com_aviso_de_erro
    def _gravar_maestro(self, preparacao: PreparacaoProjeto) -> None:
        ligar = self._maestro.get()
        definir_maestro(preparacao.arquivo_settings, ligar)
        estado = "ligado" if ligar else "desligado"
        self._registrar(f"{preparacao.pasta.name}: maestro {estado}. {AVISO_REABRIR}")
