from infrastructure.extractors.api_extractor import ApiExtractor
from infrastructure.extractors.csv_extractor import CsvExtractor
from infrastructure.extractors.database_extractor import DatabaseExtractor
from infrastructure.extractors.excel_extractor import ExcelExtractor

# Para agregar un tipo de fuente nuevo: crear su clase y registrarla aquí
REGISTRO = {
    "csv": lambda cfg, db: CsvExtractor(cfg),
    "excel": lambda cfg, db: ExcelExtractor(cfg),
    "database": lambda cfg, db: DatabaseExtractor(cfg, db),
    "api": lambda cfg, db: ApiExtractor(cfg),
}


def crear_extractores(settings):
    extractores = []
    for fuente in settings["sources"]:
        if not fuente.get("enabled", True):
            continue
        tipo = fuente["type"]
        if tipo not in REGISTRO:
            raise ValueError(f"Tipo de fuente desconocido: {tipo}")
        extractores.append(REGISTRO[tipo](fuente, settings["database"]))
    return extractores