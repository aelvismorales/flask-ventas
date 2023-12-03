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
    response=client.post('/auth/login',json={
        'nombre':'testuser3',
        'contraseña':'testpassword3'
    })

    return response.get_json()['token']

def test_crear_producto(client):

    token=get_auth_token(client)

    # Test no nombre or precio
    response=client.post('/producto/crear',data={},headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==400

    # Test crear producto sin imagen
    response=client.post('/producto/crear',data={
        'nombre':'testproducto',
        'precio':'10',
        'tipo':'General'
    },headers={'Authorization': 'Bearer ' + token})
    if response.status_code==500:
        print(response.get_json()['error'])
    assert response.status_code==201 or response.status_code==409

   # Test crear producto con imagen normal
    with open('./test_images/productos/test_producto_normal_size.png', 'rb') as img:
        response=client.post('/producto/crear', data={
            'nombre':'testproductoIMG',
            'precio':'15',
            'tipo':'General',
            'file':(img,'test.png')
        },headers={'Authorization': 'Bearer ' + token})
        assert response.status_code==201 or response.status_code==409

    # Test crear producto con imagen muy grande
    with open('./test_images/productos/test_producto_big_size.jpg', 'rb') as img:
        response=client.post('/producto/crear', data={
            'nombre':'testproductoBIG',
            'precio':'15',
            'tipo':'General',
            'file':(img,'test.jpg')
        },headers={'Authorization': 'Bearer ' + token})
        assert response.status_code==400 or response.status_code==413

    # Test crear producto repetido
    response=client.post('/producto/crear',data={
        'nombre':'testproducto',
        'precio':'10',
        'tipo':'General'
    },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==409

    # Test crear producto con tipo no existente
    response = client.post('/producto/crear', data={
        'nombre': 'testproducto2', 
        'precio': '10', 
        'tipo': 'test'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==409

    # Test crear producto con precio negativo
    response = client.post('/producto/crear', data={
        'nombre': 'testproducto2', 
        'precio': '-10', 
        'tipo': 'General'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==400

    #Test crear producto con precio no numerico
    #response = client.post('/producto/crear', data={
    #    'nombre': 'testproducto2', 
    #    'precio': 'test', 
    #    'tipo': 'General'
    #    },headers={'Authorization': 'Bearer ' + token})
    #assert response.status_code==400

    #Test crear producto con nombre vacio
    response = client.post('/producto/crear', data={
        'nombre': '', 
        'precio': '10', 
        'tipo': 'General'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==400

    #Test crear producto con nombre muy largo
    response = client.post('/producto/crear', data={
        'nombre': 'test'*100, 
        'precio': '10', 
        'tipo': 'General'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==400

    #Test crear producto con tipo vacio
    response = client.post('/producto/crear', data={
        'nombre': 'test', 
        'precio': '10', 
        'tipo': ''
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==409

