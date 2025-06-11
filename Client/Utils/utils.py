# INUTILIZADO O OBSOLETO



import json

# Utilidades para que no este tan saturado # el codigo principal, aqui se cargan y guardan los contactos en un archivo yeizon

# Esto maneja la carga y guardado de los contactos
def cargar_contactos():
    try:
        with open("contactos.json", "r") as f:
            return json.load(f)
    except:
        return {"equipo": []}

# Esta funcion guarda los contactos en un archivo geison (lo crea automaticamente si no existe)
def guardar_contactos(contactos):
    with open("contactos.json", "w") as f:
        json.dump(contactos, f, indent=4)

# TODO: Añadir la capacidad de eliminar contactos (ya lo añadi xd pero ps nomas dejo este comentario por si acaso)
def eliminar_contacto(contactos, contacto):
    if contacto in contactos["equipo"]:
        contactos["equipo"].remove(contacto)
        guardar_contactos(contactos)
        return True
    return False
