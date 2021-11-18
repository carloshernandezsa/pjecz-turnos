import json
import random
import pprint ## impresion estilizada en consola

from flask import Flask, render_template, request, url_for, session
from flask_socketio import SocketIO, send
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func, inspect, or_, and_
from werkzeug.utils import redirect
from datetime import datetime


from database import db
from forms import TurnoForm
from models import Turno, Usuarios, Ventanilla

#CSRF Protect
csrf = CSRFProtect()

# Inicializar App Flask
app = Flask(__name__)
csrf.init_app(app)

#configuracion de la base de datos

#USER_DB = "postgres"
#PASS_DB = "admin"
#URL_DB = "localhost"
#NAME_DB = "pjecz_sistema_turnos"
#FULL_URL_DB = f'mysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
USER_DB = "root"
PASS_DB = ""
URL_DB = "localhost"
NAME_DB = "pjecz_sistema_turnos"
FULL_URL_DB = f"mysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}"

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SLQALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SQLALCHEMY_ECHO"] = True ## Mostrar consultas SQL en pantalla

#inicializar conexion a base de datos
db.init_app(app)

#configurar flask-migrate
migrate = Migrate()
migrate.init_app(app, db)

#configurar FlaskWTF
app.config['SECRET_KEY']='secret_key'

#inicializar SocketIo
socketio = SocketIO(app)
socketio.run(app)

# LLave secreta para sesiones
app.secret_key = "Mi_llave_secret@"
        
#ejecutar en consola los siguientes commandos
# flask db init
# flask db migrate
# flask db upgrade
# flask db stamp head "actualiza que tod@ esta a la ultima version"
# https://flask-migrate.readthedocs.io/en/latest/

@socketio.on('message')
def handelMessage(msg):
    if(int(msg['usuario']) != session['ventanilla']):
        msg['accion']=""    
    msg['usuarioFirmado'] = session['ventanilla']
    print('*************************************** Inicia la propagacion del mensaje ***************************************')
    send(msg , broadcast=True)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def inicio():
    if 'usuario' in session:
        print(f'pagina guardada en la session {session["pagina"]}')
        return render_template('index.html', pagina = session['pagina'])
    return redirect(url_for('login'))

@app.route('/login/', methods = ['GET','POST'] )
def login():
    #constantes
    session['roles'] = {1:'Recepcionista', 2:'Capturista', 3:'Administrador', 4:'Sistemas', 5:'Pantallas' }
    session['distritos'] = {1:"Saltillo",2:"Monclova",3:"Sabinas",4:"Rio Grande",5:"Acuña",6:"Torreón",7:"San Pedro",8:"Parras"}
    session['estatus'] = {1:"Activo", 2:"Inactivo"}
    session['estatusTurno'] = {1:"En espera",2:"Atendiendo",3:"Atendido",4:"Cancelado"} 
    session['juzgados'] = {1:"Oficialía Común de Partes Saltillo",3:"Oficialía Común de Partes Torreón",4:"Oficialía Común de Partes Monclova",5:"Oficialía Común de Partes Río Grande",7:"Torreón Familiar",8:"Torreón Mercantil"}
    

    if request.method=="POST":
        #Omitimos validacion de usuario y password
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        user  = Usuarios.query.filter(Usuarios.Usuario == usuario , Usuarios.Password == contrasena).first()
        ventanilla = Ventanilla.query.filter(Ventanilla.UsuarioId == user.UsuarioId).first()
        
        if(user):      
            session['JuzgadoId'] = user.JuzgadoId
            session['Oficina'] = session['juzgados'][user.JuzgadoId]
              
            print(f'Usuario que se firmo: {user.Nombre} {user.ApellidoP} {user.ApellidoM} ')
            if user.RolId == 1:
                session['pagina'] = '/nuevo/'
                session['ventanilla'] = 0
            if user.RolId == 2:
                session['pagina'] = '/atender/'
                session['ventanilla'] = ventanilla.VentanillaId
            if user.RolId == 5:
                session['pagina'] = '/pantalla/'
                session['ventanilla'] = 0
                
            session['usuario'] = user.UsuarioId   
            session['nombre'] = user.Nombre + " " + user.ApellidoP + " " + user.ApellidoM
            return redirect(url_for('inicio'))

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('usuario',None)
    session.pop('contrasena', None)
    session.pop('ventanilla', None)
    session.pop('nombre',None)
    session.pop('comentarios',None)
    session.pop('tipo', None)
    return redirect(url_for('login'))


