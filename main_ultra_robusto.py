# main_ultra_robusto.py - VERSIÓN CON MANEJO DE ERRORES MEJORADO
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime, timedelta
import os
import uvicorn
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN ROBUSTA ===
try:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        logger.warning(" DATABASE_URL no encontrada, usando SQLite")
        DATABASE_URL = "sqlite:///./gimnasio.db"
    
    logger.info(f" Conectando a: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    
    # Intentar conexión
    with Session(engine) as test_session:
        test_session.exec(select(1))
    logger.info(" Conexión a BD exitosa")
    
except Exception as e:
    logger.error(f" Error de conexión a BD: {e}")
    # Crear engine de emergencia
    DATABASE_URL = "sqlite:///./emergencia.db"
    engine = create_engine(DATABASE_URL, echo=False)

# === MODELOS SIMPLIFICADOS ===
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str

class Clase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    dia_semana: str
    hora_inicio: str

class PlanMembresia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    duracion_dias: int

# Crear tablas con reintentos
def crear_tablas_seguras():
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            SQLModel.metadata.create_all(engine)
            logger.info(" Tablas creadas exitosamente")
            return True
        except Exception as e:
            logger.warning(f" Intento {intento + 1} falló: {e}")
            if intento < max_intentos - 1:
                time.sleep(2)
    logger.error(" No se pudieron crear las tablas después de varios intentos")
    return False

crear_tablas_seguras()

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Gimnasio API - ULTRA ROBUSTO", version="3.2.0")

# === ENDPOINTS CON MANEJO DE ERRORES MEJORADO ===
@app.get("/")
def home():
    return {"mensaje": " Sistema ULTRA ROBUSTO funcionando", "status": "active", "version": "3.2.0"}

@app.get("/health")
def health_check():
    try:
        with Session(engine) as session:
            session.exec(select(1))
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "running", 
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/socios/")
def listar_socios(session: Session = Depends(get_session)):
    try:
        socios = session.exec(select(Socio)).all()
        return {
            "socios": socios, 
            "total": len(socios), 
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f" Error en /socios/: {e}")
        return {
            "error": "Error temporal en la base de datos",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/notificaciones/vencimientos-proximos")
def vencimientos_proximos(dias: int = 3, session: Session = Depends(get_session)):
    try:
        hoy = datetime.now().date()
        socios = session.exec(select(Socio)).all()
        
        vencimientos = []
        for socio in socios:
            try:
                vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
                if hoy <= vencimiento <= (hoy + timedelta(days=dias)):
                    dias_restantes = (vencimiento - hoy).days
                    vencimientos.append({
                        "socio_id": socio.id,
                        "nombre": socio.nombre,
                        "vencimiento": socio.vencimiento,
                        "dias_restantes": dias_restantes
                    })
            except Exception as e:
                logger.warning(f" Error procesando socio {socio.id}: {e}")
                continue
        
        return {
            "vencimientos": vencimientos, 
            "total": len(vencimientos), 
            "status": "success",
            "fecha_consulta": hoy.isoformat()
        }
    except Exception as e:
        logger.error(f" Error en vencimientos-proximos: {e}")
        return {
            "error": "Error temporal en el servicio",
            "status": "error", 
            "timestamp": datetime.now().isoformat()
        }

@app.get("/clases/")
def listar_clases(session: Session = Depends(get_session)):
    try:
        clases = session.exec(select(Clase)).all()
        if not clases:
            # Crear clases de ejemplo de forma segura
            try:
                clases_ejemplo = [
                    Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00"),
                    Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30"),
                ]
                for clase in clases_ejemplo:
                    session.add(clase)
                session.commit()
                clases = session.exec(select(Clase)).all()
            except Exception as e:
                logger.error(f" Error creando clases: {e}")
                session.rollback()
        
        return {"clases": clases, "status": "success"}
    except Exception as e:
        logger.error(f" Error en /clases/: {e}")
        return {"error": "Error temporal", "status": "error"}

@app.get("/debug-db")
def debug_database():
    try:
        with Session(engine) as session:
            # Probar diferentes consultas
            socios_count = len(session.exec(select(Socio)).all())
            clases_count = len(session.exec(select(Clase)).all())
            planes_count = len(session.exec(select(PlanMembresia)).all())
            
        return {
            "database_url": DATABASE_URL,
            "socios": socios_count,
            "clases": clases_count, 
            "planes": planes_count,
            "status": "success"
        }
    except Exception as e:
        return {
            "database_url": DATABASE_URL,
            "error": str(e),
            "status": "error"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
