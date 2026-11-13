# Etapa 5 — Preparação para apresentação e hospedagem

## O que esta atualização acrescenta

1. `render.yaml` para criar um Web Service Flask e um Postgres de demonstração.
2. Conversão automática da URL PostgreSQL do Render para o driver `psycopg` v3.
3. Sessão em cookie Secure/HttpOnly/SameSite, HTTPS e headers de segurança no Render.
4. Limites simples para tentativas de login e inscrição por IP (em memória, 1 worker).
5. Aviso visível de protótipo com **dados fictícios**, `noindex` e redução de cache de páginas sensíveis.
6. Criação inicial opcional do professor via variáveis secretas de ambiente, sem senha no código.
7. Testes adicionais e documentos de apresentação/QA.

**Importante:** o programa permanece um **protótipo de demonstração**. Não use dados reais de estudantes. O Render Free Postgres expira em 30 dias e não possui backups. Certificados não têm validade institucional. O aplicativo não é uma solução LGPD homologada para a UNINASSAU.

## Instalar no Linux

1. Pressione Ctrl+C para parar o Flask.
2. Baixe `jornada-etapa5.zip`.
3. Na pasta atual do projeto:

```bash
cd ~/Projetos/jornada-academica-uninassau
source .venv/bin/activate
# backup, sem mexer no banco nem no .env
cp -a app ../jornada-academica-backup-etapa4
ZIP=$(find "$HOME" -maxdepth 5 -type f -name 'jornada-etapa5*.zip' -print -quit 2>/dev/null)
if [ -n "$ZIP" ]; then
  python -m zipfile -e "$ZIP" .
  echo 'Etapa 5 extraída!'
else
  echo 'ZIP não encontrado. Baixe o arquivo antes de seguir.'
fi
python -m pip install -r requirements.txt
python -m pytest -q
python run.py
```

Se a extração falhar, **não avance para o deploy**. O ambiente virtual e o SQLite do computador são preservados, pois `.venv`, `.env` e `instance` não são incluídos no ZIP.

## Publicar a demonstração

Siga [docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md). O novo banco na nuvem começa vazio. A conta do professor local e os alunos de teste locais **não são transferidos automaticamente** para o Postgres.

## Verificação

- Localmente: `http://127.0.0.1:5000/saude` deve retornar `{"status":"ok"}`.
- Localmente: `python -m pytest -q` deve mostrar 24 testes aprovados (17 anteriores e 7 novos).
- No Render: abra `https://SEU-SITE.onrender.com/saude` e confirme o mesmo JSON.
- Acesse `https://SEU-SITE.onrender.com/professor/login` com conta de demonstração.
- Faça inscrição fictícia, presença e certificado demonstrativo.

## Restrições conhecidas

- Limite de requisições em memória. Para escala/uso real, adotar Redis, monitoramento e logs adequados.
- A criação de tabelas com `db.create_all()` é suficiente para começar, mas alterações futuras de esquema exigem migrações.
- E-mail SMTP não está ativado na demonstração. O Render Free bloqueia saída de portas SMTP comuns 25/465/587.
- A regra de 20 horas versus 75% ainda precisa de validação institucional.
- Cadastros de teste no SQLite local não são copiados para o Postgres novo.
- A verificação pública confirma **somente um registro demonstrativo**, nunca um certificado oficial.