@app.route('/pantalla/')
def pantalla():
    #Fecha actual
    hoy = datetime.today().strftime('%Y-%m-%d')
    turnos = Turno.query.filter(Turno.EstatusTurnoId <= 2 , func.DATE(Turno.Fecha) == hoy, Turno.JuzgadoId == session['JuzgadoId'] ).order_by(Turno.TurnoId).limit(8).all() 
    #registros = Turno.query.filter(Turno.VentanillaId == None , func.DATE(Turno.Fecha) == hoy ).order_by(Turno.TurnoId).limit(5).count()
    turno = Turno.query.filter(Turno.EstatusTurnoId == 2, func.DATE(
        Turno.Fecha) == hoy, Turno.JuzgadoId == session['JuzgadoId']).order_by(Turno.TurnoId.desc()).first()
    
    return render_template('pantalla.html', turno = turno, turnos = turnos)


@app.route('/consultar_usuario/', methods = ['GET','POST'])
def consultar_usuario():
    if 'usuario' in session: 
        usuario = session['ventanilla']
        return json.dumps({'success':200 , 'usuario': usuario})
    return json.dumps({'success':300,'usuario':''})


@app.route('/finalizar/', methods=['GET'])
@app.route('/finalizar/<int:id>',methods = ['GET','POST'])
def finalizar(id = 0):
    if id > 0 :
        #Actualizamos el estatus del turno
        try:
            turno = Turno.query.filter(Turno.TurnoId == id).first()
            turno.EstatusTurnoId = 3
            db.session.commit()
        except:
            pass
    return redirect(url_for('pantalla'))

@app.route('/atender/', methods=['GET'])
@app.route('/atender/<accion>', methods=['GET','POST'])
def atender(accion = None):
    #Fecha actual
    hoy = datetime.today().strftime('%Y-%m-%d')
    print(f'valor de accion {accion}')
    if(accion=="Atender"):
        try:
            print('*************************************************** Seleccion de un turno para ATENDER ************************ ')
            turno = Turno.query.filter(and_(Turno.EstatusTurnoId == 1 , func.DATE(Turno.Fecha) == hoy , Turno.JuzgadoId == session['JuzgadoId'], or_(Turno.TipoTurnoId == 1, Turno.TipoTurnoId == 2))).order_by(Turno.TipoTurnoId.desc(), Turno.NumTurno.asc()).first()
            turno.EstatusTurnoId = 2
            turno.VentanillaId = session['ventanilla']
            turno.FechaAtencion = datetime.now()
            db.session.commit()
            return redirect(url_for('concluir'))
        except:
            print("error al marcar turno como recibido para atender")
    try:
        turnos = Turno.query.filter(Turno.EstatusTurnoId == 1, func.DATE(Turno.Fecha) == hoy, Turno.JuzgadoId == session['JuzgadoId']).order_by(Turno.TurnoId).all()
    except:
        turnos = {"success":"sin registros"}
    return render_template('atender.html', turnos = turnos)

@app.route('/concluir/', methods=['GET'])
@app.route('/concluir/<int:id>', methods=['GET','POST'])
def concluir(id = 0):
    #Fecha actual
    hoy = datetime.today().strftime('%Y-%m-%d')
    if(id>0):
        try:
            turno = Turno.query.filter(Turno.TurnoId == id).first()
            turno.EstatusTurnoId = 3
            turno.FechaTermino = datetime.now()
            db.session.commit()
            return redirect(url_for('atender'))
        except:
            print("error al marcar turno como ATENDIDO (3)")
    try:
        turnos = Turno.query.filter(Turno.EstatusTurnoId == 2, func.DATE(Turno.Fecha) == hoy, Turno.VentanillaId == session['ventanilla']).order_by(Turno.TurnoId).limit(5).all()
    except:
        turnos = {"success":"sin registros"}
    return render_template('concluir.html', turnos = turnos)

