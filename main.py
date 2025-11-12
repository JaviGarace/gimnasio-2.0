# main.py - VERSIÓN COMPLETA CON NOTIFICACIONES
from fastapi import FastAPI
import os
from datetime import datetime, timedelta

app = FastAPI()

# === DATOS DE EJEMPLO (temporal) ===
socios_ejemplo = [
    {"id": "1001", "nombre": "Ana García", "vencimiento": "2024-12-31"},
    {"id": "1002", "nombre": "Carlos López", "vencimiento": "2024-01-15"},  # Vencido
    {"id": "1003", "nombre": "María Torres", "vencimiento": "2024-01-20"}   # Próximo a vencer
]

clases_ejemplo = [
    {"nombre": "Yoga", "dia_semana": "Lunes", "hora_inicio": "18:00"},
    {"nombre": "Spinning", "dia_semana": "Martes", "hora_inicio": "19:30"}
]

planes_ejemplo = [
    {"nombre": "Básico", "precio": 50.0},
    {"nombre": "Premium", "precio": 80.0},
    {"nombre": "Familiar", "precio": 120.0}
]

# === ENDPOINTS BÁSICOS ===
@app.get("/")
def home():
    return {"status": "OK", "message": "Servidor funcionando en puerto correcto"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/socios")
def socios():
    return socios_ejemplo

@app.get("/clases")
def clases():
    return clases_ejemplo

@app.get("/planes")
def planes():
    return planes_ejemplo

# === SISTEMA DE NOTIFICACIONES (AGREGAR ESTO) ===
@app.get("/notificaciones/vencimientos-proximos")
def obtener_vencimientos_proximos(dias: int = 3):
    """Obtiene socios con vencimientos próximos para notificar"""
    hoy = datetime.now().date()
    fecha_limite = hoy + timedelta(days=dias)
    
    vencimientos_proximos = []
    for socio in socios_ejemplo:
        try:
            vencimiento = datetime.strptime(socio["vencimiento"], "%Y-%m-%d").date()
            if hoy <= vencimiento <= fecha_limite:
                dias_restantes = (vencimiento - hoy).days
                vencimientos_proximos.append({
                    "socio_id": socio["id"],
                    "nombre": socio["nombre"],
                    "vencimiento": socio["vencimiento"],
                    "dias_restantes": dias_restantes,
                    "estado": "HOY" if dias_restantes == 0 else f"en {dias_restantes} días"
                })
        except Exception as e:
            print(f"Error procesando socio {socio['id']}: {e}")
            continue
    
    return {
        "total_vencimientos": len(vencimientos_proximos),
        "vencimientos": vencimientos_proximos,
        "fecha_consulta": hoy.isoformat(),
        "dias_anticipacion": dias
    }

@app.get("/notificaciones/socios-morosos")
def obtener_socios_morosos():
    """Obtiene socios con membresía vencida"""
    hoy = datetime.now().date()
    
    socios_morosos = []
    for socio in socios_ejemplo:
        try:
            vencimiento = datetime.strptime(socio["vencimiento"], "%Y-%m-%d").date()
            if vencimiento < hoy:
                dias_vencido = (hoy - vencimiento).days
                socios_morosos.append({
                    "socio_id": socio["id"],
                    "nombre": socio["nombre"],
                    "vencimiento": socio["vencimiento"],
                    "dias_vencido": dias_vencido,
                    "estado": f"Vencida hace {dias_vencido} días"
                })
        except Exception as e:
            print(f"Error procesando socio {socio['id']}: {e}")
            continue
    
    return {
        "total_morosos": len(socios_morosos),
        "socios_morosos": socios_morosos,
        "fecha_consulta": hoy.isoformat()
    }

@app.post("/notificaciones/enviar-recordatorio")
def enviar_recordatorio_vencimiento(socio_id: str):
    """Envía recordatorio de vencimiento a un socio específico"""
    socio_encontrado = None
    for socio in socios_ejemplo:
        if socio["id"] == socio_id:
            socio_encontrado = socio
            break
    
    if not socio_encontrado:
        return {"error": "Socio no encontrado"}
    
    try:
        vencimiento = datetime.strptime(socio_encontrado["vencimiento"], "%Y-%m-%d").date()
        hoy = datetime.now().date()
        dias_restantes = (vencimiento - hoy).days
        
        if dias_restantes < 0:
            mensaje = f" Hola {socio_encontrado['nombre']}, tu membresía está VENCIDA desde hace {-dias_restantes} días. Por favor, renueva tu plan."
        elif dias_restantes == 0:
            mensaje = f" Hola {socio_encontrado['nombre']}, tu membresía VENCE HOY. ¡No te quedes sin acceso!"
        else:
            mensaje = f" Hola {socio_encontrado['nombre']}, tu membresía vence en {dias_restantes} días ({socio_encontrado['vencimiento']}). ¡Renueva a tiempo!"
        
        # Simular envío de WhatsApp
        resultado = {
            "status": "simulado",
            "numero": "+1234567890",
            "mensaje": mensaje,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "message": "Recordatorio enviado exitosamente",
            "socio": socio_encontrado["nombre"],
            "vencimiento": socio_encontrado["vencimiento"],
            "dias_restantes": dias_restantes,
            "mensaje_enviado": mensaje,
            "whatsapp_result": resultado
        }
        
    except Exception as e:
        return {"error": f"Error al enviar recordatorio: {str(e)}"}

# Debug para notificaciones
@app.get("/debug-notificaciones")
def debug_notificaciones():
    """Muestra todos los endpoints de notificaciones registrados"""
    notificaciones_routes = []
    for route in app.routes:
        route_path = getattr(route, "path", "")
        if "notificaciones" in route_path:
            notificaciones_routes.append({
                "path": route_path,
                "methods": getattr(route, "methods", "N/A")
            })
    
    return {
        "status": " Endpoints de notificaciones registrados",
        "total_endpoints": len(notificaciones_routes),
        "endpoints": notificaciones_routes
    }

# CORRECCIÓN CRÍTICA: Usar el puerto de Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render usa 10000
    uvicorn.run(app, host="0.0.0.0", port=port)
