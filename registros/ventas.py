import json
import os
from datetime import datetime

RUTA = "data/ventas.json"


def guardar_venta(items, total):
    venta = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S"),
        "total": total,
        "items": items
    }

    if not os.path.exists(RUTA):
        with open(RUTA, "w") as f:
            json.dump([], f)

    with open(RUTA, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append(venta)

    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
