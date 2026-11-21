from abc import ABC, abstractmethod


class IExtractor(ABC):
    "Contrato que debe cumplir toda fuente de datos."
    name: str

    @abstractmethod
    def extract(self) -> list[dict]:
        "Devuelve los registros extraídos como lista de diccionarios."


class IDataLoader(ABC):
    "Contrato para guardar lo extraído en staging."

    @abstractmethod
    def load(self, source_name: str, records: list[dict]) -> str:
        "Guarda los registros y devuelve el destino (ruta o tabla)."