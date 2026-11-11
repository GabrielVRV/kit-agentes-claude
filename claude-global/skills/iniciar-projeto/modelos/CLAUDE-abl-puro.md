# <Nome do projeto>

<Uma ou duas frases: o que é e para quem. Programas Progress ABL (OpenEdge 12.8) rodando direto no Datasul, sem front React.>

## Mapa
<Tabela ou lista: programa (.w, .p, .i), o que faz, onde fica na pasta, como é chamado no Datasul (menu, programa pai).>

## Comandos
<Como compilar e publicar. O ABL só compila no Datasul: diga quem compila e como o programa é testado.>

## Programas de referência
<Um programa existente de cada tipo, para os agentes copiarem o padrão: tela .w, batch, relatório, customização. Caminho de cada um.>
<PREENCHER: sem referência de um tipo, o implementador responde BLOQUEADO para esse tipo.>

## Regras do ABL
<Padrão de cabeçalho e includes obrigatórios do Datasul, nomes de programas e de procedures, padrão de comentários, regras da casa (ex.: sem FUNCTION), regras de leitura em tabelas grandes.>

## Telas .w
<Como as telas são abertas e testadas, quais blocos do AppBuilder não podem ser editados à mão, padrão de triggers.>

## Banco
O .df completo é grande demais, então o dicionário vem sob demanda: só das tabelas da tarefa, em planilha com campos (tipo, tamanho, formato) e índices.
Pasta do dicionário: <PREENCHER, ex.: dicionario/ (ignorada pelo git, se o usuário não quiser versionar)>. Guarde ali os arquivos convertidos (`<tabela>.md`).
Sem o dicionário de uma tabela, nenhum agente escreve nem revisa query dela. Use a skill `dicionario-dados`.

## Convenções de commit
<Formato usado no histórico (confira com git log). Se não houver histórico: Conventional Commits em português, como no CLAUDE.md global.>
