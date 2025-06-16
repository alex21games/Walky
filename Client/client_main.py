import socket
import threading
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class ClienteChat:
    def __init__(self, master, nombre, contrasena, ip):
        self.master = master
        self.master.title("Walky - Alpha 1.0.1")
        self.master.geometry("1200x800")

        self.nombre = nombre
        self.contrasena = contrasena
        self.ip = ip
        self.cliente = None
        self.conectado = False

        self.contactos = []
        self.contacto_destino = None
        self.historiales = {}
        self.mensajes_mostrados = {}

        self.construir_interfaz()
        self.conectar()

    def construir_interfaz(self):
        frame_main = ctk.CTkFrame(self.master)
        frame_main.pack(expand=True, fill="both")

        self.frame_izquierdo = ctk.CTkFrame(frame_main, width=300)
        self.frame_izquierdo.pack(side="left", fill="y")

        self.lista_contactos = ctk.CTkScrollableFrame(self.frame_izquierdo)
        self.lista_contactos.pack(expand=True, fill="both", padx=5, pady=5)

        frame_agregar = ctk.CTkFrame(self.frame_izquierdo)
        frame_agregar.pack(pady=5)

        self.entry_nuevo_contacto = ctk.CTkEntry(frame_agregar)
        self.entry_nuevo_contacto.pack(side="left")

        ctk.CTkButton(frame_agregar, text="+", width=30, command=self.agregar_contacto).pack(side="left", padx=2)
        ctk.CTkButton(frame_agregar, text="Eliminar", width=30, command=self.eliminar_contacto).pack(side="left", padx=2)

        self.frame_derecho = ctk.CTkFrame(frame_main)
        self.frame_derecho.pack(side="left", expand=True, fill="both")

        self.frame_mensajes = ctk.CTkScrollableFrame(self.frame_derecho)
        self.frame_mensajes.pack(expand=True, fill="both")

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
        if self.contacto_destino == nombre:
            return
        self.contacto_destino = nombre
        self.refrescar_mensajes_del_contacto()
        self.cliente.sendall(f"GET_HISTORIAL::{nombre}\n".encode())

    def refrescar_mensajes_del_contacto(self):
        if self.contacto_destino:
            for widget in self.frame_mensajes.winfo_children():
                widget.destroy()

            for linea in self.historiales.get(self.contacto_destino, []):
                if " dice: " in linea and "@" in linea:
                    contenido, ts = linea.rsplit("@", 1)
                    emisor, texto = contenido.split(" dice: ", 1)
                    self.agregar_burbuja_mensaje(texto.strip(), emisor.strip(), ts.strip())
                elif "->" in linea:
                    if "@" in linea:
                        texto, ts = linea.split("@", 1)
                        self.agregar_burbuja_mensaje(texto.split(": ", 1)[1].strip(), self.nombre, ts.strip())
                    else:
                        self.agregar_burbuja_mensaje(linea.split(": ", 1)[1].strip(), self.nombre)

            self.frame_mensajes.update_idletasks()
            self.frame_mensajes._parent_canvas.yview_moveto(1.0)


    def mostrar_mensaje_individual(self, mensaje):
        if not self.contacto_destino:
            return

        # Detecta y separa el timestamp si existe
        timestamp = ""
        if "@" in mensaje:
            contenido, timestamp = mensaje.rsplit("@", 1)
            mensaje = contenido.strip()
            timestamp = timestamp.strip()

        if "dice: " in mensaje:
            emisor, texto = mensaje.split(" dice: ", 1)
            self.agregar_burbuja_mensaje(texto.strip(), emisor.strip(), timestamp)
        elif "->" in mensaje:
            self.agregar_burbuja_mensaje(mensaje.split(": ", 1)[1].strip(), self.nombre, timestamp)

        self.frame_mensajes.update_idletasks()
        self.frame_mensajes._parent_canvas.yview_moveto(1.0)

    def agregar_contacto(self):
        nuevo = self.entry_nuevo_contacto.get().strip()
        if not nuevo:
            messagebox.showwarning("Aviso", "Escribe un nombre.")
            return
        if nuevo in self.contactos:
            messagebox.showinfo("Ya existe", f"El contacto '{nuevo}' ya está en la lista.")
            return
        try:
            self.cliente.sendall(f"ADD_CONTACTO::{nuevo}\n".encode())
            self.entry_nuevo_contacto.delete(0, "end")
            messagebox.showinfo("Solicitud enviada", f"Solicitud enviada a '{nuevo}'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar contacto: {e}")

    def eliminar_contacto(self):
        contacto = self.contacto_destino
        if not contacto:
            messagebox.showwarning("Error", "Selecciona un contacto para eliminar.")
            return
        if contacto not in self.contactos:
            messagebox.showinfo("No existe", f"El contacto '{contacto}' no está en la lista.")
            return
        try:
            self.cliente.sendall(f"DEL_CONTACTO::{contacto}".encode())
            self.contactos.remove(contacto)
            self.refrescar_contactos()
            self.mostrar_en_chat(f"Contacto '{contacto}' eliminado.")
            messagebox.showinfo("Eliminado", f"Contacto '{contacto}' eliminado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar contacto: {e}")

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
            except Exception as e:
                self.master.after(0, lambda err=e: messagebox.showerror("Error", f"No se pudo conectar: {err}"))

        threading.Thread(target=conectar_thread, daemon=True).start()

    def recibir_mensajes(self):
        while self.conectado:
            try:
                datos = self.cliente.recv(1024).decode()
                for mensaje in datos.splitlines():
                    if mensaje.startswith("[Contactos]::"):
                        _, lista = mensaje.split("::", 1)
                        self.contactos = lista.split(",") if lista else []
                        self.master.after(0, self.refrescar_contactos)

                    elif mensaje.startswith("[Solicitud]::"):
                        _, nombre = mensaje.split("::", 1)
                        self.master.after(0, lambda: self.mostrar_solicitud(nombre))

                    elif mensaje.startswith("[ContactoAceptado]::"):
                        _, nuevo = mensaje.split("::", 1)
                        if nuevo not in self.contactos:
                            self.contactos.append(nuevo)
                            self.master.after(0, self.refrescar_contactos)
                            self.historiales.setdefault(nuevo, [])
                            self.master.after(0, lambda: self.mostrar_mensaje_individual(f"Has aceptado a {nuevo} como contacto."))

                    elif mensaje.startswith("[Historial]::"):
                        try:
                            _, resto = mensaje.split("::", 1)
                            contacto, linea = resto.split("|", 1)
                            if contacto not in self.historiales:
                                self.historiales[contacto] = []

        
                            if linea in self.historiales[contacto]:
                                continue 

                            self.historiales[contacto].append(linea)
                            if self.contacto_destino == contacto:
                                self.master.after(0, lambda l=linea: self.mostrar_mensaje_individual(l))
                        
                        except ValueError:
                            print(f"Error al procesar mensaje de historial: {mensaje}")


                    elif mensaje.startswith("[Error]::"):
                        _, error_msg = mensaje.split("::", 1)
                        self.master.after(0, lambda: messagebox.showerror("Error del servidor", error_msg))

            except Exception as e:
                print(f"Error en recibir_mensajes: {e}")
                self.conectado = False
                self.mostrar_mensaje_individual("Desconectado del servidor.")
                break

    def agregar_burbuja_mensaje(self, texto, emisor, timestamp=""):
        miMsg = emisor == self.nombre
        color_fondo = "#2e8b57" if miMsg else "#444444"
        just = "e" if miMsg else "w"

        frame = ctk.CTkFrame(self.frame_mensajes, fg_color="transparent")
        frame.pack(anchor=just, pady=3, padx=10, fill="x")


        ctk.CTkLabel(
            frame,
            text=emisor,
            text_color="#aaaaaa",
            font=("Arial", 10),
            anchor=just
        ).pack(anchor=just)

        ctk.CTkLabel(
            frame,
            text=texto,
            wraplength=500,
            justify="left",
            font=("Arial", 14),
            fg_color=color_fondo,
            corner_radius=12,
            padx=10,
            pady=5,
            anchor=just
        ).pack(anchor=just)

        if timestamp:
            ctk.CTkLabel(
                frame,
                text=timestamp,
                text_color="#bbbbbb",
                font=("Arial", 9, "italic"),
                anchor=just
            ).pack(anchor=just, pady=(0, 2))

    def mostrar_en_chat(self, mensaje=None):
        if not self.contacto_destino:
            return

    
        if self.contacto_destino not in self.mensajes_mostrados:
            for widget in self.frame_mensajes.winfo_children():
                widget.destroy()
            self.mensajes_mostrados[self.contacto_destino] = 0

        historial = self.historiales.get(self.contacto_destino, [])
        ya_mostrados = self.mensajes_mostrados.get(self.contacto_destino, 0)

        nuevos = historial[ya_mostrados:]  # solo los nuevos
        for linea in nuevos:
            if "dice: " in linea:
                emisor, texto = linea.split(" dice: ", 1)
                self.agregar_burbuja_mensaje(texto, emisor)
            elif "->" in linea:
                self.agregar_burbuja_mensaje(linea.split(": ", 1)[1], self.nombre)

        self.mensajes_mostrados[self.contacto_destino] = len(historial)

        self.frame_mensajes.update_idletasks()
        self.frame_mensajes._parent_canvas.yview_moveto(1.0)


    def mostrar_solicitud(self, nombre):
        ventana = ctk.CTkToplevel(self.master)
        ventana.title("Solicitud de contacto")
        ventana.geometry("300x150")

        ctk.CTkLabel(ventana, text=f"{nombre} quiere agregarte.").pack(pady=10)

        def aceptar():
            self.cliente.sendall(f"ACEPTAR::{nombre}\n".encode())
            ventana.destroy()

        def rechazar():
            ventana.destroy()

        ctk.CTkButton(ventana, text="Aceptar", command=aceptar).pack(pady=5)
        ctk.CTkButton(ventana, text="Rechazar", command=rechazar).pack(pady=5)

    def refrescar_contactos(self):
        for widget in self.lista_contactos.winfo_children():
            widget.destroy()
        for contacto in sorted(set(self.contactos)):
            self.agregar_boton_contacto(contacto)

    def enviar_mensaje(self):
        mensaje = self.entry_mensaje.get()
        if not self.contacto_destino:
            messagebox.showwarning("Error", "Selecciona un contacto.")
            return
        if not mensaje.strip():
            return

        self.cliente.sendall(f"{self.contacto_destino}::{mensaje}\n".encode())

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formateado = f"Tú -> {self.contacto_destino}: {mensaje} @{timestamp}"
        self.historiales.setdefault(self.contacto_destino, []).append(formateado)
        self.mostrar_mensaje_individual(formateado)
        self.entry_mensaje.delete(0, "end")


    def cargar_historial(self, nombre):
        self.text_chat.configure(state="normal")
        self.text_chat.delete("1.0", "end")
        for mensaje in self.historiales.get(nombre, []):
            self.text_chat.insert("end", mensaje + "\n")
        self.text_chat.configure(state="disabled")


def registrar_usuario(usuario, contrasena):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 8080)) 
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
    return False


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
        self.entry_ip.focus_set()
        self.bind("<Return>", lambda event: self.enviar_ip())

    def enviar_ip(self):
        ip = self.entry_ip.get().strip()
        if ip:
            self.on_ip_entered(ip)
            self.destroy()
