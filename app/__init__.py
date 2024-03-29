from flask import Flask
from config import config,CORS_CONFIG
from flask_cors  import CORS
from .routes.auth import auth_scope
from .routes.producto import producto_scope
from .routes.articulo import articulo_scope
from .routes.nota_pedido import nota_scope
from .models.models import db,login_manager,Role,Tipo,Imagen
from flask_migrate import Migrate

migrate=Migrate()
cors=CORS()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config.get(config_name,"default"))
    db.init_app(app)
    with app.app_context():
        db.create_all()
        Role.insertar_roles()
        Tipo.insertar_tipos()
        Imagen.insertar_fotos()
    migrate.init_app(app,db)
    login_manager.session_protection = "strong"
    login_manager.login_view="auth.login"
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = (u"Session timed out, please re-login")
    login_manager.needs_refresh_message_category = "info"
    login_manager.init_app(app)
    cors.init_app(app, **CORS_CONFIG)
    app.register_blueprint(auth_scope,url_prefix="/auth")
    app.register_blueprint(producto_scope,url_prefix="/producto")
    app.register_blueprint(articulo_scope,url_prefix="/articulo")
    app.register_blueprint(nota_scope,url_prefix="/nota")

    return app
