import unicodedata

from openpyxl import load_workbook

from domain.interfaces import IExtractor


def _sin_tildes(texto):
    descompuesto = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn").strip()


class ExcelExtractor(IExtractor):
    def __init__(self, config):
        self.name = config["name"]
        self.path = config["path"]
        self.sheet = config.get("sheet")          #si no se indica, usa la primera hoja
        self.columns = config["columns"]

    def extract(self):
        # read_only y data_only: lectura eficiente y valores en vez de fórmulas
        libro = load_workbook(self.path, read_only=True, data_only=True)
        try:
            if self.sheet:
                if self.sheet not in libro.sheetnames:
                    raise ValueError(f"La hoja '{self.sheet}' no existe en {self.path}")
                hoja = libro[self.sheet]
            else:
                hoja = libro.active

            filas = hoja.iter_rows(values_only=True)
            encabezado = next(filas, None)
            if encabezado is None:
                raise ValueError(f"El archivo {self.path} está vacío")

            # valida la estructura, igual que en el CSV
            nombres = [_sin_tildes(c) if c is not None else "" for c in encabezado]
            faltantes = set(self.columns) - set(nombres)
            if faltantes:
                raise ValueError(f"Faltan columnas en {self.path}: {faltantes}")

            registros = []
            for fila in filas:
                if fila is None or all(c is None or str(c).strip() == "" for c in fila):
                    continue                       # salta filas completamente vacías
                registros.append({
                    nombres[i]: ("" if v is None else (v if not isinstance(v, str) else v.strip()))
                    for i, v in enumerate(fila)
                    if i < len(nombres) and nombres[i]
                })
            return registros
        finally:
            libro.close()