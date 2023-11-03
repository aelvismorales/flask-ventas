from os import environ
from dotenv import load_dotenv
load_dotenv()
class Config():
    SECRET_KEY="4KK#ASDA"
    DEBUG=False
    TESTING=False
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root:admin@127.0.0.1/markus_brasa"

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
     SQLALCHEMY_DATABASE_URI=environ.get("DATABASE_TEST")

class DevelopmentConfig(Config):
    DEBUG=True

config={
     "development":DevelopmentConfig,
     "testing":TestConfig,
     "production":ProductionConfig,
     "default":DevelopmentConfig
}