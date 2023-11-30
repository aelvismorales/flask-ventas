from functools import wraps
from flask import request,jsonify,current_app
from .models.models import Usuario
import jwt

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
            data=jwt.decode(token[1],key=current_app.config['SECRET_KEY'],algorithms=['HS256'])
            
            current_user=Usuario.query.filter_by(id=data['id']).first()
            
        except:
            return jsonify({'mensaje':'Token es invalido!','http_code':401}),401
        return f(current_user,*args,**kwargs)
    return decorated
