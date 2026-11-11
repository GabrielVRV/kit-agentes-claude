# Kit de agentes para Claude Code (Progress ABL + React)

Fluxo: o Opus (maestro) pergunta tudo o que estiver em aberto, monta o plano e delega; subagentes executam e devolvem relatório curto. A skill `/iniciar-projeto` prepara cada projeto novo do mesmo jeito.

## O que tem aqui
- `claude-global/CLAUDE.md`: suas regras pessoais (comunicação, Clean Code, Clean Architecture, SOLID, commits, ABL). Curto de propósito: todo subagente carrega este arquivo.
- `claude-global/settings.exemplo.json`: desliga o co-autor e a assinatura nos commits e nas descrições de PR, e bloqueia a leitura de `.env`, `.pem` e `.key` (o `.env.example` continua liberado). Se você já tem `settings.json`, copie só os blocos `attribution` e `permissions` para dentro dele. A regra de leitura vale para as ferramentas de arquivo e para comandos como `cat`, mas não impede um script que abra o arquivo por conta própria; para bloqueio no sistema, existe o modo sandbox do Claude Code.
- `claude-global/agents/`: os agentes que servem para qualquer projeto e ficam instalados no seu usuário: maestro (opus), explorador e verificador (haiku), revisor (opus), revisor-leve e implementador-geral (sonnet, qualquer outra stack).
- `claude-global/skills/iniciar-projeto/`: a skill, seus modelos (CLAUDE.md do projeto, hook de commit, lint de arquitetura) e, em `agentes/`, os agentes de stack que ela copia para cada projeto: implementador-abl (API ABL), implementador-abl-programa (telas .w, batch, Datasul), implementador-python (FastAPI), implementador-react e conferidor-visual.
- `claude-global/skills/dicionario-dados/`: pede ao você só as tabelas de cada tarefa e converte a planilha do dicionário em texto.

## Painel (o jeito fácil)
Uma janela que faz a instalação, as atualizações e o liga/desliga do maestro, sem comando para lembrar.

- **Abrir neste PC:** dois cliques em `iniciar_painel.pyw` (usa o Python instalado) ou em `dist\KitAgentesClaude.exe`.
- **Outro PC:** copie só o `dist\KitAgentesClaude.exe`. O kit vai embutido nele e não precisa de Python. Se o antivírus ou o SmartScreen reclamar, é por ser um executável sem assinatura digital.
- **Gerar o executável de novo** (depois de mudar o kit ou o painel): dois cliques em `construir.bat`. Ele roda os testes antes e só gera se passarem.

O que cada aba faz:
- **Meu usuário:** mostra cada agente, skill, o `CLAUDE.md` e o `settings.json` como Instalado, Desatualizado, Faltando ou Sobrando. "Instalar / atualizar tudo" copia o que falta e o que mudou. "Remover os que sobram" tira do usuário os agentes de stack de versões antigas do kit. A caixa "Usar o maestro em todas as sessões" grava ou remove `"agent": "maestro"` no `settings.json`.
- **Projetos:** adicione a pasta do projeto. O painel detecta a stack, já marca os agentes dela e, com "Aplicar no projeto", copia os agentes para `.claude/agents/`, instala o hook de commit e garante `.claude/` no `.gitignore`. A caixa "Usar o maestro neste projeto" grava em `.claude/settings.local.json`. Substitui o `/iniciar-projeto agentes`; a entrevista completa do `/iniciar-projeto` continua na skill.

Cuidados que o painel toma:
- Compara pelo conteúdo do arquivo, não pela data.
- Antes de substituir ou remover qualquer coisa, guarda a versão anterior em `~/.claude/backups-kit-agentes/<data_hora>/` e pede confirmação.
- No `settings.json`, mescla só os blocos `attribution` e `permissions.deny`; as outras chaves ficam como estão. Se o arquivo estiver com JSON inválido, não grava nada.
- Depois de qualquer mudança, feche e abra a sessão do Claude.

Para atualizar o kit em outro PC sem gerar o executável de novo, coloque a pasta `claude-global` ao lado do `.exe`: ela vence a cópia embutida.

O código fica em `painel/` (`dominio` com as regras, `aplicacao` com o que cada botão faz, `infraestrutura` com o acesso a disco, `interface` com a janela) e os testes em `testes/` (`python -m unittest discover -s testes -t .`).

## Instalar à mão (sem o painel)
No PowerShell, dentro da pasta do kit:

