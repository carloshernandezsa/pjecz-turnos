from app import db


class Turno(db.Model):
    TurnoId = db.Column(db.Integer, primary_key=True)
    NumTurno = db.Column(db.Integer)
    TipoTurnoId = db.Column(db.Integer)
    JuzgadoId = db.Column(db.Integer)
    Fecha = db.Column(db.DateTime)
    FechaAtencion = db.Column(db.DateTime , nullable=True)
    FechaTermino = db.Column(db.DateTime , nullable=True)
    UsuarioId = db.Column(db.Integer)
    VentanillaId = db.Column(db.Integer)
    EstatusTurnoId = db.Column(db.Integer)
    Comentarios = db.Column(db.String(250))
    
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