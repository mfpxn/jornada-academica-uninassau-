import re
import secrets

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Participante

public_bp = Blueprint('public', __name__)


def so_digitos(texto):
    return re.sub(r'\D', '', texto or '')


def cpf_valido(cpf):
    cpf = so_digitos(cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True


@public_bp.get('/')
def inicio():
    return render_template('index.html')


@public_bp.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'GET':
        return render_template('inscricao.html', dados={})

    dados = {
        'nome': ' '.join(request.form.get('nome', '').strip().split()),
        'email': request.form.get('email', '').strip().lower(),
        'telefone': so_digitos(request.form.get('telefone')),
        'cpf': so_digitos(request.form.get('cpf')),
        'matricula': request.form.get('matricula', '').strip().upper(),
        'curso': ' '.join(request.form.get('curso', '').strip().split()),
    }
    erros = []
    if len(dados['nome']) < 3 or len(dados['nome']) > 120 or len(dados['nome'].split()) < 2:
        erros.append('Informe o nome completo (nome e sobrenome).')
    try:
        dados['email'] = validate_email(dados['email'], check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        erros.append('Informe um e-mail válido.')
    if len(dados['telefone']) not in (10, 11):
        erros.append('Informe um telefone com DDD.')
    if not cpf_valido(dados['cpf']):
        erros.append('Informe um CPF válido.')
    if not re.fullmatch(r'[A-Z0-9.\-]{4,30}', dados['matricula']):
        erros.append('Informe uma matrícula de 4 a 30 caracteres válidos.')
    if not 2 <= len(dados['curso']) <= 120:
        erros.append('Informe o curso.')
    if request.form.get('aceite') != 'sim':
        erros.append('É necessário aceitar o tratamento dos dados para a inscrição.')

    if erros:
        for erro in erros:
            flash(erro, 'erro')
        return render_template('inscricao.html', dados=dados), 400

    existente = db.session.query(Participante.id).filter(
        or_(Participante.cpf == dados['cpf'],
            Participante.email == dados['email'],
            Participante.matricula == dados['matricula'])
    ).first()
    if existente:
        flash('Já existe inscrição com esse CPF, e-mail ou matrícula.', 'erro')
        return render_template('inscricao.html', dados=dados), 409

    participante = Participante(codigo=secrets.token_hex(6).upper(), **dados)
    try:
        db.session.add(participante)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Já existe inscrição com esse CPF, e-mail ou matrícula.', 'erro')
        return render_template('inscricao.html', dados=dados), 409

    # O código é exibido apenas após o cadastro, não em uma consulta pública.
    return render_template('sucesso.html', participante=participante), 201


@public_bp.get('/saude')
def saude():
    return {'status': 'ok'}
