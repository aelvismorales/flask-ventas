from flask import Blueprint,request,jsonify,make_response

from ..models.models import Articulo,db
from ..decorators import administrador_requerido


articulo_scope=Blueprint("articulo",__name__)

@articulo_scope.route('/crear',methods=['POST'])
@administrador_requerido
def crear():
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
                                        "http_code":500}),500)
        
    response.headers["Content-type"]="application/json"    
    return response

@articulo_scope.route('/ver/<id>',methods=['GET'])
def ver(id):
    articulo=Articulo.query.get(id)

    response=make_response(jsonify({"articulo":articulo.get_json()}))
    response.headers['Content-type']="application/json"
    return response

@articulo_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@administrador_requerido
def eliminar(id):
    articulo=Articulo.query.get(id)
    if request.method=='DELETE' and articulo is not None:
        db.session.delete(articulo)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el articulo","http_code":200}),200)
        response.headers['Content-type']="application/json"
        return response
    
    elif request.method=='DELETE' and articulo is None:
        response=make_response(jsonify({"mensaje": "El articulo que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500},500))
        response.headers['Content-type']="application/json"
        return response
    # TO DO VERIFICAR IF STATEMENTS SI ENVIAN UN ID QUE NO ES VALIDO ENTONCES EL RESPONSE DE GET NO FUNCIONARA.
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el articulo %s" % articulo.nombre,"usuario":articulo.get_json(),"http_code":200}),200)
    response.headers['Content-type']="application/json"
    return response

@articulo_scope.route('/editar/<id>',methods=['GET','PUT'])
@administrador_requerido
def editar(id):
    articulo=Articulo.query.get(id)
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
                                            "http_code":500}),500)
            response.headers["Content-type"]="application/json"
            return response
        
    response=make_response(jsonify({"messaje":"Se envian datos del articulo %s" % id,"articulo":articulo.get_json(),"http_code":200},200))
    response.headers["Content-type"]="application/json"
    return response
