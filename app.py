from flask import Flask
from pyfiles.database import db
from pyfiles.create_db_instance import create_tables
from pyfiles.config import Config


def create_app():
    app =Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.app_context().push()


    return app

app = create_app()

from pyfiles.routes import *

if __name__ =='__main__':
    create_tables()
    app.run(debug=True)