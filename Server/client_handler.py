import socket
import threading
import sqlite3
import os
import time
import datetime

DB_FILE = "DataBase/chat_data.db"

if not os.path.exists(DB_FILE):
    print(f"Error: La base de datos '{DB_FILE}' no existe. Asegúrate de que se haya creado correctamente.")
    exit(1)

clientes = {}

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

def obtener_usuario_id(nombre):
    cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (nombre,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obtener_contactos(usuario):
    usuario_id = obtener_usuario_id(usuario)
    cursor.execute("SELECT contacto_nombre FROM contactos WHERE usuario_id = ?", (usuario_id,))
    return [fila[0] for fila in cursor.fetchall()]

def son_contactos(usuario, otro):
    uid = obtener_usuario_id(usuario)
    cursor.execute("SELECT 1 FROM contactos WHERE usuario_id = ? AND contacto_nombre = ?", (uid, otro))
    return cursor.fetchone() is not None

def manejar_cliente(conn_cliente, addr):
    try:
        datos = conn_cliente.recv(1024).decode()

        if datos.startswith("REGISTER::"):
            _, usuario, contrasena = datos.split("::")
            cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (usuario,))
            if cursor.fetchone():
                conn_cliente.send("REGISTER_EXISTS".encode())
            else:
                cursor.execute("INSERT INTO usuarios (nombre, contrasena) VALUES (?, ?)", (usuario, contrasena))
                conn.commit()
                conn_cliente.send("REGISTER_OK".encode())
            conn_cliente.close()
            return

        usuario, contrasena = datos.split("::")
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND contrasena = ?", (usuario, contrasena))
        if not cursor.fetchone():
            conn_cliente.send("LOGIN_FAIL".encode())
            conn_cliente.close()
            return

        clientes[usuario] = conn_cliente
        conn_cliente.send("READY".encode())
        print(f"[+] {usuario} conectado desde {addr}")

        cursor.execute("SELECT emisor, receptor, mensaje FROM mensajes WHERE receptor = ? OR emisor = ? ORDER BY timestamp ASC", (usuario, usuario))
        for emisor, receptor, mensaje in cursor.fetchall():
            destino = receptor if emisor == usuario else emisor
            conn_cliente.send(f"{emisor} dice: {mensaje}\n".encode())

        contactos = obtener_contactos(usuario)
        if contactos:
            conn_cliente.send(f"[Contactos]::{','.join(contactos)}\n".encode())

        cursor.execute("SELECT emisor FROM solicitudes WHERE receptor = ? AND estado = 'pendiente'", (usuario,))
        for fila in cursor.fetchall():
            emisor = fila[0]
            conn_cliente.send(f"[Solicitud]::{emisor}\n".encode())

        while True:
            try:
                data = conn_cliente.recv(1024).decode()
                data = data.strip()

                if "::" not in data:
                    continue

                if data.startswith("ADD_CONTACTO::"):
                    _, nuevo_contacto = data.split("::")
                    nuevo_contacto = nuevo_contacto.strip()
                    print(f"Solicitud recibida: {usuario} quiere agregar a {nuevo_contacto}")
                    
                    cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nuevo_contacto,))
                    if not cursor.fetchone():
                        print(f"El usuario {nuevo_contacto} no existe.")
                        conn_cliente.send(f"[Error]::El usuario '{nuevo_contacto}' no existe.\n".encode())
                        continue

                    cursor.execute("SELECT timestamp, estado FROM solicitudes WHERE emisor = ? AND receptor = ?", (usuario, nuevo_contacto))
                    solicitud = cursor.fetchone()
                    now = datetime.datetime.now()

                    if solicitud:
                        ts, estado = solicitud
                        ts_dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        diferencia = (now - ts_dt).total_seconds()

                        if estado == "pendiente" and diferencia < 10:
                            conn_cliente.send(f"[Error]::Ya enviaste una solicitud recientemente. Intenta en {int(10 - diferencia)} segundos.\n".encode())
                            print(f"Solicitud reciente bloqueada. Espera {int(10 - diferencia)}s.")
                            continue
                        else:
                            cursor.execute("UPDATE solicitudes SET timestamp = ?, estado = 'pendiente' WHERE emisor = ? AND receptor = ?", 
                                           (now.strftime("%Y-%m-%d %H:%M:%S"), usuario, nuevo_contacto))
                            conn.commit()
                    else:
                        cursor.execute("INSERT INTO solicitudes (emisor, receptor, timestamp) VALUES (?, ?, ?)", 
                                       (usuario, nuevo_contacto, now.strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()

                    print(f"Solicitud (re)enviada de {usuario} a {nuevo_contacto}.")
                    if nuevo_contacto in clientes:
                        clientes[nuevo_contacto].send(f"[Solicitud]::{usuario}\n".encode())
                    else:
                        print(f"{nuevo_contacto} no está conectado.")
                    continue

                elif data.startswith("ACEPTAR::"):
                    _, aceptado = data.split("::")
                    cursor.execute("UPDATE solicitudes SET estado = 'aceptado' WHERE emisor = ? AND receptor = ?", (aceptado, usuario))
                    uid = obtener_usuario_id(usuario)
                    aid = obtener_usuario_id(aceptado)
                    cursor.execute("INSERT INTO contactos (usuario_id, contacto_nombre) VALUES (?, ?)", (uid, aceptado))
                    cursor.execute("INSERT INTO contactos (usuario_id, contacto_nombre) VALUES (?, ?)", (aid, usuario))
                    conn.commit()
                    if aceptado in clientes:
                        clientes[aceptado].send(f"[ContactoAceptado]::{usuario}\n".encode())
                    continue

                elif data.startswith("DEL_CONTACTO::"):
                    _, contacto_borrar = data.split("::")
                    usuario_id = obtener_usuario_id(usuario)
                    cursor.execute("DELETE FROM contactos WHERE usuario_id = ? AND contacto_nombre = ?", (usuario_id, contacto_borrar))
                    conn.commit()
                    continue

                destino, mensaje = data.split("::", 1)
                if not son_contactos(usuario, destino):
                    conn_cliente.send(f"[Error]::No puedes enviar mensajes a '{destino}' sin ser contactos.\n".encode())
                    continue

                cursor.execute("INSERT INTO mensajes (emisor, receptor, mensaje) VALUES (?, ?, ?)",
                               (usuario, destino, mensaje))
                conn.commit()

                if destino in clientes:
                    clientes[destino].send(f"{usuario} dice: {mensaje}\n".encode())
            except Exception as e:
                print(f"[x] {usuario} se desconectó: {e}")
                break
    finally:
        if usuario in clientes:
            del clientes[usuario]
        conn_cliente.close()
        print(f"[-] {usuario} desconectado")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8080))
server.listen()
print("Servidor corriendo en puerto 8080...")

while True:
    conn_cliente, addr = server.accept()
    threading.Thread(target=manejar_cliente, args=(conn_cliente, addr), daemon=True).start()
