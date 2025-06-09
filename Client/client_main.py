import socket
import threading
import customtkinter as ctk # Esta libreria es como tkinter pero no da asco al ver la interfaz
from tkinter import messagebox # Esto es para mostrar mensajes al usuario
from Utils.utils import cargar_contactos
from Utils.utils import guardar_contactos

# Este es el cliente entero, que pereza
class ClienteChat:
    # Inicializamos nuestra clase, aqui se definen los parametros base necesarios para el cliente
    def __init__(self, master):
        self.contacto_destino = None
        self.master = master
        self.master.title("Walky")
        self.master.geometry("500x800")

        self.nombre = None
        self.cliente = None

        self.contactos = cargar_contactos() # Esto es para cargar nuestros contactos desde el jeison
        self.contacto_actual = ctk.StringVar() # Esto es para almacenar el contacto seleccionado (para saber a quien mandar el mensaje pues)

        self.construir_interfaz() # Este es el constructor de la interfaz
        self.conectado = False 

    # Este def es pa seleccionar el contacto al que se le envia el mensaje (voy a cambiar la combo box por alguna list box o algo mas bonito por que es cutre)
    def seleccionar_contacto(self, event):
        seleccionado = self.combo_contactos.get()
        self.contacto_destino = seleccionado

    # Este es el def al que referenciamos anteriormente, sirve para construir la interfaz del cliente
    def construir_interfaz(self):
        frame_superior = ctk.CTkFrame(self.master)
        frame_superior.pack(pady=10)

        # Son todos los labels, entries y botones que componen la interfaz
        ctk.CTkLabel(frame_superior, text="Tu nombre:").pack(side="left")
        self.entry_nombre = ctk.CTkEntry(frame_superior)
        self.entry_nombre.pack(side="left")
        ctk.CTkButton(frame_superior, text="Conectar", command=self.conectar).pack(side="left")

        self.combo_contactos = ctk.CTkComboBox(self.master, values=self.contactos["equipo"], command=self.seleccionar_contacto)
        self.combo_contactos.pack(pady=5)
        frame_agregar = ctk.CTkFrame(self.master)
        frame_agregar.pack(pady=5)

        self.entry_nuevo_contacto = ctk.CTkEntry(frame_agregar)
        self.entry_nuevo_contacto.pack(side="left")

        ctk.CTkButton(frame_agregar, text="Agregar contacto", command=self.agregar_contacto).pack(side="left")
        ctk.CTkButton(frame_agregar, text="Eliminar contacto", command=self.eliminar_contacto).pack(side="left")

        self.text_chat = ctk.CTkTextbox(self.master, state="disabled")
        self.text_chat.pack(expand=True, fill="both")

        frame_inferior = ctk.CTkFrame(self.master)
        frame_inferior.pack(pady=10)

        self.entry_mensaje = ctk.CTkEntry(frame_inferior, width=340)
        self.entry_mensaje.pack(side="left")
        ctk.CTkButton(frame_inferior, text="Enviar", command=self.enviar_mensaje).pack(side="left")

    # En este def se realiza una comprobacion para el nombre del usuario, si no se ha escrito nada, se muestra un mensaje de error
    # Pero si lo ha escrito, se intenta conectar al servidor y se inicia un thread para recibir mensajes
    def conectar(self): 
        self.nombre = self.entry_nombre.get()
        if not self.nombre:
            messagebox.showerror("Error", "Escribe tu nombre.")
            return

        host = "192.168.217.131" # TODO: en vez de poner la ip del server, haremos que el usuario pueda elegir el host 
        port = 8080 # El puertoh

        # Esto es pa intentar conectar al server pero en caso de que falle se muestra un un mensaje de error
        try:
            self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente.connect((host, port))
            self.cliente.send(self.nombre.encode())
            threading.Thread(target=self.recibir_mensajes, daemon=True).start()
            self.conectado = True
            self.mostrar_en_chat("Conectado al servidor.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")
    # Este def es pa agregar un contacto a la lista de contactos, si el contacto ya existe, se muestra un mensaje de aviso
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

        self.combo_contactos.configure(values=self.contactos["equipo"])
        self.entry_nuevo_contacto.delete(0, "end")
        messagebox.showinfo("Agregado", f"Contacto '{nuevo}' añadido.")
    
    # Para borrar un contacto si ya te cae mal la persona
    def eliminar_contacto(self):
        contacto = self.combo_contactos.get()

        if not contacto:
            messagebox.showwarning("Error", "Selecciona un contacto.")
            return

        if contacto not in self.contactos["equipo"]:
            messagebox.showinfo("No existe", f"El contacto '{contacto}' no está en la lista.")
            return

        self.contactos["equipo"].remove(contacto)
        guardar_contactos(self.contactos)

        self.combo_contactos.configure(values=self.contactos["equipo"])
        self.mostrar_en_chat(f"Contacto '{contacto}' eliminado.")
        messagebox.showinfo("Eliminado", f"Contacto '{contacto}' eliminado.")

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
        self.entry_mensaje.delete(0, "end")

    def mostrar_en_chat(self, mensaje):
        self.text_chat.configure(state="normal")
        self.text_chat.insert("end", mensaje + "\n")
        self.text_chat.configure(state="disabled")
        self.text_chat.see("end")

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = ClienteChat(root)
    root.mainloop()

