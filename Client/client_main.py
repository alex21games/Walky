import socket
import threading
import customtkinter as ctk
from tkinter import messagebox
from Utils.utils import cargar_contactos, guardar_contactos

class ClienteChat:
    def __init__(self, master, nombre, contrasena, ip):
        self.master = master
        self.master.title("Walky - Alpha 1.0.0")
        self.master.geometry("1200x800")

        self.nombre = nombre
        self.contrasena = contrasena
        self.ip = ip
        self.cliente = None
        self.conectado = False

        self.contactos = cargar_contactos()
        self.contacto_destino = None

        self.construir_interfaz()
        self.conectar()

    def construir_interfaz(self):
        frame_main = ctk.CTkFrame(self.master)
        frame_main.pack(expand=True, fill="both")

        # Panel izquierdo (contactos)
        self.frame_izquierdo = ctk.CTkFrame(frame_main, width=300)
        self.frame_izquierdo.pack(side="left", fill="y")

        self.lista_contactos = ctk.CTkScrollableFrame(self.frame_izquierdo)
        self.lista_contactos.pack(expand=True, fill="both", padx=5, pady=5)

        for contacto in self.contactos["equipo"]:
            self.agregar_boton_contacto(contacto)

        frame_agregar = ctk.CTkFrame(self.frame_izquierdo)
        frame_agregar.pack(pady=5)

        self.entry_nuevo_contacto = ctk.CTkEntry(frame_agregar)
        self.entry_nuevo_contacto.pack(side="left")

        ctk.CTkButton(frame_agregar, text="+", width=30, command=self.agregar_contacto).pack(side="left", padx=2)

        # Panel derecho (chat)
        self.frame_derecho = ctk.CTkFrame(frame_main)
        self.frame_derecho.pack(side="left", expand=True, fill="both")

        self.text_chat = ctk.CTkTextbox(self.frame_derecho, state="disabled")
        self.text_chat.pack(expand=True, fill="both")

        frame_inferior = ctk.CTkFrame(self.frame_derecho)
        frame_inferior.pack(pady=10)

        self.entry_mensaje = ctk.CTkEntry(frame_inferior, width=400)
        self.entry_mensaje.pack(side="left", padx=5)
        ctk.CTkButton(frame_inferior, text="Enviar", command=self.enviar_mensaje).pack(side="left")

    def agregar_boton_contacto(self, nombre):
        btn = ctk.CTkButton(self.lista_contactos, text=nombre, width=260, anchor="w",
                            command=lambda n=nombre: self.seleccionar_contacto(n))
        btn.pack(pady=2, padx=5)

    def seleccionar_contacto(self, nombre):
        self.contacto_destino = nombre
        self.mostrar_en_chat(f"[Sistema] Hablando con {nombre}")

    def agregar_contacto(self):
        nuevo = self.entry_nuevo_contacto.get().strip()
        if not nuevo:
            messagebox.showwarning("Aviso", "Escribe un nombre.")
            return
        if nuevo in self.contactos["equipo"]:
            messagebox.showinfo("Ya existe", f"El contacto '{nuevo}' ya está en la lista.")
            return
        self.contactos["equipo"].append(nuevo)
        guardar_contactos(self.contactos)
        self.agregar_boton_contacto(nuevo)
        self.entry_nuevo_contacto.delete(0, "end")
        messagebox.showinfo("Agregado", f"Contacto '{nuevo}' añadido.")

    def conectar(self):
        if not self.nombre or not self.contrasena:
            messagebox.showerror("Error", "Debes iniciar sesión primero.")
            return

        def conectar_thread():
            try:
                self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.cliente.connect((self.ip, 8080))
                self.cliente.send(f"{self.nombre}::{self.contrasena}".encode())
                respuesta = self.cliente.recv(1024).decode()
                if respuesta == "LOGIN_FAIL":
                    self.master.after(0, lambda: (
                        messagebox.showerror("Error", "Usuario o contraseña incorrectos."),
                        self.cliente.close(),
                        self.master.destroy()
                    ))
                    return
                elif respuesta == "READY":
                    self.conectado = True
                    threading.Thread(target=self.recibir_mensajes, daemon=True).start()
                    self.master.after(0, lambda: self.mostrar_en_chat("Conectado al servidor."))
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Error", f"No se pudo conectar: {e}"))

        threading.Thread(target=conectar_thread, daemon=True).start()

    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.cliente.recv(1024).decode()
                self.mostrar_en_chat(mensaje)
            except Exception as e:
                print(f"Error en recibir_mensajes: {e}")
                self.conectado = False
                self.mostrar_en_chat("Desconectado del servidor.")
                break

    def enviar_mensaje(self):
        mensaje = self.entry_mensaje.get()
        if not self.contacto_destino:
            messagebox.showwarning("Error", "Selecciona un contacto.")
            return
        if not mensaje.strip():
            return
        self.cliente.sendall(f"{self.contacto_destino}::{mensaje}".encode())
        self.mostrar_en_chat(f"Tú -> {self.contacto_destino}: {mensaje}")
        self.entry_mensaje.delete(0, "end")

    def mostrar_en_chat(self, mensaje):
        self.text_chat.configure(state="normal")
        self.text_chat.insert("end", mensaje + "\n")
        self.text_chat.configure(state="disabled")
        self.text_chat.see("end")

def registrar_usuario(usuario, contrasena):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.217.131", 8080))  # Cambia IP si es necesario
        s.send(f"REGISTER::{usuario}::{contrasena}".encode())
        respuesta = s.recv(1024).decode()
        s.close()

        if respuesta == "REGISTER_OK":
            messagebox.showinfo("Registro", "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
        elif respuesta == "REGISTER_EXISTS":
            messagebox.showerror("Registro", "El usuario ya existe.")
        else:
            messagebox.showerror("Registro", "Error al registrar usuario.")
    except Exception as e:
        messagebox.showerror("Registro", f"Error de conexión: {e}")

class IPDialog(ctk.CTkToplevel):
    def __init__(self, master, on_ip_entered):
        super().__init__(master)
        self.title("Conectar a servidor")
        self.geometry("300x120")
        self.on_ip_entered = on_ip_entered

        ctk.CTkLabel(self, text="IP del servidor:").pack(pady=10)
        self.entry_ip = ctk.CTkEntry(self)
        self.entry_ip.pack(pady=5)
        ctk.CTkButton(self, text="Conectar", command=self.enviar_ip).pack(pady=10)

    def enviar_ip(self):
        ip = self.entry_ip.get().strip()
        if ip:
            self.on_ip_entered(ip)
            self.destroy()

