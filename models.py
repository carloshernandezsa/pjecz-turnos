from app import db


class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer)
    numero = db.Column(db.Integer)
    tipo = db.Column(db.Integer)
    juzgado_id = db.Column(db.Integer)
    creado = db.Column(db.DateTime)
    atencion = db.Column(db.DateTime , nullable=True)
    termino = db.Column(db.DateTime , nullable=True)
    ventanilla_id = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    comentarios = db.Column(db.String(250))
    
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(45))
    apellido_paterno = db.Column(db.String(45))
    apellido_materno = db.Column(db.String(45))
    usuario = db.Column(db.String(45))
    password = db.Column(db.String(45))
    rol_id = db.Column(db.Integer)
    autoridad_id = db.Column(db.Integer)
    

class Ventanilla(db.Model):
    VentanillaId = db.Column(db.Integer, primary_key=True)
    Ventanilla = db.Column(db.Integer)
    UsuarioId = db.Column(db.Integer)
    JuzgadoId = db.Column(db.Integer)
    EstatusId = db.Column(db.Integer)
    
class Autoridades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50))
    descripcion_corta = db.Column(db.String(50))
    distrito_id = db.Column(db.Integer)
    clave = db.Column(db.Integer)
