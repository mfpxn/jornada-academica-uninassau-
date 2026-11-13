from datetime import datetime, timezone
from flask_login import UserMixin
from . import db
from werkzeug.security import check_password_hash, generate_password_hash


class Participante(db.Model):
    __tablename__ = 'participantes'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(16), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(11), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False, index=True)
    matricula = db.Column(db.String(30), unique=True, nullable=False)
    curso = db.Column(db.String(120), nullable=False)
    consentimento_em = db.Column(db.DateTime(timezone=True), nullable=False,
                                 default=lambda: datetime.now(timezone.utc))
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(timezone.utc))


class Professor(UserMixin, db.Model):
    __tablename__ = 'professores'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(32), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(timezone.utc))

    @property
    def is_active(self):
        return bool(self.ativo)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Atividade(db.Model):
    __tablename__ = 'atividades'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140), nullable=False)
    data = db.Column(db.Date, nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    criada_em = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(timezone.utc))
    __table_args__ = (
        db.CheckConstraint('carga_horaria >= 1 AND carga_horaria <= 12', name='ck_atividade_horas'),
    )


class Presenca(db.Model):
    __tablename__ = 'presencas'

    id = db.Column(db.Integer, primary_key=True)
    participante_id = db.Column(db.Integer, db.ForeignKey('participantes.id'), nullable=False, index=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False, index=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    registrada_em = db.Column(db.DateTime(timezone=True), nullable=False,
                              default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('participante_id', 'atividade_id', name='uq_presenca_participante_atividade'),
    )


class Certificado(db.Model):
    """Registro de emissão do PDF de DEMONSTRAÇÃO para o evento.

    A unicidade impede emissões duplicadas para o mesmo participante.
    O token aleatório serve exclusivamente para consulta do modelo acadêmico.
    """
    __tablename__ = 'certificados'

    id = db.Column(db.Integer, primary_key=True)
    participante_id = db.Column(
        db.Integer, db.ForeignKey('participantes.id'),
        nullable=False, unique=True, index=True
    )
    codigo_verificacao = db.Column(db.String(32), nullable=False, unique=True, index=True)
    horas_emitidas = db.Column(db.Integer, nullable=False)
    emitido_em = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    email_enviado_em = db.Column(db.DateTime(timezone=True), nullable=True)

    participante = db.relationship('Participante', backref=db.backref('certificado', uselist=False))
