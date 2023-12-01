
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from flask import Blueprint,request,make_response,jsonify
from sqlalchemy import asc
from ..models.models import NotaPedido,db,detalle_venta,Producto
from ..decorators import token_required

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
    data=request.json
    np_pago_efectivo=data.get("pago_efectivo",0.00)
    np_pago_visa=data.get("pago_visa",0.00)
    np_pago_yape=data.get("pago_yape",0.00)

    np_motorizado=data.get("motorizado","-")
    np_comprador=data.get("nombre_comprador","VARIOS").strip().upper()
    np_direccion=data.get("direccion","Local").strip().upper()
    np_telefono=data.get("telefono","-").strip()
    np_estado_pago= True if data.get("estado_pago")=='True' else False
    np_comentario=data.get("comentario","")

    #np_paga=data.get("paga-con",0.0)
    np_productos=data.get("productos",[])

    #TODO VERIFICAR QUE LA SUMA TOTAL DE LOS PAGOS SEA IGUAL A LA DEL TOTAL SALE DESDE FRONT DADO QUE EN BACKEND NECESITARE EL TOTAL SALE PREVIO A CREAR LA NOTA DE PEDIDO QUE TAMBIEN ME LO PUEDEN ENVIAR DESDE FRONT.
    if np_telefono is not None and np_comprador is not None and np_direccion is not None:
        if request.method=='POST':
            if current_user.get_rol()=='Mozo':
                np_mesa_id=data.get("mesa_id")
                nota=NotaPedido(current_user.get_id(),np_motorizado,np_comprador,np_direccion,np_telefono,np_estado_pago,np_mesa_id,np_pago_efectivo,np_pago_yape,np_pago_visa,np_comentario)
            else:    
                nota=NotaPedido(current_user.get_id(),np_motorizado,np_comprador,np_direccion,np_telefono,np_estado_pago,pago_efectivo=np_pago_efectivo,pago_yape=np_pago_yape,pago_visa=np_pago_visa,comentario=np_comentario)

            db.session.add(nota)
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

            response=make_response(jsonify({"mensaje":"Nota de pedido creado correctamente-is not None","nota":nota.get_json(),"http_code":200}))

    else:
        response=make_response(jsonify({"mensaje":"Alguno de los campos ingresados no es valido o esta vacio","http_code":500}))

    response.headers['Content-type']='application/json'
    return response

@nota_scope.route('/editar/<id>',methods=['GET','PUT'])
@token_required
def editar(current_user,id):
    nota=NotaPedido.query.get(id)
    if not nota:
        response=make_response(jsonify({"mensaje":"Nota de pedido no encontrada","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    
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
            response=make_response(jsonify({"mensaje":"Se actualizo la nota de pedido correctamente","http_code":"200"}))
            response.headers['Content-Type']='application/json'
            return response
        except Exception as e:
            error=e.args[0]
            db.session.rollback()
            response=make_response(jsonify({"mensaje":"Error al editar los datos","error":error,"http_code":500}))
            response.headers['Content-Type']='application/json'
            return response
    if request.method == 'GET':
        response=make_response(jsonify({"nota":nota.get_json(),"http_code":"200"}))
        response.headers['Content-Type']='application/json'
        return response


@nota_scope.route('/editar/mozo/<id_nota>',methods=['PUT','GET'])	
@token_required
def editar_mozo_nota(current_user,id_nota):
    nota=NotaPedido.query.get(id_nota)
    if not nota:
        response=make_response(jsonify({"mensaje":"Nota de pedido no encontrada","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    
    if request.method == 'PUT':
        data=request.json
        np_productos=data.get("productos",[]) # Nuevo
        productos_nota=nota.get_productos_id() #Actual 
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
            response=make_response(jsonify({"mensaje":"Se actualizo la nota de pedido correctamente","http_code":"200"}))
            response.headers['Content-Type']='application/json'
            return response
        
        except Exception as e:
            error=e.args[0]
            db.session.rollback()
            response=make_response(jsonify({"mensaje":"Error al editar los datos","error":error,"http_code":500}))
            response.headers['Content-Type']='application/json'
            return response
    if request.method == 'GET':
        response=make_response(jsonify({"nota":nota.get_json(),"http_code":"200"}))
        response.headers['Content-Type']='application/json'
        return response

@nota_scope.route('/ver/<id>',methods=['GET'])
@token_required
def ver(current_user,id):
    nota=NotaPedido.query.get(id)
    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"nota":nota.get_json()}))
    response.headers['Content-type']="application/json"
    return response

@nota_scope.route('/resumen',methods=['GET','POST'])
@token_required
def resumen(current_user):

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response

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
                cancelado_efectivo+=notas.get_efectivo()
                cancelado_yape+=notas.get_yape()
                cancelado_visa=notas.get_visa()

            response=make_response(jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                                            ,"cancelado_general_total":cancelado_general_total,"cancelado_efectivo":cancelado_efectivo,"cancelado_yape":cancelado_yape,"cancelado_visa":cancelado_visa,"recuento_ventas":len(notas_pedidos_resumen)}))
            response.headers['Content-type']="application/json"
            return response
        else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener las notas de pedido","http_code":404}))
            response.headers['Content-type']="application/json"
            return response
    
    # En caso sea un GET SIMPLE RETORNAMOS EL RESUMEN DEL DIA ACTUAL
    notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin)).order_by(asc(NotaPedido.id)).all()
    
    if len(notas_pedidos_resumen)>0:
        for notas in notas_pedidos_resumen:
            json_notas_pedidos.append(notas.get_json())
            cancelado_general_total+=notas.get_total()
            cancelado_efectivo+=notas.get_efectivo()
            cancelado_yape+=notas.get_yape()
            cancelado_visa=notas.get_visa()
        response=make_response(jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                                        ,"cancelado_general_total":cancelado_general_total,"cancelado_efectivo":cancelado_efectivo,"cancelado_yape":cancelado_yape,"cancelado_visa":cancelado_visa,"recuento_ventas":len(notas_pedidos_resumen)}))
        response.headers['Content-type']="application/json"
        return response
    else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener las notas de pedido","http_code":500}))
            response.headers['Content-type']="application/json"
            return response


