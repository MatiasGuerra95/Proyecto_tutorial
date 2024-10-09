import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =  False






db = SQLAlchemy(app)



class Trabajador(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rut = db.Column(db.String(10), nullable = False)
    nombre = db.Column(db.String(80), nullable = False)
    correo = db.Column(db.String(120), unique = True, nullable = False)


    
    
    def __repr__(self):
        return f'<trabajador {self.nombre}>' 
    



class Contrato(db.Model):
    pass















@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"