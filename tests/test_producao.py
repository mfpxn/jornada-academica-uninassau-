import pytest

from app import create_app
from app.__init__ import normalizar_url_banco


def configuracao(tmp_path):
    return {
        "TESTING": True,
        "SECRET_KEY": "somente-para-testes",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI":
            "sqlite:///" + str(tmp_path / "teste-prod.db")
    }


def test_cabecalhos_de_seguranca(tmp_path):
    app = create_app(configuracao(tmp_path))
    resposta = app.test_client().get("/")

    assert resposta.status_code == 200
    assert resposta.headers["X-Frame-Options"] == "DENY"
    assert resposta.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in resposta.headers[
        "Content-Security-Policy"
    ]
    assert "PROTÓTIPO ACADÊMICO" in resposta.get_data(
        as_text=True
    )


def test_inscricao_sem_cache(tmp_path):
    app = create_app(configuracao(tmp_path))
    resposta = app.test_client().get("/inscricao")

    assert "no-store" in resposta.headers["Cache-Control"]


def test_normalizacao_postgresql():
    assert normalizar_url_banco(
        "postgresql://usuario@host/db"
    ) == "postgresql+psycopg://usuario@host/db"

    assert normalizar_url_banco(
        "postgres://usuario@host/db"
    ) == "postgresql+psycopg://usuario@host/db"

    assert normalizar_url_banco(
        "sqlite:///jornada.db"
    ) == "sqlite:///jornada.db"


def test_nuvem_exige_postgresql(monkeypatch):
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///jornada.db")
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("HTTPS_ONLY", "1")

    with pytest.raises(RuntimeError, match="PostgreSQL"):
        create_app()


def test_nuvem_exige_https(monkeypatch):
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://exemplo:senha@localhost/db"
    )
    monkeypatch.setenv("SECRET_KEY", "x" * 48)
    monkeypatch.setenv("HTTPS_ONLY", "0")

    with pytest.raises(RuntimeError, match="HTTPS_ONLY"):
        create_app()


def test_limite_tamanho_formulario(tmp_path):
    app = create_app(configuracao(tmp_path))
    resposta = app.test_client().post(
        "/inscricao",
        data={"nome": "A" * 40000}
    )

    assert resposta.status_code == 413


def test_professor_nao_duplica(monkeypatch, tmp_path):
    from app import db
    from app.models import Professor

    monkeypatch.setenv(
        "BOOTSTRAP_PROFESSOR_USER",
        "admin.demo"
    )
    monkeypatch.setenv(
        "BOOTSTRAP_PROFESSOR_PASSWORD",
        "SenhaForteDeTeste2026"
    )

    conf = configuracao(tmp_path)
    app = create_app(conf)
    create_app(conf)

    with app.app_context():
        professores = db.session.query(Professor).all()

        assert len(professores) == 1
        assert professores[0].usuario == "admin.demo"
        assert professores[0].verificar_senha(
            "SenhaForteDeTeste2026"
        )
