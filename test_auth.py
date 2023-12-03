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

def get_auth_token(client,usename,password):
    #Log in the Test User
    response = client.post('/auth/login', json={
        'nombre': usename,
        'contraseña': password
    },headers=headers)

    #Get the auth token
    token = response.get_json()['token']
    return token

def test_logout(client):
    #Log in the Test User
    token = get_auth_token(client,'testuser3','testpassword3')

    #Test logout
    response = client.post('/auth/logout',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200
    assert response.get_json()['mensaje'] == 'Sesión cerrada correctamente'

    #Test logout without token
    response = client.post('/auth/logout')
    assert response.status_code == 403
    assert response.get_json()['mensaje'] == 'Token no se encuentra!'

    #Test logout with invalid token
    response = client.post('/auth/logout',headers={'Authorization': 'Bearer ' + 'asdasdaawr4ad'})
    assert response.status_code == 401
    assert response.get_json()['mensaje'] == 'Token inválido'

def test_token_still_valid(client):
    #Log in the Test User
    token = get_auth_token(client,'testuser3','testpassword3')

    #Test token still valid
    response = client.get('/auth/token-still-valid',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    #Test token still valid without token
    response = client.get('/auth/token-still-valid')
    assert response.status_code == 403
    assert response.get_json()['mensaje'] == 'Token no se encuentra!'

    #Test token still valid with invalid token
    response = client.get('/auth/token-still-valid',headers={'Authorization': 'Bearer ' + 'asdasdaawr4ad'})
    assert response.status_code == 401
    assert response.get_json()['mensaje'] == 'Token inválido'

def test_buscar_nombre(client):
    # Log in Test User Usuario
    token_usuario = get_auth_token(client,'testuser','testuserpassword')

    # Test is not Administrador
    nombre_busqueda='testuser'
    response=client.get(f'/auth/buscar/{nombre_busqueda}',headers={'Authorization': 'Bearer ' + token_usuario})
    assert response.status_code == 403

    # Log in Test User Administrador
    token = get_auth_token(client,'testuser3','testpassword3')

    nombre_busqueda='testuser'
    response=client.get(f'/auth/buscar/{nombre_busqueda}',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    nombre_busqueda='testuser1256'
    response=client.get(f'/auth/buscar/{nombre_busqueda}',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404


def test_editar_usuario(client):

    # Log in Test User Administrador
    token = get_auth_token(client,'testuser3','testpassword3')

    # Test user get
    response=client.get('/auth/editar/1',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    # Test user is None
    response=client.put('/auth/editar/5',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    # Test no send nombre
    response=client.put('/auth/editar/1',data={'nombre':""},headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 400

    # Test send non existing rol
    response=client.put('/auth/editar/1',data={'nombre':"testing",'rol':"test"},headers={'Authorization': 'Bearer ' + token})
    assert  response.status_code == 409

    # Test send existing rol and no sending file
    response=client.put('/auth/editar/1',data={'nombre':"testuser3",'rol':"Administrador"},headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    # Test send existing rol and sending file with normal size
    with open('./test_images/usuario/test_user_normal_size.png','rb') as img:
        response=client.put('/auth/editar/1',data={'nombre':"testuser3",'rol':"Administrador",'file':(img,'test_user_normal_size.png')},headers={'Authorization': 'Bearer ' + token})
        assert response.status_code == 200
    # Test send existing rol and sending file with big size
    with open('./test_images/usuario/test_user_big_size.jpg','rb') as img:
        response=client.put('/auth/editar/1',data={'nombre':"testuser3",'rol':"Administrador",'file':(img,'test_user_big_size.png')},headers={'Authorization': 'Bearer ' + token})
        assert response.status_code == 400

    
def test_eliminar_usuario(client):
    # testuser
    # testuserpassword # ID 2

    # Log in Test User Administrador
    token = get_auth_token(client,'testuser3','testpassword3')
    
    # Test user get
    response=client.get('/auth/eliminar/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404 # 404 si no existe el usuario ya que se elimino en el test de abajo

    # Test user is None
    response=client.delete('/auth/eliminar/5',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    # Test user delete 
    response=client.delete('/auth/eliminar/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404 # 404 si no existe el usuario ya que se elimino en el test anterior

def test_ver_usuarios(client):

    # Log in Test User Administrador
    token = get_auth_token(client,'testuser3','testpassword3')
    
    # Test user get all users
    response=client.get('/auth/usuarios/all',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404 

    # Test get users delivery
    response=client.get('/auth/usuarios/delivery',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200 or response.status_code == 404


def test_ver_imagen_per_user_id(client):

    # Log in Test User Administrador
    token = get_auth_token(client,'testuser3','testpassword3')
    
    # Test get image
    response=client.get('/auth/ver/imagen/3',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200

    # Test get image with invalid id
    response=client.get('/auth/ver/imagen/5',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    # Test get image without id
    response=client.get('/auth/ver/imagen/',headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 404

    # Test get image without token
    response=client.get('/auth/ver/imagen/3')
    assert response.status_code == 403

    # Test get image with invalid token
    response=client.get('/auth/ver/imagen/3',headers={'Authorization': 'Bearer ' + 'asdasdaawr4ad'})
    assert response.status_code == 401

