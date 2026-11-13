from pathlib import Path
from app import create_app


def test_intro_nova_integrada(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "chave-teste",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI":
            "sqlite:///" + str(tmp_path / "intro.db"),
    })

    resposta = app.test_client().get("/")
    html = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert "intro-definitiva.css" in html
    assert "intro-definitiva.js" in html
    assert "intro-coin.js" not in html
    assert "moeda-intro.js" not in html


def test_arquivos_da_nova_abertura():
    raiz = Path(__file__).resolve().parents[1]

    css = raiz / "app/static/css/intro-definitiva.css"
    js = raiz / "app/static/js/intro-definitiva.js"

    assert css.exists()
    assert js.exists()
    assert "uni-abertura" in js.read_text(encoding="utf-8")
