# notificaciones.py - Sistema de Notificaciones Automáticas (SEGURA)
import requests
import pandas as pd
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from typing import List, Dict, Any

class SistemaNotificaciones:
    def __init__(self, api_url: str = "https://gimnasio-2-0-1.onrender.com"):
        self.api_url = api_url
        # Configurar Twilio con variables de entorno (más seguro)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("⚠️ ADVERTENCIA: Variables de entorno de Twilio no configuradas")
            print("   Configura TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN en Render")
            # Usar valores simulados para pruebas si no están configuradas
            account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Placeholder
            auth_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"    # Placeholder

        self.twilio_client = Client(account_sid, auth_token)
        self.whatsapp_from = "whatsapp:+14155238886"  # Número de Twilio Sandbox
    
    def obtener_socios_vencimiento_proximo(self, dias: int = 3) -> List[Dict[str, Any]]:
        """Obtiene socios con membresía que vence en X días"""
        try:
            response = requests.get(f"{self.api_url}/notificaciones/vencimientos-proximos?dias={dias}")
            if response.status_code == 200:
                data = response.json()
                return data.get("vencimientos", [])
            return []
        except Exception as e:
            print(f"Error obteniendo socios: {e}")
            return []
    
    def enviar_notificacion_whatsapp(self, telefono: str, mensaje: str) -> bool:
        """Envía una notificación por WhatsApp"""
        try:
            message = self.twilio_client.messages.create(
                body=mensaje,
                from_=self.whatsapp_from,
                to=f"whatsapp:{telefono}"
            )
            print(f"Notificación enviada a {telefono}: {mensaje}")
            return True
        except Exception as e:
            print(f"Error enviando notificación a {telefono}: {e}")
            return False
    
    def generar_mensaje_vencimiento(self, socio: Dict[str, Any]) -> str:
        """Genera el mensaje personalizado según días restantes"""
        nombre = socio["nombre"]
        dias_restantes = socio["dias_restantes"]
        
        if dias_restantes == 0:
            return f"🔔 Hola {nombre}, tu membresía VENCE HOY. ¡No te quedes sin acceso!"
        elif dias_restantes == 1:
            return f"🔔 Hola {nombre}, tu membresía vence mañana. ¡Renueva a tiempo!"
        elif dias_restantes <= 3:
            return f"🔔 Hola {nombre}, tu membresía vence en {dias_restantes} días ({socio['vencimiento']}). ¡Renueva a tiempo!"
        else:
            return f"🔔 Hola {nombre}, tu membresía vence en {dias_restantes} días ({socio['vencimiento']}). ¡Aprovecha!"
    
    def enviar_recordatorios_vencimiento(self, dias: int = 3) -> Dict[str, Any]:
        """Envía recordatorios de vencimiento a todos los socios afectados"""
        socios = self.obtener_socios_vencimiento_proximo(dias)
        
        resultados = {
            "enviados": 0,
            "fallidos": 0,
            "total_procesados": len(socios),
            "detalles": []
        }
        
        for socio in socios:
            # En tu sistema actual, asumiremos que el teléfono está en el campo 'telefono'
            # Si no está en la API, podrías extender el modelo Socio para incluirlo
            telefono = socio.get("telefono", "+1234567890")  # Valor por defecto para pruebas
            
            mensaje = self.generar_mensaje_vencimiento(socio)
            
            if self.enviar_notificacion_whatsapp(telefono, mensaje):
                resultados["enviados"] += 1
            else:
                resultados["fallidos"] += 1
            
            resultados["detalles"].append({
                "socio_id": socio["socio_id"],
                "nombre": socio["nombre"],
                "telefono": telefono,
                "mensaje": mensaje,
                "estado": "enviado" if self.enviar_notificacion_whatsapp(telefono, mensaje) else "fallido"
            })
        
        return resultados
    
    def enviar_notificacion_individual(self, socio_id: str) -> Dict[str, Any]:
        """Envía una notificación individual a un socio específico"""
        try:
            # Usar el endpoint existente de tu API
            response = requests.post(
                f"{self.api_url}/notificaciones/enviar-recordatorio?socio_id={socio_id}"
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

# Función principal para ejecutar notificaciones
def ejecutar_notificaciones():
    """Función para ejecutar notificaciones programadas"""
    sistema = SistemaNotificaciones()
    
    print("🚀 Iniciando sistema de notificaciones automáticas...")
    
    # Enviar recordatorios de vencimiento (3 días antes)
    print("📧 Enviando recordatorios de vencimiento...")
    resultado_vencimientos = sistema.enviar_recordatorios_vencimiento(dias=3)
    
    print(f"✅ Enviados: {resultado_vencimientos['enviados']}")
    print(f"❌ Fallidos: {resultado_vencimientos['fallidos']}")
    print(f"📊 Total procesados: {resultado_vencimientos['total_procesados']}")
    
    return resultado_vencimientos

if __name__ == "__main__":
    # Ejecutar notificaciones manualmente
    resultados = ejecutar_notificaciones()
    print("✅ Sistema de notificaciones completado")
