from flask import Blueprint,request,make_response,jsonify,current_app,send_from_directory
from werkzeug.utils import secure_filename
from ..decorators import token_required
from ..models.models import Producto,Tipo,db,Imagen
from .general import validar_imagen
from ..errors.errors import *
import os

producto_scope=Blueprint("producto",__name__)

@producto_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):    
    """
    Crea un nuevo producto en la base de datos.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.

    Formulario Datos:
    - nombre (str): El nombre del nuevo producto.
    - precio (float): El precio del nuevo producto.
    - tipo (str): El tipo de producto. Si no se proporciona, se asigna el tipo "General".
    - file (file): La imagen del nuevo producto. Si no se proporciona, se asigna una imagen por defecto.
    Retorna:
    - Si el usuario no tiene autorización, devuelve un mensaje de error de acceso prohibido.
    - Si no se envían los datos necesarios, devuelve un mensaje de error y un código de estado 400.
    - Si el producto ya existe en la base de datos, devuelve un mensaje de conflicto.
    - Si el tipo de producto no existe en la base de datos, devuelve un mensaje de conflicto.
    - Si la imagen subida no cumple con el formato permitido, devuelve un mensaje de error y un código de estado 400.
    - Si se crea el producto satisfactoriamente, devuelve un mensaje de éxito y un código de estado 201.
    - Si no se puede crear el producto, devuelve un mensaje de error y un código de estado 500.
    """
    
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder al recurso")
    
    p_nombre= request.form.get("nombre").upper().strip() if request.form.get("nombre") is not None else None
    p_precio=request.form.get("precio") if request.form.get("precio") is not None else None
    p_tipo= "General" if request.form.get("tipo") is None else request.form.get("tipo")

    if not p_nombre or not p_precio or float(p_precio)<0.0 or p_nombre=='' or len(p_nombre)>40:
        return handle_bad_request("No se enviaron los datos necesarios")

    producto=Producto.query.filter_by(nombre=p_nombre).first()
    if producto is not None:
        return handle_conflict("El producto ya existe en la base de datos")

    tipo=Tipo.query.filter_by(nombre=p_tipo).first()
    if tipo is None:
        return handle_conflict("El tipo de producto no existe en la base de datos")
    
    tipo_id=tipo.get_id()

    if 'file' in request.files:
        imagen_subida=request.files['file']
        filename=secure_filename(imagen_subida.filename)
        if filename !='':
            file_ext=os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validar_imagen(imagen_subida.stream):
                return handle_bad_request("La imagen subida no cumple con el formato permitido o excede 1024*1024 'jpg','png'")
            final_filename=p_nombre+file_ext
            imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PRODUCTOS'],final_filename))
            img=Imagen(final_filename,current_app.config['UPLOAD_PATH_PRODUCTOS'],imagen_subida.mimetype)
            db.session.add(img)
            db.session.commit()
            try:
                nuevo_producto=Producto(p_nombre,p_precio,tipo_id,img.get_id())
                db.session.add(nuevo_producto)
                db.session.commit()
                return jsonify({"mensaje":"Se creo el producto satisfactoriamente","http_code":201}),201
            except Exception as e:
                db.session.rollback()
                return jsonify({"mensaje": "El producto no se pudo crear","error":e.args[0],
                                "http_code":500}),500        
    else:        
        try:
            img_id= 3
            nuevo_producto=Producto(p_nombre,p_precio,tipo_id,img_id)
            db.session.add(nuevo_producto)
            db.session.commit()
            return jsonify({"mensaje":"Se creo el producto satisfactoriamente","http_code":201}),201
        except Exception as e:
            db.session.rollback()
            return jsonify({"mensaje": "El producto no se pudo crear","error":e.args[0],
                            "http_code":500}),500

