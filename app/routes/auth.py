import json
from flask import Blueprint, jsonify, make_response,request
from flask_login import login_user,logout_user,login_required
from ..decorators import permiso_requerido,administrador_requerido
from ..models.models import Usuario,db,Permission,Role

auth_scope=Blueprint("auth",__name__)

#TODO DEFINIRLO COMO SOLO ACCESO A ADMINISTRADOR
@auth_scope.route('/registro',methods=['POST'])
def registro():
    """ 
    La ruta de registro recibe informacion en formato Json, en donde recibira la siguiente estructura.
    {
        "nombre": "aelvismorales",
        "contraseña": "0000000",
        "rol" : "Usuario"
    }
    Finalizar, se devuelve un Json de formato:
    { 
        "mensaje": "informacion",
        "http_code":201,
        "usuario: "nombre_usuario"
    }
    """ 
    data=request.json
    u_nombre=data.get("nombre").strip()
    u_contraseña=data.get("contraseña").strip()
    u_rol= "Usuario" if data.get("rol") is None else data.get("rol") 
    
    usuario=Usuario.query.filter_by(nombre=u_nombre).first()

    if usuario is not None:
        response=make_response(jsonify({
            "mensaje": "El usuario ya existe en la base de datos",
            "http_code":409
        }),409)
        response.headers["Content-type"]="application/json"
        return response
    rol=Role.query.filter_by(nombre=u_rol).first()
    u_rol_id=rol.get_id()
    try:
        nuevo_usuario=Usuario(u_nombre,u_contraseña,u_rol_id)
        db.session.add(nuevo_usuario)
        db.session.commit()
        response=make_response(jsonify({"mensaje":"El usuario se registro correctamente",
                                        "http_code":201,
                                        "usuario":nuevo_usuario.nombre
                                        }),201)
    except Exception as e:
        db.session.rollback()
        response=make_response(jsonify({"mensaje":"No se puede registrar al usuario",
                                        "http_code":500,
                                        "error":e.args[0]}),500)
    response.headers["Content-type"]="application/json" 
    return response

@auth_scope.route('/login',methods=['POST'])
def login():
    """ 
    La ruta login recibe informacion en formato Json, de la siguiente manera:
    {
        "nombre": "aelvismorales",
        "contraseña": "0000000",
        "recuerdame": True or False
    }
     Finalizar, se devuelve un Json de formato:
    { 
        "mensaje": "informacion",
        "http_code":201
    }
    """
    data=request.json
    u_nombre=data.get("nombre")
    u_contraseña=data.get("contraseña")
    u_recuerdame=False if data.get("recuerdame") is None else data.get("recuerdame")

    usuario=Usuario.query.filter_by(nombre=u_nombre).first()
    if usuario.verificar_contraseña(u_contraseña):
        login_user(usuario,remember=u_recuerdame)
        response=make_response(jsonify({"mensaje":"Inicio de sesion correcto","http_code": 200}),200)
    else:
        response=make_response(jsonify({"mensaje":"Usuario o Contraseña incorrectos","http_code": 400}),400)

    response.headers["Content-type"]="application/json"
    return response

@auth_scope.route('/logout',methods=['POST'])
@login_required
def logout():
    """La ruta logout solo necesita ser llamada pero esta debe cumplir con que el Usuario
        halla iniciado sesion anteriormente, sino no podra ingresar a la ruta.
    """
    logout_user()
    response=make_response(jsonify({"mensaje":"Cerro sesion correctamente","http_code": 200}),200)
    response.headers['Content-type']="application/json"
    return response


@auth_scope.route('/editar/<id>',methods=['GET','PUT'])
@administrador_requerido
def editar(id):
    """ 
        RECIBIR UN FORMULARIO IMAGEN ?
    """
    usuario=Usuario.query.get(id)
    if request.method=='PUT':
        u_nombre=request.form.get("nombre").strip()
        u_rol= "Usuario" if request.form.get("rol") is None else request.form.get("rol")

        rol=Role.query.filter_by(nombre=u_rol).first()

        usuario.nombre=u_nombre
        usuario.role_id=rol.get_id()

        try:
            db.session.commit()
            response=make_response(jsonify({"mensaje": "El usuario se ha actualizado correctamente","http_code": 200}),200)
            response.headers['Content-type']="application/json"
            return response
        except Exception as e:
            response=make_response(jsonify({"mensaje":"No se ha podido actualizar los datos del usuario","error": e.args[0],"http_code":500}),500)

    response=make_response(jsonify({"messaje":"Se envian datos del Usuario %s" % id,"usuario":usuario.get_json(),"http_code":200},200))
    response.headers["Content-type"]="application/json"
    return response

@auth_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@administrador_requerido
def eliminar(id):
    usuario=Usuario.query.get(id)
    if request.method=='DELETE' and usuario is not None:
        db.session.delete(usuario)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente al Usuario","http_code":200}),200)
        response.headers['Content-type']="application/json"

        return response
    
    elif request.method=='DELETE' and usuario is None:
        response=make_response(jsonify({"mensaje": "El usuario que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500},500))
        response.headers['Content-type']="application/json"
        return response

    # TO DO VERIFICAR IF STATEMENTS SI ENVIAN UN ID QUE NO ES VALIDO ENTONCES EL RESPONSE DE GET NO FUNCIONARA.
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar al Usuario %s" % usuario.nombre,"usuario":usuario.get_json(),"http_code":200}),200)
    response.headers['Content-type']="application/json"
    return response

@auth_scope.route('/usuarios/all',methods=['GET'])
@administrador_requerido
def ver_usuarios():
    usuarios=Usuario.query.all()
    json_usuario=[]
    for u in usuarios:
        json_usuario.append(u.get_json())
    json_string=json.dumps(json_usuario,indent=4)
    return json_string
