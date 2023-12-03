import pytest
from flask import json
from app import create_app
from app.models.models import db, Usuario, Role


@pytest.fixture(scope='module')
def client():
    """
    Fixture to create a test client for the Flask application.
    """
    app = create_app('testing')
    with app.test_client() as client:
        yield client


headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}


def test_registro(client):
    # Test new user registration
    response = client.post('/auth/registro', json={
        'nombre': 'testuser',
        'contraseña': 'testpassword',
        'rol': 'Administrador'
    }, headers=headers)

    assert response.status_code == 201 or response.status_code == 409
    assert response.get_json()['http_code'] in [201, 409]
    if response.get_json().keys().__contains__('usuario'):
        assert response.get_json()['usuario'] == 'testuser'

    # Test existing user registration
    response = client.post('/auth/registro', json={
        'nombre': 'testuser',
        'contraseña': 'testpassword',
        'rol': 'Administrador'
    }, headers=headers)

    assert response.status_code == 409
    assert response.get_json()['http_code'] == 409

    # Test non-existing role
    response = client.post('/auth/registro', json={
        'nombre': 'testuser',
        'contraseña': 'testpassword',
        'rol': 'test'
    }, headers=headers)

    assert response.status_code == 409
    assert response.get_json()['http_code'] == 409


