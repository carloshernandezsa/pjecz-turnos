from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from database import db

app = Flask(__name__)
USER_DB = "root"
PASS_DB = ""
URL_DB = "localhost"
NAME_DB = "pjecz_sistema_turnos"
FULL_URL_DB = f"mysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}"

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Usersin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    
    
if __name__ == "__main__":
    app.run()