```powershell
$d = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force "$d\agents", "$d\skills" | Out-Null
Copy-Item .\claude-global\agents\*.md "$d\agents\"
Copy-Item .\claude-global\skills\* "$d\skills\" -Recurse -Force
if (-not (Test-Path "$d\CLAUDE.md")) { Copy-Item .\claude-global\CLAUDE.md "$d\CLAUDE.md" } else { "Já existe um CLAUDE.md global: una o conteúdo à mão." }
if (-not (Test-Path "$d\settings.json")) { Copy-Item .\claude-global\settings.exemplo.json "$d\settings.json" } else { "Já existe um settings.json: copie só o bloco attribution para dentro dele." }
```

Faça login no Claude Code com a conta do Claude. Se a variável `ANTHROPIC_API_KEY` estiver definida, ele usa a chave e cobra por uso.

## Dicionário de dados (sob demanda, em planilha)
O `.df` inteiro é grande demais, então o fluxo trabalha só com as tabelas de cada tarefa:
1. O maestro (pela skill `dicionario-dados`) lista as tabelas que a tarefa precisa e pede a você o que faltar, junto das outras perguntas.
2. Você envia uma planilha por tabela com campos (tipo, tamanho, formato) e índices (nome, campos na ordem, único, primário).
3. Você só envia a planilha, sem pedir conversão. O agente lê o arquivo direto e salva um `.md` por tabela na pasta do dicionário do projeto, para não pedir a mesma tabela de novo. Se a leitura direta falhar no Claude Code (eu não consegui confirmar que ele lê `.xlsx`), há o plano B automático: `scripts/xlsx_para_md.py` (Python e `pip install openpyxl`).
4. Sem o dicionário de uma tabela, nenhum agente escreve nem revisa query dela.

Se o agente não entender alguma planilha sua, me mande uma de exemplo (só a estrutura de uma tabela) para eu ajustar.

## Agentes por projeto
Os agentes de stack não ficam no seu usuário: ficam dentro da skill e vão para a pasta `.claude/agents/` de cada projeto, só os que a stack usa. Assim as outras sessões não carregam o que não usam.
- Projeto novo: o `/iniciar-projeto` detecta a stack, mostra no plano o que vai copiar e copia depois do seu ok.
- Projeto que já existe: dentro da sessão, digite `/iniciar-projeto agentes`. Ele só instala os agentes, sem mexer em mais nada.
- É um comando por projeto, uma vez. Não existe jeito totalmente sem comando que eu recomende: copiar arquivos para dentro dos seus repositórios sozinho a cada sessão seria invasivo, e os agentes só carregam ao abrir a sessão.
- Depois de instalar, feche e abra a sessão.
- Se o maestro notar que falta o especialista da stack, ele usa o `implementador-geral` e te avisa.

## Stacks, a mesma equipe
Maestro, explorador, verificador e revisores servem para qualquer projeto. O que muda é o implementador, que o maestro escolhe pelo CLAUDE.md do projeto:

| Stack do projeto | Implementadores | Modelo de CLAUDE.md |
|---|---|---|
| API Progress ABL + React (ex.: Painel-PCP) | implementador-abl + implementador-react | `modelos/CLAUDE.md` |
| Progress ABL direto: telas .w, batch, Datasul | implementador-abl-programa | `modelos/CLAUDE-abl-puro.md` |
| Python/FastAPI + React (ex.: IA de Manuais) | implementador-python + implementador-react | `modelos/CLAUDE-python-react.md` |
| Qualquer outra (Node, AngularJS, scripts, automações, site estático) | implementador-geral | `modelos/CLAUDE-generico.md` |

No ABL direto, o implementador exige um programa de referência de cada tipo (tela .w, batch, relatório, customização) e responde `BLOQUEADO` sem ele, porque os padrões do Datasul não são inventados. Preencha a seção "Programas de referência" do CLAUDE.md do projeto.

## Onde cada modelo trabalha
- **Opus:** o maestro (conversa e plano) e o `revisor`, só para ABL, contrato de API, segurança, autenticação, migração e mudança grande.
- **Sonnet:** os implementadores e o `revisor-leve` (mudança pequena em front ou Python).
- **Haiku:** o `explorador` (buscas amplas), o `conferidor-visual` (confere a página no navegador, só quando você disser que precisa) e o `verificador`, que roda lint, tipos, camadas e testes uma vez no fim e devolve só as falhas. Os três usam `effort: low`, e o `conferidor-visual` não carrega o CLAUDE.md (`omitClaudeMd`), porque só precisa do endereço e da lista do que conferir.

