# main.py - VERSIÓN CORREGIDA CON PUERTO DE RENDER
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "OK", "message": "Servidor funcionando en puerto correcto"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/socios")
def socios():
    return [{"id": "1001", "nombre": "Ana García", "vencimiento": "2024-12-31"}]

@app.get("/clases")
def clases():
    return [{"nombre": "Yoga", "dia_semana": "Lunes", "hora_inicio": "18:00"}]

@app.get("/planes")
def planes():
    return [{"nombre": "Básico", "precio": 50.0}]

# CORRECCIÓN CRÍTICA: Usar el puerto de Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  #  Render usa 10000
    uvicorn.run(app, host="0.0.0.0", port=port)
