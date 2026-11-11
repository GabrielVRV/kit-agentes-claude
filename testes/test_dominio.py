"""Regras puras: não tocam o disco."""

import unittest

from painel.dominio.configuracao import (
    blocos_do_kit_aplicados,
    com_agente_padrao,
    com_blocos_do_kit,
    com_pasta_claude_ignorada,
)
from painel.dominio.modelos import Estado, estado_por_conteudo
from painel.dominio.stack import (
    AGENTE_ABL_API,
    AGENTE_ABL_PROGRAMA,
    AGENTE_CONFERIDOR,
    AGENTE_REACT,
    SinaisProjeto,
    agentes_sugeridos,
)

EXEMPLO = {"attribution": {"commit": ""}, "permissions": {"deny": ["Read(.env)", "Read(*.pem)"]}}


class EstadoPorConteudo(unittest.TestCase):
    def test_sem_destino_esta_faltando(self):
        self.assertIs(estado_por_conteudo({"a": "1"}, {}), Estado.FALTANDO)

    def test_conteudo_igual_esta_instalado_mesmo_com_arquivo_extra(self):
        self.assertIs(estado_por_conteudo({"a": "1"}, {"a": "1", "meu": "9"}), Estado.INSTALADO)

    def test_conteudo_diferente_ou_arquivo_ausente_esta_desatualizado(self):
        self.assertIs(estado_por_conteudo({"a": "1"}, {"a": "2"}), Estado.DESATUALIZADO)
        self.assertIs(estado_por_conteudo({"a": "1", "b": "1"}, {"a": "1"}), Estado.DESATUALIZADO)


class Stack(unittest.TestCase):
    def test_abl_com_react_sugere_api_react_e_conferidor(self):
        sinais = SinaisProjeto(tem_abl=True, tem_react=True, tem_front_web=True)
        self.assertEqual(agentes_sugeridos(sinais), {AGENTE_ABL_API, AGENTE_REACT, AGENTE_CONFERIDOR})

    def test_abl_sem_front_nao_escolhe_entre_api_e_programa(self):
        sugeridos = agentes_sugeridos(SinaisProjeto(tem_abl=True))
        self.assertFalse({AGENTE_ABL_API, AGENTE_ABL_PROGRAMA} & sugeridos)

    def test_nada_detectado_nao_sugere_nada(self):
        self.assertEqual(agentes_sugeridos(SinaisProjeto()), set())


class Settings(unittest.TestCase):
    def test_mescla_preserva_o_que_ja_existia(self):
        atual = {"model": "opus", "permissions": {"allow": ["Bash(ls)"], "deny": ["Read(segredo)"]}}
        novo = com_blocos_do_kit(atual, EXEMPLO)
        self.assertEqual(novo["model"], "opus")
        self.assertEqual(novo["permissions"]["allow"], ["Bash(ls)"])
        self.assertEqual(novo["permissions"]["deny"], ["Read(segredo)", "Read(.env)", "Read(*.pem)"])
        self.assertTrue(blocos_do_kit_aplicados(novo, EXEMPLO))
        self.assertNotIn("attribution", atual)  # a entrada não é alterada

    def test_falta_de_uma_regra_conta_como_nao_aplicado(self):
        atual = {"attribution": {"commit": ""}, "permissions": {"deny": ["Read(.env)"]}}
        self.assertFalse(blocos_do_kit_aplicados(atual, EXEMPLO))

    def test_agente_padrao_liga_e_desliga_sem_tocar_no_resto(self):
        ligado = com_agente_padrao({"model": "opus"}, "maestro")
        self.assertEqual(ligado, {"model": "opus", "agent": "maestro"})
        self.assertEqual(com_agente_padrao(ligado, None), {"model": "opus"})


class Gitignore(unittest.TestCase):
    def test_acrescenta_a_linha_uma_unica_vez(self):
        texto = com_pasta_claude_ignorada("node_modules/")
        self.assertEqual(texto, "node_modules/\n.claude/\n")
        self.assertEqual(com_pasta_claude_ignorada(texto), texto)

    def test_reconhece_variacoes_da_linha(self):
        self.assertEqual(com_pasta_claude_ignorada("/.claude\n"), "/.claude\n")


if __name__ == "__main__":
    unittest.main()
