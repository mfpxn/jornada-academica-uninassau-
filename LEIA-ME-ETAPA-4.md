# Etapa 4 - PDF demonstrativo, conferência e e-mail opcional

## Antes de instalar

- O ZIP inclui todos os arquivos necessários das etapas 2 e 3 e os novos arquivos da 4.
- Não inclui `.venv`, `.env`, `run.py` ou seu banco em `instance/`. Eles permanecem como estão.
- O documento é **somente um modelo acadêmico**: o template contém nomes institucionais pendentes, não possui assinaturas homologadas e traz uma indicação explícita de **SEM VALIDADE INSTITUCIONAL**.
- O arquivo do professor menciona **20 horas**, mas os slides do Hackathon também mencionam **75%**. O aplicativo mantém `CERTIFICATE_MIN_HOURS=20` para os testes. Não libere documentos oficiais sem confirmar a regra.

## Instalação (Ubuntu/Linux)

1. Interrompa o Flask com `Ctrl+C`.
2. Baixe o `jornada-etapa4.zip` e execute na raiz do projeto:

```bash
cd ~/Projetos/jornada-academica-uninassau
source .venv/bin/activate
cp -a app ../jornada-academica-backup-etapa3
ZIP=$(find "$HOME" -maxdepth 5 -type f -name 'jornada-etapa4*.zip' -print -quit 2>/dev/null)
if [ -n "$ZIP" ]; then
    python -m zipfile -e "$ZIP" .
    echo 'Etapa 4 extraída!'
else
    echo 'Não encontrei o ZIP. Faça o download antes de continuar.'
fi
python -m pytest -q
python run.py
```

3. Acesse `http://127.0.0.1:5000/professor/login` e entre com o professor já cadastrado. **Não recrie a conta**, pois ela continua no banco.
4. Abra `http://127.0.0.1:5000/professor/frequencia`.
5. Para o aluno de teste, registre presenças em atividades que totalizem ao menos 20h; por exemplo, duas atividades distintas de 10h cada.
6. Na lista, clique em **Gerar PDF demonstrativo** e depois em **Baixar PDF** ou **Conferir código**.

## Novidades

- Nova tabela `certificados`, criada automaticamente pelo SQLite existente sem apagar alunos, atividades ou professores.
- Soma segura das horas registradas; nenhuma emissão antes da carga mínima.
- Um registro de emissão por participante; cliques repetidos não criam cópias no banco.
- Arquivo PDF em A4 paisagem baseado no template, com nome ajustado, código aleatório e marca de demonstração.
- Download restrito ao professor logado, com proteção CSRF no ato da emissão.
- Consulta pública por token de 128 bits com nome abreviado e sem CPF/e-mail.
- Envio SMTP opcional do PDF em anexo, mediante clique do professor; fica **desativado por padrão**.
- Testes adicionais para emissão autorizada, frequência insuficiente, emissão única, download, conferência e e-mail simulado.

## E-mail: configuração SOMENTE para testes (opcional)

Adicione no seu `.env`, com valores reais e seguros, sem publicar senhas:

```ini
SMTP_HOST=smtp.seu-provedor.com
SMTP_PORT=587
SMTP_USER=sua-conta
SMTP_PASSWORD=sua-senha-de-aplicativo
SMTP_FROM=sua-conta@seudominio.com
SMTP_SECURITY=starttls
# Preencha quando houver domínio público HTTPS, para habilitar QR de conferência:
# PUBLIC_BASE_URL=https://seu-dominio.com
```

**Não use credenciais reais em repositórios públicos.** Reinicie o Flask após mudar o `.env`. Se o SMTP não estiver configurado, o botão de envio não aparece.

## Importante antes da hospedagem pública

O produto ainda é um protótipo local e não deve receber CPF ou dados pessoais reais sem política de privacidade, avaliação LGPD, backups, HTTPS, proteção contra força bruta, revisão de autenticação, gestão de secrets e confirmação das regras de certificação. O arquivo de demonstração não é certificado oficial e nem foi assinado eletronicamente.
