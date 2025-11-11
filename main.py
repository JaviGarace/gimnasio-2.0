# main.py - API FastAPI Completa con Notificaciones y Datos Iniciales (CORREGIDA)
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime, timedelta
import os
import uvicorn
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN DE BASE DE DATOS ===
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./temp.db")
engine = create_engine(DATABASE_URL, echo=True)

# === MODELOS DE DATOS CORREGIDOS ===
class Socio(SQLModel, table=True):
    id: str = Field(primary_key=True)
    nombre: str
    vencimiento: str
    # REMOVER email y telefono por ahora para evitar el error
    # email: Optional[str] = None
    # telefono: Optional[str] = None

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
        # Verificar si ya existen datos
        if session.exec(select(Socio)).first() is not None:
            logger.info(" Datos ya existen, saltando inicialización")
            return
        
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

# === FUNCIONES AUXILIARES ===
def procesar_mensaje(mensaje: str, session: Session):
    texto = mensaje.lower().strip()
    respuesta = ""

    # Extraer ID
    id_socio = None
    for palabra in texto.split():
        if palabra.isdigit() and len(palabra) >= 4:
            id_socio = palabra[:4]
            break

    if any(p in texto for p in ["clase", "spinning", "yoga", "funcional", "horario"]):
        respuesta = "Hoy: Yoga 18h, Spinning 19:30, Funcional 20:30."
    elif any(p in texto for p in ["vencimiento", "caduca", "vence", "abono", "membresía"]):
        if id_socio:
            socio = session.exec(select(Socio).where(Socio.id == id_socio)).first()
            if socio:
                nombre, vencimiento = socio.nombre, socio.vencimiento
                venc = datetime.strptime(vencimiento, "%Y-%m-%d")
                hoy = datetime.today()
                dias = (venc - hoy).days
                if dias < 0:
                    respuesta = f"{nombre}, tu membresía está vencida."
                elif dias <= 3:
                    respuesta = f"Vence en {dias} días, {nombre}."
                else:
                    respuesta = f"Válida hasta {vencimiento}, {nombre}."
            else:
                respuesta = "ID no encontrado."
        else:
            respuesta = "Ej: vencimiento 1001"
    elif any(p in texto for p in ["entrada", "registr", "apunt", "llegar"]):
        if id_socio:
            socio = session.exec(select(Socio).where(Socio.id == id_socio)).first()
            if socio:
                nombre = socio.nombre
                ahora = datetime.now().strftime("%H:%M")
                respuesta = f"¡Bienvenido, {nombre}! Entrada registrada a las {ahora}."
            else:
                respuesta = "ID no válido."
        else:
            respuesta = "Ej: entrada 1005"
    else:
        respuesta = "No entendí. Usa: vencimiento 1001, entrada 1005 o clases"
    
    return respuesta

# === ENDPOINTS BÁSICOS ===
@app.get("/")
def home():
    return {"mensaje": "¡Sistema de Gimnasio con Notificaciones Automáticas!"}

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
        return {"message": " Todas las tablas creadas exitosamente", "tablas": list(SQLModel.metadata.tables.keys())}
    except Exception as e:
        return {"error": f" Error creando tablas: {str(e)}"}

# === SISTEMA DE NOTIFICACIONES AUTOMÁTICAS ===
@app.get("/notificaciones/vencimientos-proximos")
def obtener_vencimientos_proximos(dias: int = 3, session: Session = Depends(get_session)):
    """Obtiene socios con vencimientos próximos para notificar"""
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
                    # REMOVER email y telefono por ahora
                    # "email": socio.email,
                    # "telefono": socio.telefono
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

@app.get("/notificaciones/socios-morosos")
def obtener_socios_morosos(session: Session = Depends(get_session)):
    """Obtiene socios con membresía vencida"""
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
                    "estado": f"Vencida hace {dias_vencido} días",
                    # REMOVER email y telefono por ahora
                    # "email": socio.email,
                    # "telefono": socio.telefono
                })
        except Exception as e:
            logger.warning(f"Error procesando socio {socio.id}: {e}")
            continue
    
    return {
        "status": "success",
        "total_morosos": len(socios_morosos),
        "socios_morosos": socios_morosos,
        "fecha_consulta": hoy.isoformat()
    }

