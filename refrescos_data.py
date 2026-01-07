import json
from pathlib import Path

ARCHIVO = Path("refrescos.json")


def cargar_refrescos():
    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_refrescos(data):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
