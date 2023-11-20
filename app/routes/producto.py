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
        response=make_response(jsonify({"mensaje": "El producto no se pudo crear","error":e.args[0],
                                        "http_code":500}),500)
    response.headers["Content-type"]="application/json"    
    return response

@producto_scope.route('/editar/<id>',methods=['GET','PUT'])
@login_required
@administrador_requerido
def editar(id):
    # CAMBIAR EL NOMBRE DE LA IMAGEN SI ES QUE SE CAMBIA EL NOMBRE DEL PRODUCTO ?
    producto=Producto.query.get(id)
    if request.method=="PUT":
        p_nombre=request.form.get("nombre").upper().strip()
        p_precio=float(request.form.get("precio"))
        p_tipo="General" if request.form.get("tipo") is None else request.form.get("tipo")

        tipo=Tipo.query.filter_by(nombre=p_tipo).first()
        mensaje_eliminado=""
        if 'file' in request.files:
            last_image=Imagen.query.get(producto.get_imagen_id())
            imagen_subida=request.files['file']
            if imagen_subida is not None:
                filename=secure_filename(imagen_subida.filename)
                if filename !='':
                    file_ext=os.path.splitext(filename)[1]
                    if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or file_ext != validar_imagen(imagen_subida.stream):
                        response=make_response(jsonify({"mensaje":"La imagen subida no cumple con el formato permitido 'jpg','png'"
                                                        ,"http_code":400}),400)
                        response.headers["Content-type"]="application/json"
                        return response

                    #Removing the last image of producto
                    path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+last_image.get_filename()          
                    if os.path.exists(path) and last_image.get_id()!=3:
                        os.remove(path)
                        #db.session.delete(last_image)
                        #db.session.commit()
                        #print(producto.get_imagen_id())
                        mensaje_eliminado="Se elimino la imagen anterior correctamente"
                    
                    final_filename=p_nombre+file_ext
                    imagen_subida.save(os.path.join(current_app.config['UPLOAD_PATH_PRODUCTOS'],final_filename))
                    img=Imagen(final_filename,current_app.config['UPLOAD_PATH_PRODUCTOS'],imagen_subida.mimetype)
                    db.session.add(img)
                    db.session.commit()
                    producto.imagen_id=img.get_id()
                        
        try:
            response=make_response(jsonify({
                "mensaje":"Se actualizo el producto correctamente",
                "adicional":mensaje_eliminado,
                "http_code":200
            }),200)
            producto.nombre=p_nombre
            producto.precio=p_precio
            producto.tipo_id=tipo.get_id()
            db.session.commit()
            response.headers["Content-type"]="application/json" 
            return response
        except Exception as e:
            db.session.rollback()
            response=make_response(jsonify({"mensaje": "El producto no se pudo crear","error":e.args[0],
                                            "http_code":500}),500)
        response.headers["Content-type"]="application/json"    
        return response
    response=make_response(jsonify({"messaje":"Se envian datos del producto %s" % id,"producto":producto.get_json(),"http_code":200},200))
    response.headers["Content-type"]="application/json"
    return response

@producto_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@login_required
@administrador_requerido
def eliminar(id):
    producto=Producto.query.get(id)
    if request.method=='DELETE' and producto is not None:
        db.session.delete(producto)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el producto","http_code":200}),200)
        response.headers['Content-type']="application/json"
        return response
    
    elif request.method=='DELETE' and producto is None:
        response=make_response(jsonify({"mensaje": "El producto que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500},500))
        response.headers['Content-type']="application/json"
        return response
    # TO DO VERIFICAR IF STATEMENTS SI ENVIAN UN ID QUE NO ES VALIDO ENTONCES EL RESPONSE DE GET NO FUNCIONARA.
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el Producto %s" % producto.nombre,"usuario":producto.get_json(),"http_code":200}),200)
    response.headers['Content-type']="application/json"
    return response

@producto_scope.route('/buscar',methods=['GET'])
@login_required
def buscar_producto():
    tipo=request.args.get('tipo',default='*',type=str)
    nombre=request.args.get('nombre',default='pollo',type=str).replace('_',' ').upper()

    print(tipo,nombre)
    productos=Producto.query.filter(Producto.nombre.like('%'+nombre+'%')).all()
    json_producto=[]
    if request.method=='GET' and tipo=='*' and len(productos) > 0:
        for pr in productos:
            json_producto.append(pr.get_json())
        response=make_response(jsonify({"productos":json_producto,"http_code":200},200))
        response.headers['Content-type']="application/json"
        return response
    elif request.method=='GET' and tipo !='*': # Lo ideal es un in ('General','Pollo','Chifa') para el tipo pero aun no se definen todas los tipos , "ideal enviar el ID del tipo tambien"
        tipo_id=Tipo.query.filter_by(nombre=tipo).first()
        productos=Producto.query.filter(Producto.nombre.like('%'+nombre+'%'),Producto.tipo_id==tipo_id.get_id()).all()
        for pr in productos:
            json_producto.append(pr.get_json())
        response=make_response(jsonify({"productos":json_producto,"http_code":200},200))
        response.headers['Content-type']="application/json"
        return response
    

@producto_scope.route('/ver/<id_producto>',methods=['GET'])
def ver_producto(id_producto):
    producto=Producto.query.filter_by(id=id_producto).first()
    if producto is None:
        response=make_response(jsonify({"mensaje":"El producto con ese ID no se encuentra","http_code":404}),404)
        response.headers['Content-type']="application/json"
        return response
    img_id=producto.get_imagen_id()
    img=Imagen.query.filter_by(id=img_id).first()
    path=current_app.config['UPLOAD_PATH_PRODUCTOS']+'/'+img.get_filename()          
    if os.path.exists(path):
        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PRODUCTOS'],img.get_filename())
    else:
        producto.imagen_id=3
        db.session.commit()

        return send_from_directory('../'+current_app.config['UPLOAD_PATH_PRODUCTOS'],'pollo_inicial.png')