@app.post("/notificaciones/enviar-recordatorio")
def enviar_recordatorio_vencimiento(socio_id: str, session: Session = Depends(get_session)):
    """Envía recordatorio de vencimiento a un socio específico"""
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    try:
        vencimiento = datetime.strptime(socio.vencimiento, "%Y-%m-%d").date()
        hoy = datetime.now().date()
        dias_restantes = (vencimiento - hoy).days
        
        if dias_restantes < 0:
            mensaje = f" Hola {socio.nombre}, tu membresía está VENCIDA desde hace {-dias_restantes} días. Por favor, renueva tu plan."
            tipo = "MOROSO"
        elif dias_restantes == 0:
            mensaje = f" Hola {socio.nombre}, tu membresía VENCE HOY. ¡No te quedes sin acceso!"
            tipo = "VENCE_HOY"
        else:
            mensaje = f" Hola {socio.nombre}, tu membresía vence en {dias_restantes} días ({socio.vencimiento}). ¡Renueva a tiempo!"
            tipo = "RECORDATORIO"
        
        # Simular envío de notificación (en producción integrar con Twilio/Email)
        resultado_notificacion = {
            "estado": "enviado",
            "tipo": tipo,
            "mensaje": mensaje,
            "canal": "whatsapp_simulado",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Notificación enviada exitosamente",
            "socio": {
                "id": socio.id,
                "nombre": socio.nombre,
                "vencimiento": socio.vencimiento,
                "dias_restantes": dias_restantes
            },
            "notificacion": resultado_notificacion
        }
        
    except Exception as e:
        logger.error(f"Error enviando recordatorio: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar recordatorio: {str(e)}")

