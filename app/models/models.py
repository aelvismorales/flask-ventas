from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,AnonymousUserMixin

db=SQLAlchemy()

login_manager=LoginManager()

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

    def __init__(self,nombre,contraseña,role_id=None) -> None:
        self.nombre=nombre
        self.contraseña=generate_password_hash(contraseña,method="pbkdf2",salt_length=8)
        if self.role_id is None :
            if self.nombre == "aelvismorales":
                role=Role.query.filter_by(nombre="Administrador").first()
                self.role_id=role.get_id()
            elif self.role_id is None and role_id is not None:
                self.role_id=role_id
            else:
                self.role_id=1

    def __repr__(self) -> str:
        return '< User %s,%s>' % self.nombre,self.role_id
    
    def verificar_contraseña(self,contraseña):
        return check_password_hash(self.contraseña,contraseña)
    
    def can(self,permiso):
        return self.role is not None and self.role.has_permiso(permiso)
    
    def is_administrador(self):
        return self.can(Permission.ADMINISTRADOR)

class AnonymousUser(AnonymousUserMixin):
    def can(self):
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
