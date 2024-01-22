
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from flask import Blueprint,request,jsonify
from sqlalchemy import asc
from ..models.models import NotaPedido,db,detalle_venta,Usuario
from ..decorators import token_required
from ..errors.errors import *
nota_scope=Blueprint('nota_pedido',__name__)


def find_modified_deleted_and_added(data1, data2):
        modified = []
        deleted = []
        added = []

        # Crear conjuntos de 'id' para comparación
        set_ids_data1 = {item['producto_id'] for item in data1}
        set_ids_data2 = {item['producto_id'] for item in data2}

        # Encontrar elementos modificados y eliminados
        for item in data1:
            if item['producto_id'] in set_ids_data2:
                corresponding_item = next((i for i in data2 if i['producto_id'] == item['producto_id']), None)
                if corresponding_item and corresponding_item != item:
                    modified.append(item)
            else:
                deleted.append(item)

        # Encontrar elementos agregados
        for item in data2:
            if item['producto_id'] not in set_ids_data1:
                added.append(item)

        return modified, deleted, added


@nota_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):
    """
    Crea una nota de pedido con los datos proporcionados.

    Parámetros:
    - current_user: El usuario actual que realiza la creación de la nota de pedido.

    Ejemplo Json:
    {
        "nombre_comprador": "JUAN PEREZ",
        "direccion": "AV. LOS PINOS 123",
        "telefono": "987654321",
        "pago_efectivo": 10.00,
        "pago_visa": 0.00,
        "pago_yape": 0.00,
        "vuelto": 0.00,
        "motorizado": "MOTORIZADO",
        "estado_pago": "True",
        "comentario": "SIN COMENTARIOS",
        "productos": [
            {
                "producto_id": 1,
                "cantidad": 1,
                "precio": 10.00
            },
            {
                "producto_id": 2,
                "cantidad": 1,  
                "precio": 10.00
            }
        ]
    }

    Retorna:
    - Un objeto JSON que contiene el mensaje de éxito, la información de la nota de pedido y el código HTTP 200 en caso de éxito.
    - Un objeto JSON que contiene el mensaje de error y el código HTTP correspondiente en caso de fallo.

    """
    data=request.json
    np_pago_efectivo=data.get("pago_efectivo",0.00)
    np_pago_visa=data.get("pago_visa",0.00)
    np_pago_yape=data.get("pago_yape",0.00)
    np_vuelto=data.get("vuelto",0.00)

    np_motorizado=data.get("motorizado","-")
    np_comprador=data.get("nombre_comprador","VARIOS").strip().upper()
    np_direccion=data.get("direccion","Local").strip().upper()
    np_telefono=data.get("telefono","-").strip()
    np_estado_pago= True if data.get("estado_pago")=='True' else False
    np_comentario=data.get("comentario","")

    #np_paga=data.get("paga-con",0.0)
    np_productos=data.get("productos",[])

    if np_productos is None or len(np_productos)==0:
        return handle_bad_request("No se puede crear una nota de pedido sin productos")

    #TODO VERIFICAR QUE LA SUMA TOTAL DE LOS PAGOS SEA IGUAL A LA DEL TOTAL SALE DESDE FRONT DADO QUE EN BACKEND NECESITARE EL TOTAL SALE PREVIO A CREAR LA NOTA DE PEDIDO QUE TAMBIEN ME LO PUEDEN ENVIAR DESDE FRONT.
    if np_telefono is not None and np_comprador is not None and np_direccion is not None:
        if request.method=='POST':
            if current_user.get_rol()=='Mozo':
                np_mesa_id=data.get("mesa_id")
                nota=NotaPedido(current_user.get_id(),np_motorizado,np_comprador,np_direccion,np_telefono,np_estado_pago,np_mesa_id,np_pago_efectivo,np_pago_yape,np_pago_visa,np_vuelto,np_comentario)
            else:    
                nota=NotaPedido(current_user.get_id(),np_motorizado,np_comprador,np_direccion,np_telefono,np_estado_pago,pago_efectivo=np_pago_efectivo,pago_yape=np_pago_yape,pago_visa=np_pago_visa,vuelto=np_vuelto,comentario=np_comentario)

            db.session.add(nota)
            db.session.commit()
            
            if np_motorizado!='-':
                usuario_delivery=Usuario.query.filter_by(nombre=np_motorizado).first()
                if usuario_delivery:
                    usuario_delivery.ocupado=True
                    db.session.commit()

            total_sale = Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))

            for producto in np_productos:
                # Estos son los datos que deben de ser enviados en productos json
                product_id=producto.get("producto_id")
                cantidad=Decimal(producto.get("cantidad",1)).quantize(Decimal("1e-{0}".format(2)))
                producto_precio=Decimal(producto.get("precio",1)).quantize(Decimal("1e-{0}".format(2)))

                total_sale+=producto_precio*cantidad
                detalle_=detalle_venta.insert().values(nota_id=nota.get_id(),producto_id=product_id,dv_cantidad=cantidad,dv_precio=producto_precio)
                db.session.execute(detalle_)
            
            nota.total=total_sale
            db.session.commit()
            return jsonify({"mensaje":"Nota de pedido creado correctamente","nota":nota.get_json(),"http_code":200}),200
    else:
        return handle_bad_request("Alguno de los campos ingresados no es valido o esta vacio")

