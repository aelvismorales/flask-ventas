from os import environ
from dotenv import load_dotenv
load_dotenv()
class Config():
    SECRET_KEY="4KK#ASDA"
    DEBUG=False
    TESTING=False
    SQLALCHEMY_DATABASE_URI="mysql://root:admin@localhost/markus_brasa"

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