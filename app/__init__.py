import os
import re
from datetime import timedelta

import click
from dotenv import load_dotenv
from flask import Flask, request, current_app
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import IntegrityError

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'professor.login'
login_manager.login_message = 'Entre com a conta de professor para acessar esta página.'
login_manager.session_protection = 'strong'


@login_manager.user_loader
def carregar_professor(identificador):
    from .models import Professor
    try:
        return db.session.get(Professor, int(identificador))
    except (ValueError, TypeError):
        return None


def normalizar_url_banco(url):
    """Usa o driver psycopg v3 ao receber URLs PostgreSQL do Render."""
    if url.startswith('postgres://'):
        return 'postgresql+psycopg://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


def create_app(test_config=None):
    app = Flask(__name__)
    ambiente = os.environ.get('APP_ENV', 'local').lower()
    endereco_db = normalizar_url_banco(os.environ.get('DATABASE_URL', 'sqlite:///jornada.db'))
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', ''),
        SQLALCHEMY_DATABASE_URI=endereco_db,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('HTTPS_ONLY') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=4),
        MAX_CONTENT_LENGTH=32 * 1024,
        APP_ENV=ambiente,
        DEMO_ONLY=True,
        PREFERRED_URL_SCHEME='https' if os.environ.get('HTTPS_ONLY') == '1' else 'http',
        CERTIFICATE_MIN_HOURS=int(os.environ.get('CERTIFICATE_MIN_HOURS', '20')),
        # Só emitir documentos acadêmicos de demonstração enquanto o template
        # não estiver homologado pela instituição.
        CERTIFICATE_DEMO_ONLY=True,
        PUBLIC_BASE_URL=os.environ.get('PUBLIC_BASE_URL', '').rstrip('/'),
        SMTP_HOST=os.environ.get('SMTP_HOST', ''),
        SMTP_PORT=int(os.environ.get('SMTP_PORT', '587')),
        SMTP_USER=os.environ.get('SMTP_USER', ''),
        SMTP_PASSWORD=os.environ.get('SMTP_PASSWORD', ''),
        SMTP_FROM=os.environ.get('SMTP_FROM', ''),
        SMTP_SECURITY=os.environ.get('SMTP_SECURITY', 'starttls'),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Configure SECRET_KEY no arquivo .env antes de iniciar.')
    if ambiente != 'local' and not app.config.get('TESTING'):
        if not str(app.config['SQLALCHEMY_DATABASE_URI']).startswith('postgresql+psycopg://'):
            raise RuntimeError('Na nuvem use PostgreSQL: DATABASE_URL deve apontar para PostgreSQL.')
        if not app.config['SESSION_COOKIE_SECURE']:
            raise RuntimeError('Na nuvem defina HTTPS_ONLY=1 para proteger o cookie de sessao.')
        if len(app.config['SECRET_KEY']) < 32:
            raise RuntimeError('Na nuvem a SECRET_KEY precisa ter ao menos 32 caracteres.')
    # Ative somente atrás de proxy confiável (como a borda HTTPS do Render).
    if os.environ.get('TRUST_PROXY') == '1':
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from . import models  # noqa: F401
    from .routes.public import public_bp
    from .routes.professor import professor_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(professor_bp)
    from .routes.certificados import certificados_bp
    app.register_blueprint(certificados_bp)

    from .security import limitar_formularios
    app.before_request(limitar_formularios)

    @app.after_request
    def cabecalhos_de_seguranca(resposta):
        # Cabeçalhos adicionais, sem comprometer JS/CSS locais do aplicativo.
        resposta.headers['X-Content-Type-Options'] = 'nosniff'
        resposta.headers['X-Frame-Options'] = 'DENY'
        resposta.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        resposta.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        resposta.headers['Content-Security-Policy'] = (
            "default-src 'self'; base-uri 'self'; form-action 'self'; "
            "frame-ancestors 'none'; object-src 'none'; "
            "img-src 'self' data:; script-src 'self'; style-src 'self'"
        )
        if current_app.config.get('DEMO_ONLY'):
            resposta.headers['X-Robots-Tag'] = 'noindex, nofollow'
        if request.is_secure and os.environ.get('HTTPS_ONLY') == '1':
            resposta.headers['Strict-Transport-Security'] = 'max-age=31536000'
        if (request.blueprint == 'professor'
                or (request.blueprint == 'certificados'
                    and request.path.startswith('/professor/'))
                or request.path == '/inscricao'):
            resposta.headers['Cache-Control'] = 'no-store, private'
        return resposta

    @app.cli.command('criar-professor')
    def criar_professor():
        """Cria um professor com senha digitada no terminal (não salva senha no código)."""
        from .models import Professor
        usuario = click.prompt('Usuário do professor').strip().lower()
        if not re.fullmatch(r'[a-z0-9._-]{3,32}', usuario):
            raise click.ClickException('Usuário deve ter 3 a 32 letras minúsculas, números, ., _ ou -.')
        if db.session.query(Professor.id).filter_by(usuario=usuario).first():
            raise click.ClickException('Esse usuário já está cadastrado.')
        senha = click.prompt('Senha (mínimo 12 caracteres)', hide_input=True, confirmation_prompt=True)
        if len(senha) < 12:
            raise click.ClickException('A senha deve ter pelo menos 12 caracteres.')
        professor = Professor(usuario=usuario)
        professor.definir_senha(senha)
        try:
            db.session.add(professor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise click.ClickException('Não foi possível criar o professor. Confira se já existe.')
        click.echo('Professor cadastrado com sucesso.')

    # Mantido para o protótipo acadêmico. Alterações complexas do esquema deverão
    # ser feitas com migrações, não com create_all (que não altera tabelas existentes).
    with app.app_context():
        db.create_all()
        # Provisionamento inicial opcional no Render, sem publicar credenciais.
        # Depois do primeiro login, exclua essas variáveis do painel do Render.
        usuario_inicial = os.environ.get('BOOTSTRAP_PROFESSOR_USER', '').strip().lower()
        senha_inicial = os.environ.get('BOOTSTRAP_PROFESSOR_PASSWORD', '')
        if usuario_inicial or senha_inicial:
            if not re.fullmatch(r'[a-z0-9._-]{3,32}', usuario_inicial):
                raise RuntimeError('BOOTSTRAP_PROFESSOR_USER inválido.')
            if len(senha_inicial) < 12:
                raise RuntimeError('BOOTSTRAP_PROFESSOR_PASSWORD deve ter no mínimo 12 caracteres.')
            from .models import Professor
            if not db.session.query(Professor.id).filter_by(usuario=usuario_inicial).first():
                conta = Professor(usuario=usuario_inicial)
                conta.definir_senha(senha_inicial)
                db.session.add(conta)
                db.session.commit()

    return app
