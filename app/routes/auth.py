import datetime
from flask import Blueprint, jsonify, make_response,request,send_from_directory,current_app
from werkzeug.utils import secure_filename
from ..errors.errors import *
from ..decorators import token_required
from ..models.models import Usuario,db,Imagen,Role
from .general import validar_imagen

import jwt
import os

auth_scope=Blueprint("auth",__name__)


@auth_scope.route('/registro',methods=['POST'])
def registro():
    """
    Registra un nuevo usuario en la base de datos.

    Recibe un JSON con los siguientes campos:
    - nombre: El nombre del usuario (string).
    - contraseña: La contraseña del usuario (string).
    - rol: El rol del usuario (string, opcional).

    Si el nombre o la contraseña están vacíos, se devuelve un error de solicitud incorrecta.
    Si el usuario ya existe en la base de datos, se devuelve un error de conflicto.
    Si el rol no existe en la base de datos, se devuelve un error de conflicto.
    Si ocurre algún error durante el registro, se devuelve un error interno del servidor.

    Ejemplo de JSON de entrada:
    {
        "nombre": "John Doe",
        "contraseña": "password123",
        "rol": "Usuario"
    }

    Ejemplo de respuesta exitosa:
    {
        "mensaje": "El usuario se registró correctamente",
        "http_code": 201,
        "usuario": "John Doe"
    }

    Ejemplo de respuesta de error:
    {
        "mensaje": "No se puede registrar al usuario",
        "http_code": 500,
        "error": "Mensaje de error"
    }
    """
    data = request.json
    u_nombre = data.get("nombre").strip() if data.get("nombre") else None
    u_nombre_usuario=data.get("nombre_usuario").strip() if data.get("nombre_usuario") else None
    u_contraseña = data.get("contraseña").strip() if data.get("contraseña") else None
    u_rol = data.get("rol") if data.get("rol") else "Usuario"
    
    if not u_nombre or not u_contraseña:
        return handle_bad_request("El nombre o la contraseña no pueden estar vacios")
    
    usuario = Usuario.query.filter_by(nombre=u_nombre).first()

    if usuario is not None:    
        return handle_conflict("El usuario ya existe en la base de datos") 
    
    rol=Role.query.filter_by(nombre=u_rol).first()
    if rol is None:        
        return handle_conflict("El rol no existe en la base de datos")  
    try:
        nuevo_usuario = Usuario(u_nombre,u_nombre_usuario,u_contraseña,rol.get_id())
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje":"El usuario se registro correctamente",
                        "http_code":201,
                        "usuario":nuevo_usuario.nombre
                        }),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensaje":"No se puede registrar al usuario","http_code":500,"error":e.args[0]}),500

@auth_scope.route('/login',methods=['POST'])
def login():
    """
    Realiza el inicio de sesión de un usuario.

    Recibe un JSON con el nombre y la contraseña del usuario.
    Verifica si el nombre y la contraseña son válidos.
    Si son válidos, genera un token de autenticación y lo devuelve junto con el rol del usuario.
    Si no son válidos, devuelve un mensaje de error.

    Returns:
        JSON: Un JSON con el mensaje de éxito o error, el código HTTP y el token de autenticación (si es válido).

    Example JSON:
        {
            "nombre": "ejemplo",
            "contraseña": "ejemplo123"
        }
    """
    data = request.json
    u_nombre = data.get("nombre") if data.get("nombre") else None
    u_contraseña = data.get("contraseña") if data.get("contraseña") else None

    if not u_nombre or not u_contraseña:
        return handle_bad_request("El nombre o la contraseña no pueden estar vacios")

    usuario = Usuario.query.filter_by(nombre=u_nombre.strip()).first()

    if usuario is not None:
        if usuario.verificar_contraseña(u_contraseña.strip()):
            token=jwt.encode({'id':usuario.get_id(),'rol':usuario.get_rol(),'auth':True,
                              'exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=18)
                              },key=current_app.config['SECRET_KEY'])
            return jsonify({"mensaje":"Inicio de sesion correcto","http_code": 200,'token':token,'rol':usuario.get_rol(),"nombre_usuario":usuario.get_nombre_usuario()}),200
        else:
            return jsonify({"mensaje":"Usuario o Contraseña incorrectos","http_code": 400}),400
    else:
        return jsonify({"mensaje":"El usuario no existe en la base de datos","http_code": 404}),404


