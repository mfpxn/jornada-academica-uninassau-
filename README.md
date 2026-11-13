# 6ª Jornada Acadêmica — UNINASSAU Teresina (protótipo)

Projeto acadêmico de Engenharia de Software: inscrição, painel do professor, frequência e certificado PDF **demonstrativo**. Evento previsto para 09 e 10/12/2026. Apresentação do protótipo em 16/11/2026.

**Atenção:** protótipo não homologado. Utilizar **somente dados fictícios**, sem emitir documentos institucionais reais.

## Iniciar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Crie .env com uma SECRET_KEY segura e DATABASE_URL=sqlite:///jornada.db
python -m pytest -q
python run.py
```

Acesse `http://127.0.0.1:5000`.

Criar professor local:

```bash
flask --app run:app criar-professor
```

## Guia

- [LEIA-ME-ETAPA-5.md](LEIA-ME-ETAPA-5.md): atualização da Etapa 5
- [docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md): hospedar demonstração
- [docs/PITCH_5_MINUTOS.md](docs/PITCH_5_MINUTOS.md): apresentação
- [docs/QA_CHECKLIST.md](docs/QA_CHECKLIST.md): checklist final

No Render, o provisionamento inicial do professor usa `BOOTSTRAP_PROFESSOR_USER` e `BOOTSTRAP_PROFESSOR_PASSWORD` inseridas como variáveis de ambiente secretas. Remova-as do Render Dashboard após o primeiro login.

**Limitações:** regras 20h vs. 75% pendentes de aprovação institucional, e-mail desabilitado por padrão, rate limit em memória, banco gratuito na nuvem expira em 30 dias, PDFs demonstrativos sem assinatura institucional.
