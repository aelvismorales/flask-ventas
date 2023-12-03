from flask import Flask
from config import config,CORS_CONFIG
from flask_cors  import CORS
from app.routes import auth_scope,producto_scope,articulo_scope,nota_scope,mesa_scope
from app.models.models import db,Role,Tipo,Imagen
from flask_migrate import Migrate,upgrade,init,migrate

import os

migration=Migrate()
cors=CORS()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config.get(config_name,"default"))
    db.init_app(app)
    migration.init_app(app,db)
    with app.app_context():
        db.create_all()
        Role.insertar_roles()
        Tipo.insertar_tipos()
        Imagen.insertar_fotos()
        if os.path.exists("migrations"):
            upgrade()
        else:
            init()
            migrate(message="Initial database migration")
    cors.init_app(app, **CORS_CONFIG)
    
    app.register_blueprint(auth_scope,url_prefix="/auth")
    app.register_blueprint(producto_scope,url_prefix="/producto")
    app.register_blueprint(articulo_scope,url_prefix="/articulo")
    app.register_blueprint(nota_scope,url_prefix="/nota")
    app.register_blueprint(mesa_scope,url_prefix="/mesa")

    return app
