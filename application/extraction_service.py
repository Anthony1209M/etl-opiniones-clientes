import asyncio
import time


class ExtractionService:
    def __init__(self, extractores, loader, logger, max_paralelo=4):
        self.extractores = extractores
        self.loader = loader
        self.logger = logger
        self.max_paralelo = max_paralelo

    async def _procesar(self, extractor, semaforo):
        async with semaforo:
            inicio = time.perf_counter()
            try:
                self.logger.info(f"[{extractor.name}] Iniciando extracción")
                # las extracciones son bloqueantes: se ejecutan en hilos
                registros = await asyncio.to_thread(extractor.extract)
                destino = await asyncio.to_thread(self.loader.load, extractor.name, registros)
                segundos = time.perf_counter() - inicio
                self.logger.info(f"[{extractor.name}] {len(registros)} registros "
                                 f"en {segundos:.2f}s -> {destino}")
                return {"fuente": extractor.name, "estado": "OK", "registros": len(registros),
                        "segundos": segundos, "destino": destino}
            except Exception as e:
                segundos = time.perf_counter() - inicio
                self.logger.error(f"[{extractor.name}] Falló la extracción: {e}", exc_info=True)
                return {"fuente": extractor.name, "estado": "ERROR", "registros": 0,
                        "segundos": segundos, "destino": "-"}

    async def ejecutar(self):
        inicio = time.perf_counter()
        semaforo = asyncio.Semaphore(self.max_paralelo)
        # todas las fuentes corren en paralelo; si una falla, las demás continúan
        resultados = await asyncio.gather(
            *(self._procesar(e, semaforo) for e in self.extractores)
        )
        total = sum(r["registros"] for r in resultados)
        self.logger.info(f"Extracción terminada: {total} registros en "
                         f"{time.perf_counter() - inicio:.2f}s")
        return resultados