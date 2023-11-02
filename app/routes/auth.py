from flask import Blueprint, jsonify, make_response,request
from flask_login import login_user,logout_user,login_required
from ..decorators import permiso_requerido,administrador_requerido
from ..models.models import Usuario,db,Permission

auth_scope=Blueprint("auth",__name__)

@auth_scope.route('/registro',methods=['POST'])
def registro():
    data=request.json
    u_nombre=data.get("nombre")
    u_contraseña=data.get("contraseña")
    u_rol_id= None if data.get("rol") is None else data.get("rol") # LO IDEAL DESDE FRONT TENER LOS ID DE CADA TIPO DE ROL Y ENVIARLOS ASI
    
    print(u_rol_id)
    usuario=Usuario.query.filter_by(nombre=u_nombre).first()

    if usuario is not None:
        response=make_response(jsonify({
            "mensaje": "El usuario ya existe en la base de datos",
            "http_code":409
        }),409)
        response.headers["Content-type"]="application/json"
        return response

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
    logout_user()
    response=make_response(jsonify({"mensaje":"Cerro sesion correctamente","http_code": 200}),200)
    response.headers['Content-type']="application/json"
    return response

@auth_scope.route('/information')
@login_required
@permiso_requerido(Permission.CREAR_PRODUCTO)
def information():
    return "HOLA"