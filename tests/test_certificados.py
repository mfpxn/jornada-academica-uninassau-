"""Testes do fluxo de PDF acadêmico: não exige serviço externo de e-mail."""
from unittest.mock import patch

import pytest

from app import create_app, db
from app.models import Atividade, Certificado, Participante, Presenca, Professor


@pytest.fixture
def cenario(tmp_path):
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'somente-para-testes-certificado',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'certificados.db'),
        'CERTIFICATE_MIN_HOURS': 20,
    })
    with app.app_context():
        professor = Professor(usuario='docente01')
        professor.definir_senha('SenhaForte2026paraTestes')
        aluno = Participante(
            codigo='A12345678901', nome='Maria Oliveira', email='maria@example.com',
            telefone='86999998888', cpf='52998224725', matricula='ADS2026002',
            curso='Análise e Desenvolvimento de Sistemas',
        )
        db.session.add_all([professor, aluno])
        db.session.commit()
        ids = {'professor': professor.id, 'aluno': aluno.id}
    return app, app.test_client(), ids


def logar(client):
    resposta = client.post('/professor/login', data={
        'usuario': 'docente01', 'senha': 'SenhaForte2026paraTestes',
    })
    assert resposta.status_code == 302


def aprovar(app, ids):
    """Duas atividades de 10h com presenças distintas, totalizando 20h."""
    from datetime import date
    with app.app_context():
        for numero in (1, 2):
            atividade = Atividade(titulo=f'Oficina {numero}', data=date(2026, 12, numero + 8), carga_horaria=10)
            db.session.add(atividade)
            db.session.flush()
            db.session.add(Presenca(participante_id=ids['aluno'], atividade_id=atividade.id,
                                   professor_id=ids['professor']))
        db.session.commit()


def test_emissao_requer_login(cenario):
    _, client, ids = cenario
    resposta = client.post(f"/professor/certificados/{ids['aluno']}/emitir")
    assert resposta.status_code == 302
    assert '/professor/login' in resposta.location


def test_sem_frequencia_nao_emite(cenario):
    app, client, ids = cenario
    logar(client)
    resposta = client.post(f"/professor/certificados/{ids['aluno']}/emitir")
    assert resposta.status_code == 409
    with app.app_context():
        assert db.session.query(Certificado).count() == 0


def test_emissao_gera_pdf_valido_e_so_um_registro(cenario):
    app, client, ids = cenario
    aprovar(app, ids)
    logar(client)
    url = f"/professor/certificados/{ids['aluno']}/emitir"
    resposta = client.post(url)
    assert resposta.status_code == 302
    assert f"/professor/certificados/{ids['aluno']}/pdf" in resposta.location
    pdf = client.get(resposta.location)
    assert pdf.status_code == 200
    assert pdf.mimetype == 'application/pdf'
    assert pdf.data.startswith(b'%PDF-')
    assert len(pdf.data) > 90_000
    assert 'attachment;' in pdf.headers['Content-Disposition']
    assert pdf.headers['Cache-Control'] == 'no-store, private'
    assert client.post(url).status_code == 302
    with app.app_context():
        assert db.session.query(Certificado).count() == 1


def test_verificacao_publica_minimiza_dados(cenario):
    app, client, ids = cenario
    aprovar(app, ids)
    logar(client)
    assert client.post(f"/professor/certificados/{ids['aluno']}/emitir").status_code == 302
    with app.app_context():
        codigo = db.session.query(Certificado.codigo_verificacao).scalar()
    resposta = client.get(f'/certificados/verificar/{codigo}')
    texto = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert 'Maria O.' in texto
    assert '52998224725' not in texto
    assert 'maria@example.com' not in texto
    assert 'sem validade institucional' in texto.lower()
    assert client.get('/certificados/verificar/invalid!').status_code == 404
    assert client.get('/certificados/verificar/' + 'f' * 32).status_code == 404


def test_pdf_nao_emitido_retorna_404(cenario):
    _, client, ids = cenario
    logar(client)
    assert client.get(f"/professor/certificados/{ids['aluno']}/pdf").status_code == 404


def test_email_sem_smtp_nao_envia(cenario):
    app, client, ids = cenario
    aprovar(app, ids)
    logar(client)
    client.post(f"/professor/certificados/{ids['aluno']}/emitir")
    resposta = client.post(f"/professor/certificados/{ids['aluno']}/enviar-email")
    assert resposta.status_code == 302
    with app.app_context():
        assert db.session.query(Certificado).first().email_enviado_em is None


def test_email_configurado_envia_sob_acao_explicita(cenario):
    app, client, ids = cenario
    aprovar(app, ids)
    logar(client)
    client.post(f"/professor/certificados/{ids['aluno']}/emitir")
    app.config.update(SMTP_HOST='smtp.example.com', SMTP_PORT=587,
                      SMTP_USER='teste', SMTP_PASSWORD='senha-teste',
                      SMTP_FROM='jornada@example.com', SMTP_SECURITY='starttls')
    with patch('app.routes.certificados.enviar_certificado_por_email') as envio:
        resposta = client.post(f"/professor/certificados/{ids['aluno']}/enviar-email")
        assert resposta.status_code == 302
        envio.assert_called_once()
        assert envio.call_args.kwargs['pdf_bytes'].startswith(b'%PDF-')
    with app.app_context():
        assert db.session.query(Certificado).first().email_enviado_em is not None
