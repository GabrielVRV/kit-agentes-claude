"""Casos de uso contra o kit real, sempre em pastas temporárias (nunca no ~/.claude)."""

import json
import tempfile
import unittest
from pathlib import Path

from painel.aplicacao.instalacao_global import InstalacaoGlobal
from painel.aplicacao.lista_projetos import ListaProjetos
from painel.aplicacao.maestro_padrao import definir_maestro, maestro_ativo
from painel.aplicacao.projeto import PreparacaoProjeto
from painel.dominio.modelos import Estado
from painel.dominio.stack import AGENTE_REACT, agentes_sugeridos
from painel.infraestrutura.json_config import ErroConfiguracao, ler_json
from painel.infraestrutura.kit import localizar_kit


class ComPastaTemporaria(unittest.TestCase):
    def setUp(self):
        temporaria = tempfile.TemporaryDirectory()
        self.addCleanup(temporaria.cleanup)
        self.raiz = Path(temporaria.name)
        self.kit = localizar_kit()
        self.backup = self.raiz / "backups"


class InstalacaoNoUsuario(ComPastaTemporaria):
    def setUp(self):
        super().setUp()
        self.pasta_claude = self.raiz / ".claude"
        self.instalacao = InstalacaoGlobal(self.kit, self.pasta_claude, self.backup)

    def _estados(self):
        return {s.item.nome: s.estado for s in self.instalacao.situacoes()}

    def test_instala_tudo_em_pasta_vazia(self):
        self.assertEqual(set(self._estados().values()), {Estado.FALTANDO})
        self.instalacao.aplicar(self.instalacao.situacoes())
        self.assertEqual(set(self._estados().values()), {Estado.INSTALADO})
        self.assertTrue((self.pasta_claude / "agents" / "maestro.md").exists())
        self.assertFalse(self.backup.exists())  # nada foi sobrescrito

    def test_atualiza_o_que_mudou_e_guarda_backup(self):
        self.instalacao.aplicar(self.instalacao.situacoes())
        maestro = self.pasta_claude / "agents" / "maestro.md"
        maestro.write_text("versão antiga", encoding="utf-8")
        self.assertIs(self._estados()["maestro"], Estado.DESATUALIZADO)
        feitos, pasta_backup = self.instalacao.aplicar(self.instalacao.situacoes())
        self.assertEqual(feitos, ["maestro"])
        self.assertEqual((pasta_backup / "agents" / "maestro.md").read_text(encoding="utf-8"), "versão antiga")
        self.assertIs(self._estados()["maestro"], Estado.INSTALADO)

    def test_mescla_o_settings_sem_perder_chaves(self):
        self.pasta_claude.mkdir()
        settings = self.pasta_claude / "settings.json"
        settings.write_text(json.dumps({"model": "opus"}), encoding="utf-8")
        self.instalacao.aplicar(self.instalacao.situacoes())
        gravado = ler_json(settings)
        self.assertEqual(gravado["model"], "opus")
        self.assertIn("Read(.env)", gravado["permissions"]["deny"])

    def test_agente_de_stack_no_usuario_sobra_e_e_removido_com_backup(self):
        sobra = self.pasta_claude / "agents" / "implementador-react.md"
        sobra.parent.mkdir(parents=True)
        sobra.write_text("antigo", encoding="utf-8")
        self.assertIs(self._estados()["implementador-react"], Estado.SOBRANDO)
        removidos, pasta_backup = self.instalacao.remover_sobras(self.instalacao.situacoes())
        self.assertEqual(removidos, ["implementador-react"])
        self.assertFalse(sobra.exists())
        self.assertTrue((pasta_backup / "agents" / "implementador-react.md").exists())


