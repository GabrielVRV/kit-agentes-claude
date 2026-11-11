"""Alterações no settings do Claude e no .gitignore, sem tocar no que já é seu."""

import copy

CHAVE_ATRIBUICAO = "attribution"
CHAVE_PERMISSOES = "permissions"
CHAVE_NEGADAS = "deny"
CHAVE_AGENTE_PADRAO = "agent"

LINHA_GITIGNORE = ".claude/"
_FORMAS_DA_LINHA = {".claude/", ".claude", "/.claude/", "/.claude"}


def _negadas(settings: dict) -> list:
    return settings.get(CHAVE_PERMISSOES, {}).get(CHAVE_NEGADAS, [])


def blocos_do_kit_aplicados(atual: dict, exemplo: dict) -> bool:
    mesma_atribuicao = atual.get(CHAVE_ATRIBUICAO) == exemplo.get(CHAVE_ATRIBUICAO)
    return mesma_atribuicao and set(_negadas(exemplo)) <= set(_negadas(atual))


def com_blocos_do_kit(atual: dict, exemplo: dict) -> dict:
    """Mescla só os dois blocos do kit; as demais chaves do seu settings ficam como estão."""
    novo = copy.deepcopy(atual)
    novo[CHAVE_ATRIBUICAO] = copy.deepcopy(exemplo.get(CHAVE_ATRIBUICAO))
    negadas = list(_negadas(atual))
    negadas += [regra for regra in _negadas(exemplo) if regra not in negadas]
    novo.setdefault(CHAVE_PERMISSOES, {})[CHAVE_NEGADAS] = negadas
    return novo


def com_agente_padrao(atual: dict, nome_agente: str | None) -> dict:
    novo = copy.deepcopy(atual)
    if nome_agente is None:
        novo.pop(CHAVE_AGENTE_PADRAO, None)
    else:
        novo[CHAVE_AGENTE_PADRAO] = nome_agente
    return novo


def ignora_pasta_claude(gitignore: str) -> bool:
    return any(linha.strip() in _FORMAS_DA_LINHA for linha in gitignore.splitlines())


def com_pasta_claude_ignorada(gitignore: str) -> str:
    if ignora_pasta_claude(gitignore):
        return gitignore
    separador = "" if not gitignore or gitignore.endswith("\n") else "\n"
    return f"{gitignore}{separador}{LINHA_GITIGNORE}\n"
