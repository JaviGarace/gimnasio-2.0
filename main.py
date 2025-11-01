# main.py - FastAPI + SQLModel + PostgreSQL
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
import os

# Configuración de la base de datos
DATABASE_URL = "postgresql://gimnasio:seguro123@localhost:5432/gimnasio_dev"
engine = create_engine(DATABASE_URL, echo=True)

# Modelos de datos
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
    duracion_min: int = 60
    capacidad_max: int = 20

class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    socio_id: str = Field(foreign_key="socio.id")
    clase_id: int = Field(foreign_key="clase.id")
    fecha_reserva: str
    estado: str = "confirmada"

# Funciones auxiliares
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Crear la aplicación FastAPI
app = FastAPI(
    title="Gimnasio Inteligente API",
    description="API para gestión de socios, entradas y clases",
    version="2.0.0"
)

# Eventos de inicio
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        if session.exec(select(Clase)).first() is None:
            clases_ejemplo = [
                Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00"),
                Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30"),
                Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30"),
            ]
            for clase in clases_ejemplo:
                session.add(clase)
            session.commit()

# Endpoints
@app.get("/")
def home():
    return {"mensaje": "¡Bienvenido al Gimnasio Inteligente!"}

@app.get("/socios/{id_socio}")
def obtener_socio(id_socio: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == id_socio)).first()
    if socio:
        return socio
    raise HTTPException(status_code=404, detail="Socio no encontrado")

@app.post("/socios/")
def crear_socio(socio: Socio, session: Session = Depends(get_session)):
    existing = session.exec(select(Socio).where(Socio.id == socio.id)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Socio con este ID ya existe")
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio

@app.post("/entradas/")
def registrar_entrada(socio_id: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = Entrada(
        socio_id=socio_id,
        nombre_socio=socio.nombre,
        fecha_hora=ahora
    )
    session.add(entrada)
    session.commit()
    session.refresh(entrada)
    return entrada

@app.get("/clases/")
def listar_clases(session: Session = Depends(get_session)):
    return session.exec(select(Clase)).all()

@app.post("/reservas/")
def crear_reserva(socio_id: str, clase_id: int, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    clase = session.exec(select(Clase).where(Clase.id == clase_id)).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    reserva_existente = session.exec(
        select(Reserva).where(
            Reserva.socio_id == socio_id,
            Reserva.clase_id == clase_id,
            Reserva.estado == "confirmada"
        )
    ).first()
    if reserva_existente:
        raise HTTPException(status_code=409, detail="Ya tienes una reserva para esta clase")
    reservas_actuales = session.exec(
        select(Reserva).where(
            Reserva.clase_id == clase_id,
            Reserva.estado == "confirmada"
        )
    ).all()
    if len(reservas_actuales) >= clase.capacidad_max:
        raise HTTPException(status_code=409, detail="Clase llena")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reserva = Reserva(
        socio_id=socio_id,
        clase_id=clase_id,
        fecha_reserva=ahora
    )
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    return reserva

@app.delete("/reservas/{reserva_id}")
def cancelar_reserva(reserva_id: int, session: Session = Depends(get_session)):
    reserva = session.exec(select(Reserva).where(Reserva.id == reserva_id)).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.estado = "cancelada"
    session.add(reserva)
    session.commit()
    return {"mensaje": "Reserva cancelada"}