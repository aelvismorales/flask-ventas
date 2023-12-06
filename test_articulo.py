import pytest
from app import create_app

@pytest.fixture(scope='module')
def client():
    """
    Fixture to create a test client for the Flask application.
    """
    app = create_app('testing')
    app.testing = True
    with app.test_client() as client:
        yield client

def get_auth_token(client):
    response=client.post('/auth/login',json={'nombre':'testuser3','contraseña':'testpassword3'})
    return response.get_json()['token']

def test_crear_articulo(client):
    token=get_auth_token(client)

    # Test no nombre or unidad or cantidad
    response = client.post('/articulo/crear', json={}, headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 409

    # Test crear articulo
    response = client.post('/articulo/crear', json={
        'nombre': 'testarticulo',
        'unidad': 'testunidad',
        'cantidad': 10
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 201 or response.status_code == 409

def test_ver_articulo(client):
    token=get_auth_token(client)

    # Test ver articulo
    response = client.get('/articulo/ver/1', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404

def test_editar_articulo(client):

    token=get_auth_token(client)

    # Test editar articulo
    response = client.put('/articulo/editar/1', json={
        'nombre': 'testarticulo',
        'unidad': 'testunidad',
        'cantidad': 10
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404 or response == 409 #409 si los datos son los mismos

    # Test editar articulo con datos faltantes
    response = client.put('/articulo/editar/1', json={
        'nombre': 'testarticulo',
        'unidad': 'testunidad'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 409 or response.status_code == 404

def test_eliminar_articulo(client):
    token=get_auth_token(client)

    # Test eliminar articulo
    response = client.delete('/articulo/eliminar/1', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404

def test_buscar_articulo(client):
    token=get_auth_token(client)

    # Test buscar articulo
    response = client.get('/articulo/buscar/test', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404


