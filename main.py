# main.py - OPTIMIZADO PARA KOYEB
from fastapi import FastAPI
from datetime import datetime, timedelta
import os

app = FastAPI(title="Gimnasio API", version="4.0")

# [TODO: Tu código actual aquí...]

# PUERTO CRÍTICO PARA KOYEB
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))  #  KOYEB USA 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
