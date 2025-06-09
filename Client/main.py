import customtkinter as ctk
from client_main import ClienteChat, IPDialog, registrar_usuario
from client_login import LoginVentana

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.withdraw()

# Función que se llama cuando el login es exitoso
def iniciar_chat(usuario, contrasena, ip):
    root.deiconify()
    for widget in root.winfo_children():
        widget.destroy()
    ClienteChat(root, usuario, contrasena, ip)

# Función que se llama al presionar "Iniciar sesión"
def on_login(usuario, contrasena, login_window):
    def on_ip(ip):
        login_window.destroy()
        iniciar_chat(usuario, contrasena, ip)
    IPDialog(root, on_ip)

# Función que se llama al presionar "Registrarse"
def on_register(usuario, contrasena, login_window):
    registrar_usuario(usuario, contrasena)

# Lanzar ventana de login
LoginVentana(root, on_login, on_register)

# Iniciar bucle de interfaz
root.mainloop()
