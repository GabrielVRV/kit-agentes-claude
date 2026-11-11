# <Nome do projeto>

<Uma ou duas frases: o que é, para quem e a stack (Python/FastAPI no back, React + Vite + TypeScript no front).>

## Mapa
<Pastas principais: backend, frontend, docs, scripts, docker. Uma linha por pasta.>

## Comandos
Back (rodar em `backend/`):
- <ativar o ambiente virtual, instalar dependências, subir a API, migrações>
- <lint, formatação, tipos, regra de camadas, testes: os comandos reais, e quais testes precisam de Docker ou gastam cota>

Front (rodar em `frontend/`):
- <dev, typecheck, lint, formatação, testes, build>

## Regras do backend
<Camadas e a regra de dependência (quem pode importar quem). Onde ficam portas, casos de uso, adaptadores, rotas e schemas. Onde as dependências são ligadas. Padrão de testes (fakes em memória, o que é unitário e o que é integração). Idioma de identificadores e de comentários.>

## Regras do front
<Estrutura de pastas por funcionalidade, regra de dependência entre camadas (e se o lint a verifica), como os gateways são injetados, alias de import, padrão de CSS e de testes.>

## Banco
<Como o schema é versionado (ex.: Alembic), onde ficam as migrações, regra de nunca editar migração antiga. Extensões usadas.>

## Segurança
- Nunca abra, imprima nem copie arquivos `.env`, segredos ou dados reais da empresa.
<Outros arquivos locais que não vão para o git.>

## Documentação
<Onde ficam glossário do domínio e decisões de arquitetura, e a regra de registrar decisão nova.>

## Convenções de commit
<Formato usado no histórico (confira com git log). Se não houver histórico: Conventional Commits em português, como no CLAUDE.md global.>