@nota_scope.route('/anular/<id>',methods=['PUT'])
@token_required
def anular(current_user,id):
#DEBERIAS PODER CONVERTIRLO A VENTA NUEVAMENTE QUIZAS HACER UN COMBO BOX Y CAMBIARLO A TU DISPOSICION EL TIPO DE VENTA  
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    nota=NotaPedido.query.get(id)
    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response

    if request.method=='PUT' and nota is not None:
        tipo=request.args.get('tipo',default='ANULADO',type=str).upper()
        nota.tipo_pago=tipo
        db.session.commit()
        response=make_response(jsonify({"mensaje":"La nota de pedido cambio a %s" % tipo,"http_code":200}))
        response.headers['Content-type']="application/json"
        return response
    
@nota_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}))
        response.headers["Content-type"]="application/json"
        return response
    
    nota=NotaPedido.query.get(id)

    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}))
        response.headers['Content-type']="application/json"
        return response
    
    if request.method=='DELETE' and nota is not None:
        db.session.delete(nota)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el nota","http_code":200}))
        response.headers['Content-type']="application/json"
        return response
    
    elif request.method=='DELETE' and nota is None:
        response=make_response(jsonify({"mensaje": "El nota que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    elif (request.method=='DELETE' or request.method=='GET') and nota is None:
        response=make_response(jsonify({"mensaje": "La nota que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500}))
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el nota %s" % nota.id,"nota":nota.get_json(),"http_code":200}))
    response.headers['Content-type']="application/json"
    return response


@nota_scope.route('/notas-cocina',methods=['GET'])
@token_required
def notas_cocina(current_user):
    #TODO VERIFICAR QUE SEAN DEL DIA
    fecha_inicio=(datetime.now(timezone.utc)-timedelta(hours=5)).strftime('%Y/%m/%d')
    fecha_fin=(datetime.now(timezone.utc)-timedelta(hours=5)+timedelta(days=1)).strftime('%Y/%m/%d')
    notas=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin),NotaPedido.estado_atendido==False).order_by(asc(NotaPedido.id)).all()
    #notas=NotaPedido.query.filter_by(estado_atendido=False).all()
    json_notas=[]
    for nota in notas:
        json_notas.append(nota.get_json())
    response=make_response(jsonify({"notas":json_notas,"http_code":"200"}))
    response.headers['Content-type']='application/json'
    return response

@nota_scope.route('/nota-cocina-ready/<id>',methods=['PUT'])
@token_required
def nota_cocina_ready(current_user,id):
    nota=NotaPedido.query.get(id)
    if not nota:
        response=make_response(jsonify({"mensaje":"Nota de pedido no encontrada","http_code":500}))
        response.headers['Content-type']="application/json"
        return response

    nota.estado_atendido=True
    db.session.commit()
    response=make_response(jsonify({"mensaje":"Nota Atendida","http_code":"200"}))
    response.headers['Content-type']='application/json'
    return response




