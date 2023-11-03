from flask import Blueprint,request,make_response,jsonify,current_app,send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename
from ..decorators import administrador_requerido
from ..models.models import Producto,Tipo,db,Imagen
from .general import validar_imagen
import os

producto_scope=Blueprint("producto",__name__)

@producto_scope.route('/crear',methods=['POST'])
@login_required
@administrador_requerido
def crear():
    """
    Esta ruta recibe un formulario con los siguiente datos
        nombre : POLLO ENTERO
        precio : 15.90
        tipo : Pollo
        file: img.png
    Finalmente, la respuesta es en formato Json, indicando la situacion de la solicitud.
    """
    p_nombre=request.form.get("nombre").upper().strip()
    p_precio=request.form.get("precio")
    p_tipo= "General" if request.form.get("tipo") is None else request.form.get("tipo")

    producto=Producto.query.filter_by(nombre=p_nombre).first()
    if producto is not None:
        response= make_response(jsonify({
            "mensaje": "El producto ya existe en la base de datos",
            "http_code": 409
        }),409)
        response.headers["Content-type"]="application/json"
        return response

    tipo=Tipo.query.filter_by(nombre=p_tipo).first()
    tipo_id=tipo.get_id()

    if 'file' not in request.files:
        response=make_response(jsonify({
            "mensaje":"No se ha subido ninguna imagen",
            "http_code":400
        }),400)
        response.headers["Content-type"]="application/json"
        return response
    else:
        imagen_subida=request.files['file']
        filename=secure_filename(imagen_subida.filename)
        if filename !='':
            file_ext=os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validar_imagen(imagen_subida.stream):
                response=make_response(jsonify({"mensaje":"La imagen subida no cumple con el formato permitido 'jpg','png'"
                                                ,"http_code":400}),400)
                response.headers["Content-type"]="application/json"
                return response
            final_filename=p_nombre+file_ext
            imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PRODUCTOS'],final_filename))
            img=Imagen(final_filename,current_app.config['UPLOAD_PATH_PRODUCTOS'],imagen_subida.mimetype)
            db.session.add(img)
            db.session.commit()
    try:
        img_id=img.get_id()
        nuevo_producto=Producto(p_nombre,p_precio,tipo_id,img_id)
        db.session.add(nuevo_producto)
        db.session.commit()
        response=make_response(jsonify({
            "mensaje":"Se creo el producto satisfactoriamente",
            "http_code":201
        }),201)
    except Exception as e:
        db.session.rollback()
        response=make_response(jsonify({"mensaje": "El producto no se pudo crear",
                                        "http_code":500}),500)
    response.headers["Content-type"]="application/json"    
    return response


@producto_scope.route('/ver/<id_producto>',methods=['GET'])
def ver_producto(id_producto):
    producto=Producto.query.filter_by(id=id_producto).first()
    img_id=producto.get_imagen_id()
    img=Imagen.query.filter_by(id=img_id).first()
    return send_from_directory('../'+current_app.config['UPLOAD_PATH_PRODUCTOS'],img.get_filename())