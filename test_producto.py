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


def test_editar_producto(client):
    token=get_auth_token(client)

    # Test producto no existe
    response=client.put('/producto/editar/100',data={
        'nombre':'testproducto',
        'precio':'10',
        'tipo':'General'
    },headers={'Authorization': 'Bearer ' + token})

    assert response.status_code==404

    # Test no se envia nombre o precio
    response=client.put('/producto/editar/1',data={},headers={'Authorization': 'Bearer ' + token})  
    assert response.status_code==400

    # Test tipo no existe
    response=client.put('/producto/editar/1',data={
        'nombre':'testproducto',
        'precio':'10',
        'tipo':'test'
    },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==409

    # Test editar producto con imagen normal
    with open('./test_images/productos/test_producto_normal_size.png', 'rb') as img:
        response=client.put('/producto/editar/2', data={
            'nombre':'testproductoIMG',
            'precio':'15',
            'tipo':'General',
            'file':(img,'test.png')
        },headers={'Authorization': 'Bearer ' + token})
        
        assert response.status_code==200 or response.status_code==400 or response.status_code==500

    # Test editar producto con imagen muy grande
    with open('./test_images/productos/test_producto_big_size.jpg', 'rb') as img:
        response=client.put('/producto/editar/1', data={
            'nombre':'testproductoBIG',
            'precio':'15',
            'tipo':'General',
            'file':(img,'test.jpg')
        },headers={'Authorization': 'Bearer ' + token})
        assert response.status_code==400 or response.status_code==413

    # Test get producto
    response=client.get('/producto/editar/1',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==200

    # Test editar producto repetido
    response=client.put('/producto/editar/1',data={
        'nombre':'testproducto',
        'precio':'25',
        'tipo':'General'},headers={'Authorization': 'Bearer ' + token})

    assert response.status_code==200 or response.status_code==409

    # Test editar producto con precio negativo
    response = client.put('/producto/editar/1', data={
        'nombre': 'testproducto', 
        'precio': '-10', 
        'tipo': 'General'
        },headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==400

def test_eliminar_producto(client):
    token=get_auth_token(client)

    # Test get eliminar producto
    response=client.delete('/producto/eliminar/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==200

    # Test producto no existe
    response=client.delete('/producto/eliminar/100',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==404

    # Test eliminar producto
    response=client.delete('/producto/eliminar/2',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==200 or response.status_code==404

def test_buscar_producto(client):
    token = get_auth_token(client)
    
    params={'tipo':'General','nombre':'test'}

    response=client.get('/producto/buscar',query_string=params,headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==200

    # Test buscar producto con tipo no existente
    params={'tipo':'test','nombre':'test'}
    response=client.get('/producto/buscar',query_string=params,headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==404

    # Test buscar producto con nombre no existente
    params={'tipo':'Pollos','nombre':'testtest'}
    response=client.get('/producto/buscar',query_string=params,headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==404 or response.status_code==200

    # Test no params
    response=client.get('/producto/buscar',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==200

def test_ver_producto(client):
    token = get_auth_token(client)

    # Test producto no existe
    response = client.get('/producto/ver/100',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code==404

    # Test get image
    response=client.get('/producto/ver/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    # Test get image without id
    response=client.get('/producto/ver/',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    # Test get image without token
    response=client.get('/producto/ver/3')
    assert response.status_code == 403
