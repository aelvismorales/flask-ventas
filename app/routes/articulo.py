from flask import Blueprint,request,jsonify,make_response
from ..models.models import Articulo,db
from ..decorators import token_required
from ..errors.errors import *

articulo_scope=Blueprint("articulo",__name__)

@articulo_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):
    """
    Crea un nuevo artículo en la base de datos.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    Ejemplo Json:
    {
        "nombre": "ARTICULO",
        "unidad": "UNIDAD",
        "cantidad": 10
    }

    Retorna:
    - Si el usuario no tiene autorización, retorna un mensaje de error de acceso prohibido.
    - Si faltan datos para crear el artículo, retorna un mensaje de conflicto.
    - Si el artículo ya existe en la base de datos, retorna un mensaje de conflicto.
    - Si se crea el artículo satisfactoriamente, retorna un mensaje de éxito y el código HTTP 201.
    - Si ocurre un error al crear el artículo, retorna un mensaje de error y el código HTTP 500.
    """
    if not current_user.is_administrador():
        return  handle_forbidden("No tienes Autorizacion para acceder")
    
    data=request.json
    a_nombre=data.get("nombre").upper().strip()
    a_unidad=data.get("unidad").upper().strip()
    a_cantidad=data.get("cantidad")

    if not a_nombre or not a_unidad or not a_cantidad:
        return handle_conflict("Faltan datos para crear el articulo")
    
    articulo=Articulo.query.filter_by(nombre=a_nombre).first()
    if articulo is not None:
        return handle_conflict("El articulo ya existe en la base de datos")
    
    try:
        nuevo_articulo=Articulo(a_nombre,a_unidad,a_cantidad)
        db.session.add(nuevo_articulo)
        db.session.commit()
        return jsonify({"mensaje":"Se creo el articulo satisfactoriamente","http_code":201}),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje": "El articulo no se pudo crear","error":e.args[0],
                        "http_code":500}),500

@articulo_scope.route('/ver/<id>',methods=['GET'])
@token_required
def ver(current_user,id): 
    """
    Obtiene y devuelve los datos de un artículo específico.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    - id: El ID del artículo que se desea obtener.

    Retorna:
    - Un objeto JSON que contiene los datos del artículo solicitado y un mensaje de éxito.
    - Código de estado HTTP 200 si la solicitud se procesa correctamente.

    Restricciones:
    - Solo los administradores tienen autorización para acceder a esta ruta.
    - Si el artículo no se encuentra en la base de datos, se devuelve un mensaje de error y un código de estado HTTP 404.
    - Si el usuario no tiene autorización para acceder, se devuelve un mensaje de error y un código de estado HTTP 403.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")
    
    articulo=Articulo.query.get(id)
    if articulo is None:
        return handle_not_found("El articulo con ese ID no se encuentra")
    
    return jsonify({"mensaje":"Se envian datos del articulo %s" % id,"articulo":articulo.get_json(),"http_code":200}),200

@articulo_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    """
    Elimina un artículo según su ID.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID del artículo a eliminar.

    Retorna:
    - Si el método de la solicitud es DELETE:
        - Un objeto JSON con el mensaje de éxito y el código HTTP 200.
    - Si el método de la solicitud es GET:
        - Un objeto JSON con el mensaje de confirmación, los detalles del artículo y el código HTTP 200.

    Si el usuario actual no es un administrador, se devuelve un mensaje de error de autorización.
    Si no se encuentra ningún artículo con el ID proporcionado, se devuelve un mensaje de error de no encontrado.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")

    articulo=Articulo.query.get(id)
    if articulo is None:
        return handle_not_found("El articulo con ese ID no se encuentra")
    
    if request.method=='DELETE':
        db.session.delete(articulo)
        db.session.commit()
        return jsonify({"mensaje": "Se ha eliminado satisfactoriamente el articulo","http_code":200}),200
    
    if request.method=='GET':
        return jsonify({"mensaje":"Estas seguro de querer eliminar el articulo %s" % articulo.nombre,"articulo":articulo.get_json(),"http_code":200}),200


@articulo_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):
    """
    Edita un artículo existente.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID del artículo a editar.

    Retorna:
    - Si el método de la solicitud es PUT:
        - Si se actualiza el artículo correctamente, retorna un JSON con el mensaje "Se actualizó el artículo correctamente" y el código de estado 200.
        - Si ocurre un error al actualizar el artículo, retorna un JSON con el mensaje "El artículo no se pudo actualizar", el error específico y el código de estado 500.
    - Si el método de la solicitud es GET:
        - Retorna un JSON con el mensaje "¿Estás seguro de querer editar el artículo {nombre del artículo}?", los detalles del artículo y el código de estado 200.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorización para acceder")

    articulo=Articulo.query.get(id)
    if articulo is None:
        return handle_not_found("El artículo con ese ID no se encuentra")

    if request.method=='PUT':
        data=request.json
        a_nombre=data.get("nombre").upper().strip()
        a_unidad=data.get("unidad").upper().strip()
        a_cantidad=data.get("cantidad")

        if not a_nombre or not a_unidad or not a_cantidad:
            return handle_conflict("Faltan datos para crear el artículo")

        try:
            articulo.nombre=a_nombre
            articulo.unidad=a_unidad
            articulo.cantidad=a_cantidad
            
            db.session.commit()
            return jsonify({"mensaje":"Se actualizó el artículo correctamente","http_code":200}),200
        except Exception as e:
            db.session.rollback()
            return jsonify({"mensaje": "El artículo no se pudo actualizar","error":e.args[0],
                            "http_code":500}),500
    
    if request.method=='GET':
        return jsonify({"mensaje":"¿Estás seguro de querer editar el artículo %s?" % articulo.nombre,"articulo":articulo.get_json(),"http_code":200}),200

@articulo_scope.route('/buscar/<string:nombre>',methods=['GET'])
@token_required
def buscar_articulo(current_user,nombre):
    """
    Busca un artículo por su nombre.

    Parámetros:
    - current_user: El usuario actual.
    - nombre: El nombre del artículo a buscar.

    Retorna:
    - Si el usuario no es administrador, retorna un mensaje de error de autorización.
    - Si se encuentra el artículo, retorna una lista de artículos que coinciden con el nombre y el código de estado HTTP 200.
    - Si no se encuentra el artículo, retorna un mensaje de error de no encontrado.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")
    
    nombre_arti=nombre.replace("_"," ").upper()
    
    articulos=Articulo.query.filter(Articulo.nombre.like('%'+nombre_arti+'%')).all()
    json_articulos=[]
    if request.method=='GET' and len(articulos)>0:
        for ar in articulos:
            json_articulos.append(ar.get_json())
        return jsonify({"articulos":json_articulos,"http_code":200}),200
    
    return handle_not_found("No se pudo encontrar el articulo")