@producto_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):
    """
    Edita un producto existente en la base de datos.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    - id: El ID del producto a editar.

    Formulario Datos:
    - nombre (str): El nuevo nombre del producto.
    - precio (float): El nuevo precio del producto.
    - tipo (str): El nuevo tipo de producto. Si no se proporciona, se asigna el tipo "General".
    - file (file): La nueva imagen del producto. Si no se proporciona, se mantiene la imagen actual.

    Retorna:
    - Si la solicitud es exitosa, devuelve un mensaje de éxito y el código HTTP 200.
    - Si hay un error en la solicitud, devuelve un mensaje de error y el código HTTP correspondiente.

    Requiere autenticación de token.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder al recurso")
    
    producto=Producto.query.get(id)

    if producto is None:
        return handle_not_found("El producto con ese ID no se encuentra")

    if request.method=="PUT":
        p_nombre=request.form.get("nombre").upper().strip() if request.form.get("nombre") is not None else None
        p_precio=float(request.form.get("precio")) if request.form.get("precio") is not None else None
        p_tipo="General" if request.form.get("tipo") is None else request.form.get("tipo")

        if not p_nombre or not p_precio or float(p_precio)<0.0:
            return handle_bad_request("No se enviaron los datos necesarios")
        
        tipo=Tipo.query.filter_by(nombre=p_tipo).first()

        if tipo is None:
            return handle_conflict("El tipo de producto no existe en la base de datos")

        if 'file' in request.files:
            last_image=Imagen.query.filter_by(id=producto.get_imagen_id()).first()
            imagen_subida=request.files['file']
            if imagen_subida is not None:
                filename=secure_filename(imagen_subida.filename)
                if filename !='':
                    file_ext=os.path.splitext(filename)[1]
                    if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validar_imagen(imagen_subida.stream):
                        return handle_bad_request("La imagen subida no cumple con el formato permitido 'jpg','png'")

                    #Removing the last image of producto
                    path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+last_image.get_filename()          
                    if os.path.exists(path) and last_image.get_id()!=3:
                        os.remove(path)
                        final_filename=p_nombre+file_ext
                        imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PRODUCTOS'],final_filename))
                        img=Imagen(final_filename,current_app.config['UPLOAD_PATH_PRODUCTOS'],imagen_subida.mimetype)
                        db.session.add(img)
                        db.session.commit()

                        producto.imagen_id=img.get_id()
                        db.session.commit()

                        db.session.delete(last_image)
                        db.session.commit()

                    elif last_image.get_id()==3:
                        final_filename=p_nombre+file_ext
                        imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PRODUCTOS'],final_filename))
                        img=Imagen(final_filename,current_app.config['UPLOAD_PATH_PRODUCTOS'],imagen_subida.mimetype)
                        db.session.add(img)
                        db.session.commit()

                        producto.imagen_id=img.get_id()
                        db.session.commit()              

        try:
            nombre=producto.get_nombre()
            precio=producto.get_precio()
            tipo_id_actual = producto.get_tipo_id()
            tipo_id_nuevo = tipo.get_id()
            
            if p_nombre != nombre:
                producto.nombre=p_nombre
                db.session.commit()

            if p_precio != precio:
                producto.precio=p_precio
                db.session.commit()

            if tipo_id_actual != tipo_id_nuevo:
                producto.tipo_id=tipo.get_id()
                db.session.commit()
            

            if p_nombre == nombre and p_precio == precio and tipo_id_actual == tipo_id_nuevo:
                if 'file' in request.files:
                    return jsonify({"mensaje":"Se edito el producto satisfactoriamente","http_code":200}),200
                else:
                    return handle_conflict("Los datos enviados son iguales a los actuales")
            
            return jsonify({"mensaje":"Se edito el producto satisfactoriamente","http_code":200}),200 
        except Exception as e:
            db.session.rollback()
            return jsonify({"mensaje": "El producto no se pudo editar","error":e.args[0],
                            "http_code":500}),500
    return jsonify({"mensaje":"Se envian datos del producto %s" % id,"producto":producto.get_json(),"http_code":200}),200

@producto_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    """
    Elimina un producto según su ID.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID del producto a eliminar.

    Retorna:
    - Si el método de la solicitud es DELETE:
        - Si se elimina el producto satisfactoriamente, retorna un JSON con el mensaje "Se elimino el producto satisfactoriamente" y el código HTTP 200.
    - Si el método de la solicitud es GET:
        - Retorna un JSON con el mensaje "Estas seguro de querer eliminar el Producto {nombre del producto}" y el código HTTP 200.

    Restricciones:
    - El usuario actual debe ser un administrador para acceder a este recurso.
    - Si el producto no existe, retorna un JSON con el mensaje "El producto con ese ID no se encuentra" y el código HTTP correspondiente.
    - Si el método de la solicitud es DELETE y el producto tiene una imagen asociada, la imagen también se elimina del sistema de archivos.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder al recurso")
    producto=Producto.query.get(id)
    if producto is None:
        return handle_not_found("El producto con ese ID no se encuentra")

    if request.method=='DELETE':
        img_id=producto.get_imagen_id()
        img=Imagen.query.filter_by(id=img_id).first()
        path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+img.get_filename()  
        
        db.session.delete(producto)
        db.session.commit()
        if os.path.exists(path) and img_id!=3:
            os.remove(path)
        return jsonify({"mensaje":"Se elimino el producto satisfactoriamente","http_code":200}),200
    
    elif request.method=='GET':
        return jsonify({"mensaje":"Estas seguro de querer eliminar el Producto %s" % producto.nombre,"producto":producto.get_json(),"http_code":200}),200
 
