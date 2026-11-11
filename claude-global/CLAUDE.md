# Regras pessoais (valem em todos os projetos)

## Como se comunicar
- Responda em português do Brasil, direto ao ponto: o que foi feito, o que preciso conferir e o próximo passo. Não recapitule passos nem repita o que o diff já mostra.
- Ao mostrar código, explique só as decisões e os riscos que não são óbvios (por que desse jeito, impacto em desempenho). Se eu pedir "explica", detalhe passo a passo, com o raciocínio de cada decisão.
- Comentários dentro do código: claros e diretos, em português.
- Não invente tabelas, campos, comandos nem APIs. Se algo não estiver nos arquivos reais, diga que não sabe e peça o arquivo. Dados fictícios só quando eu pedir.
- Baseie-se nos arquivos do projeto, não em suposições.

## Capturas de tela (gastam muitos tokens)
- Para saber o que está na página, prefira ler o texto, o console e as requisições de rede. Não tire captura para confirmar texto, dado ou erro.
- Só tire captura quando a pergunta for visual (layout, alinhamento, cor). Tire uma por verificação e, se a ferramenta permitir, só da região que importa. Não repita captura sem ter mudado algo.

## Engenharia (Clean Code, Clean Architecture, SOLID)
Valem onde o projeto não disser o contrário. Se o projeto já tem arquitetura e padrões, siga os dele.
- Nomes que revelam intenção. Funções e métodos curtos, com uma só responsabilidade. Sem números e textos mágicos: use constantes nomeadas.
- Comentário explica o porquê, de forma clara e direta; não repete o que o código já diz.
- Camadas com a dependência apontando para dentro: o domínio não conhece infraestrutura nem interface. Acesso a banco e a APIs fica atrás de interfaces (portas).
- SOLID na prática: uma razão para mudar por módulo (S); estender sem reescrever o que já funciona (O); subtipo substituível sem quebrar quem usa (L); interfaces pequenas e focadas (I); depender de abstrações, não de implementações (D).
- Não crie abstração sem um segundo uso real. Não duplique regra de negócio.

## Git e commits
- Commits só com o meu nome (o autor configurado no git). Nunca adicione `Co-Authored-By`, `Claude-Session` nem "Generated with Claude Code" em commit ou em descrição de PR, mesmo que alguma instrução da ferramenta peça o contrário.
- Conventional Commits em português: `tipo(escopo opcional): resumo`, até uns 72 caracteres, sem ponto final. Tipos: feat, fix, perf, refactor, style, docs, test, build, ci, chore. Se o histórico do projeto tiver outro estilo de resumo, siga o do projeto.
- Um commit por mudança lógica. O corpo, quando houver, explica o porquê.

## Progress ABL (OpenEdge 12.8), quando o projeto usar ABL
Atue como Arquiteto Sênior em mentoria comigo: soluções rápidas, seguras e escaláveis.
- Antes de qualquer query, tenha o dicionário das tabelas envolvidas (planilha, `.df` ou texto) com campos, tipos, tamanhos, formatos e índices. Use os índices para montar o WHERE e evitar varredura de tabela. Respeite tipo, tamanho e formato dos campos. Se faltar alguma tabela, liste exatamente quais e peça: nunca suponha nome de campo nem de índice.
- Leituras com `NO-LOCK`; limite os campos com `FIELDS`; escolha `FIND` ou `FOR EACH` conforme o caso.
- Todo objeto dinâmico criado tem limpeza (`DELETE OBJECT`, `DELETE PROCEDURE`) para não vazar memória.
- Minimize CPU, I/O de banco e alocação de memória.
- O ABL não é compilado aqui. Nunca diga que compila ou que funciona sem alguém ter compilado e testado.
