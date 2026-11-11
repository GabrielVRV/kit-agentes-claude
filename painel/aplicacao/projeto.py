"""Prepara um projeto: agentes da stack, hook de commit e .gitignore."""

from pathlib import Path

from painel.dominio.configuracao import com_pasta_claude_ignorada, ignora_pasta_claude
from painel.dominio.modelos import ItemKit, Situacao, Tipo, estado_por_conteudo
from painel.dominio.stack import SinaisProjeto
from painel.infraestrutura.arquivos import Backup, copiar, copiar_script_shell, impressoes_de
from painel.infraestrutura.kit import Kit
from painel.infraestrutura.projeto_fs import ler_sinais

NOME_ITEM_HOOK = "Hook de commit (tira co-autor e assinatura de IA)"
NOME_ITEM_GITIGNORE = ".claude/ no .gitignore"


class PreparacaoProjeto:
    def __init__(self, kit: Kit, pasta: Path, base_backup: Path) -> None:
        self._kit = kit
        self.pasta = pasta
        self._base_backup = base_backup
        self._gitignore = pasta / ".gitignore"
        # settings.local.json é o arquivo pessoal do projeto; não mexe no settings do time.
        self.arquivo_settings = pasta / ".claude" / "settings.local.json"

    @property
    def eh_repositorio_git(self) -> bool:
        # Em worktree o .git é um arquivo e os hooks ficam em outro lugar: fica de fora.
        return (self.pasta / ".git").is_dir()

    def sinais(self) -> SinaisProjeto:
        return ler_sinais(self.pasta)

    def situacoes_agentes(self) -> list[Situacao]:
        pasta_agentes = self.pasta / ".claude" / "agents"
        itens = [
            ItemKit(a.stem, Tipo.AGENTE, a, pasta_agentes / a.name)
            for a in self._kit.agentes_de_stack()
        ]
        return [self._situacao(item) for item in itens]

    def situacao_hook(self) -> Situacao:
        destino = self.pasta / ".git" / "hooks" / "commit-msg"
        return self._situacao(ItemKit(NOME_ITEM_HOOK, Tipo.HOOK, self._kit.hook_commit, destino))

    def gitignore_em_dia(self) -> bool:
        return self._gitignore.exists() and ignora_pasta_claude(self._ler_gitignore())

    def aplicar(
        self, agentes: list[Situacao], com_hook: bool, com_gitignore: bool
    ) -> tuple[list[str], Path]:
        backup = Backup(self._base_backup)
        feitos = []
        for situacao in agentes:
            if situacao.pendente:
                backup.guardar(situacao.item.destino)
                copiar(situacao.item.origem, situacao.item.destino)
                feitos.append(situacao.item.nome)
        hook = self.situacao_hook()
        if com_hook and self.eh_repositorio_git and hook.pendente:
            backup.guardar(hook.item.destino)
            copiar_script_shell(hook.item.origem, hook.item.destino)
            feitos.append(NOME_ITEM_HOOK)
        if com_gitignore and self.eh_repositorio_git and not self.gitignore_em_dia():
            self._gravar_gitignore(com_pasta_claude_ignorada(self._ler_gitignore()))
            feitos.append(NOME_ITEM_GITIGNORE)
        return feitos, backup.pasta

    def _situacao(self, item: ItemKit) -> Situacao:
        estado = estado_por_conteudo(impressoes_de(item.origem), impressoes_de(item.destino))
        return Situacao(item, estado)

    def _ler_gitignore(self) -> str:
        if not self._gitignore.exists():
            return ""
        # Bytes na ida e na volta: preserva o fim de linha que o arquivo já usa.
        return self._gitignore.read_bytes().decode("utf-8", errors="replace")

    def _gravar_gitignore(self, texto: str) -> None:
        self._gitignore.write_bytes(texto.encode("utf-8"))
