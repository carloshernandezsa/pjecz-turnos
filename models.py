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
    UsuarioId = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(45))
    ApellidoP = db.Column(db.String(45))
    ApellidoM = db.Column(db.String(45))
    NumEmpleado = db.Column(db.Integer)
    Usuario = db.Column(db.String(45))
    Password = db.Column(db.String(45))
    RolId = db.Column(db.Integer)
    JuzgadoId = db.Column(db.Integer)
    EstatusId = db.Column(db.Integer)
    

class Ventanilla(db.Model):
    VentanillaId = db.Column(db.Integer, primary_key=True)
    Ventanilla = db.Column(db.Integer)
    UsuarioId = db.Column(db.Integer)
    JuzgadoId = db.Column(db.Integer)
    EstatusId = db.Column(db.Integer)
    
class Juzgados(db.Model):
    JuzgadoId = db.Column(db.Integer, primary_key=True)
    Juzgado = db.Column(db.String(50))
    DistritoId = db.Column(db.Integer)