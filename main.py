# main.py - API FastAPI Corregida (Compatible con base de datos existente)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
import os

# Configuración de base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./gym_clean.db")
engine = create_engine(DATABASE_URL)

# Modelos corregidos (compatibles con la base de datos existente)
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str

class Clase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    dia_semana: str
    hora_inicio: str
    # REMOVER 'instructor' porque no existe en la base de datos
    duracion_min: int = 60
    capacidad_max: int = 20
    # NOTA: No incluimos 'instructor' porque causa el error

class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str
    clase_id: int
    estado: str = "confirmada"

# Crear tablas (solo las que son compatibles)
SQLModel.metadata.create_all(engine)

# Dependencia de sesión
def get_session():
    with Session(engine) as session:
        yield session

# Aplicación FastAPI
app = FastAPI(title="API Gimnasio - Compatible")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints corregidos
@app.get("/")
def root():
    return {"mensaje": "API funcionando", "status": "activo"}

@app.get("/clases/")
def get_clases(session: Session = Depends(get_session)):
    try:
        # SELECCIONAR SOLO LAS COLUMNAS QUE EXISTEN EN LA BASE DE DATOS
        clases = session.exec(select(Clase)).all()
        return clases
    except Exception as e:
        print(f"Error obteniendo clases: {e}")  # Para debugging
        raise HTTPException(status_code=500, detail=f"Error obteniendo clases: {str(e)}")

@app.get("/socios/")
def get_socios(session: Session = Depends(get_session)):
    try:
        socios = session.exec(select(Socio)).all()
        return socios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo socios: {str(e)}")

@app.get("/reservas/")
def get_reservas(session: Session = Depends(get_session)):
    try:
        reservas = session.exec(select(Reserva)).all()
        return reservas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo reservas: {str(e)}")

# Inicializar datos básicos (solo si no existen)
def inicializar_datos():
    with Session(engine) as session:
        # Verificar si ya hay clases
        try:
            primera_clase = session.exec(select(Clase)).first()
            if primera_clase is not None:
                print(" Clases ya existen, no se inicializan de nuevo")
                return
        except:
            pass  # Si hay error, asumimos que no hay datos
        
        print(" Creando datos iniciales...")
        
        # Crear clases de ejemplo (SIN instructor para evitar el error)
        clases_ejemplo = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", duracion_min=60, capacidad_max=15),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", duracion_min=45, capacidad_max=20),
            Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30", duracion_min=60, capacidad_max=18),
        ]
        
        for clase in clases_ejemplo:
            session.add(clase)
        
        session.commit()
        print(" Clases de ejemplo creadas")

# Iniciar datos al arrancar
@app.on_event("startup")
def startup():
    inicializar_datos()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
