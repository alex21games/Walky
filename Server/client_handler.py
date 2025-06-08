# Este es el handler para el cliente, solo es una manera mas fancy de decir que es el servidor como tal xd
# este se encargara de las conexiones, media y mensajes enviados, con protocolos para cada usuario individual#

# Librerias a importar#
import socket
import threading

# Esto es para almacenar los clientes conectados
clientes = {}


# Funcion prinicipal para manejar a los clientes conectados
def manejar_cliente(conn, addr):
    nombre = conn.recv(1024).decode()
    clientes[nombre] = conn
    print(f"{nombre} conectado desde {addr}")

    # Avisos a la terminal del servidor, conectados, desconectados y mensajes enviados (este ultimo solo para el cliente destinatario)

    while True:
        try:
            data = conn.recv(1024).decode()
            destino, mensaje = data.split("::")
            if destino in clientes:
                clientes[destino].send(f"{nombre} dice: {mensaje}".encode())
        except:
            print(f"{nombre} se desconectó.")
            del clientes[nombre]
            conn.close()
            break

# Configuracion del servidor, abrir un socket y escuchar conexiones

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8080))
server.listen()

# Mensaje de aviso de inicio del server
print("Servidor corriendo...")

# Aceptar conexiones y crear un thread para cada uno de los clientes
while True:
    conn, addr = server.accept()
    threading.Thread(target=manejar_cliente, args=(conn, addr)).start()
