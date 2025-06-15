import socket
import threading
import customtkinter as ctk
from tkinter import messagebox

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
        self.text_chat.configure(state="normal")
        self.text_chat.delete("1.0", "end")
        self.text_chat.configure(state="disabled")
        self.mostrar_en_chat(f"[Sistema] Hablando con {nombre}")

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
                            self.mostrar_en_chat(f"Has aceptado a {nuevo} como contacto.")

                    elif mensaje.startswith("[Historial]::"):
                        try:
                            _, resto = mensaje.split("::", 1)
                            contacto, linea = resto.split("|", 1)
                            if contacto not in self.historiales:
                                self.historiales[contacto] = []
                            self.historiales[contacto].append(linea)
                            if self.contacto_destino == contacto:
                                self.master.after(0, lambda l=linea: self.mostrar_en_chat(l))
                        except ValueError:
                            print(f"[!] Error de formato en mensaje de historial: {mensaje}")

                    elif mensaje.startswith("[Error]::"):
                        _, error_msg = mensaje.split("::", 1)
                        self.master.after(0, lambda: messagebox.showerror("Error del servidor", error_msg))

            except Exception as e:
                print(f"Error en recibir_mensajes: {e}")
                self.conectado = False
                self.mostrar_en_chat("Desconectado del servidor.")
                break


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
        # Elimina todos los widgets hijos del scrollable frame, pero sin destruirlo
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
        self.historiales.setdefault(self.contacto_destino, []).append(f"Tú -> {self.contacto_destino}: {mensaje}")
        self.mostrar_en_chat(f"Tú -> {self.contacto_destino}: {mensaje}")
        self.entry_mensaje.delete(0, "end")

    def mostrar_en_chat(self, mensaje):
        if self.contacto_destino:
            self.text_chat.configure(state="normal")
            self.text_chat.delete("1.0", "end")
            for linea in self.historiales.get(self.contacto_destino, []):
                self.text_chat.insert("end", linea + "\n")
            self.text_chat.configure(state="disabled")
            self.text_chat.see("end")

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
