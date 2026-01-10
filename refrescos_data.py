import json
import sys
import os


def resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ARCHIVO = "refrescos.json"


def cargar_refrescos():
    # Primero buscar en directorio actual (para guardar cambios)
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Si no existe, buscar en recursos empaquetados
    ruta = resource_path(ARCHIVO)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {}


def guardar_refrescos(data):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)