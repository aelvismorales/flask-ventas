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

def test_crear_mesas(client):
    token=get_auth_token(client)

    # Test no piso or numero_mesa
    response=client.post('/mesa/crear',json={},headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 409

    # Test crear mesa
    response=client.post('/mesa/crear',json={
        'piso': 1,
        'numero_mesa': 1
        },headers={'Authorization': 'Bearer ' + token})
    
    assert response.status_code == 201 or response.status_code == 409

def test_editar_mesa(client): 

    token=get_auth_token(client)

    #Test not found mesa
    response=client.put('/mesa/editar/100',json={
        'piso': 1,
        'numero_mesa': 1
        },headers={'Authorization': 'Bearer ' + token})

    assert response.status_code == 404

    #Test editar mesa
    response=client.put('/mesa/editar/1',json={
        'piso': 1,
        'numero_mesa': 4
        },headers={'Authorization': 'Bearer ' + token})
    
    assert response.status_code == 200 or response.status_code == 404


def test_editar_estado_mesa(client):
    token=get_auth_token(client)

    #Test not found mesa
    response=client.put('/mesa/editar-estado/100',json={
        'estado_mesa': True
        },headers={'Authorization': 'Bearer ' + token})

    assert response.status_code == 404

    #Test editar estado mesa
    response=client.put('/mesa/editar-estado/1',json={
        'estado_mesa': True
        },headers={'Authorization': 'Bearer ' + token})
    
    assert response.status_code == 200 or response.status_code == 404


def test_obtener_mesa(client):
    token=get_auth_token(client)

    #Test not found mesa
    response=client.get('mesa/obtener/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    #Test obtener mesa
    response=client.get('mesa/obtener/1',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404

def test_eliminar_mesa(client):
    token=get_auth_token(client)

    #Test not found mesa
    response=client.delete('/mesa/eliminar/100',headers={'Authorization': 'Bearer ' + token})

    assert response.status_code == 404

    #Test eliminar mesa
    response=client.delete('/mesa/eliminar/1',headers={'Authorization': 'Bearer ' + token})

    assert response.status_code == 200 or response.status_code == 404