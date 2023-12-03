from flask import Blueprint,request,make_response,jsonify
from ..decorators import token_required
from ..models.models import Mesa,db
from ..errors.errors import *

mesa_scope=Blueprint('mesa',__name__)

#TODO PENSAR EN VALIDACIONES 
# Verificar si ya existe una mesa en Piso 1 - 1 o 1-2, para no crear el valor nuevamente
@mesa_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):
    """
    Crea una nueva mesa en el sistema.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.

    Retorna:
    - Si el usuario no es un administrador, devuelve un mensaje de error de autorización.
    - Si se crea la mesa exitosamente, devuelve un mensaje de éxito y el código HTTP 200.
    - Si ocurre un error al crear la mesa, devuelve un mensaje de error y el código HTTP 500.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")\
    
    data=request.json
    me_piso=data.get("piso")
    me_numero_mesa=data.get("numero_mesa")

    nueva_mesa=Mesa(me_piso,me_numero_mesa)

    try:
        db.session.add(nueva_mesa)
        db.session.commit()
        return jsonify({"mensaje":"Se creo con exito la mesa","http_code":200}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje":"No se pudo crear la mesa","error":e.args[0],"http_code":500}),500
    
@mesa_scope.route('/editar/<id>',methods=['GET','POST'])
@token_required
def editar(current_user,id):  
    """
    Edita una mesa existente en la base de datos.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID de la mesa a editar.

    Ejmplo JSON:
    {
        "piso": 1,
        "numero_mesa": 1
    }

    Métodos HTTP permitidos:
    - GET: Obtiene los datos de la mesa especificada por su ID.
    - POST: Actualiza los datos de la mesa especificada por su ID.

    Retorna:
    - Si el método HTTP es POST y la mesa existe, retorna un JSON con el mensaje "Actualizado con exito" y el código de estado 200.
    - Si el método HTTP es POST y la mesa no existe, retorna un JSON con el mensaje "No se pudo obtener datos" y el código de estado 500.
    - Si el método HTTP es GET y la mesa existe, retorna un JSON con los datos de la mesa y el código de estado 200.
    - Si el método HTTP es GET y la mesa no existe, retorna un JSON con el mensaje "No se pudo obtener datos" y el código de estado 500.
    """
    if request.method=='POST':
        mesa=Mesa.query.filter_by(id=id).first()
        if mesa is not None:
            data=request.json
            m_piso=data.get('piso')
            m_numero_mesa=data.get('numero_mesa')
             
            mesa.piso=m_piso
            mesa.numero_mesa=m_numero_mesa
            db.session.commit()
            return jsonify({"mensaje":"Actualizado con exito","http_code":200}),200
        else:
            return jsonify({"mensaje":"No se pudo obtener datos","http_code":500}),500
    else:
        mesa=Mesa.query.filter_by(id=id).first()
        if mesa is not None:
            return jsonify({"mesa":mesa.get_json(),"http_code":200}),200
        else:
            return  jsonify({"mensaje":"No se pudo obtener datos","http_code":500}),500

@mesa_scope.route('/editar-estado/<id>',methods=['POST'])
@token_required
def editar_estados(current_user,id):
    """
    Actualiza el estado de una mesa en la base de datos.

    Ejemplo JSON:
    {
        "estado_mesa": "True"
    }

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    - id: El ID de la mesa que se desea editar.

    Retorna:
    - Si la mesa existe, se actualiza su estado en la base de datos y se retorna un mensaje de éxito con código HTTP 200.
    - Si la mesa no existe, se retorna un mensaje de error con código HTTP 500.
    """
    mesa=Mesa.query.filter_by(id=id).first()
    if mesa is not None:
        data=request.json
        m_estado=True if data.get('estado_mesa')=='True' else False

        mesa.estado_mesa=m_estado
        db.session.commit()
        return jsonify({"mensaje":"Actualizado con exito","http_code":200}),200
    else:
        return jsonify({"mensaje":"No se pudo obtener datos","http_code":500}),500


@mesa_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    """
    Elimina una mesa según su ID.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID de la mesa a eliminar.

    Retorna:
    - Si el método de la solicitud es DELETE:
        - Un objeto JSON con el mensaje "Se ha eliminado satisfactoriamente el mesa" y el código HTTP 200.
    - Si el método de la solicitud es GET:
        - Un objeto JSON con el mensaje "Estas seguro de querer eliminar el mesa {ID}" y el código HTTP 200.

    Si el usuario actual no es un administrador, se devuelve un mensaje de error de autorización.
    Si no se encuentra una mesa con el ID proporcionado, se devuelve un mensaje de error de no encontrado.
    """
    
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")\
    
    mesa=Mesa.query.get(id)

    if mesa is None:
        return handle_not_found("El mesa con ese ID no se encuentra")
    
    if request.method=='DELETE':
        db.session.delete(mesa)
        db.session.commit()
        return jsonify({"mensaje": "Se ha eliminado satisfactoriamente el mesa","http_code":200}),200
    
    elif request.method=='GET':
        return jsonify({"mensaje":"Estas seguro de querer eliminar el mesa %s" % mesa.id,"http_code":200}),200


@mesa_scope.route('/obtener/<n_piso>',methods=['GET'])
@token_required
def obtener(current_user,n_piso):
    """
    Obtiene las mesas de un piso específico.

    Parámetros:
    - current_user: Usuario actual autenticado.
    - n_piso: Número del piso del cual se desean obtener las mesas.

    Retorna:
    - JSON con las mesas del piso especificado y el código HTTP correspondiente.
    """
    mesas=Mesa.query.filter_by(piso=n_piso).all()
    if mesas is not None:
        json_mesas=[]
        for m in mesas:
            json_mesas.append(m.get_json())
        return jsonify({"mesas":json_mesas,"piso":n_piso,"http_code":200}),200
    else:
        return jsonify({"mensaje":"No se pudo obtener datos","http_code":500}),500
    
