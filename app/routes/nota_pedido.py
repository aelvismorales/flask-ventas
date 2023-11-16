from decimal import Decimal
from flask import Blueprint,request,make_response,jsonify
from flask_login import login_required,current_user
from ..models.models import NotaPedido,Cliente,db,detalle_venta

nota_scope=Blueprint('nota_pedido',__name__)

@nota_scope.route('/crear',methods=['POST'])
@login_required
def crear():
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
@login_required
def ver(id):
    nota=NotaPedido.query.get(id)
    if nota is None:
        response=make_response(jsonify({"mensaje":"El nota con ese ID no se encuentra","http_code":404}),404)
        response.headers['Content-type']="application/json"
        return response
    
    response=make_response(jsonify({"nota":nota.get_json()}))
    response.headers['Content-type']="application/json"
    return response