import pytest
from app import create_app
#from app.models.models import db, Usuario, Role
from werkzeug.security import generate_password_hash,check_password_hash

@pytest.fixture(scope='module')
def client():
    """
    Fixture to create a test client for the Flask application.
    """
    app = create_app('testing')
    app.testing = True
    with app.test_client() as client:
        #with app.app_context():
        #    db.create_all()
        yield client


headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}


def test_registro(client):
    # Test new user registration
    response = client.post('/auth/registro', json={
        'nombre': 'testuser3',
        'contraseña': 'testpassword3',
        'rol': 'Administrador'
    }, headers=headers)

    assert response.status_code == 201 or response.status_code == 409
    assert response.get_json()['http_code'] in [201, 409]
    if response.get_json().keys().__contains__('usuario'):
        assert response.get_json()['usuario'] == 'testuser3'

    # Test existing user registration
    response = client.post('/auth/registro', json={
        'nombre': 'testuser3',
        'contraseña': 'testpassword3',
        'rol': 'Administrador'
    }, headers=headers)

    assert response.status_code == 409
    assert response.get_json()['http_code'] == 409

    # Test non-existing role
    #Por que se genera otra contraseña si hemos puesto la misma?
    response = client.post('/auth/registro', json={
        'nombre': 'testuser3',
        'contraseña': 'testpassword3',
        'rol': 'test'
    }, headers=headers)

    assert response.status_code == 409
    assert response.get_json()['http_code'] == 409


def test_login(client):
    # Test not sending data
    response = client.post('/auth/login', json={},headers=headers)
    assert response.status_code == 400

    # Test successful login
    response = client.post('/auth/login', json={
        'nombre': 'testuser3',
        'contraseña': 'testpassword3'
    },headers=headers)
    assert response.status_code == 200

    # Test unsuccessful login
    response = client.post('/auth/login', json={
        'nombre': 'testuser3',
        'contraseña': 'wrongpassword'
    },headers=headers)
    assert response.status_code == 400
    assert 'Usuario o Contraseña incorrectos' in response.get_json()['mensaje']

