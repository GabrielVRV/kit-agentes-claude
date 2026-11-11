"""Instala e atualiza a parte do kit que fica no seu usuário (~/.claude)."""

from pathlib import Path

from painel.dominio.configuracao import blocos_do_kit_aplicados, com_blocos_do_kit
from painel.dominio.modelos import Estado, ItemKit, Situacao, Tipo, estado_por_conteudo
from painel.infraestrutura.arquivos import Backup, copiar, impressoes_de, remover
from painel.infraestrutura.json_config import gravar_json, ler_json
from painel.infraestrutura.kit import Kit

NOME_ITEM_SETTINGS = "settings.json (commits sem co-autor, bloqueio de .env e chaves)"
NOME_ITEM_REGRAS = "CLAUDE.md (regras pessoais)"


class InstalacaoGlobal:
    def __init__(self, kit: Kit, pasta_claude: Path, base_backup: Path) -> None:
        self._kit = kit
        self._pasta_claude = pasta_claude
        self._base_backup = base_backup
        self.arquivo_settings = pasta_claude / "settings.json"

    def situacoes(self) -> list[Situacao]:
        copiaveis = [
            Situacao(item, estado_por_conteudo(impressoes_de(item.origem), impressoes_de(item.destino)))
            for item in self._itens_copiaveis()
        ]
        return [*copiaveis, self._situacao_settings(), *self._sobras()]

    def aplicar(self, situacoes: list[Situacao]) -> tuple[list[str], Path]:
        """Instala o que falta e atualiza o que mudou. Devolve os nomes e a pasta de backup."""
        backup = Backup(self._base_backup)
        feitos = []
        for situacao in situacoes:
            if not situacao.pendente:
                continue
            item = situacao.item
            backup.guardar(item.destino)
            if item.tipo is Tipo.CONFIGURACAO:
                self._mesclar_settings()
            else:
                copiar(item.origem, item.destino)
            feitos.append(item.nome)
        return feitos, backup.pasta

    def remover_sobras(self, situacoes: list[Situacao]) -> tuple[list[str], Path]:
        backup = Backup(self._base_backup)
        removidos = []
        for situacao in situacoes:
            if situacao.estado is not Estado.SOBRANDO:
                continue
            backup.guardar(situacao.item.destino)
            remover(situacao.item.destino)
            removidos.append(situacao.item.nome)
        return removidos, backup.pasta

    def _itens_copiaveis(self) -> list[ItemKit]:
        pasta_agentes = self._pasta_claude / "agents"
        pasta_skills = self._pasta_claude / "skills"
        itens = [
            ItemKit(a.stem, Tipo.AGENTE, a, pasta_agentes / a.name)
            for a in self._kit.agentes_globais()
        ]
        itens += [
            ItemKit(s.name, Tipo.SKILL, s, pasta_skills / s.name) for s in self._kit.skills()
        ]
        itens.append(
            ItemKit(NOME_ITEM_REGRAS, Tipo.REGRAS, self._kit.regras, self._pasta_claude / "CLAUDE.md")
        )
        return itens

    def _situacao_settings(self) -> Situacao:
        item = ItemKit(
            NOME_ITEM_SETTINGS, Tipo.CONFIGURACAO, self._kit.settings_exemplo, self.arquivo_settings
        )
        if not self.arquivo_settings.exists():
            return Situacao(item, Estado.FALTANDO)
        em_dia = blocos_do_kit_aplicados(
            ler_json(self.arquivo_settings), ler_json(self._kit.settings_exemplo)
        )
        return Situacao(item, Estado.INSTALADO if em_dia else Estado.DESATUALIZADO)

    def _mesclar_settings(self) -> None:
        mesclado = com_blocos_do_kit(
            ler_json(self.arquivo_settings), ler_json(self._kit.settings_exemplo)
        )
        gravar_json(self.arquivo_settings, mesclado)

    def _sobras(self) -> list[Situacao]:
        """Agentes de stack no usuário: o kit os quer por projeto, para não pesar nas outras sessões."""
        pasta_agentes = self._pasta_claude / "agents"
        return [
            Situacao(ItemKit(a.stem, Tipo.AGENTE, None, pasta_agentes / a.name), Estado.SOBRANDO)
            for a in self._kit.agentes_de_stack()
            if (pasta_agentes / a.name).exists()
        ]
