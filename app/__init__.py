from flask import Flask
from config import config
from .routes.auth import auth_scope
from .routes.producto import producto_scope
from .models.models import db,login_manager,Role,Tipo
from flask_migrate import Migrate

migrate=Migrate()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config.get(config_name,"default"))
    db.init_app(app)
    with app.app_context():
        db.create_all()
        Role.insertar_roles()
        Tipo.insertar_tipos()
    migrate.init_app(app,db)
    login_manager.init_app(app)
    app.register_blueprint(auth_scope,url_prefix="/auth")
    app.register_blueprint(producto_scope,url_prefix="/producto")
    return app
