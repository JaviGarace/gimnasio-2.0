# main_completo.py - SISTEMA COMPLETO RESTAURADO
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime, timedelta
import os
import uvicorn
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN ===
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./temp.db")
engine = create_engine(DATABASE_URL, echo=True)

# === MODELOS COMPLETOS ===
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str
    email: Optional[str] = None
    telefono: Optional[str] = None

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
    duracion_min: int = 60
    capacidad_max: int = 20
    instructor: str = Field(default="Instructor Por Definir")

class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str = Field(foreign_key="socio.id")
    clase_id: int = Field(foreign_key="clase.id")
    fecha_reserva: str
    estado: str = "confirmada"

class PlanMembresia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    precio: float
    duracion_dias: int
    descripcion: str
    activo: bool = Field(default=True)

class Pago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str = Field(foreign_key="socio.id")
    plan_id: int = Field(foreign_key="planmembresia.id")
    monto: float
    fecha_pago: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    fecha_vencimiento: str
    estado: str = Field(default="pendiente")
    metodo_pago: Optional[str] = None
    referencia: Optional[str] = None

# Crear tablas
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(
    title="Gimnasio Inteligente API - RESTAURADO",
    description="Sistema completo restaurado después de daño por Qwen",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ENDPOINTS BÁSICOS ===
@app.get("/")
def home():
    return {"mensaje": " Sistema completo RESTAURADO y funcionando", "status": "active"}

@app.get("/debug-routes")
def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": getattr(route, "path", "N/A"),
            "methods": getattr(route, "methods", "N/A"),
            "name": getattr(route, "name", "N/A")
        })
    return {"routes": routes}

@app.get("/create-tables")
def create_tables():
    try:
        SQLModel.metadata.create_all(engine)
        return {"message": " Todas las tablas creadas", "tablas": list(SQLModel.metadata.tables.keys())}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

# === SOCIOS - COMPLETO ===
@app.get("/socios/{id_socio}")
def obtener_socio(id_socio: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == id_socio)).first()
    if socio:
        return socio
    raise HTTPException(status_code=404, detail="Socio no encontrado")

@app.get("/socios/")
def listar_socios(session: Session = Depends(get_session)):
    try:
        socios = session.exec(select(Socio)).all()
        return socios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/socios/")
def crear_socio(socio: Socio, session: Session = Depends(get_session)):
    existing = session.exec(select(Socio).where(Socio.id == socio.id)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Socio ya existe")
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio

# === SISTEMA DE NOTIFICACIONES - COMPLETO ===
@app.get("/notificaciones/vencimientos-proximos")
def obtener_vencimientos_proximos(dias: int = 3, session: Session = Depends(get_session)):
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(days=dias)
    
    socios = session.exec(select(Socio)).all()
    
    vencimientos_proximos = []
    for socio in socios:
        try:
            vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
            if hoy <= vencimiento <= fecha_limite:
                dias_restantes = (vencimiento - hoy).days
                vencimientos_proximos.append({
                    "socio_id": socio.id,
                    "nombre": socio.nombre,
                    "vencimiento": socio.vencimiento,
                    "dias_restantes": dias_restantes,
                    "estado": "HOY" if dias_restantes == 0 else f"en {dias_restantes} días"
                })
        except:
            continue
    
    return {
        "status": "success",
        "total_vencimientos": len(vencimientos_proximos),
        "vencimientos": vencimientos_proximos,
        "fecha_consulta": hoy.isoformat()
    }

@app.get("/notificaciones/socios-morosos")
def obtener_socios_morosos(session: Session = Depends(get_session)):
    hoy = datetime.now().date()
    
    socios = session.exec(select(Socio)).all()
    
    socios_morosos = []
    for socio in socios:
        try:
            vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
            if vencimiento < hoy:
                dias_vencido = (hoy - vencimiento).days
                socios_morosos.append({
                    "socio_id": socio.id,
                    "nombre": socio.nombre,
                    "vencimiento": socio.vencimiento,
                    "dias_vencido": dias_vencido,
                    "estado": f"Vencida hace {dias_vencido} días"
                })
        except:
            continue
    
    return {
        "status": "success",
        "total_morosos": len(socios_morosos),
        "socios_morosos": socios_morosos
    }

@app.post("/notificaciones/enviar-recordatorio")
def enviar_recordatorio_vencimiento(socio_id: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    try:
        vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
        hoy = datetime.now().date()
        dias_restantes = (vencimiento - hoy).days
        
        if dias_restantes < 0:
            mensaje = f" Hola {socio.nombre}, tu membresía está VENCIDA desde hace {-dias_restantes} días."
            tipo = "MOROSO"
        elif dias_restantes == 0:
            mensaje = f" Hola {socio.nombre}, tu membresía VENCE HOY."
            tipo = "VENCE_HOY"
        else:
            mensaje = f" Hola {socio.nombre}, tu membresía vence en {dias_restantes} días."
            tipo = "RECORDATORIO"
        
        return {
            "status": "success",
            "message": "Notificación enviada",
            "socio": socio.nombre,
            "tipo": tipo,
            "mensaje": mensaje,
            "dias_restantes": dias_restantes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/sistema-notificaciones/status")
def status_notificaciones():
    return {
        "sistema": "Notificaciones Automáticas - RESTAURADO",
        "version": "3.0.0",
        "status": "ACTIVO",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/datos-prueba/notificaciones")
def crear_datos_prueba_notificaciones(session: Session = Depends(get_session)):
    try:
        hoy = datetime.now().date()
        
        # Crear socios de prueba
        socios = [
            Socio(id="2001", nombre="Ana Prueba", vencimiento=(hoy + timedelta(days=2)).strftime("%Y-%m-%d")),
            Socio(id="2002", nombre="Carlos Prueba", vencimiento=(hoy - timedelta(days=5)).strftime("%Y-%m-%d")),
            Socio(id="2003", nombre="Maria Prueba", vencimiento=(hoy + timedelta(days=30)).strftime("%Y-%m-%d")),
        ]
        
        for socio in socios:
            session.merge(socio)
        
        session.commit()
        
        return {
            "status": "success",
            "message": " Datos de prueba creados",
            "socios_creados": len(socios)
        }
    except Exception as e:
        session.rollback()
        return {"error": f"Error: {str(e)}"}

# === MANTENER ENDPOINTS EXISTENTES ===
@app.get("/planes/")
def listar_planes(session: Session = Depends(get_session)):
    return session.exec(select(PlanMembresia)).all()

@app.get("/clases/")
def listar_clases(session: Session = Depends(get_session)):
    if session.exec(select(Clase)).first() is None:
        clases = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", instructor="María Silva"),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", instructor="Carlos Ruiz"),
        ]
        for clase in clases:
            session.add(clase)
        session.commit()
    return session.exec(select(Clase)).all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
