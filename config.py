import os
from os import environ
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__),'.env')
load_dotenv(dotenv_path)

CORS_CONFIG = {"resources": {"/*": {"origins": '*', "supports_credentials": True}}}
#CORS_CONFIG = {"resources": {"/*": {"origins": [environ.get('CORS_CF')] if environ.get('CORS_CF') is not None else '*',"supports_credentials":bool(environ.get('CORS_CREDENTIAL')) if environ.get('CORS_CREDENTIAL') is not None else False}}}

print(environ.get('SECRET_KEY'))
class Config():
    SECRET_KEY="ABC123"
    DEBUG=False
    TESTING=False
    SQLALCHEMY_DATABASE_URI=environ.get('DB_DEV')
    #,"mysql+mysqlconnector://root:admin@127.0.0.1/markus_brasa"

    # Configuracion ruta de Imagenes
    MAX_CONTENT_LENGTH=1024*1024
    UPLOAD_EXTENSIONS=['.jpg','.png']
    UPLOAD_PATH_PRODUCTOS='/var/www/html/flask-ventas/uploads/productos'
    UPLOAD_PATH_PERFILES='/var/www/html/flask-ventas/uploads/perfiles'

class ProductionConfig(Config):
     SQLALCHEMY_DATABASE_URI=environ.get("DATABASE_PRODUCTION")

class TestConfig(Config):
     TESTING=True
     DEBUG=True
     #SQLALCHEMY_DATABASE_URI="mysql://remote:admin@192.168.100.17:3307/markus_brasa_test"
     SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:admin@localhost/markus_brasa_test"

class DevelopmentConfig(Config):
    DEBUG=True

config={
     "development":DevelopmentConfig,
     "testing":TestConfig,
     "production":ProductionConfig,
     "default":DevelopmentConfig
}
