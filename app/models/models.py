from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone,timedelta

db=SQLAlchemy()
scale=2
class Permission:
    VER_APLICACION=1
    CREAR_NOTA=2
    CREAR_PRODUCTO=4
    CREAR_ARTICULO=8
    ADMINISTRADOR=16


class Usuario(db.Model):
    __tablename__='usuarios'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),unique=True,index=True)
    contraseña=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id',ondelete='SET DEFAULT',name="fk_Role"),nullable=False,server_default='1')
    imagen_id=db.Column(db.Integer,db.ForeignKey('imagenes.id',ondelete='SET DEFAULT',name='FK_imagen_usuario'),nullable=False,server_default='1')
    nota_pedidos=db.relationship('NotaPedido',backref='usuario',lazy='dynamic')
    
    # OCUPADO : TRUE OR FALSE;
    #mesas=db.relationship('Mesa',backref='usuario',lazy='dynamic',cascade='all,delete-orphan')


    # Para que el role_id sea uno se debe eliminar el rol de la siguiente manera
    # role=Role.query.filter_By(id=3).first()
    # db.session.delete(role)
    # db.session.commit()  -> De esta manera podremos eliminar sin problemas un rol 
    #TODO - Modificar seleccion de imagenes segun el rol creado.
    def __init__(self, nombre, contraseña, role_id=None) -> None:
        self.nombre = nombre
        self.contraseña = generate_password_hash(contraseña, method="pbkdf2", salt_length=8)
        if self.role_id is None:
            role = None
            img_filename = 'usuario_perfil.png'
            if self.nombre == "aelvismorales":
                role = Role.query.filter_by(nombre="Administrador").first()
                img_filename = 'administrador_perfil.png'
            elif role_id is not None and role_id ==5:
                role = Role.query.get(role_id)
                img_filename = 'administrador_perfil.png'
                
            if role is not None:
                self.role_id = role.id
            else:
                self.role_id = 1
            img = Imagen.query.filter_by(filename=img_filename).first()
            self.imagen_id = img.id

    def __repr__(self) -> str:
        return str('id:%s,nombre:%s,role:%s') % (self.id,self.nombre,self.role.get_nombre())
    
    def verificar_contraseña(self,contraseña):
        return check_password_hash(self.contraseña,contraseña)
    
    def can(self,permiso):
        return self.role is not None and self.role.has_permiso(permiso)
    
    def is_administrador(self):
        return self.can(Permission.ADMINISTRADOR)

    def get_json(self):
        json={"id":self.id,"nombre":self.nombre,"role_id":self.role.get_nombre()}
        return json
    
    def get_imagen_id(self):
        return self.imagen_id
    
    def get_id(self):
        return self.id
    
    def get_rol(self):
        return self.role.get_nombre()
    
    def get_nombre(self):
        return self.nombre

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permisos=db.Column(db.Integer)
    usuarios=db.relationship('Usuario',backref='role',lazy='dynamic',cascade='all,delete-orphan')
    # Con All -> Si elimino un Role todos los usuarios asociados a este se eliminaran, pero en realidad se pondra como 1 dado al SET DEFAULT
    # Con delete-orphan -> Si se elimina usuarios de la lista de Roles, este usuario se eliminara automaticamente si ya no esta asociado a ningun rol.

    def __init__(self,nombre) -> None:
        self.nombre=nombre
        if self.permisos is None:
            self.permisos=0

    def __repr__(self) -> str:
        return '<Rol %s>' % self.nombre
    
    def has_permiso(self,permiso):
        return self.permisos & permiso == permiso

    def agregar_permiso(self,permiso):
        if not self.has_permiso(permiso):
            self.permisos+=permiso
    
    def remover_permiso(self,permiso):
        if self.has_permiso(permiso):
            self.permisos-=permiso
    
    def reiniciar_permisos(self):
        self.permisos=0

    def get_id(self):
        return self.id
    
    def get_nombre(self):
        return self.nombre

    @staticmethod
    def insertar_roles():
        roles={
            'Usuario':[Permission.CREAR_NOTA],
            'Cajero': [Permission.CREAR_NOTA],
            'Mozo': [Permission.CREAR_NOTA],
            'Delivery':[Permission.VER_APLICACION],
            'Administrador':[Permission.CREAR_NOTA,Permission.CREAR_ARTICULO,Permission.CREAR_PRODUCTO,Permission.ADMINISTRADOR]
        }
        default_role='Usuario'
        for r in roles:
            role=Role.query.filter_by(nombre=r).first()
            if role is None:
                role=Role(nombre=r)
            role.reiniciar_permisos()

            for permisos in roles[r]:
                role.agregar_permiso(permisos)
            role.default=(role.nombre == default_role)
            db.session.add(role)
        db.session.commit()

