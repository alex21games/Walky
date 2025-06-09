import sqlite3
import os

DB_FILE = "chat_data.db"

# Crear conexión
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Crear tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL
)
''')

# Crear tabla de contactos por usuario
cursor.execute('''
CREATE TABLE IF NOT EXISTS contactos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    contacto_nombre TEXT NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

# Crear tabla de mensajes
cursor.execute('''
CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emisor TEXT NOT NULL,
    receptor TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("Base de datos SQLite inicializada correctamente.")
