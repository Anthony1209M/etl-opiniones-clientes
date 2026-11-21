import asyncio
import time

from application.extraction_service import ExtractionService
from infrastructure.config_loader import cargar_configuracion
from infrastructure.extractor_factory import crear_extractores
from infrastructure.logger_service import crear_logger
from infrastructure.staging.json_loader import JsonStagingLoader
from infrastructure.staging.sql_loader import SqlStagingLoader


def imprimir_resumen(resultados):
    print("\n===== RESUMEN DE EXTRACCIÓN =====")
    for r in resultados:
        print(f"{r['fuente']:<18} {r['estado']:<6} {r['registros']:>6} registros  "
              f"{r['segundos']:.2f}s  -> {r['destino']}")


def crear_loader(settings):
    if settings["staging"]["mode"] == "sql":
        return SqlStagingLoader(settings["database"])
    return JsonStagingLoader(settings["staging"]["directory"])


def main():
    logger = crear_logger()
    settings = cargar_configuracion()

    servicio = ExtractionService(
        extractores=crear_extractores(settings),
        loader=crear_loader(settings),
        logger=logger,
        max_paralelo=settings["worker"]["max_parallel_sources"],
    )
    intervalo = settings["worker"]["run_interval_seconds"]

    logger.info("Worker de extracción iniciado")
    try:
        while True:
            resultados = asyncio.run(servicio.ejecutar())
            imprimir_resumen(resultados)
            if intervalo <= 0:
                break                       # una sola ejecución
            logger.info(f"Próxima ejecución en {intervalo}s")
            time.sleep(intervalo)           # modo worker: se repite
    except KeyboardInterrupt:
        logger.info("Worker detenido por el usuario")


if __name__ == "__main__":
    main()