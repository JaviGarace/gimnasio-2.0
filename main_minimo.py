# main.py - VERSIÓN MÍNIMA GARANTIZADA
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "OK", "message": "Servidor funcionando"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/socios")
def socios():
    return [{"id": "1001", "nombre": "Test", "vencimiento": "2024-12-31"}]

@app.get("/clases")
def clases():
    return [{"nombre": "Yoga", "dia_semana": "Lunes", "hora_inicio": "18:00"}]

@app.get("/planes")
def planes():
    return [{"nombre": "Básico", "precio": 50.0}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
