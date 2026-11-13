# 6ª Jornada Acadêmica - Entrega da etapa 2

Atualização incremental sobre a estrutura Flask que já está no computador.

## Instalação

1. Pare `python run.py` com Ctrl+C.
2. Abra o terminal e execute:

    cd ~/Projetos/jornada-academica-uninassau
    cp -a app ../jornada-academica-backup-etapa1
    python -m zipfile -e "$HOME/Downloads/jornada-etapa2.zip" .

3. Confirme que o ambiente Python está ativo (`(.venv)`), ou execute `source .venv/bin/activate`.
4. Execute `python -m pytest -q` e `python run.py`.
5. Acesse http://127.0.0.1:5000 e http://127.0.0.1:5000/inscricao.

## O que foi implementado

- Site responsivo da Jornada com identidade institucional e logo fornecida pela equipe.
- Formulário real de inscrição com validação de CPF, e-mail e telefone.
- Persistência inicial em SQLite e índices únicos de CPF, e-mail e matrícula.
- Proteção CSRF em formulários com Flask-WTF.
- Geração de código de inscrição e confirmação visual.
- Testes automatizados básicos da inscrição.
- Imagem oficial do certificado preservada em app/static/img/modelo-certificado.jpeg para próxima etapa.

## Importante

- O banco local é criado automaticamente em `instance/jornada.db` se `DATABASE_URL=sqlite:///jornada.db`.
- Este sistema é uma versão acadêmica inicial e não deve ser divulgado para inscrições reais antes da revisão de privacidade e segurança, autenticação do painel, backup, políticas de retenção e hospedagem HTTPS.
- O módulo de check-in, a regra de horas para certificado, o envio de e-mail e o deploy serão desenvolvidos nas próximas etapas.
- O `run.py` existente no computador é mantido, assim como seu `.env` e `requirements.txt`.
