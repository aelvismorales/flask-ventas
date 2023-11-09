from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,AnonymousUserMixin

db=SQLAlchemy()

login_manager=LoginManager()
scale = 2

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Permission:
    VER_APLICACION=1
    CREAR_NOTA=2
    CREAR_PRODUCTO=4
    CREAR_ARTICULO=8
    ADMINISTRADOR=16


class Usuario(UserMixin,db.Model):
    __tablename__='usuarios'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(64),unique=True,index=True)
    contraseña=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id',ondelete='SET DEFAULT',name="fk_Role"),nullable=False,server_default='1')
    imagen_id=db.Column(db.Integer,db.ForeignKey('imagenes.id',ondelete='SET DEFAULT',name='FK_imagen_usuario'),nullable=False,server_default='1')
    
    # Para que el role_id sea uno se debe eliminar el rol de la siguiente manera
    # role=Role.query.filter_By(id=3).first()
    # db.session.delete(role)
    # db.session.commit()  -> De esta manera podremos eliminar sin problemas un rol 
    def __init__(self,nombre,contraseña,role_id=None) -> None:
        self.nombre=nombre
        self.contraseña=generate_password_hash(contraseña,method="pbkdf2",salt_length=8)
        if self.role_id is None :
            if self.nombre == "aelvismorales":
                role=Role.query.filter_by(nombre="Administrador").first()
                self.role_id=role.get_id()
                img=Imagen.query.filter_by(filename='administrador_perfil.png').first()
                self.imagen_id=img.get_id()

            elif self.role_id is None and role_id is not None:
                self.role_id=role_id
                img=Imagen.query.filter_by(filename='usuario_perfil.png').first()
                self.imagen_id=img.get_id()
            else:
                self.role_id=1
                img=Imagen.query.filter_by(filename='usuario_perfil.png').first()
                self.imagen_id=img.get_id()

    def __repr__(self) -> str:
        return str('id:%s,nombre:%s,role:%s') % (self.id,self.nombre,self.role.get_nombre())
        #return '< User %s,%s>' % (self.nombre,self.role_id)
    
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

class AnonymousUser(AnonymousUserMixin):
    def can(self,permiso):
        return False
    def is_administrador(self):
        return False   
    
login_manager.anonymous_user=AnonymousUser


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
    
    def get_json(self):
        json={"id":self.id,"nombre":"%s" % self.nombre, "precio":f'{self.precio:.2f}',"tipo_id":self.tipo_id,"imagen_id":self.imagen_id}
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

