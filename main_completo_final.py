# main_completo_final.py - API COMPLETA PARA DASHBOARD
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime, timedelta
import os
import uvicorn
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN ===
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./gimnasio.db")
engine = create_engine(DATABASE_URL, echo=False)

# === MODELOS COMPLETOS ===
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str

class Entrada(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str = Field(foreign_key="socio.id")
    nombre_socio: str
    fecha_hora: str

class Clase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    dia_semana: str
    hora_inicio: str
    instructor: str = "Instructor"

class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str = Field(foreign_key="socio.id")
    clase_id: int = Field(foreign_key="clase.id")
    fecha_reserva: str
    estado: str = "confirmada"

class PlanMembresia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    duracion_dias: int
    descripcion: str

# Crear tablas
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Gimnasio API - COMPATIBLE DASHBOARD", version="3.3.0")

# === ENDPOINTS COMPATIBLES CON DASHBOARD ===

@app.get("/")
def home():
    return {"mensaje": " API compatible con dashboard", "version": "3.3.0"}

# Endpoint para dashboard - devuelve array directo (compatible)
@app.get("/socios")
def listar_socios_dashboard():
    """Endpoint compatible con dashboard - devuelve array directo"""
    try:
        with Session(engine) as session:
            socios = session.exec(select(Socio)).all()
            # Limpiar datos y asegurar formato correcto
            socios_limpios = []
            for socio in socios:
                if socio.id != "string":  # Filtrar el registro corrupto
                    socios_limpios.append({
                        "id": socio.id,
                        "nombre": socio.nombre,
                        "vencimiento": socio.vencimiento
                    })
            return socios_limpios
    except Exception as e:
        logger.error(f"Error en /socios: {e}")
        return []

@app.get("/clases")
def listar_clases_dashboard():
    """Endpoint compatible con dashboard - devuelve array directo"""
    try:
        with Session(engine) as session:
            clases = session.exec(select(Clase)).all()
            return clases
    except Exception as e:
        logger.error(f"Error en /clases: {e}")
        return []

@app.get("/planes")
def listar_planes_dashboard():
    """Endpoint para dashboard - planes"""
    try:
        with Session(engine) as session:
            planes = session.exec(select(PlanMembresia)).all()
            if not planes:
                # Crear planes de ejemplo
                planes_ejemplo = [
                    PlanMembresia(nombre="Básico", precio=50.0, duracion_dias=30, descripcion="Acceso básico"),
                    PlanMembresia(nombre="Premium", precio=80.0, duracion_dias=30, descripcion="Acceso completo"),
                    PlanMembresia(nombre="Familiar", precio=120.0, duracion_dias=30, descripcion="Plan familiar"),
                ]
                for plan in planes_ejemplo:
                    session.add(plan)
                session.commit()
                planes = session.exec(select(PlanMembresia)).all()
            return planes
    except Exception as e:
        logger.error(f"Error en /planes: {e}")
        return []

@app.get("/reservas")
def listar_reservas_dashboard():
    """Endpoint para dashboard - reservas"""
    try:
        with Session(engine) as session:
            reservas = session.exec(select(Reserva)).all()
            return reservas
    except Exception as e:
        logger.error(f"Error en /reservas: {e}")
        return []

@app.get("/entradas")
def listar_entradas_dashboard():
    """Endpoint para dashboard - entradas"""
    try:
        with Session(engine) as session:
            entradas = session.exec(select(Entrada)).all()
            return entradas
    except Exception as e:
        logger.error(f"Error en /entradas: {e}")
        return []

# === LIMPIAR DATOS CORRUPTOS ===
@app.post("/limpiar-datos")
def limpiar_datos_corruptos():
    """Limpiar datos corruptos de la base de datos"""
    try:
        with Session(engine) as session:
            # Eliminar socios corruptos
            socios_corruptos = session.exec(select(Socio).where(Socio.id == "string")).all()
            for socio in socios_corruptos:
                session.delete(socio)
            
            session.commit()
            return {"message": f" Datos corruptos limpiados: {len(socios_corruptos)} socios eliminados"}
    except Exception as e:
        return {"error": f"Error limpiando datos: {e}"}

# === ENDPOINTS EXISTENTES (para mantener compatibilidad) ===
@app.get("/health")
def health_check():
    try:
        with Session(engine) as session:
            session.exec(select(1))
        return {"status": "running", "database": "healthy"}
    except:
        return {"status": "running", "database": "unhealthy"}

@app.get("/notificaciones/vencimientos-proximos")
def vencimientos_proximos(dias: int = 3):
    try:
        hoy = datetime.now().date()
        with Session(engine) as session:
            socios = session.exec(select(Socio)).all()
            
            vencimientos = []
            for socio in socios:
                try:
                    if socio.id != "string":  # Ignorar corruptos
                        vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
                        if hoy <= vencimiento <= (hoy + timedelta(days=dias)):
                            dias_restantes = (vencimiento - hoy).days
                            vencimientos.append({
                                "socio_id": socio.id,
                                "nombre": socio.nombre,
                                "dias_restantes": dias_restantes
                            })
                except:
                    continue
            
            return {"vencimientos": vencimientos, "total": len(vencimientos)}
    except Exception as e:
        return {"error": f"Error: {e}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