#class Cliente(db.Model):
#    __tablename__="clientes"
#    id=db.Column(db.Integer,primary_key=True)
#    nombre=db.Column(db.String(64),nullable=False)
#    direccion=db.Column(db.String(64),nullable=False)
#    telefono=db.Column(db.String(64),nullable=False,unique=True)
#    nota_pedidos=db.relationship('NotaPedido',backref='cliente',lazy='dynamic')

#    def __init__(self,nombre,direccion,telefono) -> None:
#        self.nombre=nombre
#        self.direccion=direccion
#        self.telefono=telefono

#    def get_json(self):
#        json={"id":self.id,"nombre":self.nombre,"direccion":self.direccion,"telefono":self.telefono}
#        return json
    
#    def get_id(self):
#        return self.id

detalle_venta=db.Table('detalle_venta',
                       db.Column('nota_id',db.Integer,db.ForeignKey('nota_pedidos.id')),
                       db.Column('producto_id',db.Integer,db.ForeignKey('productos.id')),
                       db.Column('dv_cantidad',db.Numeric(precision=10,scale=2)),
                       db.Column('dv_precio',db.Numeric(precision=10,scale=2)),
                       db.Column('dv_atendido',db.Boolean(),default=False)
                       )
    
class Producto(db.Model):
    __tablename__="productos"
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),unique=True)
    precio=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    tipo_id=db.Column(db.Integer,db.ForeignKey('tipos.id',ondelete='SET DEFAULT',name='FK_tipo_producto'),nullable=False,server_default='1')
    imagen_id=db.Column(db.Integer,db.ForeignKey('imagenes.id',ondelete='SET DEFAULT',name='FK_imagen_producto'),nullable=False,server_default='3')
    # TO DO - CUANDO INICIES EN LA BASE DE DATOS PARA CREAR UN PRODUCTO POR DEFECTO DEBER EXISTIR LA IMAGEN 1
    def __init__(self,nombre,precio,tipo_id=1,imagen_id=3) -> None:
        self.nombre=nombre
        self.precio= Decimal(precio).quantize(Decimal("1e-{0}".format(scale)))
        self.tipo_id=tipo_id
        self.imagen_id=imagen_id
    
    def __repr__(self) -> str:
        return '<Producto %s,precio:%.2f>' % (self.nombre,self.precio)

    def get_imagen_id(self):
        return self.imagen_id
    
    def get_nombre(self):
        return self.nombre
    
    def get_json(self):
        json={"id":self.id,"nombre":"%s" % self.nombre, "precio":f'{self.precio:.2f}',"tipo_id":self.tipo_id,"imagen_id":self.imagen_id}
        
        return json if json is not None else {}
    def get_id(self):
        return self.id

