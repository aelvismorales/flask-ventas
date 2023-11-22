from functools import wraps
from flask import abort,request,jsonify,current_app
from flask_login import current_user
from .models.models import Permission,Usuario
import jwt

def permiso_requerido(permiso):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permiso):
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def administrador_requerido(f):
    return permiso_requerido(Permission.ADMINISTRADOR)(f)

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=None
        #pelao debe verificar aqui
        if 'Authorization' in request.headers:
            token=request.headers['Authorization'].split(" ")

        if not token:
            return jsonify({'mensaje':'Token no se encuentra!','http_code':403}),403 #no tiene autorizacion ni login
        try:
            data=jwt.decode(token[1],key=current_app.config['SECRET_KEY'],algorithms='HS256')
            current_user=Usuario.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'mensaje':'Token es invalido!','http_code':401}),401
        return f(current_user,*args,**kwargs)
    return decorated
