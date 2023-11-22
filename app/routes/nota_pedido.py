import datetime
from decimal import Decimal
from flask import Blueprint,request,make_response,jsonify
from sqlalchemy import asc
from ..models.models import NotaPedido,Cliente,db,detalle_venta
from ..decorators import token_required

nota_scope=Blueprint('nota_pedido',__name__)

@nota_scope.route('/crear',methods=['POST'])
@token_required
def crear(current_user):
    data=request.json
    np_tipo_pago=data.get("tipo")
    np_motorizado=data.get("motorizado","-")
    np_comprador=data.get("nombre_comprador").strip().upper()
    np_direccion=data.get("direccion").strip().upper()
    np_telefono=data.get("telefono","-").strip()
    #np_paga=data.get("paga-con",0.0)
    np_productos=data.get("productos",[])

    cliente_reg=Cliente.query.filter_by(telefono=np_telefono).first()
    if np_telefono != "-" and cliente_reg is None:
        nuevo_cliente=Cliente(np_comprador,np_direccion,np_telefono)
        db.session.add(nuevo_cliente)
        db.session.commit()
        print(nuevo_cliente.get_id())
        if request.method=='POST':
            #Verificar si existe cliente_id y usuario id
            nota=NotaPedido(np_tipo_pago,nuevo_cliente.get_id(),current_user.get_id(),np_motorizado)
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

            response=make_response(jsonify({"mensaje":"Nota de pedido creado correctamente-is None","nota":nota.get_json(),"http_code":200}),200)


    elif np_telefono!="-" and cliente_reg is not None:
        if request.method=='POST':
            nota=NotaPedido(np_tipo_pago,cliente_reg.get_id(),current_user.get_id(),np_motorizado)
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

            response=make_response(jsonify({"mensaje":"Nota de pedido creado correctamente-is not None","nota":nota.get_json(),"http_code":200}),200)

    else:
        response=make_response(jsonify({"mensaje":"Alguno de los campos ingresados no es valido","http_code":500}),500)

    response.headers['Content-type']='application/json'
    return response


@nota_scope.route('/ver/<id>',methods=['GET'])
@token_required
def ver(current_user,id):
    nota=NotaPedido.query.get(id)
    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}),404)
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"nota":nota.get_json()}))
    response.headers['Content-type']="application/json"
    return response

@nota_scope.route('/resumen',methods=['GET','POST'])
@token_required
def resumen(current_user):

    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}),403)
        response.headers["Content-type"]="application/json"
        return response

    fecha_inicio=request.args.get('fecha_inicio',default=(datetime.datetime.now()).strftime('%Y/%m/%d'),type=str)
    fecha_fin=request.args.get('fecha_fin',default=(datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y/%m/%d'),type=str)
    np_motorizado=request.args.get('motorizado',default='-',type=str)

    json_notas_pedidos=[]
    cancelado_total=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_yape=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_plin=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))
    cancelado_visa=Decimal(0.0).quantize(Decimal("1e-{0}".format(2)))

    if request.method=='POST':
        if np_motorizado!='-':
            notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin),NotaPedido.motorizado==np_motorizado).order_by(asc(NotaPedido.id)).all()
        else:
            notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin)).order_by(asc(NotaPedido.id)).all()    

        if len(notas_pedidos_resumen)>0:
            for notas in notas_pedidos_resumen:
                json_notas_pedidos.append(notas.get_json())
                if notas.get_tipo() == 'CANCELADO':
                    cancelado_total+=notas.get_total()
                elif notas.get_tipo()=='CANCELADO-YAPE':
                    cancelado_yape+=notas.get_total()
                elif notas.get_tipo()=='CANCELADO-PLIN':
                    cancelado_plin+=notas.get_total()
                elif notas.get_tipo()=='CANCELADO-VISA':
                    cancelado_visa+=notas.get_total()
                else:
                    continue
            response=make_response(jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                                            ,"cancelado_total":cancelado_total,"cancelado_yape":cancelado_yape,"cancelado_plin":cancelado_plin,"cancelado_visa":cancelado_visa}),200)
            response.headers['Content-type']="application/json"
            return response
        else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener las notas de pedido","http_code":404}),404)
            response.headers['Content-type']="application/json"
            return response
    
    # En caso sea un GET SIMPLE RETORNAMOS EL RESUMEN DEL DIA ACTUAL
    notas_pedidos_resumen=NotaPedido.query.filter(NotaPedido.fecha_venta.between(fecha_inicio,fecha_fin)).order_by(asc(NotaPedido.id)).all()
    
    if len(notas_pedidos_resumen)>0:
        for notas in notas_pedidos_resumen:
            json_notas_pedidos.append(notas.get_json())
            if notas.get_tipo() == 'CANCELADO':
                cancelado_total+=notas.get_total()
            elif notas.get_tipo()=='CANCELADO-YAPE':
                cancelado_yape+=notas.get_total()
            elif notas.get_tipo()=='CANCELADO-PLIN':
                cancelado_plin+=notas.get_total()
            elif notas.get_tipo()=='CANCELADO-VISA':
                cancelado_visa+=notas.get_total()
            else:
                continue
        response=make_response(jsonify({"mensaje":"Resumen de Notas obtenido","fecha_inicio":fecha_inicio,"fecha_fin":fecha_fin,"notas":json_notas_pedidos,"http_code":200
                                        ,"cancelado_total":cancelado_total,"cancelado_yape":cancelado_yape,"cancelado_plin":cancelado_plin,"cancelado_visa":cancelado_visa}),200)
        response.headers['Content-type']="application/json"
        return response
    else:
            response=make_response(jsonify({"mensaje":"No se pudo obtener las notas de pedido","http_code":500}),500)
            response.headers['Content-type']="application/json"
            return response