@nota_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):    
    """
    Función para editar una nota de pedido.

    Parámetros:
    - current_user: Usuario actual.
    - id: ID de la nota de pedido a editar.

    Ejemplo Json:
    {
        "nombre_comprador": "JUAN PEREZ",
        "direccion": "AV. LOS PINOS 123",
        "telefono": "987654321",
        "pago_efectivo": 10.00,
        "pago_visa": 0.00,
        "pago_yape": 0.00,
        "motorizado": "MOTORIZADO",
        "estado_pago": "True",
        "comentario": "SIN COMENTARIOS",
        "productos": [
            {
                "producto_id": 1,
                "cantidad": 1,
                "precio": 10.00
            },
            {
                "producto_id": 2,
                "cantidad": 1,
                "precio": 10.00
            }
        ]
    }
    Retorna:
    - Si el método de la solicitud es PUT:
        - Si se actualiza la nota de pedido correctamente, retorna un JSON con el mensaje "Se actualizó la nota de pedido correctamente" y el código HTTP 200.
        - Si ocurre un error al editar los datos, retorna un JSON con el mensaje "Error al editar los datos", el error específico y el código HTTP 500.
    - Si el método de la solicitud es GET:
        - Retorna un JSON con la información de la nota de pedido y el código HTTP 200.
    """
    nota=NotaPedido.query.get(id)
    if not nota:
        return handle_not_found("Nota de pedido no encontrada")
    
    if request.method == 'PUT':
        data=request.json
        np_pago_efectivo=data.get("pago_efectivo",0.00)
        np_pago_visa=data.get("pago_visa",0.00)
        np_pago_yape=data.get("pago_yape",0.00)
        np_motorizado=data.get("motorizado","-")
        np_comprador=data.get("nombre_comprador").strip().upper()
        np_direccion=data.get("direccion").strip().upper()
        np_telefono=data.get("telefono","-").strip()
        np_estado_pago= True if data.get("estado_pago")=='True' else False
        np_comentario=data.get("comentario","")
        np_productos=data.get("productos",[])
        total_sale = Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
        try:
            for producto in np_productos:
                producto_id=producto.get("producto_id")
                cantidad=Decimal(producto.get("cantidad",1)).quantize(Decimal("1e-{0}".format(2)))
                producto_precio=Decimal(producto.get("precio",1)).quantize(Decimal("1e-{0}".format(2)))

                total_sale+=producto_precio*cantidad
                detalle=(detalle_venta.update()
                        .where(detalle_venta.c.nota_id==id)
                        .where(detalle_venta.c.producto_id==producto_id).values(dv_cantidad=cantidad,dv_precio=producto_precio)
                        )
                db.session.execute(detalle)

            nota.pago_efectivo=np_pago_efectivo
            nota.pago_yape=np_pago_yape
            nota.pago_visa=np_pago_visa

            nota.nombre=np_comprador
            nota.direccion=np_direccion
            nota.telefono=np_telefono
            nota.motorizado=np_motorizado
            nota.estado_pago=np_estado_pago
            nota.comentario=np_comentario
            nota.total=total_sale
            
            db.session.commit()
            return jsonify({"mensaje":"Se actualizo la nota de pedido correctamente","http_code":"200"}),200
        except Exception as e:
            error=e.args[0]
            db.session.rollback()
            return jsonify({"mensaje":"Error al editar los datos","error":error,"http_code":500}),500

    if request.method == 'GET':
        return jsonify({"nota":nota.get_json(),"http_code":"200"}),200


