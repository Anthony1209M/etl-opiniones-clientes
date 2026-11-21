import csv
import unicodedata

from domain.interfaces import IExtractor


def _sin_tildes(texto):
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn").strip()


class CsvExtractor(IExtractor):
    def __init__(self, config):
        self.name = config["name"]
        self.path = config["path"]
        self.columns = config["columns"]

    def extract(self):
        with open(self.path, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)

            # valida la estructura del archivo
            encabezados = [_sin_tildes(c) for c in (lector.fieldnames or [])]
            faltantes = set(self.columns) - set(encabezados)
            if faltantes:
                raise ValueError(f"Faltan columnas en {self.path}: {faltantes}")

            return [
                {_sin_tildes(k): (v or "").strip() for k, v in fila.items() if k is not None}
                for fila in lector
            ]