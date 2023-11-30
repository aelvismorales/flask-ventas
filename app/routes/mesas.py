from flask import Blueprint,request,make_response,jsonify
from ..decorators import token_required
from ..models.models import Mesa,db


mesa_scope=Blueprint('mesa',__name__)

@mesa_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    #TODO PENSAR EN VALIDACIONES 
    # Verificar si ya existe una mesa en Piso 1 - 1 o 1-2, para no crear el valor nuevamente
    data=request.json
    me_piso=data.get("piso")
    me_numero_mesa=data.get("numero_mesa")

    nueva_mesa=Mesa(me_piso,me_numero_mesa)

    db.session.add(nueva_mesa)
    db.session.commit()
    response=make_response(jsonify({"mensaje":"Se creo con exito la mesa","http_code":200}))
    response.headers["Content-type"]="application/json"
    return response
    
@mesa_scope.route('/editar/<id>',methods=['GET','POST'])
@token_required
def editar(current_user,id):  
    if request.method=='POST':
        mesa=Mesa.query.filter_by(id=id).first()
        if mesa is not None:
            data=request.json
            m_piso=data.get('piso')
            m_numero_mesa=data.get('numero_mesa')
             
            mesa.piso=m_piso
            mesa.numero_mesa=m_numero_mesa
            db.session.commit()
            response=make_response(jsonify({"mensaje":"Actualizado con exito","http_code":200}))
            response.headers["Content-type"]="application/json"
            return response
        else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener datos","http_code":500}))
            response.headers["Content-type"]="application/json"
            return response
    else:
        mesa=Mesa.query.filter_by(id=id).first()
        if mesa is not None:
            response=make_response(jsonify({"mesas":mesa.get_json(),"http_code":200}))
            response.headers["Content-type"]="application/json"
        else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener datos","http_code":500}))
            response.headers["Content-type"]="application/json"
            return response

@mesa_scope.route('/editar-estado/<id>',methods=['POST'])
@token_required
def editar_estados(current_user,id):
    mesa=Mesa.query.filter_by(id=id).first()
    if mesa is not None:
        data=request.json
        m_estado=True if data.get('estado_mesa')=='True' else False

        mesa.estado_mesa=m_estado
        db.session.commit()
        response=make_response(jsonify({"mensaje":"Actualizado con exito","http_code":200}))
        response.headers["Content-type"]="application/json"
        return response
    else:
        response=make_response(jsonify({"mensaje":"No se pudo obtener datos","http_code":500}))
        response.headers["Content-type"]="application/json"
        return response


@mesa_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    mesa=Mesa.query.get(id)

    if mesa is None:
        response=make_response(jsonify({"mensaje":"El mesa con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    
    if request.method=='DELETE' and mesa is not None:
        db.session.delete(mesa)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el mesa","http_code":200}))
        response.headers['Content-type']="application/json"
        return response
    
    elif request.method=='DELETE' and mesa is None:
        response=make_response(jsonify({"mensaje": "El mesa que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    elif (request.method=='DELETE' or request.method=='GET') and mesa is None:
        response=make_response(jsonify({"mensaje": "La mesa que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el mesa %s" % mesa.id,"http_code":200}))
    response.headers['Content-type']="application/json"
    return response


@mesa_scope.route('/obtener/<n_piso>',methods=['GET'])
@token_required
def obtener(current_user,n_piso):

    mesas=Mesa.query.filter_by(piso=n_piso).all()
    if mesas is not None:
        json_mesas=[]
        for m in mesas:
            json_mesas.append(m.get_json())
        response=make_response(jsonify({"mesas":json_mesas,"piso":n_piso,"http_code":200}))
        response.headers["Content-type"]="application/json"
        return response
    else:
        response=make_response(jsonify({"mensaje":"No se pudo obtener datos","http_code":500}))
        response.headers["Content-type"]="application/json"
        return response
    
