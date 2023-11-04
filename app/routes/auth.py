from flask import Blueprint, jsonify, make_response,request
from flask_login import login_user,logout_user,login_required
from ..decorators import permiso_requerido,administrador_requerido
from ..models.models import Usuario,db,Permission,Role

auth_scope=Blueprint("auth",__name__)

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
    u_nombre=data.get("nombre")
    u_contraseña=data.get("contraseña")
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
