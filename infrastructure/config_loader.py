import json
import os
import re

from dotenv import load_dotenv

load_dotenv()  # carga el archivo .env (credenciales fuera del código)

_PATRON = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _expandir(valor):
    # reemplaza ${VARIABLE} por el valor de la variable de entorno
    if isinstance(valor, str):
        return _PATRON.sub(lambda m: os.environ.get(m.group(1), ""), valor)
    if isinstance(valor, dict):
        return {k: _expandir(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_expandir(v) for v in valor]
    return valor


def cargar_configuracion(ruta="settings.json"):
    with open(ruta, encoding="utf-8") as archivo:
        return _expandir(json.load(archivo))