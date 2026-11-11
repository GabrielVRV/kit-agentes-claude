"""Aba "Meu usuário": o que do kit está em ~/.claude e o maestro como padrão global."""

import tkinter as tk
from tkinter import messagebox, ttk

from painel.aplicacao.instalacao_global import InstalacaoGlobal
from painel.aplicacao.maestro_padrao import NOME_AGENTE_MAESTRO, definir_maestro, maestro_ativo
from painel.dominio.modelos import Estado, Situacao
from painel.interface.comum import (
    AVISO_REABRIR,
    COR_DO_ESTADO,
    TITULO,
    com_aviso_de_erro,
    lista_em_texto,
)

COLUNAS = (("item", "Item", 430), ("tipo", "Tipo", 110), ("estado", "Estado", 120))
TEXTO_MAESTRO = (
    "Ligado, toda sessão nova já abre com o maestro (Opus), até para perguntas pequenas. "
    "Para ligar só em um projeto, use a aba Projetos."
)


class AbaUsuario(ttk.Frame):
    def __init__(self, pai, instalacao: InstalacaoGlobal, registrar) -> None:
        super().__init__(pai, padding=12)
        self._instalacao = instalacao
        self._registrar = registrar
        self._situacoes: list[Situacao] = []
        self._maestro = tk.BooleanVar()
        self._resumo = tk.StringVar()
        self._montar()
        self.recarregar()

    def _montar(self) -> None:
        ttk.Label(self, textvariable=self._resumo).pack(anchor="w", pady=(0, 6))

        self._tabela = ttk.Treeview(
            self, columns=[c[0] for c in COLUNAS], show="headings", height=12, selectmode="none"
        )
        for chave, titulo, largura in COLUNAS:
            self._tabela.heading(chave, text=titulo, anchor="w")
            self._tabela.column(chave, width=largura, anchor="w")
        for estado, cor in COR_DO_ESTADO.items():
            self._tabela.tag_configure(estado.name, foreground=cor)
        self._tabela.pack(fill="both", expand=True)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=8)
        ttk.Button(botoes, text="Instalar / atualizar tudo", command=self._instalar_tudo).pack(side="left")
        ttk.Button(botoes, text="Remover os que sobram", command=self._remover_sobras).pack(side="left", padx=8)
        ttk.Button(botoes, text="Reler", command=self.recarregar).pack(side="right")

        quadro = ttk.LabelFrame(self, text="Maestro como padrão", padding=10)
        quadro.pack(fill="x")
        ttk.Checkbutton(
            quadro,
            text="Usar o maestro em todas as sessões",
            variable=self._maestro,
            command=self._alternar_maestro,
        ).pack(anchor="w")
        ttk.Label(quadro, text=TEXTO_MAESTRO, wraplength=780, foreground="#57606a").pack(anchor="w")

    @com_aviso_de_erro
    def recarregar(self) -> None:
        self._situacoes = self._instalacao.situacoes()
        self._tabela.delete(*self._tabela.get_children())
        for situacao in self._situacoes:
            item = situacao.item
            self._tabela.insert(
                "", "end",
                values=(item.nome, item.tipo.value, situacao.estado.value),
                tags=(situacao.estado.name,),
            )
        pendentes = sum(1 for s in self._situacoes if s.estado is not Estado.INSTALADO)
        self._resumo.set("Tudo em dia." if not pendentes else f"{pendentes} item(ns) pedem atenção.")
        self._maestro.set(maestro_ativo(self._instalacao.arquivo_settings))

    @com_aviso_de_erro
    def _instalar_tudo(self) -> None:
        if not any(s.pendente for s in self._situacoes):
            messagebox.showinfo(TITULO, "Nada para instalar ou atualizar.")
            return
        sobrescritos = [s.item.nome for s in self._situacoes if s.estado is Estado.DESATUALIZADO]
        if sobrescritos and not messagebox.askyesno(
            TITULO,
            "Estes itens estão diferentes do kit e serão substituídos pela versão do kit:\n\n"
            f"{lista_em_texto(sobrescritos)}\n\n"
            "A versão atual de cada um vai para a pasta de backup. Continuar?",
        ):
            return
        feitos, pasta_backup = self._instalacao.aplicar(self._situacoes)
        self._registrar(f"Instalados ou atualizados: {', '.join(feitos)}.")
        if pasta_backup.exists():
            self._registrar(f"Backup das versões anteriores em {pasta_backup}")
        self._registrar(AVISO_REABRIR)
        self.recarregar()

    @com_aviso_de_erro
    def _remover_sobras(self) -> None:
        sobras = [s.item.nome for s in self._situacoes if s.estado is Estado.SOBRANDO]
        if not sobras:
            messagebox.showinfo(TITULO, "Não há agentes sobrando no seu usuário.")
            return
        if not messagebox.askyesno(
            TITULO,
            "Estes agentes de stack estão no seu usuário e carregam em todo projeto:\n\n"
            f"{lista_em_texto(sobras)}\n\n"
            "O kit os instala por projeto (aba Projetos). Se você remover daqui antes de "
            "instalar nos projetos, eles deixam de existir neles. Uma cópia vai para o backup. "
            "Remover?",
        ):
            return
        removidos, pasta_backup = self._instalacao.remover_sobras(self._situacoes)
        self._registrar(f"Removidos do usuário: {', '.join(removidos)}. Backup em {pasta_backup}")
        self.recarregar()

    def _alternar_maestro(self) -> None:
        self._gravar_maestro()
        # Reler do disco garante que a caixa mostre o que ficou gravado, mesmo após erro.
        self.recarregar()

    @com_aviso_de_erro
    def _gravar_maestro(self) -> None:
        ligar = self._maestro.get()
        maestro_faltando = any(
            s.item.nome == NOME_AGENTE_MAESTRO and s.estado is Estado.FALTANDO
            for s in self._situacoes
        )
        if ligar and maestro_faltando:
            messagebox.showwarning(TITULO, "Instale o kit antes: o agente maestro ainda não está no seu usuário.")
            return
        definir_maestro(self._instalacao.arquivo_settings, ligar)
        self._registrar(
            ("Maestro ligado" if ligar else "Maestro desligado") + f" para todas as sessões. {AVISO_REABRIR}"
        )
