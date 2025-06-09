import socket
import threading
import json
import os

clientes = {}

def cargar_usuarios():
    if not os.path.exists("usuarios.json"):
        with open("usuarios.json", "w") as f:
            json.dump({}, f, indent=4)
    with open("usuarios.json", "r") as f:
        return json.load(f)

usuarios = cargar_usuarios()

def manejar_cliente(conn, addr):
    try:
        datos = conn.recv(1024).decode()
        if datos.startswith("REGISTER::"):
            _, usuario, contrasena = datos.split("::")
            if usuario in usuarios:
                conn.send("REGISTER_EXISTS".encode())
            else:
                usuarios[usuario] = contrasena
                with open("usuarios.json", "w") as f:
                    json.dump(usuarios, f, indent=4)
                conn.send("REGISTER_OK".encode())
            conn.close()
            return

        usuario, contrasena = datos.split("::")
        if usuario not in usuarios or usuarios[usuario] != contrasena:
            conn.send("LOGIN_FAIL".encode())
            conn.close()
            return

        clientes[usuario] = conn
        conn.send("READY".encode())  
        print(f"[+] {usuario} conectado desde {addr}")

        while True:
            try:
                data = conn.recv(1024).decode()

                if "::" not in data:
                    print(f"[!] Mensaje malformado de {usuario}: {data}")
                    continue

                destino, mensaje = data.split("::", 1)

                if destino in clientes:
                    clientes[destino].send(f"{usuario} dice: {mensaje}".encode())
                else:
                    conn.send(f"Error: {destino} no está conectado.".encode())

            except Exception as e:
                print(f"[x] {usuario} se desconectó. Error interno: {e}")
                break
    finally:
        if usuario in clientes:
            del clientes[usuario]
        conn.close()
        print(f"[-] {usuario} desconectado.")

# Configuración del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8080))
server.listen()

print("Servidor corriendo en el puerto 8080...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True).start()