class NotaPedido(db.Model):
    __tablename__="nota_pedidos"
    id=db.Column(db.Integer,primary_key=True)
    fecha_venta=db.Column(db.DateTime,default=datetime.now(timezone.utc)-timedelta(hours=5))
    #tipo_pago=db.Column(db.String(64),nullable=False)
    pago_efectivo=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pago_yape=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pago_visa=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    nombre=db.Column(db.String(64),nullable=False)
    direccion=db.Column(db.String(64),nullable=False)
    telefono=db.Column(db.String(64),nullable=True)
    usuario_id=db.Column(db.Integer,db.ForeignKey('usuarios.id'))
    motorizado=db.Column(db.String(64),nullable=False,default='-')
    comentario=db.Column(db.String(128),nullable=False,default="-")


    productos=db.relationship('Producto',secondary=detalle_venta,
                              backref=db.backref('nota_pedidos',lazy='dynamic'),
                              lazy='dynamic')
    total=db.Column(db.Numeric(precision=10,scale=2),default=0.00)
    estado_pago=db.Column(db.Boolean,default=False) # True-Cancelado False Por cancelar
    estado_atendido=db.Column(db.Boolean,default=False) # True Atendido False No Atendido
    mesa_id=db.Column(db.Integer,db.ForeignKey('mesas.id',ondelete='SET DEFAULT',),nullable=True,server_default=None)

    def __init__(self,usuario_id,motorizado,nombre,direccion,telefono,estado_pago=False,mesa_id=None,pago_efectivo=0.00,pago_yape=0.00,pago_visa=0.00,comentario="") -> None:
        self.pago_efectivo=pago_efectivo
        self.pago_yape=pago_yape
        self.pago_visa=pago_visa
        self.usuario_id=usuario_id
        self.motorizado=motorizado
        self.nombre=nombre
        self.direccion=direccion
        self.telefono=telefono
        self.estado_pago=estado_pago
        self.mesa_id=mesa_id
        self.comentario=comentario
        

    def get_productos(self):
        """
        Retorna una lista con los productos en la nota de pedido. solo nombre y cantidad.
        """
        detalles=db.session.query(Producto,detalle_venta.c.dv_cantidad,detalle_venta.c.dv_precio,detalle_venta.c.dv_atendido).join(detalle_venta,Producto.id==detalle_venta.c.producto_id).filter(detalle_venta.c.nota_id==self.id)
        lista_productos=[]
        for producto,cantidad,dv_precio,dv_atendido in detalles:
            lista_productos.append({
                "nombre":producto.get_nombre(),
                "cantidad": Decimal(cantidad).quantize(Decimal("1e-{0}".format(scale))),
                "precio":Decimal(dv_precio).quantize(Decimal("1e-{0}".format(scale))),
                "atendido":dv_atendido
            })

        return lista_productos
    
    def get_productos_id(self):
        """
        Retorna una lista con los productos en la nota de pedido. solo nombre y cantidad.
        """
        detalles=db.session.query(Producto,detalle_venta.c.dv_cantidad,detalle_venta.c.dv_precio).join(detalle_venta,Producto.id==detalle_venta.c.producto_id).filter(detalle_venta.c.nota_id==self.id)
        lista_productos=[]
        for producto,cantidad,dv_precio in detalles:
            lista_productos.append({
                "producto_id":producto.get_id(),
                "cantidad": Decimal(cantidad).quantize(Decimal("1e-{0}".format(scale))),
                "precio":Decimal(dv_precio).quantize(Decimal("1e-{0}".format(scale)))
            })

        return lista_productos
    
    def get_fecha_venta(self):
        if self.fecha_venta is not None:
            return self.fecha_venta.strftime('%d/%m/%Y %H:%M:%S')
        return None
    
    def get_efectivo(self):
        return self.pago_efectivo
    
    def get_yape(self):
        return self.pago_yape
    
    def get_visa(self):
        return self.pago_visa

    def get_total(self):
        return self.total

    def get_json(self):
        json={"id":self.id,"fecha_venta":self.get_fecha_venta(),"pago_efectivo":self.pago_efectivo,"pago_yape":self.pago_yape,"pago_visa":self.pago_visa,"cliente":self.nombre,"direccion":self.direccion,"telefono":self.telefono,
              "usuario":self.usuario.get_nombre(),"productos":self.get_productos(),"motorizado":self.motorizado,"total":self.total,"estado_pago":self.estado_pago,"estado_atendido":self.estado_atendido,"mesa":self.mesa_id}

        return json
    
    def get_id(self):
        return self.id

