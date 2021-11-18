setInterval( consultarTurnos , 40000000);
const socket = io() ;

function seleccionarTurno(id, accion, usuario){
    socket.send({"id" : id, "accion":accion, "usuario":usuario});
}

function validarInfo(){
    if(document.getElementById('tipo').value==2 && document.getElementById('comentarios').value==""){
        swal('Si es un turno urgente, en comentarios describa la situación');
    }
    else{
        document.getElementById('accion').value="Nuevo turno" ;
        document.getElementById('forma').submit();
        //seleccionarTurno('','Nuevo turno',usuario,document.getElementById('tipo').value,document.getElementById('comentarios').value) ;
    }
} 

socket.on('message', function(msg){
        metodo = location.pathname ;
        
        $.ajax({
            url : "/consultar_usuario/",
            dataType : "json",
            success: function(respuesta){

                var usuario = respuesta.usuario;
                
                switch(metodo){
                    case '/nuevo/':
                        if(msg.accion == "Nuevo turno"){ 
                            window.open( location.href +="Nuevo turno")
                        }
                        else{
                            setTimeout(function() { location.reload(); },1000 );
                        }
                        break;    
                    case '/atender/':
                        if(usuario == msg.usuario){
                            window.open( location.href += msg.accion  );
                        }
                        else{
                        //    consultarTurnos() ;
                            setTimeout(function() { location.reload(); },1000 );
                        }
                        break;
                    case '/concluir/':
                        if(usuario == msg.usuario){
                            window.open( location.href += msg.id  );
                        }
                        break;
                    case '/pantalla/':
                        setTimeout(function(){location.reload();},1000);
                        break;
                    default :
                        //alert("Error al procesar la peticion");
                        break;
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            }
        });

    });

function consultarTurnos(){
    $.ajax({
        data : {"accion":"consultar turnos"},
        url : "/consultar_turnos/",
        type : "POST" ,
        dataType : "json",
        success: function(respuesta){
            if(respuesta['success']==200){
                console.log(respuesta['success']);
                var tabla = "\
                        <table width='80%' border='1' align='top' cellpadding='20' cellspacing='0'  style='margin:0 auto'>\
			    			<thead>\
						      <tr>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px; border-collapse:collapse;' cellpadding='0' cellspacing='0' align='center' valign='top' width='25%'>TURNO</td>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px;' cellpadding='0' cellspacing='0' align='center' valign='middle' width='25%'>VENTANILLA</td>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px;' cellpadding='0' cellspacing='0' align='center' valign='middle' width='25%'>ESTATUS</td>\
						      </tr>\
							</thead>\
							<tbody style='font-size:3em; text-align:center'>\
								<tr>\
									<td>"  + respuesta['turno'] + "</td>\
									<td>" + respuesta['ventanilla'] + "</td>\
									<td>Atendiendo</td>\
								</tr>\
								<tr>\
									<td></td>\
									<td colspan='2'>En espera</td>\
								</tr>\
							</tbody>\
						  </table>" ;

                document.getElementById('divTurnos').innerHTML = tabla ;
                document.getElementById('datoTurno').innerHTML = respuesta['turno'] ;
                document.getElementById('datoVentanilla').innerHTML = respuesta['ventanilla'] ;
            }
           else{
                var tabla = "\
                        <table  width='80%' border='1' align='top' cellpadding='20' cellspacing='0'  style='margin:0 auto'>\
			    			<thead>\
						      <tr>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px; border-collapse:collapse;' cellpadding='0' cellspacing='0' align='center' valign='top' width='25%'>TURNO</td>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px;' cellpadding='0' cellspacing='0' align='center' valign='middle' width='25%'>VENTANILLA</td>\
						      	<td style='background-color:black; font-weight: bold; color:white; font-size:30px;' cellpadding='0' cellspacing='0' align='center' valign='middle' width='25%'>ESTATUS</td>\
						      </tr>\
							</thead>\
							<tbody style='font-size:3em; text-align:center'>\
								<tr>\
									<td colspan='3'>Aun no hay turnos asignados</td>\
								</tr>\
							</tbody>\
						</table>";
						document.getElementById('datoTurno').innerHTML = '0' ;
                        document.getElementById('datoVentanilla').innerHTML = '0' ;

           }
           document.getElementById('divTurnos').innerHTML = tabla ;
        }
    });
}