O maestro escolhe o fluxo pelo tamanho da tarefa, para não pagar três subagentes em mudança pequena:
- **Pequena** (até 2 arquivos, pouca lógica, fora de ABL): o maestro faz e roda o lint.
- **Média** (um implementador, até uns 5 arquivos ou 200 linhas, sem risco): implementador com a suíte completa e `revisor-leve`. Sem `verificador`.
- **Grande ou de risco** (ABL, contrato de API, segurança, autenticação, migração): implementador, `verificador` e `revisor`.

O critério de pronto combinado com você vai até o revisor, que confere item por item se a mudança faz o que foi pedido, antes de olhar as regras.

Para gastar menos do limite: no seletor de modelo do chat, use Sonnet com o maestro nas tarefas de rotina e deixe o Opus para ABL, arquitetura e planejamento difícil. E abra um chat novo quando a tarefa seguinte não depender da anterior, porque conversa longa reenvia o histórico a cada turno.

As respostas do maestro e dos agentes são curtas de propósito. A explicação do código cobre só decisões e riscos; peça "explica" quando quiser o passo a passo.

## Dia a dia
1. No Claude Desktop, abra um chat na pasta do projeto: com a caixa do maestro ligada no painel, ele já entra sozinho. No terminal, rode `claude --agent maestro`.
2. Diga em uma ou duas frases o que quer fazer.
3. O maestro lê o CLAUDE.md e o que precisar, e faz todas as perguntas em aberto (até 4 por rodada). Responda.
4. Ele apresenta o plano: passos, quem faz cada um e em qual modelo. Diga "ok" ou ajuste.
5. Ele delega, revisa e explica o resultado.
6. Você testa: o front com `npm run dev`, o ABL compilando no Datasul. Quando estiver satisfeito, peça o commit.

Cada sessão nova começa do zero: o contexto vem do CLAUDE.md, dos docs e do histórico do git. Quando uma decisão importante for tomada, peça ao maestro para registrá-la no CLAUDE.md do projeto.

## Projeto que já existe (como o Painel-PCP)
1. Se o projeto já tem CLAUDE.md, não precisa rodar o `/iniciar-projeto` completo. Só preencha o que estiver como `<PREENCHER>` (principalmente a pasta do dicionário).
2. Rode `/iniciar-projeto agentes` dentro da sessão, para instalar os agentes da stack.
3. Copie o hook de commit para o repositório (veja a seção abaixo).

Se você instalou uma versão anterior do kit, os agentes de stack ficaram em `$d\agents`, carregando em todo projeto. Depois de instalar o kit novo e rodar `/iniciar-projeto agentes` nos projetos, remova as cópias globais antigas:

```powershell
$d = "$env:USERPROFILE\.claude"
"implementador-abl","implementador-abl-programa","implementador-python","implementador-react","conferidor-visual" | ForEach-Object { Remove-Item "$d\agents\$_.md" -ErrorAction SilentlyContinue }
```

## Ignorar a pasta `.claude/` em todos os repositórios (opcional, uma vez)
A skill `/iniciar-projeto` já coloca `.claude/` no `.gitignore` de cada projeto. Para valer em todos os repositórios da sua máquina de uma vez, inclusive os que você nunca rodou a skill, use um ignore global do Git:

```powershell
$atual = git config --global core.excludesFile
if (-not $atual) { $atual = "$env:USERPROFILE\.gitignore_global"; git config --global core.excludesFile $atual }
if (-not (Test-Path $atual) -or -not (Select-String -Path $atual -Pattern '^\.claude/$' -Quiet)) { Add-Content $atual ".claude/" }
"Ignore global em: $atual"
```

O comando respeita um ignore global que você já tenha e só acrescenta a linha se ela não existir. Dois avisos: arquivos que já estão versionados dentro de `.claude/` continuam versionados (para parar de acompanhá-los, use `git rm -r --cached .claude` no projeto), e o `CLAUDE.md` da raiz não é afetado, então ele continua indo para o git.

## Commits sem co-autor (três camadas)
1. `settings.json`: o bloco `attribution` (commit e pr vazios, sessionUrl falso). Usei a forma de objeto porque `"attribution": false` só existe a partir do Claude Code 2.1.281 e versões antigas rejeitam o arquivo inteiro.
2. Regra no `CLAUDE.md` global: nunca adicionar co-autor nem assinatura.
3. Hook `commit-msg`: remove `Co-Authored-By`, `Claude-Session` e a linha "Generated with Claude" da mensagem, mesmo que as duas primeiras camadas falhem. Testado com `-m` múltiplo e com `--trailer`. A skill `/iniciar-projeto` copia o hook sozinha. Em projeto existente, copie à mão:

