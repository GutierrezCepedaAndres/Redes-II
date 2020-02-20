#!/usr/bin/python3
from socket import *
from stack import Stack #La clase pila ha sido utilizada del autor Brad Miller trabajador de pythonds
#Si se desea mas informacion del autor consultar la clase Stack que contiene los datos referentes al mismo
from math import floor
import threading
servidor= 'atclab.esi.uclm.es' #Se define el servidor
import time
import struct

global respuesta #Declaramos la respuesta de la etapa 1 como variable global para poderla mover entre el hilo servidor y el principal
respuesta = None 



#############################################################
#															#
#	  ///FUNCIONES COMPLEMENTARIAS A LA ETAPA UNO///		#	
#															#
#############################################################

# https://bitbucket.org/arco_group/python-net/src/tip/raw/icmp_checksum.py
# Codigo otorgado por el profesor de la UCLM perteneciente a la escuela superior de informatica David Villa

def crearServidor():

	servidorUDP = socket(AF_INET, SOCK_DGRAM) #Se crea el servidor UDP
	servidorUDP.bind(('', 7798))
	mensaje, origen = servidorUDP.recvfrom(1024) #Se recibe el mensaje
	global respuesta
	respuesta = mensaje #Se pasa el mensaje a la variable global
	servidorUDP.close()


#############################################################
#															#
#	  ///FUNCIONES COMPLEMENTARIAS A LA ETAPA DOS///		#	
#															#
#############################################################

	#Este metodo comprueba que el numero de parentesis que se abren sea igual al que se cierra
	#Debido a que si esto no es asi la operacion habria llegado incompleta

def comprobarParentesis(operacion):
	abrir = 0
	cerrar = 0
	for caracter in operacion:
		if (caracter == ("(")) or (caracter==("{")) or (caracter==("[")):
			abrir+=1
		elif(caracter == (")")) or (caracter==("}")) or (caracter==("]")):
			cerrar+=1

	if abrir != cerrar:
		return False
	else:
		return True

		#Una vez se han retirado los 3 operandos de la pila se debera debera de comprobar
		#Que tipo de operacion hay que ejecutar, cabe señalar que en el caso de la division en todo
		#Momento se debe de utilizar la funcion suelo para que el resultado sea el correcto

def calcularResultadoOperacion(operando1,operando2,operando3):
	if operando2=='*':
		resultado=int(operando3)*int(operando1)
	elif operando2=='+':
		resultado=int(operando3)+int(operando1)
	elif operando2=='-':
		resultado=int(operando3)-int(operando1)
	elif operando2=='/':
		resultado=int(floor((int(operando3)/int(operando1))))
	return resultado

def realizarOperacion(operacion):
	s = Stack()
	index = 0
	resultado=0
	while index < len(operacion): #se va recorriendo la operacion entera para meter los valores en la pila
		caracter = operacion[index]
		if (caracter == ("(")) or (caracter==("{")) or (caracter==("[")):
			s.push(caracter) #Si el caracter que se ha seleccionado es un parentesis de apertura este se almacena en la pila
		else:
			if(caracter != ' '): #En todo momento se omiten los espacion en blanco dado que no afectan a la operacion
				s.push(caracter) #Se van metiendo valores en la pila hasta que se encuentra con un parentesis de cierre
				if(caracter == (")")) or (caracter==("}")) or (caracter==("]")):
					s.pop() #Se extrae el parentesis de cierre dado que no nos interesa para la realizacion de la operacion
					operando1='' #Se declaran y se inicializan a vacio los operandos
					operando2=''
					operando3=''
					while isinstance(s.peek(),int) or s.peek().isnumeric(): #En el caso del operando 1 y 3 al ser numericos pueden ser de mas de 1 digito, de esta manera se seleccionan todos los digitos
						operando1=str(s.pop())+operando1
					operando2=s.pop()
					while isinstance(s.peek(),int) or s.peek().isnumeric():
						operando3=str(s.pop())+operando3
					resultado=calcularResultadoOperacion(operando1,operando2,operando3)
					s.pop() #Se extrae el parentesis de apertura dado que el metodo finalizara cuando solo quede un unico valor numerico en la pila
					s.push((resultado)) #Una vez se tiene el resultado se introduce en la pila para continuar con las operaciones siguientes
		index = index + 1
	return resultado

