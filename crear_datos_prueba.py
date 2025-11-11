# crear_datos_prueba.py
import requests
import json

# URL base de tu API
BASE_URL = "https://gimnasio-2-0-1.onrender.com"

print(" Creando datos de prueba...")

# 1. Crear planes de membresía
planes = [
    {"nombre": "Básico", "precio": 50.0, "duracion_dias": 30, "descripcion": "Acceso a instalaciones básicas"},
    {"nombre": "Premium", "precio": 80.0, "duracion_dias": 30, "descripcion": "Acceso ilimitado a todas las clases"},
    {"nombre": "Familiar", "precio": 120.0, "duracion_dias": 30, "descripcion": "Para hasta 4 personas"}
]

for plan in planes:
    try:
        response = requests.post(f"{BASE_URL}/planes/", json=plan)
        if response.status_code == 200:
            print(f" Plan creado: {plan['nombre']}")
        else:
            print(f" Error creando plan {plan['nombre']}: {response.text}")
    except Exception as e:
        print(f" Error con plan {plan['nombre']}: {e}")

# 2. Crear socios
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
        if response.status_code == 200:
            print(f" Socio creado: {socio['nombre']}")
        else:
            print(f" Error creando socio {socio['nombre']}: {response.text}")
    except Exception as e:
        print(f" Error con socio {socio['nombre']}: {e}")

# 3. Crear clases
clases = [
    {"nombre": "Yoga", "dia_semana": "lunes", "hora_inicio": "18:00", "instructor": "María Silva"},
    {"nombre": "Spinning", "dia_semana": "martes", "hora_inicio": "19:30", "instructor": "Carlos Ruiz"},
    {"nombre": "Funcional", "dia_semana": "miércoles", "hora_inicio": "20:30", "instructor": "Ana Torres"},
    {"nombre": "CrossFit", "dia_semana": "jueves", "hora_inicio": "19:00", "instructor": "Pedro García"}
]

for clase in clases:
    try:
        response = requests.post(f"{BASE_URL}/clases/", json=clase)
        if response.status_code == 200:
            print(f" Clase creada: {clase['nombre']}")
        else:
            print(f" Error creando clase {clase['nombre']}: {response.text}")
    except Exception as e:
        print(f" Error con clase {clase['nombre']}: {e}")

print(" Datos de prueba creados exitosamente!")
print(" Refresca tu dashboard Streamlit para ver los datos")