class Maestro(ComPastaTemporaria):
    def test_liga_e_desliga_preservando_o_resto(self):
        settings = self.raiz / "settings.json"
        settings.write_text(json.dumps({"model": "opus"}), encoding="utf-8")
        definir_maestro(settings, True)
        self.assertTrue(maestro_ativo(settings))
        definir_maestro(settings, False)
        self.assertEqual(ler_json(settings), {"model": "opus"})

    def test_desligar_sem_arquivo_nao_cria_arquivo(self):
        settings = self.raiz / "settings.local.json"
        definir_maestro(settings, False)
        self.assertFalse(settings.exists())

    def test_json_invalido_nao_e_sobrescrito(self):
        settings = self.raiz / "settings.json"
        settings.write_text("{ quebrado", encoding="utf-8")
        with self.assertRaises(ErroConfiguracao):
            definir_maestro(settings, True)
        self.assertEqual(settings.read_text(encoding="utf-8"), "{ quebrado")


class Projeto(ComPastaTemporaria):
    def setUp(self):
        super().setUp()
        self.pasta = self.raiz / "meu-projeto"
        (self.pasta / ".git" / "hooks").mkdir(parents=True)
        (self.pasta / "front").mkdir()
        (self.pasta / "front" / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^18.0.0"}}), encoding="utf-8"
        )
        (self.pasta / ".gitignore").write_bytes(b"node_modules/\r\n")
        self.preparacao = PreparacaoProjeto(self.kit, self.pasta, self.backup)

    def test_detecta_react_em_subpasta(self):
        self.assertIn(AGENTE_REACT, agentes_sugeridos(self.preparacao.sinais()))

    def test_aplica_agentes_hook_e_gitignore(self):
        escolhidos = [s for s in self.preparacao.situacoes_agentes() if s.item.nome == AGENTE_REACT]
        feitos, _ = self.preparacao.aplicar(escolhidos, com_hook=True, com_gitignore=True)
        self.assertEqual(len(feitos), 3)
        self.assertTrue((self.pasta / ".claude" / "agents" / "implementador-react.md").exists())
        self.assertFalse((self.pasta / ".claude" / "agents" / "implementador-abl.md").exists())
        hook = (self.pasta / ".git" / "hooks" / "commit-msg").read_bytes()
        self.assertNotIn(b"\r\n", hook)
        self.assertIs(self.preparacao.situacao_hook().estado, Estado.INSTALADO)
        self.assertEqual((self.pasta / ".gitignore").read_bytes(), b"node_modules/\r\n.claude/\n")
        # Segunda vez não faz nada.
        feitos, _ = self.preparacao.aplicar(self.preparacao.situacoes_agentes()[:0], True, True)
        self.assertEqual(feitos, [])

    def test_hook_diferente_vai_para_o_backup(self):
        hook = self.pasta / ".git" / "hooks" / "commit-msg"
        hook.write_text("#!/bin/sh\necho meu\n", encoding="utf-8")
        _, pasta_backup = self.preparacao.aplicar([], com_hook=True, com_gitignore=False)
        self.assertIn("echo meu", (pasta_backup / "hooks" / "commit-msg").read_text(encoding="utf-8"))

    def test_pasta_sem_git_nao_recebe_hook_nem_gitignore(self):
        pasta = self.raiz / "sem-git"
        pasta.mkdir()
        feitos, _ = PreparacaoProjeto(self.kit, pasta, self.backup).aplicar([], True, True)
        self.assertEqual(feitos, [])
        self.assertFalse((pasta / ".gitignore").exists())


class Lista(ComPastaTemporaria):
    def test_adiciona_sem_repetir_e_remove(self):
        lista = ListaProjetos(self.raiz / "prefs" / "projetos.json")
        lista.adicionar(Path("F:/a"))
        lista.adicionar(Path("F:/a"))
        lista.adicionar(Path("F:/b"))
        self.assertEqual(lista.todos(), [Path("F:/a"), Path("F:/b")])
        lista.remover(Path("F:/a"))
        self.assertEqual(lista.todos(), [Path("F:/b")])


if __name__ == "__main__":
    unittest.main()
