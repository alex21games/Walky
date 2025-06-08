import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from Utils.utils import cargar_contactos
from Utils.utils import guardar_contactos

class ClienteChat:
    def __init__(self, master):
        self.contacto_destino = None
        self.master = master
        self.master.title("Chat LAN")
        self.master.geometry("500x500")

        self.nombre = None
        self.cliente = None

        self.contactos = cargar_contactos()
        self.contacto_actual = tk.StringVar()

        self.construir_interfaz()
        self.conectado = False

    def seleccionar_contacto(self, event):
        seleccionado = self.combo_contactos.get()
        self.contacto_destino = seleccionado


    def construir_interfaz(self):
        frame_superior = tk.Frame(self.master)
        frame_superior.pack(pady=10)

        tk.Label(frame_superior, text="Tu nombre:").pack(side=tk.LEFT)
        self.entry_nombre = tk.Entry(frame_superior)
        self.entry_nombre.pack(side=tk.LEFT)
        tk.Button(frame_superior, text="Conectar", command=self.conectar).pack(side=tk.LEFT)

        self.combo_contactos = ttk.Combobox(self.master, values=self.contactos["equipo"])
        self.combo_contactos.pack(pady=5)
        self.combo_contactos.bind("<<ComboboxSelected>>", self.seleccionar_contacto)
        frame_agregar = tk.Frame(self.master)
        frame_agregar.pack(pady=5)

        self.entry_nuevo_contacto = tk.Entry(frame_agregar)
        self.entry_nuevo_contacto.pack(side=tk.LEFT)
        tk.Button(frame_agregar, text="Agregar contacto", command=self.agregar_contacto).pack(side=tk.LEFT)


        self.text_chat = tk.Text(self.master, state="disabled")
        self.text_chat.pack(expand=True, fill=tk.BOTH)

        frame_inferior = tk.Frame(self.master)
        frame_inferior.pack(pady=10)

        self.entry_mensaje = tk.Entry(frame_inferior, width=40)
        self.entry_mensaje.pack(side=tk.LEFT)
        tk.Button(frame_inferior, text="Enviar", command=self.enviar_mensaje).pack(side=tk.LEFT)

    def conectar(self):
        self.nombre = self.entry_nombre.get()
        if not self.nombre:
            messagebox.showerror("Error", "Escribe tu nombre.")
            return

        host = "192.168.1.9"  
        port = 8080

        try:
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente.connect((host, port))
            self.cliente.send(self.nombre.encode())
            threading.Thread(target=self.recibir_mensajes, daemon=True).start()
            self.conectado = True
            self.mostrar_en_chat("Conectado al servidor.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")

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

        self.combo_contactos["values"] = self.contactos["equipo"]
        self.entry_nuevo_contacto.delete(0, tk.END)
        messagebox.showinfo("Agregado", f"Contacto '{nuevo}' añadido.")


    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.cliente.recv(1024).decode()
                self.mostrar_en_chat(mensaje)
            except:
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
        self.entry_mensaje.delete(0, tk.END)

    def mostrar_en_chat(self, mensaje):
        self.text_chat.config(state="normal")
        self.text_chat.insert(tk.END, mensaje + "\n")
        self.text_chat.config(state="disabled")
        self.text_chat.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteChat(root)
    root.mainloop()

