# Este es el archivo main, inicia el cliente y las ventanas (pa que sea mas modular)

import customtkinter as ctk
from client_main import ClienteChat, IPDialog, registrar_usuario
from client_login import LoginVentana

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.withdraw()

# Cuanto el usuario inicia sesion se destruye la ventana para el login y se inicia la ventana del chat
def iniciar_chat(usuario, contrasena, ip):
    root.deiconify()
    for widget in root.winfo_children():
        widget.destroy()
    ClienteChat(root, usuario, contrasena, ip)

# Al presionar iniciar sesion pasa a la ventana de la ip
def on_login(usuario, contrasena, login_window):
    def on_ip(ip):
        login_window.destroy()
        iniciar_chat(usuario, contrasena, ip)
    IPDialog(root, on_ip)

# Si el usuario no tenia cuenta esta funcion es para registrarlo
def on_register(usuario, contrasena, login_window):
    registrar_usuario(usuario, contrasena)

# Lanzar la ventana login
LoginVentana(root, on_login, on_register)

# bucle principal
root.mainloop()
