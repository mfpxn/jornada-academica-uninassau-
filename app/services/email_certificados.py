"""Envio opcional de PDF por SMTP, somente após solicitação do professor."""
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def smtp_configurado():
    config = current_app.config
    return all(config.get(chave) for chave in (
        'SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'SMTP_FROM',
    )) and config.get('SMTP_SECURITY') in ('ssl', 'starttls')


def enviar_certificado_por_email(destinatario, nome, codigo, pdf_bytes, verificacao=None):
    if not smtp_configurado():
        raise RuntimeError('SMTP não configurado para o envio de e-mails.')
    config = current_app.config
    mensagem = EmailMessage()
    mensagem['Subject'] = 'Modelo de certificado - 6a Jornada Academica (DEMONSTRACAO)'
    mensagem['From'] = config['SMTP_FROM']
    mensagem['To'] = destinatario
    mensagem.set_content(
        f'Ola, {nome}!\n\n'
        'Este e um CERTIFICADO DE DEMONSTRACAO, sem validade institucional.\n'
        'O arquivo PDF anexo foi gerado apenas para testes academicos.\n'
        f'Codigo do prototipo: {codigo}\n'
        + (f'Consulta do prototipo: {verificacao}\n' if verificacao else '')
        + '\nAtenciosamente,\nProjeto Academico Jornada UNINASSAU\n'
    )
    mensagem.add_attachment(pdf_bytes, maintype='application', subtype='pdf',
                           filename='certificado-demonstracao.pdf')
    contexto = ssl.create_default_context()
    if config['SMTP_SECURITY'] == 'ssl':
        with smtplib.SMTP_SSL(config['SMTP_HOST'], config['SMTP_PORT'],
                              timeout=15, context=contexto) as servidor:
            servidor.login(config['SMTP_USER'], config['SMTP_PASSWORD'])
            servidor.send_message(mensagem)
    else:
        with smtplib.SMTP(config['SMTP_HOST'], config['SMTP_PORT'], timeout=15) as servidor:
            servidor.ehlo()
            servidor.starttls(context=contexto)
            servidor.ehlo()
            servidor.login(config['SMTP_USER'], config['SMTP_PASSWORD'])
            servidor.send_message(mensagem)
