# Publicação da demonstração no Render, passo a passo

**Proibido usar dados reais nesta demonstração:** o sistema é uma atividade acadêmica em desenvolvimento, sem homologação de segurança e sem adequação institucional formal à LGPD.

## 0. Antes do GitHub

Confirme que todos os testes passaram no seu Linux. Revise arquivos que serão versionados:

```bash
cd ~/Projetos/jornada-academica-uninassau
source .venv/bin/activate
python -m pytest -q
git status --short
git check-ignore .env instance/jornada.db .venv/pyvenv.cfg
```

O Git **não** deve incluir `.env`, bancos SQLite, senhas ou arquivos do ambiente virtual. Não envie banco de testes com CPFs para o GitHub. Se segredos já estiverem no histórico, será necessário revogá-los e limpar o histórico, não basta editar o `.gitignore`.

## 1. Enviar o projeto ao GitHub

Crie um **novo repositório privado** chamado `jornada-academica-uninassau` na sua conta do GitHub, sem marcar README inicial (o projeto já tem um). No terminal:

```bash
cd ~/Projetos/jornada-academica-uninassau
# caso já exista Git, o comando abaixo é inofensivo
git init
git add .
git status --short
# confira a lista para ter certeza de que não inclui .env nem bancos
git commit -m "feat: prepara demonstracao com Render e verificacoes de seguranca"
git branch -M main
git remote -v
```

Se `git remote -v` não mostrar `origin`, adicione a URL **real** do repositório que você criou:

```bash
git remote add origin https://github.com/SEU_USUARIO/jornada-academica-uninassau.git
git push -u origin main
```

Se `origin` já existir, **não** adicione outra vez; confirme que aponta para o repositório certo e use `git push -u origin main`.

## 2. Criar Web Service + PostgreSQL

1. Acesse https://dashboard.render.com/ e faça login.
2. Selecione **New > Blueprint** (ou o fluxo de Blueprints da interface atual).
3. Autorize o acesso ao repositório privado no GitHub, se necessário.
4. Selecione `jornada-academica-uninassau`. O Render detectará o arquivo `render.yaml` no diretório raiz.
5. Revise os recursos: 1 web service `jornada-academica-demo` no plano `free` e 1 banco `jornada-academica-db` no plano `free`.
6. No formulário de variáveis de ambiente para o primeiro deploy, informe:
   - `BOOTSTRAP_PROFESSOR_USER`: nome de login de 3 a 32 caracteres, sem espaços, usando letras minúsculas, números, ponto, traço ou sublinhado. Exemplo fictício: `docente.demo`.
   - `BOOTSTRAP_PROFESSOR_PASSWORD`: uma senha **forte e única**, de ao menos 12 caracteres. **Não a envie em chat ou print.**
7. Confira eventuais cobranças e escolha opções gratuitas somente se forem disponibilizadas na sua conta; finalize a criação.
8. Aguarde o status de deploy concluído e consulte os logs **sem compartilhar senhas ou variáveis de ambiente**.

A senha informada acima é usada para criar a conta uma única vez, se ainda não existir. O banco do Render nasce **vazio**; o login local criado anteriormente não estará nesse banco. **Após confirmar o login na nuvem, remova as duas variáveis `BOOTSTRAP_...` do Render Dashboard** para não manter uma senha de provisionamento armazenada desnecessariamente. Remover as variáveis não apaga a conta já criada no banco.

## 3. Abrir e testar

O Render apresentará uma URL própria, parecida com `https://jornada-academica-demo.onrender.com` (a URL real depende da disponibilidade do nome). Teste:

1. `/saude`: JSON `{"status":"ok"}`.
2. `/`: logo e aviso de dados fictícios.
3. `/inscricao`: cadastre um participante totalmente fictício.
4. `/professor/login`: entre com o usuário criado no Render.
5. `/professor/atividades/nova`: crie duas atividades de 10h.
6. Nos dois check-ins, marque o participante fictício.
7. `/professor/frequencia`: confirme 20h e gere o PDF demonstrativo.
8. Confira o código de verificação e o aviso de ausência de validade institucional.
9. Abra o site em um celular e teste a responsividade.

Para a apresentação em 16/11, abra o site 5–10 minutos antes, porque a instância gratuita pode precisar despertar. Tenha um plano B local, com `python run.py` e dados fictícios, caso haja indisponibilidade da nuvem.

## Limitações e cautelas

- **Render Free Postgres expira 30 dias após criado**, tem 1 GB, não faz backups e é destinado a testes, não a dados de produção.
- **Render Free Web Service** entra em repouso quando ocioso e pode demorar a acordar.
- **SMTP Free:** portas de saída 25, 465 e 587 são bloqueadas. O envio de certificado por SMTP não deve fazer parte do pitch na nuvem sem outro serviço compatível e configuração responsável.
- A solução usa um único Gunicorn worker de demonstração, com rate limit em memória. Para operação real: migrar para controle distribuído (Redis), monitoramento e revisão de segurança.
- O `.python-version` fixa Python 3.11, para evitar variação do padrão do provedor.
- O código `db.create_all()` cria tabelas novas, mas **não migra esquemas existentes**. Migrações devem ser planejadas antes de ampliar o sistema.
- Para uso institucional real é necessária aprovação da instituição, política de privacidade, base legal adequada, termos, medidas de segurança, retenção/exclusão de dados, backup e recuperação, revisões jurídicas/técnicas.

Fontes: documentação oficial https://render.com/docs/deploy-flask, https://render.com/docs/blueprint-spec, https://render.com/docs/free e https://render.com/docs/python-version.
