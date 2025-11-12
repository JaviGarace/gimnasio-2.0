# main.py - API LIMPIA Y FUNCIONAL (RESET TOTAL)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime, timedelta
import os

# Usar base de datos limpia
DATABASE_URL = "sqlite:///./gimnasio_limpio.db"
engine = create_engine(DATABASE_URL, echo=True)

# Modelos limpios y simples
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str

class Clase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    dia_semana: str
    hora_inicio: str
    instructor: str = "Instructor Por Definir"  # AHORA SÍ INCLUIMOS ESTA COLUMNA
    capacidad_max: int = 20

class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str
    clase_id: int
    estado: str = "confirmada"

class PlanMembresia(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    precio: float
    duracion_dias: int
    descripcion: str
    activo: bool = True

class Pago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str
    plan_id: int
    monto: float
    fecha_pago: str
    fecha_vencimiento: str
    estado: str = "pendiente"
    metodo_pago: str = "efectivo"

class Entrada(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str
    nombre_socio: str
    fecha_hora: str

# Crear tablas
SQLModel.metadata.create_all(engine)

# Dependencia de sesión
def get_session():
    with Session(engine) as session:
        yield session

# Aplicación FastAPI
app = FastAPI(title="Gimnasio Limpio - RESET TOTAL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints funcionales
@app.get("/")
def root():
    return {"mensaje": "API limpia y funcional", "estado": "activo"}

@app.get("/clases/")
def get_clases(session: Session = Depends(get_session)):
    try:
        clases = session.exec(select(Clase)).all()
        return clases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/socios/")
def get_socios(session: Session = Depends(get_session)):
    try:
        socios = session.exec(select(Socio)).all()
        return socios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/reservas/")
def get_reservas(session: Session = Depends(get_session)):
    try:
        reservas = session.exec(select(Reserva)).all()
        return reservas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/planes/")
def get_planes(session: Session = Depends(get_session)):
    try:
        planes = session.exec(select(PlanMembresia)).all()
        return planes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/pagos/")
def get_pagos(session: Session = Depends(get_session)):
    try:
        pagos = session.exec(select(Pago)).all()
        return pagos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/entradas/")
def get_entradas(session: Session = Depends(get_session)):
    try:
        entradas = session.exec(select(Entrada)).all()
        return entradas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Inicializar datos limpios
def inicializar_datos():
    with Session(engine) as session:
        # Verificar si ya hay datos
        if session.exec(select(Socio)).first() is not None:
            return  # Ya hay datos, no inicializar de nuevo
        
        # Crear planes
        planes = [
            PlanMembresia(nombre="Básico", precio=50.0, duracion_dias=30, descripcion="Acceso básico"),
            PlanMembresia(nombre="Premium", precio=80.0, duracion_dias=30, descripcion="Acceso completo"),
            PlanMembresia(nombre="Familiar", precio=120.0, duracion_dias=30, descripcion="Hasta 4 personas")
        ]
        for plan in planes:
            session.add(plan)
        
        # Crear socios
        hoy = datetime.now().date()
        socios = [
            Socio(id="1001", nombre="Ana García", vencimiento=(hoy + timedelta(days=30)).strftime("%Y-%m-%d")),
            Socio(id="1002", nombre="Carlos López", vencimiento=(hoy + timedelta(days=15)).strftime("%Y-%m-%d")),
            Socio(id="1003", nombre="María Rodríguez", vencimiento=hoy.strftime("%Y-%m-%d")),
        ]
        for socio in socios:
            session.add(socio)
        
        # Crear clases CORRECTAS (con instructor)
        clases = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", instructor="María Silva"),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", instructor="Carlos Ruiz"),
            Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30", instructor="Ana Torres"),
        ]
        for clase in clases:
            session.add(clase)
        
        session.commit()

@app.on_event("startup")
def startup():
    inicializar_datos()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
