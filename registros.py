import json
from datetime import datetime, timedelta
import os

ARCHIVO = "ventas.json"

def _leer():
    if not os.path.exists(ARCHIVO):
        return []
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def total_hoy():
    hoy = datetime.now().strftime("%Y-%m-%d")
    return sum(v["total"] for v in _leer() if v["fecha"] == hoy)

def total_semana():
    hoy = datetime.now()
    inicio = hoy - timedelta(days=hoy.weekday())
    return sum(
        v["total"]
        for v in _leer()
        if datetime.strptime(v["fecha"], "%Y-%m-%d") >= inicio
    )

def total_mes():
    hoy = datetime.now()
    return sum(
        v["total"]
        for v in _leer()
        if datetime.strptime(v["fecha"], "%Y-%m-%d").month == hoy.month
    )

def listar_cortes():
    return _leer()
