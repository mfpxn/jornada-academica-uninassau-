from datetime import date

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Atividade, Participante, Presenca, Professor, Certificado

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')


@professor_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('professor.painel'))
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip().lower()
        senha = request.form.get('senha', '')
        professor = db.session.query(Professor).filter_by(usuario=usuario).first()
        if professor and professor.is_active and professor.verificar_senha(senha):
            login_user(professor, remember=False)
            return redirect(url_for('professor.painel'))
        flash('Usuário ou senha incorretos.', 'erro')
    return render_template('professor/login.html')


@professor_bp.post('/sair')
@login_required
def sair():
    logout_user()
    return redirect(url_for('professor.login'))


@professor_bp.get('/')
@login_required
def painel():
    atividades = db.session.query(Atividade).order_by(Atividade.data, Atividade.id).all()
    totais = dict(
        db.session.query(Presenca.atividade_id, func.count(Presenca.id))
        .group_by(Presenca.atividade_id).all()
    )
    participantes_total = db.session.query(func.count(Participante.id)).scalar()
    return render_template('professor/painel.html', atividades=atividades,
                           totais=totais, participantes_total=participantes_total,
                           minimo=current_app.config['CERTIFICATE_MIN_HOURS'])


@professor_bp.route('/atividades/nova', methods=['GET', 'POST'])
@login_required
def nova_atividade():
    if request.method == 'POST':
        titulo = ' '.join(request.form.get('titulo', '').strip().split())
        data_str = request.form.get('data', '').strip()
        try:
            data_atividade = date.fromisoformat(data_str)
            horas = int(request.form.get('carga_horaria', ''))
        except (ValueError, TypeError):
            flash('Informe uma data válida e uma carga horária inteira.', 'erro')
            return render_template('professor/nova_atividade.html'), 400
        if len(titulo) < 4 or len(titulo) > 140 or not 1 <= horas <= 12:
            flash('Título entre 4 e 140 caracteres; carga horária entre 1 e 12 horas.', 'erro')
            return render_template('professor/nova_atividade.html'), 400
        nova = Atividade(titulo=titulo, data=data_atividade, carga_horaria=horas)
        db.session.add(nova)
        db.session.commit()
        flash('Atividade cadastrada. Você já pode registrar a presença.', 'sucesso')
        return redirect(url_for('professor.checkin', atividade_id=nova.id))
    return render_template('professor/nova_atividade.html')


@professor_bp.route('/atividades/<int:atividade_id>/checkin', methods=['GET', 'POST'])
@login_required
def checkin(atividade_id):
    atividade = db.get_or_404(Atividade, atividade_id)
    filtro = request.args.get('q', '').strip()[:80] if request.method == 'GET' else request.form.get('q', '').strip()[:80]

    if request.method == 'POST':
        enviados = request.form.getlist('participante_ids')
        if len(enviados) > 150:
            flash('Selecione até 150 participantes por operação.', 'erro')
            return redirect(url_for('professor.checkin', atividade_id=atividade.id, q=filtro))
        try:
            ids = {int(valor) for valor in enviados if int(valor) > 0}
        except ValueError:
            flash('Lista de participantes inválida.', 'erro')
            return redirect(url_for('professor.checkin', atividade_id=atividade.id, q=filtro))

        if not ids:
            flash('Selecione pelo menos um aluno sem presença registrada.', 'erro')
        else:
            existentes = set(db.session.scalars(db.select(Participante.id).where(Participante.id.in_(ids))).all())
            if len(existentes) != len(ids):
                flash('Há um participante inexistente na seleção.', 'erro')
            else:
                ja_presentes = set(db.session.scalars(db.select(Presenca.participante_id)
                                   .where(Presenca.atividade_id == atividade.id,
                                          Presenca.participante_id.in_(ids))).all())
                novos = ids - ja_presentes
                try:
                    for aluno_id in novos:
                        db.session.add(Presenca(participante_id=aluno_id,
                                               atividade_id=atividade.id,
                                               professor_id=current_user.id))
                    db.session.commit()
                    flash(f'{len(novos)} nova(s) presença(s) registrada(s).', 'sucesso')
                except IntegrityError:
                    db.session.rollback()
                    flash('Uma presença foi registrada simultaneamente. Atualize a página e tente novamente.', 'erro')
        return redirect(url_for('professor.checkin', atividade_id=atividade.id, q=filtro))

    consulta = db.session.query(Participante)
    if filtro:
        padrao = f'%{filtro}%'
        consulta = consulta.filter(or_(Participante.nome.ilike(padrao),
                                       Participante.matricula.ilike(padrao),
                                       Participante.codigo.ilike(padrao)))
    participantes = consulta.order_by(Participante.nome, Participante.id).limit(150).all()
    ids_pagina = [p.id for p in participantes]
    presentes = set()
    if ids_pagina:
        presentes = set(db.session.scalars(db.select(Presenca.participante_id)
                        .where(Presenca.atividade_id == atividade.id,
                               Presenca.participante_id.in_(ids_pagina))).all())
    total = db.session.query(func.count(Presenca.id)).filter_by(atividade_id=atividade.id).scalar()
    return render_template('professor/checkin.html', atividade=atividade, participantes=participantes,
                           presentes=presentes, total=total, filtro=filtro)


@professor_bp.get('/frequencia')
@login_required
def frequencia():
    filtro = request.args.get('q', '').strip()[:80]
    consulta = (
        db.session.query(Participante.id, Participante.nome, Participante.matricula,
                         Participante.curso, func.coalesce(func.sum(Atividade.carga_horaria), 0).label('horas'))
        .outerjoin(Presenca, Presenca.participante_id == Participante.id)
        .outerjoin(Atividade, Atividade.id == Presenca.atividade_id)
    )
    if filtro:
        padrao = f'%{filtro}%'
        consulta = consulta.filter(or_(Participante.nome.ilike(padrao),
                                       Participante.matricula.ilike(padrao)))
    registros = (consulta.group_by(Participante.id, Participante.nome, Participante.matricula, Participante.curso)
                 .order_by(Participante.nome).limit(150).all())
    ids = [aluno.id for aluno in registros]
    certificados = {}
    if ids:
        certificados = {c.participante_id: c for c in db.session.query(Certificado)
                        .filter(Certificado.participante_id.in_(ids)).all()}
    from app.services.email_certificados import smtp_configurado
    return render_template('professor/frequencia.html', registros=registros,
                           filtro=filtro, minimo=current_app.config['CERTIFICATE_MIN_HOURS'],
                           certificados=certificados, smtp_habilitado=smtp_configurado())
