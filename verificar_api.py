# verificar_api.py
import requests
import json
from datetime import datetime

print(" Verificando estado de la API FastAPI...")
print("="*50)

BASE_URL = "https://gimnasio-2-0-1.onrender.com"

# 1. Verificar endpoints básicos
endpoints = [
    "/",
    "/socios/",
    "/planes/",
    "/clases/",
    "/reservas/",
    "/entradas/",
    "/pagos/",
    "/debug-routes",
    "/create-tables"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        status = "" if response.status_code == 200 else ""
        print(f"{status} {endpoint:<20} - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:100]}...")
    except Exception as e:
        print(f" {endpoint:<20} - Error: {str(e)[:50]}...")

print("="*50)
print(" Probando creación de datos iniciales...")
try:
    response = requests.post(f"{BASE_URL}/datos-prueba/notificaciones")
    if response.status_code == 200:
        print(" Datos de prueba creados exitosamente")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f" Error creando datos: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f" Error general: {e}")

print("="*50)
print(" Verificando datos después de inicialización...")
tables_to_check = ["/socios/", "/clases/", "/reservas/", "/pagos/"]
for table in tables_to_check:
    try:
        response = requests.get(f"{BASE_URL}{table}")
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print(f" {table:<15} - {count} registros")
        else:
            print(f" {table:<15} - Error: {response.status_code}")
    except Exception as e:
        print(f" {table:<15} - Error: {str(e)[:50]}...")
