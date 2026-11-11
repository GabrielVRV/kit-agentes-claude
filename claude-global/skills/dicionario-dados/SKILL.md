---
name: dicionario-dados
description: Obtém o dicionário de dados das tabelas do banco (campos, tipos, tamanhos, formatos e índices) sob demanda, antes de escrever ou revisar queries ABL. Use sempre que uma tarefa envolver tabelas do banco e o dicionário delas ainda não estiver carregado.
---

# Dicionário de dados sob demanda

O `.df` completo é grande demais. Trabalhe só com as tabelas da tarefa, enviadas pelo usuário (em geral, em planilha Excel).

Regras:
- Nunca suponha nome de tabela, campo, tipo, formato ou índice.
- Peça somente as tabelas necessárias.

## Passo a passo
1. **Liste as tabelas da tarefa.** Tire os nomes do código existente (use o explorador) ou da especificação. Se não souber quais tabelas a tarefa exige, pergunte ao usuário.
2. **Procure no dicionário local.** A pasta está na seção "Banco" do CLAUDE.md do projeto (se não estiver, pergunte e registre lá). Procure `<tabela>.md`, `.csv` ou `.xlsx`.
3. **Peça o que faltar, em uma única mensagem.** Liste exatamente as tabelas e o que precisa de cada uma: campos (nome, tipo, tamanho, formato) e índices (nome, campos na ordem, se é único e se é primário). Junte esse pedido às demais perguntas do plano.
4. **Leia a planilha direto.** Não peça nenhuma conversão ao usuário: ele só envia o arquivo. Tente ler o `.xlsx` normalmente. Só se a leitura falhar ou vier ilegível (binário, sem células), use o plano B: `python "${CLAUDE_SKILL_DIR}/scripts/xlsx_para_md.py" "<planilha.xlsx>" "<pasta-do-dicionario>"` (precisa de `pip install openpyxl`; o script avisa se faltar). Sem Python, peça CSV ou o texto colado.
5. **Guarde e confirme.** Salve na pasta do dicionário um `<tabela>.md` com os campos e índices lidos, para não pedir de novo. Diga ao usuário, em uma linha por tabela, o que carregou (quantidade de campos e nomes dos índices). Se a planilha não trouxer índices ou tipos, peça de novo: não complete por dedução.
6. **Passe os caminhos adiante.** Ao delegar ao implementador-abl ou ao revisor, informe os caminhos dos arquivos do dicionário.

## Cuidados
- O dicionário é um retrato da base: se ela mudou depois, peça a planilha de novo.
- Guarde os arquivos convertidos na pasta do dicionário, para não pedir a mesma tabela outra vez.
- Confira no `.gitignore` se a pasta do dicionário está fora do versionamento, quando o usuário não quiser versioná-la.
