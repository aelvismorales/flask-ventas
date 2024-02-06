from os import environ
from dotenv import load_dotenv
load_dotenv()

#CORS_CONFIG = {"resources": {"/*": {"origins": ["http://localhost:61656"],"supports_credentials":False}}}
CORS_CONFIG = {"resources": {"/*": {"origins": [environ.get('CORS_CF')] if environ.get('CORS_CF') is not None else '*',"supports_credentials":bool(environ.get('CORS_CREDENTIAL')) if environ.get('CORS_CREDENTIAL') is not None else False}}}


class Config():
    SECRET_KEY=environ.get('SECRET_KEY')
    DEBUG=False
    TESTING=False
    SQLALCHEMY_DATABASE_URI=environ.get('DB_DEV')
    #,"mysql+mysqlconnector://root:admin@127.0.0.1/markus_brasa"

    # Configuracion ruta de Imagenes
    MAX_CONTENT_LENGTH=1024*1024
    UPLOAD_EXTENSIONS=['.jpg','.png']
    UPLOAD_PATH_PRODUCTOS='uploads/productos'
    UPLOAD_PATH_PERFILES='uploads/perfiles'

class ProductionConfig(Config):
     SQLALCHEMY_DATABASE_URI=environ.get("DATABASE_PRODUCTION")

class TestConfig(Config):
     TESTING=True
     DEBUG=True
     SQLALCHEMY_DATABASE_URI=environ.get("DATABASE_TEST_2")

class DevelopmentConfig(Config):
    DEBUG=True

config={
     "development":DevelopmentConfig,
     "testing":TestConfig,
     "production":ProductionConfig,
     "default":DevelopmentConfig
}