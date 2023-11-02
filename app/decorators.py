from functools import wraps
from flask import abort
from flask_login import current_user
from .models.models import Permission

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