@nota_scope.route('/editar/mozo/<id_nota>',methods=['PUT','GET'])	
@token_required
def editar_mozo_nota(current_user,id_nota):
    """
    Edita la información de una nota de pedido
    seleccionando los productos de una mesa en específico, seleccionada por el mozo.

    Parámetros:
    - current_user: El usuario actual.
    - id_nota: El ID de la nota de pedido a editar.

    Ejemplo Json:
    {
        "productos": [
            {
                "producto_id": 1,
                "cantidad": 1,
                "precio": 10.00
            },
            {
                "producto_id": 2,
                "cantidad": 1,
                "precio": 10.00
            }
        ]
    }

    Métodos HTTP permitidos:
    - PUT: Actualiza la información de la nota de pedido.
    - GET: Obtiene la información de la nota de pedido.

    Retorna:
    - Si el método es PUT:
        - Si la actualización es exitosa, retorna un mensaje de éxito y el código HTTP 200.
        - Si ocurre un error durante la edición, retorna un mensaje de error y el código HTTP 500.
    - Si el método es GET:
        - Retorna la información de la nota de pedido y el código HTTP 200.

    """
    nota=NotaPedido.query.get(id_nota)
    if not nota:
        return handle_not_found("Nota de pedido no encontrada")
    
    if request.method == 'PUT':
        data=request.json
        np_productos=data.get("productos",[]) # Nuevo
        productos_nota=nota.get_productos_id() # Actual 
        total_sale = Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
        
        modified_items, deleted_items, added_items = find_modified_deleted_and_added(productos_nota, np_productos)
        
        for deleted_item in deleted_items:
            detalle_delete=detalle_venta.delete().where(detalle_venta.c.nota_id==id_nota).where(detalle_venta.c.producto_id==deleted_item.get('producto_id'))
            db.session.execute(detalle_delete)

        for modified_item in modified_items:
            detalle_modified=detalle_venta.update().where(detalle_venta.c.nota_id==id_nota).where(detalle_venta.c.producto_id==modified_item.get('producto_id')).values(dv_cantidad=modified_item.get('cantidad'),dv_precio=modified_item.get('precio'))
            db.session.execute(detalle_modified)
        
        for added_item in added_items:
            detalle_added=detalle_venta.insert().values(nota_id=id_nota, producto_id=added_item.get('producto_id'),dv_cantidad=added_item.get('cantidad'),dv_precio=added_item.get('precio'))
            db.session.execute(detalle_added)

        nota.total=total_sale
        nota.estado_atendido=False
    
        try:
            db.session.commit()
            return jsonify({"mensaje":"Se actualizo la nota de pedido correctamente","http_code":"200"}),200
        except Exception as e:
            error=e.args[0]
            db.session.rollback()
            return jsonify({"mensaje":"Error al editar los datos","error":error,"http_code":500}),500
    if request.method == 'GET':
        return jsonify({"nota":nota.get_json(),"http_code":"200"}),200

