---
name: iniciar-projeto
description: Prepara um projeto novo ou existente do meu jeito, com entrevista de todas as perguntas, CLAUDE.md do projeto, hook que impede co-autor nos commits, arquitetura em camadas, lint de arquitetura e os agentes da stack. Com o argumento agentes, só instala no projeto os agentes que a stack usa. Use quando eu pedir para iniciar, configurar ou preparar um projeto.
argument-hint: "[agentes | nome do projeto ou pasta]"
disable-model-invocation: true
---

# Iniciar projeto

Projeto alvo: $ARGUMENTS (se vazio, a pasta atual).

Modo `agentes`: se $ARGUMENTS começar com `agentes`, faça só o passo 1, o item 6 do passo 4 (com plano e ok) e o relatório. Não faça a entrevista completa nem crie outros arquivos.

Regras desta skill:
- Pergunte tudo antes de criar qualquer arquivo. Nunca preencha por suposição: o que não for confirmado fica como `<PREENCHER>`.
- Não pergunte o que dá para descobrir lendo a pasta.
- Nunca sobrescreva um arquivo existente: mostre a diferença e peça para mesclar.
- Não faça commit.

## 1. Reconhecer a pasta
Leia, sem alterar, o que existir: `.git`, `package.json`, `tsconfig*.json`, programas ABL (`.p`, `.i`, `.cls`), `CLAUDE.md`, `.claude/`, `README.md`. Rode `git config user.name` e `git config user.email` para saber o autor atual.

## 2. Entrevista
Use AskUserQuestion, até 4 perguntas por vez, em quantas rodadas forem necessárias. Cubra:
- Projeto novo do zero ou existente; objetivo e quem usa, em duas frases.
- Stack: (a) API Progress ABL + front React, (b) Progress ABL direto (.w, .p, Datasul, sem front), (c) Python/FastAPI + front React, ou (d) outra (Node, AngularJS, scripts, automações, site estático). A escolha decide o modelo de CLAUDE.md do passo 4.
- ABL: como o dicionário do banco chega (em geral, sob demanda por tabela) e em qual pasta guardar, onde ficam os programas, regras da casa (por exemplo, sem FUNCTION, padrão de comentários).
- Front: design system existente a seguir ou design livre; comandos de dev, lint e build.
- Git: repositório remoto; confirmar nome e e-mail dos commits (os lidos do git config).
- Quer a estrutura de arquitetura em camadas com lint de arquitetura? (recomendado em React)

## 3. Plano e ok
Liste em poucas linhas os arquivos que vai criar ou alterar e espere o meu ok.

## 4. Executar
1. **CLAUDE.md do projeto**: parta do modelo da stack escolhida: [modelos/CLAUDE.md](modelos/CLAUDE.md) (API ABL + React), [modelos/CLAUDE-abl-puro.md](modelos/CLAUDE-abl-puro.md) (ABL direto), [modelos/CLAUDE-python-react.md](modelos/CLAUDE-python-react.md) (Python + React) ou [modelos/CLAUDE-generico.md](modelos/CLAUDE-generico.md) (qualquer outra stack). Preencha só com fatos confirmados (entrevista ou arquivos lidos). Mantenha curto: ele é carregado em toda sessão e por todo subagente.
2. **Git**: se não houver repositório, pergunte e faça `git init`. Copie [modelos/commit-msg](modelos/commit-msg) para `.git/hooks/commit-msg` e torne executável (`chmod +x`, se o sistema permitir). O hook remove co-autor e assinaturas de IA das mensagens de commit. Confira `user.name` e `user.email` do repositório.
3. **`.gitignore`**: garanta a linha `.claude/` (a pasta inteira fica fora do git, sem perguntar). Se `git ls-files .claude` mostrar arquivos já versionados, avise-me e não os remova do git sozinho.
4. **Arquitetura (se eu aceitei)**:
   - Front React: estrutura `src/modules/<id>/{domain,application,infrastructure,presentation}` e `src/shared`. Copie [modelos/dependency-cruiser.cjs](modelos/dependency-cruiser.cjs) para a pasta do front, adicione `dependency-cruiser` como devDependency e o script `"lint:arquitetura": "depcruise src --config .dependency-cruiser.cjs"`. Ajuste o nome do arquivo de tsconfig se o projeto usar outro.
   - Backend Python/FastAPI: estrutura `src/<pacote>/{domain,application/{ports,use_cases},infrastructure,presentation/http}` mais `main.py`. Cole no `pyproject.toml` o trecho de [modelos/importlinter-fastapi.toml](modelos/importlinter-fastapi.toml) (trocando `<pacote>`) e confirme comigo as dependências de desenvolvimento (ruff, mypy, import-linter, pytest) antes de instalar.
   - Projeto novo de React: confirme comigo e crie com o template `react-ts` do Vite antes de aplicar a estrutura.
   - ABL: siga a estrutura dos projetos ABL que eu já tiver (por exemplo, uma pasta por API com `.i`, `.p` e `RP.p`). Se não houver referência, pergunte.
   - Design livre: pergunte se quero a skill ui-ux-pro-max neste projeto. Se eu quiser, não instale por conta própria (exige npm e Python 3): passe o comando `uipro init --ai claude`, para eu rodar dentro da pasta do projeto. Com design system existente, não ofereça.
5. **Verificação**: rode o lint e o build do front, se existirem. Teste o hook com um commit de teste num repositório temporário, nunca no real.
6. **Agentes da stack**: ficam em `${CLAUDE_SKILL_DIR}/agentes/` e não em `~/.claude/agents/`, de propósito: assim só entram no projeto que os usa e não pesam nas outras sessões.
   - Detecte a stack pelos arquivos: `.p`, `.w`, `.i` ou `.cls` indicam ABL; `package.json` com `react` indica implementador-react; `pyproject.toml` ou `requirements.txt` com fastapi, flask ou django indica implementador-python. Front web (React, AngularJS ou HTML) indica também conferidor-visual.
   - ABL com front React: implementador-abl. ABL sem front: pergunte se é API para outro sistema consumir (implementador-abl) ou programa direto, tela .w ou batch (implementador-abl-programa).
   - Nada detectado: não copie nada e diga isso. O implementador-geral já está nos agentes globais.
   - Liste no plano os arquivos que serão copiados e espere o meu ok. Copie com Read e Write para `<projeto>/.claude/agents/`, criando a pasta se faltar. Nunca sobrescreva: se já existir arquivo com o mesmo nome, compare e mostre a diferença.
   - Garanta `.claude/` no `.gitignore` (passo 3): os agentes copiados não vão para o git. Em modo `agentes`, faça só essa linha do `.gitignore`.
   - Avise que os agentes só carregam ao reabrir a sessão.

## 5. Relatório
Em poucas linhas: o que foi criado, os agentes copiados, o que ficou como `<PREENCHER>` (cite a pasta do dicionário) e o próximo passo.