# === DATOS DE PRUEBA ===
@app.post("/datos-prueba/notificaciones")
def crear_datos_prueba_notificaciones(session: Session = Depends(get_session)):
    """Crea datos de prueba completos para el sistema de notificaciones"""
    try:
        # LIMPIAR DATOS EN ORDEN CORRECTO (para evitar Foreign Key violations)
        session.exec(select(Entrada).delete())
        session.exec(select(Reserva).delete())
        session.exec(select(Pago).delete())
        session.exec(select(Socio).delete())
        session.exec(select(Clase).delete())
        session.exec(select(PlanMembresia).delete())
        
        session.commit()
        
        # Crear planes de membresía
        planes = [
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
        
        for plan in planes:
            session.add(plan)
        
        session.commit()
        
        # Crear socios con diferentes estados de vencimiento
        hoy = datetime.now().date()
        socios = [
            # Vencen pronto
            Socio(id="1001", nombre="Ana García", vencimiento=(hoy + timedelta(days=2)).strftime("%Y-%m-%d")),
            Socio(id="1002", nombre="Carlos López", vencimiento=(hoy + timedelta(days=1)).strftime("%Y-%m-%d")),
            # Morosos
            Socio(id="1003", nombre="María Rodríguez", vencimiento=(hoy - timedelta(days=5)).strftime("%Y-%m-%d")),
            Socio(id="1004", nombre="Pedro Martínez", vencimiento=(hoy - timedelta(days=15)).strftime("%Y-%m-%d")),
            # Al día
            Socio(id="1005", nombre="Laura Hernández", vencimiento=(hoy + timedelta(days=30)).strftime("%Y-%m-%d")),
            # Vence hoy
            Socio(id="1006", nombre="Juan Pérez", vencimiento=hoy.strftime("%Y-%m-%d")),
        ]
        
        for socio in socios:
            session.add(socio)
        
        # Crear clases
        clases = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", instructor="María Silva"),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", instructor="Carlos Ruiz"),
            Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30", instructor="Ana Torres"),
        ]
        
        for clase in clases:
            session.add(clase)
        
        session.commit()
        
        return {
            "status": "success",
            "message": " Datos de prueba creados exitosamente",
            "resumen": {
                "planes": len(planes),
                "socios": len(socios),
                "clases": len(clases),
                "estados_socios": {
                    "vencen_pronto": 3,  # 1001, 1002, 1006
                    "morosos": 2,        # 1003, 1004
                    "al_dia": 1          # 1005
                }
            }
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creando datos de prueba: {e}")
        return {"status": "error", "message": f"Error creando datos: {str(e)}"}

# === ENDPOINT DE VERIFICACIÓN ===
@app.get("/sistema-notificaciones/status")
def status_notificaciones():
    """Estado completo del sistema de notificaciones"""
    return {
        "sistema": "Notificaciones Automáticas",
        "version": "2.1.0",
        "status": "ACTIVO",
        "endpoints_principales": [
            "GET /notificaciones/vencimientos-proximos",
            "GET /notificaciones/socios-morosos", 
            "POST /notificaciones/enviar-recordatorio?socio_id=1001",
        ],
        "caracteristicas": [
            "Recordatorios de vencimiento",
            "Detección de morosidad", 
            "Integración WhatsApp simulada",
            "Gestión de contactos"
        ],
        "timestamp": datetime.now().isoformat()
    }

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
        logger.info(f"Encontrados {len(socios)} socios")
        return socios
    except Exception as e:
        logger.error(f"Error al listar socios: {e}")
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

# === ENDPOINTS EXISTENTES - CLASES ===
@app.get("/clases/")
def listar_clases(session: Session = Depends(get_session)):
    # Inicialización perezosa: crea clases si no existen
    if session.exec(select(Clase)).first() is None:
        clases_ejemplo = [
            Clase(nombre="Yoga", dia_semana="lunes", hora_inicio="18:00", instructor="María Silva"),
            Clase(nombre="Spinning", dia_semana="martes", hora_inicio="19:30", instructor="Carlos Ruiz"),
            Clase(nombre="Funcional", dia_semana="miércoles", hora_inicio="20:30", instructor="Ana Torres"),
        ]
        for clase in clases_ejemplo:
            session.add(clase)
        session.commit()
    return session.exec(select(Clase)).all()

# === ENDPOINTS EXISTENTES - RESERVAS ===
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
    # Verificar si ya existen planes, si no, crearlos
    planes_existentes = session.exec(select(PlanMembresia)).first()
    
    if not planes_existentes:
        # Crear planes de ejemplo
        planes_ejemplo = [
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
        
        for plan in planes_ejemplo:
            session.add(plan)
        session.commit()
        print(" Planes de membresía creados automáticamente")
    
    # Devolver todos los planes
    planes = session.exec(select(PlanMembresia)).all()
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
    from datetime import datetime, timedelta
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

@app.get("/pagos/socio/{socio_id}")
def obtener_pagos_socio(socio_id: str, session: Session = Depends(get_session)):
    pagos = session.exec(select(Pago).where(Pago.socio_id == socio_id)).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos para este socio")
    return pagos

@app.get("/estado-cuenta/{socio_id}")
def obtener_estado_cuenta(socio_id: str, session: Session = Depends(get_session)):
    socio = session.exec(select(Socio).where(Socio.id == socio_id)).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    pagos = session.exec(select(Pago).where(Pago.socio_id == socio_id)).all()
    
    return {
        "socio": socio,
        "pagos": pagos,
        "total_gastado": sum(pago.monto for pago in pagos),
        "pagos_totales": len(pagos)
    }

# === ENDPOINTS EXISTENTES - REPORTES (VERSIÓN MEJORADA) ===
@app.get("/reportes/ingresos-mensuales")
def reporte_ingresos_mensuales(
    año: int = None, 
    session: Session = Depends(get_session)
):
    """Reporte de ingresos mensuales con comparativa - VERSIÓN MEJORADA"""
    try:
        if año is None:
            año = datetime.now().year
        
        # Obtener pagos del año especificado
        pagos = session.exec(select(Pago).where(Pago.estado == "pagado")).all()
        
        if not pagos:
            return {"message": "No hay datos de pagos para generar el reporte"}
        
        # Procesamiento manual sin pandas
        ingresos_por_mes = {mes: 0 for mes in range(1, 13)}
        ingresos_anterior = {mes: 0 for mes in range(1, 13)}
        planes_count = {}
        
        for pago in pagos:
            try:
                fecha = datetime.strptime(pago.fecha_pago, "%Y-%m-%d")
                mes = fecha.month
                año_pago = fecha.year
                
                if año_pago == año:
                    ingresos_por_mes[mes] += pago.monto
                    planes_count[pago.plan_id] = planes_count.get(pago.plan_id, 0) + 1
                elif año_pago == año - 1:
                    ingresos_anterior[mes] += pago.monto
            except:
                continue
        
        # Filtrar meses con datos
        ingresos_por_mes = {k: v for k, v in ingresos_por_mes.items() if v > 0}
        ingresos_anterior = {k: v for k, v in ingresos_anterior.items() if v > 0}
        
        # Top planes
        planes_populares = dict(sorted(planes_count.items(), key=lambda x: x[1], reverse=True)[:5])
        
        total_ingresos = sum(ingresos_por_mes.values())
        total_pagos = sum(planes_count.values())
        
        return {
            "año_actual": año,
            "ingresos_totales": total_ingresos,
            "ingresos_mensuales": ingresos_por_mes,
            "comparativa_año_anterior": ingresos_anterior,
            "planes_populares": planes_populares,
            "total_pagos": total_pagos,
            "promedio_pago": total_ingresos / total_pagos if total_pagos > 0 else 0
        }
    except Exception as e:
        return {"error": f"Error generando reporte: {str(e)}"}

@app.get("/reportes/asistencia-horarios")
def reporte_asistencia_horarios(
    mes: int = None,
    año: int = None,
    session: Session = Depends(get_session)
):
    """Reporte de análisis de asistencia por horarios - VERSIÓN MEJORADA"""
    try:
        if mes is None:
            mes = datetime.now().month
        if año is None:
            año = datetime.now().year
        
        # Obtener entradas
        entradas = session.exec(select(Entrada)).all()
        
        if not entradas:
            return {"message": "No hay datos de entradas para generar el reporte"}
        
        # Procesamiento manual
        asistencia_por_hora = {}
        asistencia_por_dia = {}
        socios_count = {}
        
        for entrada in entradas:
            try:
                fecha_hora = datetime.strptime(entrada.fecha_hora, "%Y-%m-%d %H:%M:%S")
                if fecha_hora.month == mes and fecha_hora.year == año:
                    hora = fecha_hora.hour
                    dia_semana = fecha_hora.strftime("%A")  # Monday, Tuesday, etc.
                    
                    # Conteo por hora
                    asistencia_por_hora[hora] = asistencia_por_hora.get(hora, 0) + 1
                    
                    # Conteo por día
                    asistencia_por_dia[dia_semana] = asistencia_por_dia.get(dia_semana, 0) + 1
                    
                    # Conteo por socio
                    socios_count[entrada.nombre_socio] = socios_count.get(entrada.nombre_socio, 0) + 1
            except:
                continue
        
        # Top 10 socios más activos
        socios_activos = dict(sorted(socios_count.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Encontrar hora pico y día más activo
        hora_pico = max(asistencia_por_hora, key=asistencia_por_hora.get) if asistencia_por_hora else None
        dia_mas_activo = max(asistencia_por_dia, key=asistencia_por_dia.get) if asistencia_por_dia else None
        
        total_entradas = sum(asistencia_por_hora.values())
        
        return {
            "mes": mes,
            "año": año,
            "total_entradas": total_entradas,
            "asistencia_por_hora": asistencia_por_hora,
            "asistencia_por_dia": asistencia_por_dia,
            "socios_mas_activos": socios_activos,
            "hora_pico": hora_pico,
            "dia_mas_activo": dia_mas_activo
        }
    except Exception as e:
        return {"error": f"Error generando reporte: {str(e)}"}

@app.get("/reportes/popularidad-instructores")
def reporte_popularidad_instructores(session: Session = Depends(get_session)):
    """Reporte de popularidad de instructores - VERSIÓN MEJORADA"""
    try:
        # Obtener reservas confirmadas
        reservas = session.exec(select(Reserva).where(Reserva.estado == "confirmada")).all()
        
        if not reservas:
            return {"message": "No hay datos de reservas para generar el reporte"}
        
        # Procesamiento manual
        instructores_count = {}
        clases_count = {}
        horarios_count = {}
        
        for reserva in reservas:
            try:
                clase = session.exec(select(Clase).where(Clase.id == reserva.clase_id)).first()
                if clase:
                    # Popularidad por instructor
                    instructores_count[clase.instructor] = instructores_count.get(clase.instructor, 0) + 1
                    
                    # Popularidad por clase
                    clases_count[clase.nombre] = clases_count.get(clase.nombre, 0) + 1
                    
                    # Popularidad por horario
                    horarios_count[clase.hora_inicio] = horarios_count.get(clase.hora_inicio, 0) + 1
            except:
                continue
        
        # Top 5 de cada categoría
        instructores_populares = dict(sorted(instructores_count.items(), key=lambda x: x[1], reverse=True))
        clases_populares = dict(sorted(clases_count.items(), key=lambda x: x[1], reverse=True)[:5])
        horarios_populares = dict(sorted(horarios_count.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return {
            "popularidad_instructores": instructores_populares,
            "clases_populares": clases_populares,
            "horarios_populares": horarios_populares,
            "total_reservas_analizadas": len(reservas)
        }
    except Exception as e:
        return {"error": f"Error generando reporte: {str(e)}"}

@app.get("/debug-reportes")
def debug_reportes():
    """Debug específico para endpoints de reportes"""
    reportes_routes = []
    for route in app.routes:
        if "reportes" in getattr(route, "path", ""):
            reportes_routes.append({
                "path": getattr(route, "path", "N/A"),
                "methods": getattr(route, "methods", "N/A")
            })
    
    return {
        "total_reportes_routes": len(reportes_routes),
        "reportes_routes": reportes_routes,
        "status": " Endpoints de reportes registrados" if reportes_routes else " No hay endpoints de reportes"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
