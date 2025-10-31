# main.py - Primera API REST con FastAPI
from fastapi import FastAPI

app = FastAPI(
    title="Gimnasio Inteligente API",
    description="API para gestión de socios, entradas y clases",
    version="2.0.0"
)

@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido al Gimnasio Inteligente!"}

@app.get("/socios/{id_socio}")
def obtener_socio(id_socio: str):
    # Aquí irá la lógica con base de datos
    return {
        "id": id_socio,
        "nombre": "Ana López",
        "vencimiento": "2025-11-15"
    }