@producto_scope.route('/buscar', methods=['GET'])
@token_required
def buscar_producto(current_user):
    """
    Busca productos según los parámetros proporcionados.

    Parámetros:
    - tipo (str): El tipo de producto a buscar. Si se proporciona '*', se buscarán todos los tipos de productos.
    - nombre (str): El nombre del producto a buscar. Si se proporciona '-', se buscarán todos los productos del tipo especificado.

    Retorna:
    - JSON: Un objeto JSON que contiene una lista de productos encontrados y el código de estado HTTP 200 si se encontraron productos.
    """
    tipo = request.args.get('tipo', default='*', type=str)
    nombre = request.args.get('nombre', default='-', type=str).replace('_', ' ').upper()

    json_productos = []
    if request.method == 'GET':
        if tipo == '*':
            productos = Producto.query.all()
        elif tipo in ['General', 'Pollos', 'Chifa'] and nombre == '-':
            tipo_id = Tipo.query.filter_by(nombre=tipo).first()
            productos = Producto.query.filter_by(tipo_id=tipo_id.get_id()).all()
        elif tipo in ['General', 'Pollos', 'Chifa'] and nombre != '-':
            tipo_id = Tipo.query.filter_by(nombre=tipo).first()
            productos = Producto.query.filter(Producto.nombre.like('%' + nombre + '%'), Producto.tipo_id == tipo_id.get_id()).all()
        else:
            return handle_not_found("No se encontró ningún producto")

        for producto in productos:
            json_productos.append(producto.get_json())

        return jsonify({"productos": json_productos, "http_code": 200}), 200


@producto_scope.route('/ver/<id_producto>',methods=['GET'])
@token_required
def ver_producto(current_user,id_producto):
    """
    Muestra la información de un producto específico.

    Parámetros:
    - current_user: El usuario actual.
    - id_producto: El ID del producto a mostrar.

    Retorna:
    - Si el producto existe, se devuelve la imagen asociada al producto.
    - Si la imagen no existe, se asigna una imagen por defecto al producto y se devuelve esa imagen.
    - Si el producto no existe, se devuelve un mensaje de error.

    """
    producto=Producto.query.filter_by(id=id_producto).first()
    if producto is None:
        return handle_not_found("El producto con ese ID no se encuentra")
    img_id=producto.get_imagen_id()
    img=Imagen.query.filter_by(id=img_id).first()
    path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+img.get_filename()          
    if os.path.exists(path):
        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PRODUCTOS'],img.get_filename())
    else:
        producto.imagen_id=3
        db.session.commit()
        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PRODUCTOS'],'pollo_inicial.png')



