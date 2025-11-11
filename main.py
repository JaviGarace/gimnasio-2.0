# main.py - API FastAPI Completa (LIMPIA Y CORREGIDA)
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime, timedelta
import os
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN DE BASE DE DATOS ===
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./temp.db")
engine = create_engine(DATABASE_URL, echo=True)

# === MODELOS DE DATOS (SIMPLIFICADOS Y CORREGIDOS) ===
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

# === CREAR TABLAS ===
SQLModel.metadata.create_all(engine)

# === DEPENDENCIAS ===
def get_session():
    with Session(engine) as session:
        yield session

# === APLICACIÓN FASTAPI ===
app = FastAPI(
    title="Gimnasio Inteligente API",
    description="Sistema completo de gestión con notificaciones automáticas",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === INICIALIZAR DATOS INICIALES ===
def inicializar_datos_iniciales():
    """Crea datos iniciales cuando la API inicia"""
    logger.info(" Inicializando datos iniciales...")
    
    with Session(engine) as session:
        # Verificar si ya existen datos (chequeo simple)
        try:
            primer_socio = session.exec(select(Socio)).first()
            if primer_socio is not None:
                logger.info(" Datos ya existen, saltando inicialización")
                return
        except:
            pass  # Si hay error en la consulta, asumimos que no hay datos
        
        logger.info(" Creando datos iniciales...")
        
        # Crear planes de membresía
        planes = [
            PlanMembresia(
                nombre="Básico",
                precio=50.00,
                duracion_dias=30,
                descripcion="Acceso a instalaciones básicas en horario estándar"
            ),
            PlanMembresia(
                nombre="Premium", 
                precio=80.00,
                duracion_dias=30,
                descripcion="Acceso ilimitado a todas las clases e instalaciones"
            ),
            PlanMembresia(
                nombre="Familiar",
                precio=120.00,
                duracion_dias=30, 
                descripcion="Para hasta 4 personas - Ahorro familiar"
            )
        ]
        
        for plan in planes:
            session.add(plan)
        
        session.commit()
        
        # Crear socios con diferentes estados de vencimiento
        hoy = datetime.now().date()
        socios = [
            # Socios con membresía vigente
            Socio(id="1001", nombre="Ana García", vencimiento=(hoy + timedelta(days=15)).strftime("%Y-%m-%d")),
            Socio(id="1002", nombre="Carlos López", vencimiento=(hoy + timedelta(days=30)).strftime("%Y-%m-%d")),
            Socio(id="1003", nombre="María Rodríguez", vencimiento=(hoy + timedelta(days=45)).strftime("%Y-%m-%d")),
            Socio(id="1004", nombre="Pedro Martínez", vencimiento=(hoy + timedelta(days=60)).strftime("%Y-%m-%d")),
            
            # Socios con membresía próxima a vencer
            Socio(id="1005", nombre="Laura Hernández", vencimiento=(hoy + timedelta(days=3)).strftime("%Y-%m-%d")),
            Socio(id="1006", nombre="Juan Pérez", vencimiento=(hoy + timedelta(days=2)).strftime("%Y-%m-%d")),
            Socio(id="1007", nombre="Sofía Torres", vencimiento=(hoy + timedelta(days=1)).strftime("%Y-%m-%d")),
            Socio(id="1008", nombre="Diego Sánchez", vencimiento=hoy.strftime("%Y-%m-%d")),
            
            # Socios con membresía vencida
            Socio(id="1009", nombre="Elena Vega", vencimiento=(hoy - timedelta(days=5)).strftime("%Y-%m-%d")),
            Socio(id="1010", nombre="Miguel Ruiz", vencimiento=(hoy - timedelta(days=10)).strftime("%Y-%m-%d")),
        ]
        
        for socio in socios:
            session.add(socio)
        
        # Crear clases
        clases = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", instructor="María Silva", capacidad_max=15),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", instructor="Carlos Ruiz", capacidad_max=20),
            Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30", instructor="Ana Torres", capacidad_max=18),
            Clase(nombre="CrossFit", dia_semana="jueves", hora_inicio="19:00", instructor="Pedro García", capacidad_max=12),
            Clase(nombre="Zumba", dia_semana="viernes", hora_inicio="18:30", instructor="Lucía Fernández", capacidad_max=25),
            Clase(nombre="Pilates", dia_semana="sábado", hora_inicio="10:00", instructor="Elena Martínez", capacidad_max=10),
            Clase(nombre="Boxeo", dia_semana="domingo", hora_inicio="11:00", instructor="José Ramírez", capacidad_max=8)
        ]
        
        for clase in clases:
            session.add(clase)
        
        # Crear algunas entradas de ejemplo
        entradas = [
            Entrada(socio_id="1001", nombre_socio="Ana García", fecha_hora=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            Entrada(socio_id="1002", nombre_socio="Carlos López", fecha_hora=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            Entrada(socio_id="1003", nombre_socio="María Rodríguez", fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        
        for entrada in entradas:
            session.add(entrada)
        
        # Crear algunas reservas de ejemplo
        reservas = [
            Reserva(socio_id="1001", clase_id=1, fecha_reserva=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            Reserva(socio_id="1002", clase_id=2, fecha_reserva=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            Reserva(socio_id="1003", clase_id=3, fecha_reserva=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        
        for reserva in reservas:
            session.add(reserva)
        
        # Crear algunos pagos de ejemplo
        pagos = [
            Pago(socio_id="1001", plan_id=1, monto=50.0, metodo_pago="efectivo", estado="pagado"),
            Pago(socio_id="1002", plan_id=2, monto=80.0, metodo_pago="tarjeta", estado="pagado"),
            Pago(socio_id="1003", plan_id=3, monto=120.0, metodo_pago="transferencia", estado="pagado"),
        ]
        
        for pago in pagos:
            session.add(pago)
        
        session.commit()
        logger.info(" Datos iniciales creados exitosamente")

# Inicializar datos cuando la aplicación arranque
@app.on_event("startup")
def startup_event():
    inicializar_datos_iniciales()

# === ENDPOINTS EXISTENTES - CLASES (CORREGIDO) ===
@app.get("/clases/")
def listar_clases(session: Session = Depends(get_session)):
    """Endpoint corregido para listar clases"""
    try:
        logger.info("Intentando listar clases...")
        clases = session.exec(select(Clase)).all()
        logger.info(f" Encontradas {len(clases)} clases")
        return clases
    except Exception as e:
        logger.error(f" Error al listar clases: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener clases: {str(e)}")

@app.post("/clases/")
def crear_clase(clase: Clase, session: Session = Depends(get_session)):
    """Crear una nueva clase"""
    try:
        session.add(clase)
        session.commit()
        session.refresh(clase)
        return clase
    except Exception as e:
        session.rollback()
        logger.error(f" Error creando clase: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando clase: {str(e)}")

# === ENDPOINTS EXISTENTES - SOCIOS ===
@app.get("/socios/{id_socio}")
def obtener_socio(id_socio: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == id_socio)).first()
    if socio:
        return socio
    raise HTTPException(status_code=404, detail="Socio no encontrado")

@app.get("/socios/")
def listar_socios(session: Session = Depends(get_session)):
    logger.info("Intentando listar socios...")
    try:
        socios = session.exec(select(Socio)).all()
        logger.info(f" Encontrados {len(socios)} socios")
        return socios
    except Exception as e:
        logger.error(f" Error al listar socios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/socios/")
def crear_socio(socio: Socio, session: Session = Depends(get_session)):
    existing = session.exec(select(Socio).where(Socio.id == socio.id)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Socio con este ID ya existe")
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio

# === ENDPOINTS EXISTENTES - ENTRADAS ===
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

@app.get("/entradas/")
def listar_entradas(session: Session = Depends(get_session)):
    return session.exec(select(Entrada)).all()

# === ENDPOINTS EXISTENTES - RESERVAS ===
@app.post("/reservas/")
def crear_reserva(socio_id: str, clase_id: int, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    clase = session.exec(select(Clase).where(Clase.id == clase_id)).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    
    # Verificar si ya existe una reserva para esta clase
    reserva_existente = session.exec(
        select(Reserva).where(
            Reserva.socio_id == socio_id,
            Reserva.clase_id == clase_id,
            Reserva.estado == "confirmada"
        )
    ).first()
    if reserva_existente:
        raise HTTPException(status_code=409, detail="Ya tienes una reserva para esta clase")
    
    # Verificar capacidad
    reservas_clase = session.exec(
        select(Reserva).where(
            Reserva.clase_id == clase_id,
            Reserva.estado == "confirmada"
        )
    ).all()
    if len(reservas_clase) >= clase.capacidad_max:
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

@app.get("/reservas/")
def listar_reservas(session: Session = Depends(get_session)):
    return session.exec(select(Reserva)).all()

@app.delete("/reservas/{reserva_id}")
def cancelar_reserva(reserva_id: int, session: Session = Depends(get_session)):
    reserva = session.exec(select(Reserva).where(Reserva.id == reserva_id)).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.estado = "cancelada"
    session.add(reserva)
    session.commit()
    return {"mensaje": "Reserva cancelada"}

# === ENDPOINTS EXISTENTES - PLANES DE MEMBRESÍA ===
@app.get("/planes/")
def listar_planes(session: Session = Depends(get_session)):
    planes = session.exec(select(PlanMembresia)).all()
    if not planes:
        # Crear planes por defecto si no existen
        planes_ejemplo = [
            PlanMembresia(
                nombre="Básico",
                precio=50.00,
                duracion_dias=30,
                descripcion="Acceso a instalaciones básicas"
            ),
            PlanMembresia(
                nombre="Premium", 
                precio=80.00,
                duracion_dias=30,
                descripcion="Acceso ilimitado a todas las clases"
            ),
            PlanMembresia(
                nombre="Familiar",
                precio=120.00,
                duracion_dias=30, 
                descripcion="Para hasta 4 personas"
            )
        ]
        for plan in planes_ejemplo:
            session.add(plan)
        session.commit()
        planes = session.exec(select(PlanMembresia)).all()
        logger.info(" Planes de membresía creados automáticamente")
    
    return planes

# === ENDPOINTS EXISTENTES - PAGOS ===
@app.post("/pagos/")
def registrar_pago(
    socio_id: str, 
    plan_id: int, 
    metodo_pago: str = "efectivo",
    session: Session = Depends(get_session)
):
    # Verificar que el socio existe
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    # Verificar que el plan existe
    plan = session.exec(select(PlanMembresia).where(PlanMembresia.id == plan_id)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Calcular fechas
    fecha_pago = datetime.now().strftime("%Y-%m-%d")
    fecha_vencimiento = (datetime.now() + timedelta(days=plan.duracion_dias)).strftime("%Y-%m-%d")
    
    # Crear el pago
    nuevo_pago = Pago(
        socio_id=socio_id,
        plan_id=plan_id,
        monto=plan.precio,
        fecha_pago=fecha_pago,
        fecha_vencimiento=fecha_vencimiento,
        metodo_pago=metodo_pago,
        estado="pagado"
    )
    
    # Actualizar vencimiento del socio
    socio.vencimiento = fecha_vencimiento
    
    # Guardar en base de datos
    session.add(nuevo_pago)
    session.add(socio)
    session.commit()
    session.refresh(nuevo_pago)
    
    return {
        "message": " Pago registrado exitosamente",
        "pago": nuevo_pago,
        "socio_actualizado": {
            "nombre": socio.nombre,
            "nuevo_vencimiento": socio.vencimiento
        }
    }

@app.get("/pagos/")
def listar_pagos(session: Session = Depends(get_session)):
    return session.exec(select(Pago)).all()

# === SISTEMA DE NOTIFICACIONES AUTOMÁTICAS ===
@app.get("/notificaciones/vencimientos-proximos")
def obtener_vencimientos_proximos(dias: int = 3, session: Session = Depends(get_session)):
    """Obtiene socios con vencimientos próximos"""
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
                    "estado": "HOY" if dias_restantes == 0 else f"en {dias_restantes} días",
                })
        except Exception as e:
            logger.warning(f"Error procesando socio {socio.id}: {e}")
            continue
    
    return {
        "status": "success",
        "total_vencimientos": len(vencimientos_proximos),
        "vencimientos": vencimientos_proximos,
        "fecha_consulta": hoy.isoformat(),
        "dias_anticipacion": dias
    }

@app.get("/sistema-notificaciones/status")
def status_notificaciones():
    """Estado del sistema de notificaciones"""
    return {
        "sistema": "Notificaciones Automáticas",
        "version": "2.1.0",
        "status": "ACTIVO",
        "endpoints_disponibles": [
            "GET /notificaciones/vencimientos-proximos",
            "POST /notificaciones/enviar-recordatorio"
        ],
        "timestamp": datetime.now().isoformat()
    }

# === ENDPOINT RAÍZ ===
@app.get("/")
def home():
    return {"mensaje": "¡Sistema de Gimnasio con Notificaciones Automáticas!", "status": "activo"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
