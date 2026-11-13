import pytest

from app import create_app
from app.routes.public import cpf_valido


@pytest.fixture
def cliente(tmp_path):
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'somente-para-testes',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'testes.db'),
    })
    return app.test_client()


def dados_validos():
    return {
        'nome': 'Maria Oliveira',
        'email': 'maria@example.com',
        'telefone': '86999998888',
        'cpf': '529.982.247-25',
        'matricula': 'ADS2026001',
        'curso': 'Análise e Desenvolvimento de Sistemas',
        'aceite': 'sim',
    }


def test_paginas_responsivas_disponiveis(cliente):
    assert cliente.get('/').status_code == 200
    assert cliente.get('/inscricao').status_code == 200
    assert cliente.get('/saude').json == {'status': 'ok'}


def test_cpf(cliente):
    assert cpf_valido('529.982.247-25')
    assert not cpf_valido('111.111.111-11')
    assert not cpf_valido('529.982.247-26')


def test_inscricao_cria_registro(cliente):
    resp = cliente.post('/inscricao', data=dados_validos())
    assert resp.status_code == 201
    assert 'Inscrição confirmada!' in resp.get_data(as_text=True)


def test_inscricao_repetida_bloqueada(cliente):
    assert cliente.post('/inscricao', data=dados_validos()).status_code == 201
    assert cliente.post('/inscricao', data=dados_validos()).status_code == 409


def test_inscricao_invalida_rejeitada(cliente):
    dados = dados_validos()
    dados['cpf'] = '123.123.123-12'
    assert cliente.post('/inscricao', data=dados).status_code == 400