@nota_scope.route('/ver/<id>',methods=['GET'])
@token_required
def ver(current_user,id):
    nota=NotaPedido.query.get(id)
    if nota is None:
        return handle_not_found("El nota con ese ID no se encuentra")
    
    return jsonify({"nota":nota.get_json(),"http_code":200}),200

@nota_scope.route('/ver/mesa-id/<id_mesa>',methods=['GET'])
@token_required
def ver_mesa_id(current_user,id_mesa):
    nota=NotaPedido.query.filter_by(mesa_id=id_mesa).first()
    if nota is None:
        return handle_not_found("El nota con ese ID no se encuentra")
    
    return jsonify({"nota":nota.get_json(),"http_code":200}),200


@nota_scope.route('/resumen',methods=['GET','POST'])
@token_required
def resumen(current_user):
    """
    Obtiene el resumen de las notas de pedido, dependiendo de la fecha de inicio y fecha de fin.

    Parámetros:
    - current_user: El usuario actual.

    Retorna:
    - Un objeto JSON con el resumen de las notas de pedido, incluyendo la fecha de inicio, fecha de fin, notas de pedido, total cancelado, total en efectivo, total en Yape, total en Visa y el recuento de ventas.

    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")

    fecha_inicio=request.args.get('fecha_inicio',default=(datetime.now(timezone.utc)-timedelta(hours=5)).strftime('%Y/%m/%d'),type=str)
    fecha_fin=request.args.get('fecha_fin',default=(datetime.now(timezone.utc)-timedelta(hours=5)+timedelta(days=1)).strftime('%Y/%m/%d'),type=str)
    np_motorizado=request.args.get('motorizado',default='-',type=str)

    json_notas_pedidos=[]

    cancelado_general_total=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_efectivo=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_yape=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_visa=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))

    if request.method=='POST':
        if np_motorizado!='-':
            notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin),NotaPedido.motorizado==np_motorizado).order_by(asc(NotaPedido.id)).all()
        else:
            notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin)).order_by(asc(NotaPedido.id)).all()    

        if len(notas_pedidos_resumen)>0:
            for notas in notas_pedidos_resumen:
                json_notas_pedidos.append(notas.get_json())
                cancelado_general_total+=notas.get_total()
                cancelado_efectivo+=notas.get_efectivo() - notas.get_vuelto()
                cancelado_yape+=notas.get_yape()
                cancelado_visa=notas.get_visa()

            return jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                            ,"cancelado_general_total":cancelado_general_total,"cancelado_efectivo":cancelado_efectivo,"cancelado_yape":cancelado_yape,"cancelado_visa":cancelado_visa,"recuento_ventas":len(notas_pedidos_resumen)}),200
        else:
            return handle_not_found("No se pudo obtener las notas de pedido")
    
    # En caso sea un GET SIMPLE RETORNAMOS EL RESUMEN DEL DIA ACTUAL
    notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin)).order_by(asc(NotaPedido.id)).all()
    
    if len(notas_pedidos_resumen)>0:
        for notas in notas_pedidos_resumen:
            json_notas_pedidos.append(notas.get_json())
            cancelado_general_total+=notas.get_total()
            cancelado_efectivo+=notas.get_efectivo() - notas.get_vuelto()
            cancelado_yape+=notas.get_yape()
            cancelado_visa=notas.get_visa()
        return jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                        ,"cancelado_general_total":cancelado_general_total,"cancelado_efectivo":cancelado_efectivo,"cancelado_yape":cancelado_yape,"cancelado_visa":cancelado_visa,"recuento_ventas":len(notas_pedidos_resumen)}),200
    else:
        return handle_not_found("No se pudo obtener las notas de pedido")


@nota_scope.route('/anular/<id>',methods=['PUT'])
@token_required
def anular(current_user,id):
#DEBERIAS PODER CONVERTIRLO A VENTA NUEVAMENTE QUIZAS HACER UN COMBO BOX Y CAMBIARLO A TU DISPOSICION EL TIPO DE VENTA  
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")
    
    nota=NotaPedido.query.get(id)
    if nota is None:
        return handle_not_found("El nota con ese ID no se encuentra")

    if request.method=='PUT':
        nota.anulado=True
        db.session.commit()
        return jsonify({"mensaje":"La nota de pedido %s cambio a ANULADO" % id,"http_code":200}),200
    
@nota_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):    
    """
    Elimina una nota de pedido.

    Parámetros:
    - current_user: El usuario actual.
    - id: El ID de la nota de pedido a eliminar.

    Retorna:
    - Si el método de la solicitud es DELETE:
        - Un objeto JSON con el mensaje de éxito y el código HTTP 200.
    - Si el método de la solicitud es GET:
        - Un objeto JSON con el mensaje de confirmación, la información de la nota de pedido y el código HTTP 200.

    Si el usuario actual no es un administrador, se devuelve un mensaje de error de autorización.
    Si no se encuentra una nota de pedido con el ID proporcionado, se devuelve un mensaje de error de no encontrado.
    """
    if not current_user.is_administrador():
        return handle_forbidden("No tienes Autorizacion para acceder")
    
    nota=NotaPedido.query.get(id)

    if nota is None:
        return handle_not_found("El nota con ese ID no se encuentra")
    
    if request.method=='DELETE':
        db.session.delete(nota)
        db.session.commit()
        
        return jsonify({"mensaje": "Se ha eliminado satisfactoriamente el nota","http_code":200}),200
    
    elif request.method=='GET':
        return jsonify({"mensaje":"Estas seguro de querer eliminar el nota %s" % nota.id,"nota":nota.get_json(),"http_code":200}),200


@nota_scope.route('/notas-cocina',methods=['GET'])
@token_required
def notas_cocina(current_user):
    """
    Obtiene las notas de pedido de cocina que aun no se han atendido, en el dia actual.

    Parámetros:
    - current_user: El usuario actual autenticado.

    Retorna:
    - Un objeto JSON que contiene las notas de pedido de cocina encontradas y el código HTTP 200 si se encontraron notas.
    - Un mensaje de error y el código HTTP 404 si no se encontraron notas de pedido.
    """
    fecha_inicio=(datetime.now(timezone.utc)-timedelta(hours=5)).strftime('%Y/%m/%d')
    fecha_fin=(datetime.now(timezone.utc)-timedelta(hours=5)+timedelta(days=1)).strftime('%Y/%m/%d')
    notas=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin),NotaPedido.estado_atendido==False).order_by(asc(NotaPedido.id)).all()

    if notas is None:
        return handle_not_found("No se encontraron notas de pedido")    
    json_notas=[]
    for nota in notas:
        json_notas.append(nota.get_json())
    return jsonify({"notas":json_notas,"http_code":"200"}),200

@nota_scope.route('/nota-cocina-ready/<id>',methods=['PUT'])
@token_required
def nota_cocina_ready(current_user,id):
    """
    Marca una nota de pedido como atendida por la cocina.

    Parámetros:
    - current_user: El usuario actual que realiza la solicitud.
    - id: El ID de la nota de pedido.

    Retorna:
    - Un objeto JSON con un mensaje de éxito y el código HTTP 200 si la nota de pedido se marcó como atendida correctamente.
    - Un objeto JSON con un mensaje de error y el código HTTP correspondiente si la nota de pedido no se encontró.

    """
    nota=NotaPedido.query.get(id)
    if not nota:
        return handle_not_found("Nota de pedido no encontrada")

    nota.estado_atendido=True
    db.session.commit()
    return jsonify({"mensaje":"Nota de pedido atendida","http_code":"200"}),200




