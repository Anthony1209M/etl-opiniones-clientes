import pyodbc

from domain.interfaces import IExtractor
from infrastructure.db_connection import construir_cadena


class DatabaseExtractor(IExtractor):
    def __init__(self, config, db_config):
        self.name = config["name"]
        self.query = config["query"]          # consulta fija definida en settings.json
        self.db = db_config
        self.batch_size = db_config.get("batch_size", 5000)

    def extract(self):
        registros = []
        with pyodbc.connect(construir_cadena(self.db)) as conexion:
            cursor = conexion.cursor()
            cursor.execute(self.query)
            columnas = [c[0] for c in cursor.description]

            # lectura por lotes para no cargar todo de golpe
            while True:
                lote = cursor.fetchmany(self.batch_size)
                if not lote:
                    break
                registros.extend(dict(zip(columnas, fila)) for fila in lote)
        return registros