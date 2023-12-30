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

def crear_nota_pedido(client):
    json_data={"nombre_comprador":"Alonso Fernandez",
               "direccion": "Calle 123",
               "telefono": "12345678",
               "pago_efectivo":10,
               "pago_visa":10,
               "pago_yape":10,
               "motorizado":"-",
               "estado_pago":"True",
               "comentario": "Sin comentarios",	
               "productos":[{
                   "producto_id":1,
                   "cantidad":5,
                     "precio":6
                     }]	
               }
    response=client.post('/nota/crear',json=json_data,headers={'Authorization': 'Bearer '+get_auth_token(client)})
    assert response.status_code==200

def test_invalid_auth_token(client):
    response = client.post('/nota/crear', headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401

def test_missing_fields(client):
    json_data = {"nombre_comprador":"Alonso Fernandez"}  # Missing other fields
    response = client.post('/nota/crear', json=json_data, headers={'Authorization': 'Bearer '+get_auth_token(client)})
    assert response.status_code == 400