@auth_scope.route('/logout',methods=['POST'])
@token_required
def logout(current_user):
    """La ruta logout solo necesita ser llamada pero esta debe cumplir con que el Usuario
        halla iniciado sesion anteriormente, sino no podra ingresar a la ruta.
    """
    return jsonify({"mensaje":"Sesión cerrada correctamente","http_code": 200}),200


@auth_scope.route('/token-still-valid',methods=['GET'])
@token_required
def token_still_valid(current_user):
    """
    Verifica si el token de autenticación aún es válido.

    Parámetros:
    - current_user: El usuario actual autenticado.

    Retorna:
    - Un objeto JSON que indica si el token aún es válido, junto con el token actualizado.
    """
    token = jwt.encode({'id':current_user.get_id(),'rol':current_user.get_rol(),'auth':True,
                              'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=18)
                              },key=current_app.config['SECRET_KEY'])
    return jsonify({"mensaje":"Token still valid","http_code": 200,'rol':current_user.get_rol(),'token':token,"nombre_usuario":current_user.get_nombre_usuario()}),200


# USUARIO
#Quizas utilizar url queries para obtener los datos ordenados y que no lo realice el front ?
@auth_scope.route('/buscar/<string:nombre>',methods=['GET'])
@token_required
def buscar_nombre(current_user,nombre):
    """
    Busca usuarios por nombre y devuelve una lista de usuarios que coinciden con el nombre proporcionado.

    Parámetros:
    - current_user: El usuario actual que realiza la búsqueda.
    - nombre: El nombre a buscar.

    Retorna:
    - Una lista de usuarios que coinciden con el nombre proporcionado en formato JSON.
    - Código de estado HTTP 200 si la búsqueda fue exitosa.

    Restricciones:
    - Solo los administradores tienen autorización para acceder a este recurso.
    - Si no se encuentra ningún usuario con el nombre proporcionado, se devuelve un código de estado HTTP 404.
    - Solo se permite el método GET para esta ruta.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder a este recurso")

    nombre = nombre.strip()
    usuarios = Usuario.query.filter(Usuario.nombre.like('%'+nombre+'%')).all()
    if usuarios is None or len(usuarios) == 0:
        return handle_not_found("No se encontro ningun usuario con ese nombre")    

    json_usuario=[]
    if request.method=='GET':
        for u in usuarios:
            json_usuario.append(u.get_json())
        
        return jsonify({"usuarios":json_usuario,"http_code":200}),200
    

@auth_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):
    """
    Edita un usuario existente.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    - id: El ID del usuario a editar.

    Formulario Datos:
    - nombre: El nuevo nombre del usuario.
    - nombre_usuario: El nombre de la persona que esta usando el sistema.
    - rol: El nuevo rol del usuario.
    - file: La nueva imagen de perfil del usuario.

    Retorna:
    - Si la solicitud es un PUT:
        - Si el usuario no tiene permisos de administrador, retorna un mensaje de error de autorización.
        - Si no se encuentra ningún usuario con el ID proporcionado, retorna un mensaje de error de no encontrado.
        - Si se actualizan correctamente los datos del usuario, retorna un mensaje de éxito y el código HTTP 200.
        - Si ocurre un error al actualizar los datos del usuario, retorna un mensaje de error y el código HTTP 500.
    - Si la solicitud es un GET:
        - Si no se encuentra ningún usuario con el ID proporcionado, retorna un mensaje de error de no encontrado.
        - Si se encuentra el usuario, retorna los datos del usuario y el código HTTP 200.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder a este recurso")

    usuario = Usuario.query.get(id)

    if usuario is None:
        return handle_not_found("No se encontro ningun usuario con ese ID")

    if request.method == 'PUT':
        u_nombre = request.form.get("nombre").strip()
        u_nombre_usuario=request.form.get("nombre_usuario").strip()
        if u_nombre is None or u_nombre == "" or u_nombre_usuario is None or u_nombre_usuario == "":
            return handle_bad_request("El nombre o nombre de usuario no puede estar vacio")
        
        u_rol = "Usuario" if request.form.get("rol") is None else request.form.get("rol")

        rol = Role.query.filter_by(nombre=u_rol).first()
        if rol is None:        
            return handle_conflict("El rol no existe en la base de datos")
        
        mensaje_eliminado=""
        if 'file' in request.files:
            last_image = Imagen.query.get(usuario.get_imagen_id())
            imagen_subida = request.files['file']
            if imagen_subida is not None:
                filename = secure_filename(imagen_subida.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validar_imagen(imagen_subida.stream):
                        return jsonify({"mensaje": "La imagen subida no cumple con el formato permitido o es muy grande 'jpg','png'", "http_code": 400}), 400
                    path = current_app.config['UPLOAD_PATH_PRODUCTOS'] + '/' + last_image.get_filename()
                    if os.path.exists(path) and (last_image.get_id() != 1 or last_image.get_id() != 2):
                        os.remove(path)
                        final_filename = u_nombre + file_ext
                        imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PERFILES'], final_filename))
                        img = Imagen(final_filename, current_app.config['UPLOAD_PATH_PERFILES'], imagen_subida.mimetype)
                        db.session.add(img)
                        db.session.commit()
                        usuario.imagen_id = img.get_id()
                        db.session.commit()
                        db.session.delete(last_image)
                        db.session.commit()
                        mensaje_eliminado = "Se elimino la imagen anterior correctamente"
                    elif last_image.get_id() == 1 or last_image.get_id() == 2:
                        final_filename = u_nombre + file_ext
                        imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PERFILES'], final_filename))
                        img = Imagen(final_filename, current_app.config['UPLOAD_PATH_PERFILES'], imagen_subida.mimetype)
                        db.session.add(img)
                        db.session.commit()
                        usuario.imagen_id = img.get_id()
                        db.session.commit()

#TODO VERIFICAR COMO TRABAJAR CUANDO EXISTA IN FILE IN REQUEST FILE, DADO QUE DA ERROR AL MOMENTO DE ACTUALIZAR LOS DATOS DEL USUARIO   
        try:
            nombre=usuario.get_nombre()
            nombre_usuario=usuario.get_nombre_usuario()
            role_actual=usuario.get_rol_id()
            role_nuevo=rol.get_id()

            if nombre!=u_nombre:
                usuario.nombre=u_nombre
                db.session.commit()

            if nombre_usuario!=u_nombre_usuario:
                usuario.nombre_usuario=u_nombre_usuario
                db.session.commit()
                
            if role_actual!=role_nuevo:
                usuario.role_id=role_nuevo
                db.session.commit()
            
            if u_nombre == nombre and role_actual == role_nuevo and u_nombre_usuario == nombre_usuario:
                if 'file' in request.files:
                    return jsonify({"mensaje": "El usuario se ha actualizado correctamente", "adicional": mensaje_eliminado, "http_code": 200}), 200
                else:
                    return jsonify({"mensaje": "Los datos del usuario no han cambiado", "http_code": 409}), 409
            
            return jsonify({"mensaje": "El usuario se ha actualizado correctamente", "adicional": mensaje_eliminado, "http_code": 200}), 200
        except Exception as e:
            return jsonify({"mensaje": "No se ha podido actualizar los datos del usuario", "error": e.args[0], "http_code": 500}), 500
        
    if request.method == 'GET':
        return jsonify({"mensaje": "Se envian datos del Usuario %s" % id, "usuario": usuario.get_json(), "http_code": 200}), 200

@auth_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    """
    Elimina un usuario de la base de datos.

    Parámetros:
    - current_user: El usuario actual que realiza la acción.
    - id: El ID del usuario a eliminar.

    Retorna:
    - Si el método de la solicitud es DELETE:
        - Si se elimina el usuario correctamente, retorna un JSON con el mensaje "Se ha eliminado satisfactoriamente al Usuario" y el código HTTP 200.
    - Si el método de la solicitud es GET:
        - Retorna un JSON con el mensaje "Estas seguro de querer eliminar al Usuario [nombre del usuario]", los datos del usuario y el código HTTP 200.

    Restricciones:
    - Solo los administradores tienen autorización para acceder a este recurso.
    - Si el usuario no existe, retorna un JSON con el mensaje "No se encontro ningun usuario con ese ID" y el código HTTP correspondiente.
    - Si el archivo de imagen asociado al usuario existe en el sistema de archivos y no es una imagen predeterminada, también se elimina.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder a este recurso")
    
    usuario=Usuario.query.filter_by(id=id).first()
    if usuario is None:
        return handle_not_found("No se encontro ningun usuario con ese ID")

    if request.method=='DELETE':
        img_id=usuario.get_imagen_id()
        img=Imagen.query.filter_by(id=img_id).first()
        path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+img.get_filename()          

        db.session.delete(usuario)
        db.session.commit()
    
        if os.path.exists(path) and (img_id.get_id()!=1 or img_id.get_id()!=2):
            os.remove(path)

        return jsonify({"mensaje":"Se ha eliminado satisfactoriamente al Usuario","http_code":200}),200
    
    elif request.method=='GET':
        return jsonify({"mensaje":"Estas seguro de querer eliminar al Usuario %s" % usuario.nombre,"usuario":usuario.get_json(),"http_code":200}),200

@auth_scope.route('/usuarios/all',methods=['GET'])
@token_required
def ver_usuarios(current_user):
    """
    Obtiene la lista de todos los usuarios.

    Parameters:
        current_user (User): El usuario actual que realiza la solicitud.

    Returns:
        tuple: Una tupla que contiene un diccionario con la lista de usuarios y el código HTTP 200 si se encuentra al menos un usuario, 
        de lo contrario, devuelve un mensaje de error y el código HTTP 404.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder a este recurso")

    usuarios=Usuario.query.all()
    if usuarios is None or len(usuarios)==0:
        return handle_not_found("No se encontro ningun usuario con ese ID")

    json_usuario=[]

    for u in usuarios:
        json_usuario.append(u.get_json())
    return jsonify({"usuarios":json_usuario,"http_code":200}),200

@auth_scope.route('/usuarios/delivery',methods=['GET'])
@token_required
def ver_usuarios_delivery(current_user):
    """
    Obtiene la lista de usuarios de tipo 'delivery'.

    Parameters:
        current_user (User): El usuario actual.

    Returns:
        tuple: Una tupla que contiene un diccionario con la lista de usuarios y el código de estado HTTP.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder a este recurso")
    usuarios=Usuario.query.filter_by(role_id = 4,ocupado = False).all()

    if usuarios is None or len(usuarios)==0:
        return handle_not_found("No se encontro ningun usuario con ese ID")

    json_usuario=[]
    for u in usuarios:
        json_usuario.append(u.get_json())

    return jsonify({"usuarios":json_usuario,"http_code":200}),200

@auth_scope.route('/ver/imagen/<id>',methods=['GET'])
@token_required
def ver_imagen(current_user,id):
    """
    Devuelve la imagen de perfil de un usuario específico.

    Parámetros:
    - current_user: El usuario actual autenticado.
    - id: El ID del usuario cuya imagen de perfil se desea obtener.

    Retorna:
    - Si se encuentra la imagen de perfil, se devuelve la imagen.
    - Si no se encuentra la imagen de perfil, se devuelve la imagen de perfil predeterminada.
    """
    usuario=Usuario.query.filter_by(id=id).first()
    if usuario is None:
        return handle_not_found("No se encontro ningun usuario con ese ID")
    
    img_id=usuario.get_imagen_id()
    img=Imagen.query.filter_by(id=img_id).first()

    path=current_app.config['UPLOAD_PATH_PERFILES']+'/'+img.get_filename()          
    if os.path.exists(path):
        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PERFILES'],img.get_filename())
    else:
        usuario.imagen_id=1
        db.session.commit()
        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PERFILES'],'usuario_perfil.png')