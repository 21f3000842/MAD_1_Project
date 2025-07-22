from flask import Flask
from pyfiles.database import db
from pyfiles.config import Config
from pyfiles.models import *
from pyfiles.create_db_instance import create_tables

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.drop_all()  # Ensure old tables are dropped
    db.create_all()
    create_tables()

print("✅ Database reset and all tables recreated.")
