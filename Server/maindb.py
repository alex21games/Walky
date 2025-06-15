import sqlite3
import os

# Asegúrate de que exista la carpeta DataBase
os.makedirs("Server/DataBase", exist_ok=True)
DB_FILE = "Server/DataBase/chat_data.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL
)
''')

# Tabla de contactos
cursor.execute('''
CREATE TABLE IF NOT EXISTS contactos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    contacto_nombre TEXT NOT NULL,
    UNIQUE(usuario_id, contacto_nombre),
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

# Tabla de mensajes
cursor.execute('''
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emisor TEXT NOT NULL,
    receptor TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla de solicitudes con timestamp para cooldown
cursor.execute('''
CREATE TABLE IF NOT EXISTS solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emisor TEXT NOT NULL,
    receptor TEXT NOT NULL,
    estado TEXT DEFAULT 'pendiente',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("Base de datos inicializada correctamente.")
