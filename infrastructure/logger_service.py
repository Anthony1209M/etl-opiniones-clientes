import logging
import os
from logging.handlers import RotatingFileHandler


def crear_logger(nombre="etl", ruta="logs/etl.log"):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    logger = logging.getLogger(nombre)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    archivo = RotatingFileHandler(ruta, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    archivo.setFormatter(formato)
    consola = logging.StreamHandler()
    consola.setFormatter(formato)

    logger.addHandler(archivo)
    logger.addHandler(consola)
    return logger