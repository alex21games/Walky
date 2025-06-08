import json

def cargar_contactos():
    try:
        with open("contactos.json", "r") as f:
            return json.load(f)
    except:
        return {"equipo": []}

def guardar_contactos(contactos):
    with open("contactos.json", "w") as f:
        json.dump(contactos, f, indent=4)
