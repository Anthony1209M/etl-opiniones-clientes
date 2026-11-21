import csv
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

load_dotenv("../.env")

app = FastAPI(title="API simulada de comentarios de redes sociales")
TOKEN = os.environ.get("API_TOKEN", "")
RUTA_CSV = "../csvs/social_comments.csv"


@app.get("/comments")
def comments(authorization: str = Header(default="")):
    if TOKEN and authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")
    with open(RUTA_CSV, encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))