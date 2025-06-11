import customtkinter as ctk
from tkinter import messagebox
import os

class LoginVentana(ctk.CTkToplevel):
    def __init__(self, master, on_login, on_register):
        super().__init__(master)
        self.title("Login")
        self.geometry("300x220")
        self.on_login = on_login
        self.on_register = on_register

        ctk.CTkLabel(self, text="Usuario:").pack(pady=5)
        self.entry_usuario = ctk.CTkEntry(self)
        self.entry_usuario.pack(pady=5)

        ctk.CTkLabel(self, text="Contraseña:").pack(pady=5)
        self.entry_contrasena = ctk.CTkEntry(self, show="*")
        self.entry_contrasena.pack(pady=5)

        ctk.CTkButton(self, text="Iniciar sesión", command=self.login).pack(pady=5)
        ctk.CTkButton(self, text="Registrarse", command=self.registrar).pack(pady=5)
        self.entry_usuario.focus_set()
        self.bind("<Return>", lambda event: self.login())


    def login(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Debes ingresar usuario y contraseña.")
            return

        self.on_login(usuario, contrasena, self)

    def registrar(self):
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Debes ingresar usuario y contraseña.")
            return
        
        self.on_register(usuario, contrasena, self)