```powershell
Copy-Item .\claude-global\skills\iniciar-projeto\modelos\commit-msg "F:\Projetos\Painel-PCP\.git\hooks\commit-msg"
```

Teste num repositório temporário antes de confiar (confirma que o Git do Windows executa o hook):

```powershell
$t = "$env:TEMP\teste-hook"; New-Item -ItemType Directory -Force $t | Out-Null; Set-Location $t
git init; Copy-Item "<pasta-do-kit>\claude-global\skills\iniciar-projeto\modelos\commit-msg" .git\hooks\commit-msg
git commit --allow-empty -m "feat: teste" --trailer "Co-Authored-By: Fulano <f@x.com>"
git log -1
```
A mensagem do último commit deve sair só com `feat: teste`.

## Skills de terceiros (o que ficou)
Todas rodam com as permissões do seu usuário. Leia o que vai instalar.

- **humanizer (global).** Para reescrever textos que você envia (currículo, e-mail). Não é para código. Os exemplos do README são em inglês: teste com um texto seu em português. Exige Claude Code 2.1.142 ou mais novo; depois de instalado, o comando é `/humanizer:humanizer`.

```
/plugin marketplace add blader/humanizer
/plugin install humanizer@humanizer
```

- **ui-ux-pro-max (por projeto).** Só em projeto de design livre, nunca em projeto com design system existente (como o Painel-PCP). Precisa de Node e de Python 3. Instale dentro da pasta do projeto, para a skill ficar em `.claude/skills/ui-ux-pro-max` e não pesar nas outras sessões:

```
npm install -g ui-ux-pro-max-cli
uipro init --ai claude --dry-run
uipro init --ai claude
```
O `--dry-run` só mostra o que seria feito, sem gravar nada.

Em projeto de design livre, quem usa a ui-ux-pro-max é o maestro, no planejamento: ele escreve as decisões de design no pedido do `implementador-react`, que não tem acesso a skills.

- **Descartadas** (reavaliadas lendo cada repositório):
  - **graphify:** a lista de linguagens da documentação não inclui Progress ABL (`.p`, `.w`, `.i`; o `.cls` listado é Salesforce Apex). Em Python e React funcionaria, mas instala hooks que interceptam `Read` e `Grep`, e o explorador não tem como consultar o grafo.
  - **claude-mem:** hooks em toda chamada de ferramenta, um segundo agente que consome o plano ou um provedor externo, e telemetria ligada por padrão.
  - **superpowers:** fluxo obrigatório (brainstorm, worktree, plano, TDD) que conflita com o maestro; o TDD obrigatório combina mal com ABL, que não compila aqui.
  - **caveman:** estilo telegráfico baseado em inglês controlado, ativo em toda sessão e nos subagentes, com cerca de 1.160 tokens de regras; no teste do próprio autor, "responda de forma concisa" ficou quase igual. O maestro já tem regra de resposta curta.
  - **ponytail:** plugin ativo em toda sessão; os ganhos divulgados são do próprio autor.
  - **vibe-coding-toolkit:** pacote que instala vários dos itens acima, voltado a Next.js.
  - **taste-skill:** só para site institucional, e tem um gate no Stop que segura a tarefa por até três rodadas.
  - **emilkowalski/skills:** animação; só faria sentido em projeto de design livre, instalada por projeto.
  - **planning-with-files:** hooks reinjetam o plano em todo turno e há um gate no Stop.

  Três ideias desses projetos foram incorporadas direto nos agentes, sem instalar nada: reutilizar antes de criar e entregar a menor mudança completa (ponytail), achar a causa raiz antes de corrigir bug e conferir o critério de pronto antes de dizer que terminou (superpowers).

## Ajustes
- Modelo de cada agente: campo `model` no topo do arquivo (`haiku`, `sonnet`, `opus`).
- Limite de turnos: `maxTurns`.
- Os executores não têm a ferramenta `Agent`, então não criam outros subagentes. Para liberar, acrescente `Agent` em `tools`.
- Maestro como padrão de toda sessão: `"agent": "maestro"` no settings. Não recomendo no global, porque abriria o Opus até para perguntas pequenas.
- Um agente em `.claude/agents/` dentro do projeto vale mais que o de mesmo nome em `~/.claude/agents/`.

## Como saber se compensa
Compare o consumo de tokens em tarefas parecidas com e sem o maestro, por uma ou duas semanas. Se a delegação estiver custando mais que fazer direto, aumente o que o maestro faz sozinho.
