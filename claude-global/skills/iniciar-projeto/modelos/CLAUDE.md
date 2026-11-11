# <Nome do projeto>

<Uma ou duas frases: o que é, para quem e a stack.>

## Mapa
<Tabela ou lista: tela/módulo, pasta do front, pasta ou arquivo da API, endpoint.>

## Comandos
<Comandos reais, com a pasta onde rodam: dev, lint, lint de arquitetura, build, testes.>
<Diga o que NÃO roda aqui (ex.: o ABL só compila no Datasul).>

## Regras do front
<Estrutura de pastas e camadas, fronteiras proibidas entre módulos, como chamar a API, como funciona o mock, como criar uma tela nova.>

## Design
<Design system existente a seguir (ex.: Bootstrap 3 e a cor da empresa), ou "livre". Em projeto com design system existente, não use skills de UI/UX para trocar o visual.>

## Regras do ABL
<Estrutura dos arquivos de cada API, regras da casa (ex.: sem FUNCTION), padrão de cabeçalho e de comentários, regras de leitura em tabelas grandes.>

## Banco
O .df completo é grande demais, então o dicionário vem sob demanda: só das tabelas da tarefa, em planilha com campos (tipo, tamanho, formato) e índices.
Pasta do dicionário: <PREENCHER, ex.: Exemplos/dicionario/ (ignorada pelo git)>. Guarde ali os arquivos convertidos (`<tabela>.md`).
Sem o dicionário de uma tabela, nenhum agente escreve nem revisa query dela. Use a skill `dicionario-dados`.

## Convenções de commit
<Formato usado no histórico (confira com git log). Se não houver histórico: Conventional Commits em português, como no CLAUDE.md global.>
