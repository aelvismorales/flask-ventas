from app import create_app
from os import environ

app=create_app(environ.get("FLASK_CONFIG","default"))

if __name__=="__main__":
    app.run()