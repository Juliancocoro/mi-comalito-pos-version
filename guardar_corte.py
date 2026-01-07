import json
from datetime import datetime
from pathlib import Path

ARCHIVO = Path("ventas.json")


def guardar_corte(total_vendido, tickets_pagados):
    corte = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "total_vendido": total_vendido,
        "tickets_pagados": tickets_pagados
    }

    if ARCHIVO.exists():
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(corte)

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
