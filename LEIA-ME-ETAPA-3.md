# Etapa 3: painel do professor e controle de frequência

Este arquivo ZIP contém a versão **completa** dos arquivos da Etapa 2 acrescida do painel de professor. Não contém `.env`, banco `instance/jornada.db`, ambiente virtual, nem seu `run.py`.

## Instalação no Linux

1. Pare o Flask: `Ctrl+C`.
2. Na pasta `~/Projetos/jornada-academica-uninassau`:

```bash
cp -a app ../jornada-academica-backup-etapa2
python3 -m zipfile -e "$HOME/Downloads/jornada-etapa3.zip" .
source .venv/bin/activate
python -m pytest -q
```

3. Crie a primeira conta de professor **sem colocar senha no código**:

```bash
flask --app run:app criar-professor
```

Digite um usuário (exemplo `professor01`) e uma senha de pelo menos 12 caracteres. A senha fica oculta durante a digitação.

4. Execute `python run.py` e acesse:

- http://127.0.0.1:5000 (landing page)
- http://127.0.0.1:5000/inscricao (inscrições)
- http://127.0.0.1:5000/professor/login (login do professor)
- http://127.0.0.1:5000/professor/ (painel restrito)
- http://127.0.0.1:5000/professor/frequencia (horas acumuladas)

## O que há de novo

- Conta de professor criada pelo terminal com senha armazenada em hash.
- Login/logout de professor com formulário protegido por CSRF.
- Cadastro de atividade/palestra com data e duração inteira (1 a 12h).
- Lista de alunos para cada atividade, com busca e seleção em lote.
- Check-in persistente e índice de unicidade para não contar duas vezes a mesma atividade.
- Relatório de horas acumuladas por aluno, comparado com o valor configurável `CERTIFICATE_MIN_HOURS` (padrão 20).
- Testes de autenticação, atividade, frequência, duplicidade e relatório.

## Importante

- Se o comando `flask --app run:app criar-professor` não encontrar o Flask, certifique-se de que `.venv` esteja ativo.
- O SQLite preexistente **é preservado**, e o `db.create_all()` criará as três novas tabelas. Em mudanças futuras, use migrações.
- Não envie seu `.env` ou banco de dados ao GitHub. Este protótipo não deve receber dados pessoais reais antes de revisar LGPD, política de privacidade, segurança, autenticação, HTTPS e backups.
- O relatório indica quem alcançou o limite configurado, mas **ainda não emite certificados** nem manda e-mails.
- O material acadêmico apresenta exigências de **20h** e **75% de frequência** em lugares diferentes. Confirme a regra final antes de emitir certificados reais.
- A conta de professor não possui recuperação automática de senha nesta etapa. Também falta limitar tentativas de login; o deploy público deve aguardar esses controles.
