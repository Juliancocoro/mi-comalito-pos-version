import json
from pathlib import Path

ARCHIVO_GUISOS = Path("guisos.json")


def cargar_guisos():
    """
    Carga los guisos desde el archivo JSON.
    Si no existe, lo crea con valores por defecto.
    """
    if not ARCHIVO_GUISOS.exists():
        guisos_default = {
            "Frijol con Queso": 0,
            "Huevo verde": 0,
            "Huevo rojo": 0,
            "Chicharrón": 0,
            "Deshebrada": 0,
            "Picadillo": 0,
            "Papa con chorizo": 0,
            "Calabazas a la Mexicana": 0,
            "Nopales a la Mexicana": 0
        }
        guardar_guisos(guisos_default)
        return guisos_default

    with open(ARCHIVO_GUISOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_guisos(guisos):
    """Guarda los guisos en el archivo JSON"""
    with open(ARCHIVO_GUISOS, "w", encoding="utf-8") as f:
        json.dump(guisos, f, indent=4, ensure_ascii=False)


# ⚠️ ESTA VARIABLE SE MANTIENE PARA NO ROMPER NADA
GUISOS = cargar_guisos()
