"""Testes de integração dos novos templates com o Flask."""
from app import create_app


def cliente(tmp_path):
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "teste-front-end",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(tmp_path / "visual.db"),
    })
    return app.test_client()


def test_pagina_3d_carrega_com_assets(tmp_path):
    resposta = cliente(tmp_path).get("/")
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "experience.css" in html
    assert "experience.js" in html
    assert 'data-tilt' in html
    assert "logo-jornada.jpeg" in html


def test_pilares_interativos_estao_na_pagina(tmp_path):
    html = cliente(tmp_path).get("/").get_data(as_text=True)
    for pilar in ("ensino", "pesquisa", "extensao", "inovacao", "transformacao"):
        assert f'data-pillar="{pilar}"' in html
    assert 'role="tabpanel"' in html


def test_formulario_preserva_campos_e_csrf(tmp_path):
    html = cliente(tmp_path).get("/inscricao").get_data(as_text=True)
    for campo in ("nome", "email", "telefone", "cpf", "matricula", "curso", "aceite"):
        assert f'name="{campo}"' in html
    assert 'name="csrf_token"' in html
    assert 'id="xp-form-progress-bar"' in html
