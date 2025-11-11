# crear_datos_simulados.py
import requests
import json
import time
from datetime import datetime, timedelta

print(" Creando datos simulados para todos los escenarios...")

# URL base de tu API
BASE_URL = "https://gimnasio-2-0-1.onrender.com"

# 1. Crear planes de membresía
print(" Creando planes de membresía...")
planes = [
    {"nombre": "Básico", "precio": 50.0, "duracion_dias": 30, "descripcion": "Acceso a instalaciones básicas en horario estándar"},
    {"nombre": "Premium", "precio": 80.0, "duracion_dias": 30, "descripcion": "Acceso ilimitado a todas las clases e instalaciones"},
    {"nombre": "Familiar", "precio": 120.0, "duracion_dias": 30, "descripcion": "Para hasta 4 personas - Ahorro familiar"}
]

for plan in planes:
    try:
        response = requests.post(f"{BASE_URL}/planes/", json=plan)
        print(f"   - {plan['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con {plan['nombre']}: {e}")

time.sleep(1)  # Esperar un poco

# 2. Crear socios (4 ejemplos de cada escenario)
print(" Creando socios...")
socios = [
    # Socios con membresía vigente
    {"id": "1001", "nombre": "Ana García", "vencimiento": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")},
    {"id": "1002", "nombre": "Carlos López", "vencimiento": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")},
    {"id": "1003", "nombre": "María Rodríguez", "vencimiento": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")},
    {"id": "1004", "nombre": "Pedro Martínez", "vencimiento": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")},
    
    # Socios con membresía próxima a vencer
    {"id": "1005", "nombre": "Laura Hernández", "vencimiento": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")},
    {"id": "1006", "nombre": "Juan Pérez", "vencimiento": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")},
    {"id": "1007", "nombre": "Sofía Torres", "vencimiento": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
    {"id": "1008", "nombre": "Diego Sánchez", "vencimiento": (datetime.now()).strftime("%Y-%m-%d")},
    
    # Socios con membresía vencida
    {"id": "1009", "nombre": "Elena Vega", "vencimiento": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")},
    {"id": "1010", "nombre": "Miguel Ruiz", "vencimiento": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")},
    {"id": "1011", "nombre": "Carmen Díaz", "vencimiento": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")},
    {"id": "1012", "nombre": "Roberto Jiménez", "vencimiento": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")},
    
    # Socios inactivos
    {"id": "1013", "nombre": "Isabel Morales", "vencimiento": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")},
    {"id": "1014", "nombre": "Francisco Gómez", "vencimiento": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")},
    {"id": "1015", "nombre": "Patricia López", "vencimiento": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")},
    {"id": "1016", "nombre": "Alberto Castro", "vencimiento": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")}
]

for socio in socios:
    try:
        response = requests.post(f"{BASE_URL}/socios/", json=socio)
        print(f"   - {socio['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con {socio['nombre']}: {e}")

time.sleep(1)  # Esperar un poco

# 3. Crear clases
print(" Creando clases...")
clases = [
    {"nombre": "Yoga", "dia_semana": "lunes", "hora_inicio": "18:00", "instructor": "María Silva", "capacidad_max": 15},
    {"nombre": "Spinning", "dia_semana": "martes", "hora_inicio": "19:30", "instructor": "Carlos Ruiz", "capacidad_max": 20},
    {"nombre": "Funcional", "dia_semana": "miércoles", "hora_inicio": "20:30", "instructor": "Ana Torres", "capacidad_max": 18},
    {"nombre": "CrossFit", "dia_semana": "jueves", "hora_inicio": "19:00", "instructor": "Pedro García", "capacidad_max": 12},
    {"nombre": "Zumba", "dia_semana": "viernes", "hora_inicio": "18:30", "instructor": "Lucía Fernández", "capacidad_max": 25},
    {"nombre": "Pilates", "dia_semana": "sábado", "hora_inicio": "10:00", "instructor": "Elena Martínez", "capacidad_max": 10},
    {"nombre": "Boxeo", "dia_semana": "domingo", "hora_inicio": "11:00", "instructor": "José Ramírez", "capacidad_max": 8}
]

for clase in clases:
    try:
        response = requests.post(f"{BASE_URL}/clases/", json=clase)
        print(f"   - {clase['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con {clase['nombre']}: {e}")

time.sleep(1)  # Esperar un poco

# 4. Crear entradas (últimos 7 días)
print(" Creando entradas...")
fechas_entrada = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(7)]
socios_para_entradas = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
nombres_socios = ["Ana García", "Carlos López", "María Rodríguez", "Pedro Martínez", "Laura Hernández", "Juan Pérez", "Sofía Torres", "Diego Sánchez", "Elena Vega", "Miguel Ruiz"]

for i in range(50):  # 50 entradas aleatorias
    socio_idx = i % len(socios_para_entradas)
    fecha_idx = i % len(fechas_entrada)
    socio_id = socios_para_entradas[socio_idx]
    nombre_socio = nombres_socios[socio_idx]
    fecha_entrada = (datetime.now() - timedelta(days=i%7)).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.post(f"{BASE_URL}/entradas/?socio_id={socio_id}")
        print(f"   - Entrada {i+1}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con entrada {i+1}: {e}")

time.sleep(1)  # Esperar un poco

# 5. Crear reservas
print(" Creando reservas...")
clases_ids = [1, 2, 3, 4, 5, 6, 7]
socios_para_reservas = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]

for i in range(30):  # 30 reservas
    socio_id = socios_para_reservas[i % len(socios_para_reservas)]
    clase_id = clases_ids[i % len(clases_ids)]
    try:
        response = requests.post(f"{BASE_URL}/reservas/?socio_id={socio_id}&clase_id={clase_id}")
        print(f"   - Reserva {i+1}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con reserva {i+1}: {e}")

time.sleep(1)  # Esperar un poco

# 6. Crear pagos
print(" Creando pagos...")
planes_ids = [1, 2, 3]  # Básico, Premium, Familiar
metodos_pago = ["efectivo", "tarjeta", "transferencia"]

for i in range(20):  # 20 pagos
    socio_id = socios_para_reservas[i % len(socios_para_reservas)]
    plan_id = planes_ids[i % len(planes_ids)]
    metodo_pago = metodos_pago[i % len(metodos_pago)]
    try:
        response = requests.post(f"{BASE_URL}/pagos/?socio_id={socio_id}&plan_id={plan_id}&metodo_pago={metodo_pago}")
        print(f"   - Pago {i+1}: {response.status_code}")
    except Exception as e:
        print(f"   - Error con pago {i+1}: {e}")

print("\n ¡Datos simulados creados exitosamente!")
print(" Refresca tu dashboard Streamlit para ver todos los datos")
print(" Ya puedes probar todas las funcionalidades: Socios, Pagos, Clases, Entradas, Reservas, Reportes y Notificaciones")
