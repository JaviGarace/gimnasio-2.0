# crear_datos_manual.py
import requests
import json

BASE_URL = "https://gimnasio-2-0-1.onrender.com"

print(" Creando datos manualmente...")

# Crear planes de membresía
planes = [
    {"nombre": "Básico", "precio": 50.0, "duracion_dias": 30, "descripcion": "Acceso a instalaciones básicas en horario estándar"},
    {"nombre": "Premium", "precio": 80.0, "duracion_dias": 30, "descripcion": "Acceso ilimitado a todas las clases e instalaciones"},
    {"nombre": "Familiar", "precio": 120.0, "duracion_dias": 30, "descripcion": "Para hasta 4 personas - Ahorro familiar"}
]

for plan in planes:
    try:
        response = requests.post(f"{BASE_URL}/planes/", json=plan)
        print(f"Plan {plan['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"Error con plan {plan['nombre']}: {e}")

# Crear socios
socios = [
    {"id": "1001", "nombre": "Ana García", "vencimiento": "2025-12-15"},
    {"id": "1002", "nombre": "Carlos López", "vencimiento": "2025-11-30"},
    {"id": "1003", "nombre": "María Rodríguez", "vencimiento": "2025-12-20"},
    {"id": "1004", "nombre": "Pedro Martínez", "vencimiento": "2025-11-25"},
    {"id": "1005", "nombre": "Laura Hernández", "vencimiento": "2026-01-10"}
]

for socio in socios:
    try:
        response = requests.post(f"{BASE_URL}/socios/", json=socio)
        print(f"Socio {socio['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"Error con socio {socio['nombre']}: {e}")

# Crear clases
clases = [
    {"nombre": "Yoga", "dia_semana": "lunes", "hora_inicio": "18:00", "instructor": "María Silva", "capacidad_max": 15},
    {"nombre": "Spinning", "dia_semana": "martes", "hora_inicio": "19:30", "instructor": "Carlos Ruiz", "capacidad_max": 20},
    {"nombre": "Funcional", "dia_semana": "miércoles", "hora_inicio": "20:30", "instructor": "Ana Torres", "capacidad_max": 18},
    {"nombre": "CrossFit", "dia_semana": "jueves", "hora_inicio": "19:00", "instructor": "Pedro García", "capacidad_max": 12}
]

for clase in clases:
    try:
        response = requests.post(f"{BASE_URL}/clases/", json=clase)
        print(f"Clase {clase['nombre']}: {response.status_code}")
    except Exception as e:
        print(f"Error con clase {clase['nombre']}: {e}")

print(" Datos creados. Refresca tu dashboard Streamlit")
