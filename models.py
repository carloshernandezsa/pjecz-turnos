from app import db


class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer)
    numero = db.Column(db.Integer)
    tipo = db.Column(db.Integer)
    autoridad_id = db.Column(db.Integer)
    creado = db.Column(db.DateTime)
    atencion = db.Column(db.DateTime , nullable=True)
    termino = db.Column(db.DateTime , nullable=True)
    ventanilla_id = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    comentarios = db.Column(db.String(250))

class Ventanilla(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autoridad_id = db.Column(db.Integer)
    numero = db.Column(db.Integer)
    descripcion = db.Column(db.String(50))
    creado = db.Column(db.DateTime , nullable=True)
    usuario_id = db.Column(db.Integer)
    estatus = db.Column(db.Integer)

        
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(45))
    apellido_paterno = db.Column(db.String(45))
    apellido_materno = db.Column(db.String(45))
    usuario = db.Column(db.String(45))
    password = db.Column(db.String(45))
    rol_id = db.Column(db.Integer)
    autoridad_id = db.Column(db.Integer)
    
    
class Autoridades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distrito_id = db.Column(db.Integer)
    descripcion = db.Column(db.String(50))
    descripcion_corta = db.Column(db.String(50))
    clave = db.Column(db.Integer)
    
class Departamentos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    nombre_corto = db.Column(db.String(50))    
    
#class Roles(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    nombre = db.Column(db.String(30))
 