import socket
import threading
import sqlite3
import os

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

        cursor.execute("SELECT emisor, mensaje FROM mensajes WHERE receptor = ? ORDER BY timestamp ASC", (usuario,))
        for emisor, mensaje in cursor.fetchall():
            try:
                conn_cliente.send(f"{emisor} dice: {mensaje}".encode())
            except:
                break

        while True:
            try:
                data = conn_cliente.recv(1024).decode()
                if "::" not in data:
                    continue

                destino, mensaje = data.split("::", 1)

                # Guardar mensaje en base de datos
                cursor.execute("INSERT INTO mensajes (emisor, receptor, mensaje) VALUES (?, ?, ?)",
                               (usuario, destino, mensaje))
                conn.commit()

                if destino in clientes:
                    clientes[destino].send(f"{usuario} dice: {mensaje}".encode())
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