@nota_scope.route('/anular/<id>',methods=['PUT'])
@token_required
def anular(current_user,id):
#DEBERIAS PODER CONVERTIRLO A VENTA NUEVAMENTE QUIZAS HACER UN COMBO BOX Y CAMBIARLO A TU DISPOSICION EL TIPO DE VENTA  
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}),403)
        response.headers["Content-type"]="application/json"
        return response
    
    nota=NotaPedido.query.get(id)
    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}),404)
        response.headers['Content-type']="application/json"
        return response

    if request.method=='PUT' and nota is not None:
        tipo=request.args.get('tipo',default='ANULADO',type=str).upper()
        nota.tipo_pago=tipo
        db.session.commit()
        response=make_response(jsonify({"mensaje":"La nota de pedido cambio a %s" % tipo,"http_code":200},200))
        response.headers['Content-type']="application/json"
        return response
    
@nota_scope.route('/eliminar/<id>',methods=['GET','DELETE'])
@token_required
def eliminar(current_user,id):
    
    if not current_user.is_administrador():
        response=make_response(jsonify({"mensaje":"No tienes Autorizacion para acceder","http_code":403}),403)
        response.headers["Content-type"]="application/json"
        return response
    
    nota=NotaPedido.query.get(id)
    if request.method=='DELETE' and nota is not None:
        db.session.delete(nota)
        db.session.commit()
        response=make_response(jsonify({"mensaje": "Se ha eliminado satisfactoriamente el nota","http_code":200}),200)
        response.headers['Content-type']="application/json"
        return response
    
    elif request.method=='DELETE' and nota is None:
        response=make_response(jsonify({"mensaje": "El nota que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500},500))
        response.headers['Content-type']="application/json"
        return response
    elif (request.method=='DELETE' or request.method=='GET') and nota is None:
        response=make_response(jsonify({"mensaje": "La nota que quieres eliminar no existe o no se puede acceder a sus datos","http_code":500},500))
        response.headers['Content-type']="application/json"
        return response
    # TO DO VERIFICAR IF STATEMENTS SI ENVIAN UN ID QUE NO ES VALIDO ENTONCES EL RESPONSE DE GET NO FUNCIONARA.
    response=make_response(jsonify({"mensaje":"Estas seguro de querer eliminar el nota %s" % nota.id,"nota":nota.get_json(),"http_code":200}),200)
    response.headers['Content-type']="application/json"
    return response