class Mesa(db.Model):
    __tablename__='mesas'
    id=db.Column(db.Integer,primary_key=True)
    piso=db.Column(db.Integer,nullable=False)
    numero_mesa=db.Column(db.Integer,nullable=False)
    estado_mesa=db.Column(db.Boolean,default=False) # True Ocupado False Desocupado
    #usuario_id=db.Column(db.Integer,db.ForeignKey('usuarios.id'))
    nota_pedidos=db.relationship('NotaPedido',backref='mesa',lazy='dynamic',cascade='all,delete-orphan')

    def __init__(self,piso,numero_mesa) -> None:
        self.piso=piso
        self.numero_mesa=numero_mesa
    
    def set_estado(self,estado):
        if estado is not None:
            self.estado=estado
        else:
            self.estado=False
    
    def get_json(self):
        json={"id":self.id,"piso":self.piso,"numero_mesa":self.numero_mesa,"estado_mesa":self.estado_mesa}
        return json
    


class Tipo(db.Model):
    __tablename__="tipos"
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),nullable=False)
    productos=db.relationship('Producto',backref='tipo',lazy='dynamic')
    def __init__(self,nombre) -> None:
        self.nombre=nombre
    
    def insertar_tipos():
        tipos=['General','Pollos','Chifa']
        for t in tipos:
            tipo=Tipo.query.filter_by(nombre=t).first()
            if tipo is None:
                tipo=Tipo(t)
                db.session.add(tipo)
        db.session.commit()

    def get_id(self):
        return self.id
    
class Imagen(db.Model):
    __tablename__="imagenes"
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.Text,nullable=False)
    filepath=db.Column(db.Text,nullable=False)
    mimetype=db.Column(db.String(24),nullable=False)
    productos=db.relationship('Producto',backref='imagen',lazy='dynamic')
    usuarios=db.relationship('Usuario',backref='imagen',lazy='dynamic')

    def __init__(self,filename,filepath,mimetype) -> None:
        self.filename=filename
        self.filepath=filepath
        self.mimetype=mimetype
    
    def __repr__(self) -> str:
        return "<Imagen %s>" % self.id
    def get_filename(self):
        return "%s" % self.filename
    
    def get_id(self):
        return self.id
    
    def insertar_fotos():
        filename_administrador='administrador_perfil.png'
        filename_usuario='usuario_perfil.png'
        filename_producto='pollo_inicial.png'
        mimetype="mime/png"
        filepath_perfiles='uploads/perfiles'
        filepath_productos='uploas/productos'

        imagenes=[filename_administrador,filename_usuario]
        imageni=[filename_producto]
        for i in imagenes:
            img=Imagen.query.filter_by(filename=i).first()
            if img is None:
                imagen=Imagen(i,filepath_perfiles,mimetype)
                db.session.add(imagen)

        for i in imageni:
            img=Imagen.query.filter_by(filename=i).first()
            if img is None:
                imagen=Imagen(i,filepath_productos,mimetype)
                db.session.add(imagen)

        db.session.commit()

class Articulo(db.Model):
    __tablename__="articulos"
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),unique=True)
    unidad=db.Column(db.String(32))
    cantidad=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    fecha_actualizacion=db.Column(db.DateTime,default=datetime.now)

    def __init__(self,nombre,unidad,cantidad) -> None:
        self.nombre=nombre
        self.unidad=unidad
        self.cantidad=cantidad

    def get_id(self):
        return self.id
    
    def get_fecha_actualizacion(self):
        if self.fecha_actualizacion is not None:
            return self.fecha_actualizacion.strftime('%d/%m/%Y')
        return None
    
    def get_json(self):
        json={"id":self.id,"nombre":self.nombre,"unidad":self.unidad,"cantidad":f'{self.cantidad:.2f}',"fecha_actualizacion":self.get_fecha_actualizacion()}
        return json