#############################################################
#															#
#	  ///FUNCIONES COMPLEMENTARIAS A LA ETAPA TRES///		#	
#															#
#############################################################


def cksum(data):

    def sum16(data):
        "sum all the the 16-bit words in data"
        if len(data) % 2: #Si es divisible por dos se le coloca al final del mensaje a enviar un \0 en formato de bytes
            data += ('\0').encode()

        return sum(struct.unpack("!%sH" % (len(data) // 2), data)) 

    retval = sum16(data)                       # sum
    retval = sum16(struct.pack('!L', retval))  # one's complement sum
    retval = (retval & 0xFFFF) ^ 0xFFFF        # one's complement
    return retval

#############################################################
#															#
#					///ETAPA CERO///						#	
#															#
#############################################################
	
	#En la etapa cero se realiza la creacion de un cliente udp
	#Una vez el cliente es creado se conecta a la direccion y puerto de la gymkana
	#El servidor nos envia un mensaje con el siguiente paso 
	#En el siguiente paso necesitaremos el primer valor de mensaje que es el puerto 
	#Que se enviara como mensaje en la siguiente etapa, por ello se realiza un .split.

def etapaCero():
	cliente=socket(AF_INET, SOCK_STREAM)
	cliente.connect((servidor,2000))
	msg=(cliente.recv(1024)).decode()
	print (msg)
	cliente.close()
	auxiliar = msg.split('\n')
	puerto = auxiliar[0]
	return puerto


#############################################################
#															#
#					///ETAPA UNO///						    #	
#															#
#############################################################

	#En la etapa uno se realizara la creacion de un servidor UDP al cual le colocaremos el puerto deseado
	#Tras esto se debe mandar un mensaje al servidor de la Gymkana con el mensaje antes seccionado del paso anterior
	#Junto con el puerto de nuestro servidor, el servidor de la Gymkana nos respondera con un mensaje con el enunciado
	#Para la etapa dos del cual deveremos seleccionar tambien la primera parte por eso el .split.

def etapaUno(puerto):
	hiloservidor= threading.Thread(name="hiloservidor",target=crearServidor) #Se crea el hilo que ejecutara el servidor UDP que recibira el mensaje de respuesta del servidor de la Gymkana
	hiloservidor.start() #Se ejecuta el hilo

	clienteUDP=socket(AF_INET, SOCK_DGRAM) #Se crea el cluente UDP que mandara el mensaje necesario al servidor de la gymkana con los datos del servidor creado en el hilo
	mensaje= puerto+' 7798'
	clienteUDP.sendto(mensaje.encode(),(servidor,2000))
	while 1: #Se crea un bucle de espera activa el cual se ejecutara hasta que el servidor UDP reciba la respuesta del servidor de la gymkana.
		if respuesta!=None:
			break

	resp=respuesta.decode()
	print (resp)
	clienteUDP.close()

	auxiliar2 = resp.split('\n')
	puerto2= auxiliar2[0]
	return puerto2


#############################################################
#															#
#					///ETAPA DOS///				    		#	
#															#
#############################################################

	#En la etapa dos se debe de crear un servidor TCP con el que nos conectaremos al servidor de la Gymkana
	#Este servidor recivira varias operaciones sobre las cuales debera de comprobar que la operacion ha llegado por completo
	#Y comprobar que esta no es el mensaje con el enunciado de la siguiente etapa
	#Nota: El codigo de los metodos viene explicado en los mismos.

def etapaDos(puerto2):

	clienteTCP = socket(AF_INET, SOCK_STREAM)
	clienteTCP.connect((servidor, int(puerto2)))
	esOperacion=True
	operacion = (clienteTCP.recv(1024)).decode()
	while len(operacion)<100: #Si el mensaje recibido es mayor a 100 significara que es el mensaje con el enunciado de la etapa 3
		if (comprobarParentesis(operacion)==False): #Si la operacion esta incompleta se pedira la otra mitad de la misma al servidor
			operacion+=(clienteTCP.recv(1024)).decode()
		resultado="("+str(realizarOperacion(operacion))+")" #El resultado se debe mandar entre parentesis
		clienteTCP.send(resultado.encode())
		operacion = (clienteTCP.recv(1024)).decode()

	print (operacion)

	clienteTCP.close()	

	auxiliar3 = operacion.split('\n')
	url= auxiliar3[0]
	return url



#############################################################
#															#
#					///ETAPA TRES///				    	#	
#															#
#############################################################


def etapaTres(url):

	peticion = 'GET /' + url + ' HTTP/1.1\n\n' #Estructura de una peticion Get para http1.1

		
	sock_http = socket(AF_INET, SOCK_STREAM) #Se crea el socket

	sock_http.connect((servidor, 5000))

	sock_http.send(peticion.encode()) #Se envia la peticion en formato de bytes por la conexion creada

	mensajehttp=sock_http.recv(2048) #Mensaje de confirmacion del servidor OK
	print(mensajehttp.decode())
	mensajehttp2=sock_http.recv(114) #Mensaje con informacion referente al servidor
	print(mensajehttp2.decode())
	mensajehttp3=sock_http.recv(2048) #Mensaje de respuesta y el deseado para continuar con el desarrollo
	mensajehttp3=mensajehttp3.decode()
	print(mensajehttp3)
	sock_http.close()

	auxiliar4 = mensajehttp3.split('\n') #Se parte el mensaje en distintas lineas

	puerto4 = auxiliar4[1] #Se parte el mensaje por la segunda linea dado que la primera esta en blanco
	return puerto4


#############################################################
#															#
#					///ETAPA CUATRO///				    	#	
#															#
#############################################################


def etapaCuatro(puerto4):
	socket4 = socket(AF_INET,SOCK_RAW,getprotobyname("icmp")) #Para realizar el envio se necesita crear un socket raw del tipo icmp
	
	tiempo = time.strftime("%H:%M:%S").encode() #Recoges la hora del sistema para introducirlo al paquete
	PaqueteIcmpSinCheck = struct.pack('!1B1B3H8s',8,0,0,33,0,tiempo) + puerto4.encode() #Se crea el paquete sin el checksum para poderlo calcular posteriormente
	checksum = cksum(PaqueteIcmpSinCheck) #Se calcula el checksum del paquete antes creado
	packet = struct.pack('!1B1B3H8s',8,0,checksum,33,0,tiempo) + puerto4.encode() #Se crea el paquete compuesto de dos caracteres sin asignar, tres shorts sin asgnar y un vector de caracteres de tamaño 8 que contendra el tiempo
	#print(packet)
	socket4.sendto(packet,(servidor,2000)) #Se envia el paquete al servidor
    
	ping = socket4.recv(512) #se obtiene la respuesta del ping
	#print(ping)
	ping2 = socket4.recv(4096) #se obtiene el mensaje de la siguiente etapa
	#print(ping2)
	data = ping2[28:].decode() #se elimina la cabecera ip y la icmp para quedarnos solo con el mensaje
	print(data) 
	socket4.close()
	return data.split('\n')[0]






#############################################################
#															#
#					///MAIN///				         		#	
#															#
#############################################################


puerto=etapaCero()
print("\n\n\n#########################/////////SE HA COMPLETADO LA ETAPA CERO///////##############################\n\n\n")
time.sleep(1)
puerto2=etapaUno(puerto)
print("\n\n\n#########################/////////SE HA COMPLETADO LA ETAPA UNO///////##############################\n\n\n")
time.sleep(1)
url=etapaDos(puerto2)
print("\n\n\n#########################/////////SE HA COMPLETADO LA ETAPA DOS///////##############################\n\n\n")
time.sleep(1)
puerto4=etapaTres(url)
print("\n\n\n#########################/////////SE HA COMPLETADO LA ETAPA TRES///////##############################\n\n\n")
time.sleep(1)
etapaCuatro(puerto4)
print("\n\n\n#########################/////////SE HA COMPLETADO LA ETAPA CUATRO///////##############################\n\n\n")
time.sleep(1)




	

