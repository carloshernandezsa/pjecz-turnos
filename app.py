import json
import random
import pprint
import pdfkit 
import base64 

from jinja2.loaders import FileSystemLoader  
from jinja2 import Environment

from flask import Flask, render_template, request, url_for, session, make_response
from flask_socketio import SocketIO, send, emit
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func, or_, and_
from werkzeug.utils import redirect
from datetime import datetime


from database import db
from forms import TurnoForm
from models import Turno, Usuarios, Ventanilla, Departamentos

#CSRF Protect
csrf = CSRFProtect()

# Inicializar App Flask
app = Flask(__name__)
csrf.init_app(app)

# Configuracion de la base de datos
USER_DB = "root"
PASS_DB = ""
URL_DB = "localhost"
NAME_DB = "pjecz_sistema_turnos"
FULL_URL_DB = f"mysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}"

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
        
        user  = Usuarios.query.filter(Usuarios.usuario == usuario , Usuarios.password == contrasena).first()
        numero_registros = Usuarios.query.filter(Usuarios.usuario == usuario , Usuarios.password == contrasena).count()
        
        if(numero_registros>0):      
            ventanilla = Ventanilla.query.filter(Ventanilla.usuario_id == user.id).first()
            session['autoridad_id'] = user.autoridad_id
            session['Oficina'] = session['juzgados'][user.autoridad_id]
              
            print(f'Usuario que se firmo: {user.nombres} {user.apellido_paterno} {user.apellido_materno} ')
            if user.rol_id == 1:
                session['pagina'] = '/nuevo/'
                session['ventanilla'] = 0
            if user.rol_id == 2:
                session['pagina'] = '/atender/'
                session['ventanilla'] = ventanilla.id
            if user.rol_id == 5:
                session['pagina'] = '/pantalla/'
                session['ventanilla'] = 0
                
            session['usuario'] = user.id   
            session['nombre'] = user.nombres + " " + user.apellido_paterno + " " + user.apellido_materno
            session['rol'] = user.rol_id
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error="Usuario no encontrado")

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('usuario',None)
    session.pop('contrasena', None)
    session.pop('ventanilla', None)
    session.pop('nombre',None)
    session.pop('comentarios',None)
    session.pop('tipo', None)
    session.pop('rol',None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/pantalla/')
def pantalla():
    if 'rol' in session and session['rol']==5: # Rol de usuario de Pantalla
        #Fecha actual
        hoy = datetime.today().strftime('%Y-%m-%d')
        turnos = Turno.query.filter(Turno.estado <= 2 , func.DATE(Turno.creado) == hoy, Turno.autoridad_id == session['autoridad_id'] ).order_by(Turno.id).limit(8).all() 
        #registros = Turno.query.filter(Turno.ventanilla_id == None , func.DATE(Turno.creado) == hoy ).order_by(Turno.id).limit(5).count()
        turno = Turno.query.filter(Turno.estado == 2, func.DATE(Turno.creado) == hoy, Turno.autoridad_id == session['autoridad_id']).order_by(Turno.atencion.desc()).first()
        
        return render_template('pantalla.html', turno = turno, turnos = turnos)
    return redirect(url_for('login'))


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
            turno = Turno.query.filter(Turno.id == id).first()
            turno.estado = 3
            db.session.commit()
        except:
            pass
    return redirect(url_for('pantalla'))

@app.route('/atender/', methods=['GET'])
@app.route('/atender/<accion>', methods=['GET','POST'])
def atender(accion = None):
    if 'rol' in session and session['rol'] == 2:  # Rol de usuario de Recepción
        #Fecha actual
        hoy = datetime.today().strftime('%Y-%m-%d')
        print(f'valor de accion {accion}')
        if(accion=="Atender"):
            try:
                print('*************************************************** Seleccion de un turno para ATENDER ************************ ')
                turno = Turno.query.filter(and_(Turno.estado == 1 , func.DATE(Turno.creado) == hoy , Turno.autoridad_id == session['autoridad_id'], or_(Turno.tipo == 1, Turno.tipo == 2))).order_by(Turno.tipo.desc(), Turno.numero.asc()).first()
                turno.estado = 2
                turno.ventanilla_id = session['ventanilla']
                turno.atencion = datetime.now()
                db.session.commit()
                return redirect(url_for('concluir'))
            except:
                print("error al marcar turno como recibido para atender")
        try:
            turnos = Turno.query.filter(Turno.estado == 1, func.DATE(Turno.creado) == hoy, Turno.autoridad_id == session['autoridad_id']).order_by(Turno.id).all()
        except:
            turnos = {"success":"sin registros"}
        return render_template('atender.html', turnos = turnos)
    return redirect(url_for('login'))


@app.route('/concluir/', methods=['GET'])
@app.route('/concluir/<int:id>', methods=['GET','POST'])
def concluir(id = 0):
    if 'rol' in session and session['rol'] == 2:  # Rol de usuario de Atención al público
        #Fecha actual
        hoy = datetime.today().strftime('%Y-%m-%d')
        if(id>0):
            try:
                turno = Turno.query.filter(Turno.id == id).first()
                turno.estado = 3
                turno.termino = datetime.now()
                db.session.commit()
                return redirect(url_for('atender'))
            except:
                print("error al marcar turno como ATENDIDO (3)")
        try:
            turnos = Turno.query.filter(Turno.estado == 2, func.DATE(Turno.creado) == hoy, Turno.ventanilla_id == session['ventanilla']).order_by(Turno.id).limit(5).all()
        except:
            turnos = {"success":"sin registros"}
        return render_template('concluir.html', turnos = turnos)
    return redirect(url_for('login'))

@app.route('/nuevo/', methods=['GET','POST'])
@app.route('/nuevo/<accion>',methods=['GET','POST'])
def nuevo(accion = None):
    if 'rol' in session and session['rol'] == 1:  # Rol de usuario de Recepción
        if(request.method == 'POST'):
            print(f' ***********---------------------- Inicia proceso de alta {request.form["accion"]}')
            #print(f'######################  Accion: {accion} , Usuario Firmado:{session["usuario"]} ')
            if(request.form['accion']=="Nuevo turno"):
                
                #Registrar nuevo renglon en la tabla de turnos
                hoy = datetime.today().strftime('%Y-%m-%d')
                turno = Turno.query.filter(func.DATE(Turno.creado) == hoy, Turno.autoridad_id == session['autoridad_id']).order_by(Turno.numero.desc()).first()
                if(turno):
                    maximo = turno.numero + 1
                else:
                    maximo = 1
                
                turno = Turno()
                turno.numero = maximo
                turno.creado =  datetime.now()
                turno.usuario_id = session['usuario']
                turno.estado = 1
                turno.comentarios = request.form['comentarios']
                turno.tipo = request.form['tipo']
                turno.autoridad_id = session['autoridad_id']
                
                db.session.add(turno)
                db.session.commit()
                print("se agregara un nuevo turno en la tabla")
                accion=""

                socketio.send('message')
                return redirect(url_for('nuevo'))
        
        data =  consultar_turnos()
        turno = Turno()
        turnoForm = TurnoForm(obj=turno)
        print('tipo de dato regresado' , type(data))
        if(isinstance(data,list)):
            #, forma=turnoForm
            return render_template('nuevo.html', turnos=data) 
        else:
            #, forma=turnoForm
            return render_template('nuevo.html', turnos={})
    return redirect(url_for('login'))

    
@app.route('/consultar_turnos/', methods = ['GET','POST'])
def consultar_turnos():
    if 'usuario' in session:
        # Fecha actual
        hoy = datetime.today().strftime('%Y-%m-%d')
        print('************************* inicia consulta de turnos por dia *****************************')
        turnos = Turno.query.filter(Turno.estado <= 2, func.DATE(Turno.creado) == hoy, Turno.autoridad_id == session['autoridad_id']).order_by(Turno.id).all()
        data = {}
        pp = pprint.PrettyPrinter(indent=4)
        if(turnos):
            for datos in turnos:
                #pp.pprint(datos.__dict__)
                print('registro')
            return turnos 
            
        print(type(turnos))
        #print(json.dumps(objeto))    
    return redirect(url_for('login'))


@app.route('/crearPDF/', methods=['GET', 'POST'])
@app.route('/crearPDF/<int:turno_id>', methods = ['GET', 'POST'])
def crearPDF(turno_id = 0):
    entorno = Environment(
        loader=FileSystemLoader('templates'),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    
    archivo = 'static/img/img_escudo.png'
    imagen = open(archivo, 'rb')
    imagen_read = imagen.read()
    imagen_64_encode = base64.encodebytes(imagen_read)

    turno = Turno.query.get(turno_id)
    tiempo = turno.creado
    
    pdf_plantilla = entorno.get_template("pdf_body.html")
    pdf_html = pdf_plantilla.render(
        turno=turno.numero,
        fecha=formato_fecha(turno.creado),
       
        hora = tiempo.strftime("%I:%M:%S %p"),
        imagen = imagen_64_encode
    )
    
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    options = {
        "enable-local-file-access": None
    }
    # Crear archivo PDF 
    try:
        pdf = pdfkit.from_string(pdf_html, False, configuration=config, options=options)
        respuesta = make_response(pdf)
        respuesta.headers['Content-type'] = "application/pdf"
        respuesta.headers['Content-Disposition']="attachment; filename=turno.pdf"
        return respuesta
    except IOError as error:
        mensaje = str(error)
        print(f'Error: {mensaje}')
        return "Error : ",mensaje
    

def formato_fecha(date = datetime.now()):
    dias = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
    meses = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio",
              "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    
    dia_semana = date.weekday()
    dia = date.day
    mes = meses[date.month - 1]
    anio = date.year
    letra = dias[dia_semana]
    messsage = "{}, {} de {} del {}".format(letra, dia, mes, anio)

    return messsage


