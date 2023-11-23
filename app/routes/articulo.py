from flask import Blueprint,request,jsonify,make_response
from ..models.models import Articulo,db
from ..decorators import token_required


articulo_scope=Blueprint("articulo",__name__)

@articulo_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):
    
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    data=request.json
    a_nombre=data.get("nombre").upper().strip()
    a_unidad=data.get("unidad").upper().strip()
    a_cantidad=data.get("cantidad")

    articulo=Articulo.query.filter_by(nombre=a_nombre).first()
    if articulo is not None:
        response= make_response(jsonify({
            "mensaje": "El articulo ya existe en la base de datos",
            "http_code": 409
        }),409)
        response.headers["Content-type"]="application/json"
        return response
    
    try:
        nuevo_articulo=Articulo(a_nombre,a_unidad,a_cantidad)
        db.session.add(nuevo_articulo)
        db.session.commit()
        response=make_response(jsonify({
            "mensaje":"Se creo el articulo satisfactoriamente",
            "http_code":201
        }),201)
    except Exception as e:
        db.session.rollback()
        response=make_response(jsonify({"mensaje": "El articulo no se pudo crear","error":e.args[0],
                                        "http_code":500}))
        
    response.headers["Content-type"]="application/json"    
    return response

@articulo_scope.route('/ver/<id>',methods=['GET'])
@token_required
def ver(current_user,id): #unuse?

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    articulo=Articulo.query.get(id)
    if articulo is None:
        response=make_response(jsonify({"mensaje":"El articulo con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"articulo":articulo.get_json()}))
    response.headers['Content-type']="application/json"
    return response

@articulo_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response

    articulo=Articulo.query.get(id)
    if articulo is None:
        response=make_response(jsonify({"mensaje":"El articulo con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    
    if request.method=='DELETE' and articulo is not None:
        db.session.delete(articulo)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el articulo","http_code":200}))
        response.headers['Content-type']="application/json"
        return response
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el articulo %s" % articulo.nombre,"usuario":articulo.get_json(),"http_code":200}))
    response.headers['Content-type']="application/json"
    return response

@articulo_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response

    articulo=Articulo.query.get(id)
    if articulo is None:
        response=make_response(jsonify({"mensaje":"El articulo con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    if request.method=='PUT':
        data=request.json
        a_nombre=data.get("nombre").upper().strip()
        a_unidad=data.get("unidad").upper().strip()
        a_cantidad=data.get("cantidad")

        try:
            articulo.nombre=a_nombre
            articulo.unidad=a_unidad
            articulo.cantidad=a_cantidad
            
            db.session.commit()
            response=make_response(jsonify({
                "mensaje":"Se actualizo el articulo correctamente",
                "http_code":200
            }),200)
            response.headers["Content-type"]="application/json" 
            return response
        except Exception as e:
            db.session.rollback()
            response=make_response(jsonify({"mensaje": "El producto no se pudo crear","error":e.args[0],
                                            "http_code":500}))
            response.headers["Content-type"]="application/json"
            return response
    
    response=make_response(jsonify({"messaje":"Se envian datos del articulo %s" % id,"articulo":articulo.get_json(),"http_code":200}))
    response.headers["Content-type"]="application/json"
    return response

@articulo_scope.route('/buscar/<string:nombre>',methods=['GET'])
@token_required
def buscar_articulo(current_user,nombre):
    
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    nombre_arti=nombre.replace("_"," ").upper()
    articulos=Articulo.query.filter(Articulo.nombre.like('%'+nombre_arti+'%')).all()
    json_articulos=[]
    if request.method=='GET' and len(articulos)>0:
        for ar in articulos:
            json_articulos.append(ar.get_json())
        response=make_response(jsonify({"articulos":json_articulos,"http_code":200}))
        response.headers['Content-type']='application/json'
        return response
    response=make_response(jsonify({"mensaje":"No se pudo encontrar el articulo","http_code":404}))
    response.headers['Content-type']='application/json'
    return response