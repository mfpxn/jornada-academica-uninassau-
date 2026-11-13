"""Emissão demonstrativa, download autenticado, e validação do código de teste."""
import secrets
import smtplib
from datetime import datetime, timezone

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Certificado, Participante
from app.services.certificados import (gerar_pdf_certificado, horas_participante,
                                        pode_emitir, url_verificacao)
from app.services.email_certificados import (enviar_certificado_por_email,
                                             smtp_configurado)

certificados_bp = Blueprint('certificados', __name__)


def _verificar_frequencia(participante_id):
    if not pode_emitir(participante_id):
        abort(409, description='Aluno ainda não atingiu a carga horária mínima.')


@certificados_bp.post('/professor/certificados/<int:participante_id>/emitir')
@login_required
def emitir(participante_id):
    participante = db.get_or_404(Participante, participante_id)
    _verificar_frequencia(participante.id)

    existente = db.session.query(Certificado).filter_by(participante_id=participante.id).first()
    if not existente:
        registro = Certificado(
            participante_id=participante.id,
            codigo_verificacao=secrets.token_hex(16),
            horas_emitidas=horas_participante(participante.id),
        )
        try:
            db.session.add(registro)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Outros administradores podem ter emitido simultaneamente.
            if not db.session.query(Certificado.id).filter_by(participante_id=participante.id).first():
                raise
    flash('Modelo de certificado gerado. Confira o PDF demonstrativo.', 'sucesso')
    return redirect(url_for('certificados.baixar', participante_id=participante.id))


@certificados_bp.get('/professor/certificados/<int:participante_id>/pdf')
@login_required
def baixar(participante_id):
    participante = db.get_or_404(Participante, participante_id)
    certificado = db.session.query(Certificado).filter_by(participante_id=participante.id).first()
    if certificado is None:
        abort(404, description='Nenhum certificado de demonstração foi emitido.')
    _verificar_frequencia(participante_id)
    arquivo = gerar_pdf_certificado(participante, certificado)
    resposta = send_file(arquivo, mimetype='application/pdf', as_attachment=True,
                         download_name=f'certificado-demo-{participante.codigo}.pdf')
    resposta.headers['Cache-Control'] = 'no-store, private'
    return resposta


@certificados_bp.post('/professor/certificados/<int:participante_id>/enviar-email')
@login_required
def enviar_email(participante_id):
    participante = db.get_or_404(Participante, participante_id)
    certificado = db.session.query(Certificado).filter_by(participante_id=participante.id).first()
    if certificado is None:
        abort(404, description='Emita o modelo antes de enviar.')
    _verificar_frequencia(participante_id)
    if not smtp_configurado():
        flash('Envio indisponível: configure as credenciais SMTP no .env.', 'erro')
        return redirect(url_for('professor.frequencia'))
    arquivo = gerar_pdf_certificado(participante, certificado)
    try:
        enviar_certificado_por_email(
            destinatario=participante.email,
            nome=participante.nome,
            codigo=certificado.codigo_verificacao,
            pdf_bytes=arquivo.getvalue(),
            verificacao=url_verificacao(certificado.codigo_verificacao),
        )
    except (OSError, smtplib.SMTPException) as exc:
        current_app.logger.warning('Falha no envio de certificado para participante #%s: %s',
                                   participante.id, type(exc).__name__)
        flash('Não foi possível enviar o e-mail. Confira a configuração SMTP.', 'erro')
        return redirect(url_for('professor.frequencia'))
    certificado.email_enviado_em = datetime.now(timezone.utc)
    db.session.commit()
    flash('E-mail com certificado de demonstração enviado.', 'sucesso')
    return redirect(url_for('professor.frequencia'))


@certificados_bp.get('/certificados/verificar/<codigo>')
def verificar(codigo):
    # Evita buscas malformadas; token único aleatório de 128 bits.
    if len(codigo) != 32 or any(c not in '0123456789abcdef' for c in codigo):
        abort(404)
    certificado = db.session.query(Certificado).filter_by(codigo_verificacao=codigo).first()
    if certificado is None:
        abort(404)
    participante = db.get_or_404(Participante, certificado.participante_id)
    fragmentos = participante.nome.split()
    nome_resumido = fragmentos[0] + (' ' + fragmentos[-1][0] + '.' if len(fragmentos) > 1 else '')
    vigente = pode_emitir(participante.id)
    resposta = render_template('certificados/verificar.html', certificado=certificado,
                               nome_resumido=nome_resumido, vigente=vigente)
    # Evitar indexação e cache dos dados de validação (a página só tem nome parcial).
    return resposta, 200, {'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow'}