@app.route('/nuevo/', methods=['GET','POST'])
@app.route('/nuevo/<accion>',methods=['GET','POST'])
def nuevo(accion = None):
    if(request.method == 'POST'):
        print(f' ***********---------------------- Inicia proceso de alta {request.form["accion"]}')
        #print(f'######################  Accion: {accion} , Usuario Firmado:{session["usuario"]} ')
        if(request.form['accion']=="Nuevo turno"):
            
            #Registrar nuevo renglon en la tabla de turnos
            hoy = datetime.today().strftime('%Y-%m-%d')
            turno  = Turno.query.filter(func.DATE(Turno.Fecha) == hoy, Turno.JuzgadoId == session['JuzgadoId']).order_by(Turno.NumTurno.desc()).first()
            if(turno):
                maximo = turno.NumTurno + 1
            else:
                maximo = 1
            
            turno = Turno()
            turno.NumTurno = maximo
            turno.Fecha =  datetime.now()
            turno.UsuarioId = session['usuario']
            turno.EstatusTurnoId = 1
            turno.Comentarios = request.form['comentarios']
            turno.TipoTurnoId = request.form['tipo']
            turno.JuzgadoId = session['JuzgadoId']
            
            db.session.add(turno)
            db.session.commit()
            print("se agregara un nuevo turno en la tabla")
            accion=""
            return redirect(url_for('nuevo'))
     
    data =  consultar_turnos()
    turno = Turno()
    turnoForm = TurnoForm(obj=turno)
    if(data):
        #, forma=turnoForm
        return render_template('nuevo.html', turnos=data) 
    else:
        #, forma=turnoForm
        return render_template('nuevo.html', turnos={'NumTurno': '', 'EstatusTurnoId': '', 'VentanillaId': ''})


    
@app.route('/consultar_turnos/', methods = ['GET','POST'])
def consultar_turnos():
    # Fecha actual
    hoy = datetime.today().strftime('%Y-%m-%d')
    
    turnos = Turno.query.filter(Turno.EstatusTurnoId <=2, func.DATE(Turno.Fecha) == hoy, Turno.JuzgadoId == session['JuzgadoId']).order_by(Turno.TurnoId).all()
    data = {}
    pp = pprint.PrettyPrinter(indent=4)
    if(turnos):
        for datos in turnos:
            #pp.pprint(datos.__dict__)
            print('')
        return turnos 
        
    print(type(data))
    #print(json.dumps(objeto))    
    
    
#def listado():
    #listado de personas
#    personas = Persona.query.order_by('nombre')
#    total_personas = Persona.query.count()
#    app.logger.debug(f'Listado Personas: {personas}')
#    app.logger.debug(f'Total de personas : {total_personas}')
#    return render_template('listado.html', personas=personas, total_personas = total_personas)

#@app.route('/ver/<int:id>')
#def ver(id):
    # Recuperamos la persona segun id proporcionado
    # persona = Persona.query.get(id)
#    persona = Persona.query.get_or_404(id)
#    app.logger.debug(f'Ver persona: {persona}')
#    return render_template('detalle.html' , persona = persona)

# @app.route('/agregar/', methods=['GET','POST'])
# def agregar():
#     persona = Persona()
#     personaForm = PersonaForm(obj=persona)
#     if request.method == "POST":
#         if personaForm.validate_on_submit():
#             personaForm.populate_obj(persona)
#             app.logger.debug(f'persona a insertar : {persona}')
#             #insertamos el nuevo registro
#             db.session.add(persona)
#             db.session.commit()
#             return redirect(url_for('inicio'))
#     return render_template('agregar.html', forma = personaForm)

# @app.route('/editar/<int:id>', methods = ['GET', 'POST'])
# def editar(id):
#     persona = Persona.query.get_or_404(id)
#     personaForm = PersonaForm(obj=persona)
#     if request.method == "POST":
#         if personaForm.validate_on_submit():
#             personaForm.populate_obj(persona)
#             app.logger.debug(f'persona a cambiar : {persona}')
#             # actualizamos el nuevo registro
#             db.session.commit()
#             return redirect(url_for('inicio'))
#     return render_template('editar.html', forma = personaForm)

# @app.route('/eliminar/<int:id>', methods=['GET','POST'])
# def eliminar(id):
#     persona = Persona.query.get_or_404(id)
#     db.session.delete(persona)
#     db.session.commit()
#     return redirect(url_for('inicio'))
