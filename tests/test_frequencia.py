import pytest

from app import create_app, db
from app.models import Atividade, Participante, Presenca, Professor


@pytest.fixture
def ambiente(tmp_path):
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'chave-de-teste-apenas',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'frequencia.db'),
        'CERTIFICATE_MIN_HOURS': 20,
    })
    with app.app_context():
        professor = Professor(usuario='professor01')
        professor.definir_senha('SenhaFortedeTestes2026')
        aluno = Participante(codigo='ABC123456789', nome='Maria Oliveira',
                            email='maria2@example.com', telefone='86999998888',
                            cpf='52998224725', matricula='ADS2026001',
                            curso='Análise e Desenvolvimento de Sistemas')
        db.session.add_all([professor, aluno])
        db.session.commit()
        aluno_id = aluno.id
    return app, app.test_client(), aluno_id


def autenticar(cliente):
    resposta = cliente.post('/professor/login', data={
        'usuario': 'professor01', 'senha': 'SenhaFortedeTestes2026',
    })
    assert resposta.status_code == 302


def test_painel_protegido(ambiente):
    _, cliente, _ = ambiente
    resposta = cliente.get('/professor/')
    assert resposta.status_code == 302
    assert '/professor/login' in resposta.location
    assert cliente.get('/professor/login').status_code == 200
    assert cliente.post('/professor/login', data={'usuario': 'professor01', 'senha': 'errada'}).status_code == 200


def test_professor_cria_atividade(ambiente):
    app, cliente, _ = ambiente
    autenticar(cliente)
    resp = cliente.post('/professor/atividades/nova', data={
        'titulo': 'Oficina Python', 'data': '2026-12-09', 'carga_horaria': '5'
    })
    assert resp.status_code == 302
    with app.app_context():
        assert db.session.query(Atividade).count() == 1
    assert cliente.get('/professor/').status_code == 200


def test_registro_unico_e_horas(ambiente):
    app, cliente, aluno_id = ambiente
    autenticar(cliente)
    ids = []
    for numero in range(2):
        resp = cliente.post('/professor/atividades/nova', data={
            'titulo': f'Oficina {numero}', 'data': '2026-12-09', 'carga_horaria': '10'
        })
        assert resp.status_code == 302
        with app.app_context():
            ids.append(db.session.query(Atividade.id).order_by(Atividade.id.desc()).first()[0])
    for atividade_id in ids:
        url = f'/professor/atividades/{atividade_id}/checkin'
        assert cliente.get(url).status_code == 200
        assert cliente.post(url, data={'participante_ids': str(aluno_id)}).status_code == 302
        assert cliente.post(url, data={'participante_ids': str(aluno_id)}).status_code == 302
    with app.app_context():
        assert db.session.query(Presenca).count() == 2
    relatorio = cliente.get('/professor/frequencia')
    assert relatorio.status_code == 200
    assert '20h' in relatorio.get_data(as_text=True)
    assert 'Carga horária atingida' in relatorio.get_data(as_text=True)


def test_checkin_rejeita_id_inexistente(ambiente):
    app, cliente, _ = ambiente
    autenticar(cliente)
    cliente.post('/professor/atividades/nova', data={
        'titulo': 'Oficina Dados', 'data': '2026-12-10', 'carga_horaria': '6'
    })
    with app.app_context():
        atividade_id = db.session.query(Atividade.id).first()[0]
    resposta = cliente.post(f'/professor/atividades/{atividade_id}/checkin',
                            data={'participante_ids': '999999'})
    assert resposta.status_code == 302
    with app.app_context():
        assert db.session.query(Presenca).count() == 0


def test_logout_encerra_sessao(ambiente):
    _, cliente, _ = ambiente
    autenticar(cliente)
    assert cliente.post('/professor/sair').status_code == 302
    assert cliente.get('/professor/frequencia').status_code == 302
