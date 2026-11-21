import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from domain.interfaces import IExtractor


class ApiExtractor(IExtractor):
    def __init__(self, config):
        self.name = config["name"]
        self.url = config["url"]
        self.token = config.get("token", "")
        self.timeout = config.get("timeout", 10)
        self.retries = config.get("retries", 3)

    def extract(self):
        # sesión reutilizable con reintentos ante errores temporales
        sesion = requests.Session()
        reintentos = Retry(total=self.retries, backoff_factor=1,
                           status_forcelist=[429, 500, 502, 503, 504])
        sesion.mount("http://", HTTPAdapter(max_retries=reintentos))
        sesion.mount("https://", HTTPAdapter(max_retries=reintentos))

        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"   # token fuera del código

        respuesta = sesion.get(self.url, headers=headers, timeout=self.timeout)
        respuesta.raise_for_status()

        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("La API debe devolver una lista JSON")
        return datos