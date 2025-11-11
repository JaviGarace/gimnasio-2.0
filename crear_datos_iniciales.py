# crear_datos_iniciales.py
import requests
import json
import time

# URL base de tu API
BASE_URL = "https://gimnasio-2-0-1.onrender.com"

print(" Inicializando base de datos...")

# 1. Intentar crear la base de datos (esto activará los datos de prueba en tu API)
try:
    response = requests.get(f"{BASE_URL}/datos-prueba/notificaciones")
    if response.status_code == 200:
        print(" Base de datos inicializada con datos de prueba")
        print(response.json())
    else:
        print(f" No se pudo inicializar con datos de prueba: {response.status_code}")
except Exception as e:
    print(f" Error inicializando base de datos: {e}")

# Esperar un momento para que se procesen los datos
time.sleep(3)

# 2. Verificar que los planes estén disponibles
try:
    response = requests.get(f"{BASE_URL}/planes/")
    if response.status_code == 200:
        planes = response.json()
        print(f" Planes disponibles: {len(planes)}")
        for plan in planes:
            print(f"   - {plan.get('nombre', 'N/A')} - ")
    else:
        print(f" Error obteniendo planes: {response.status_code}")
except Exception as e:
    print(f" Error con planes: {e}")

# 3. Verificar socios (ahora debería funcionar)
try:
    response = requests.get(f"{BASE_URL}/socios/")
    if response.status_code == 200:
        socios = response.json()
        print(f" Socios disponibles: {len(socios)}")
        for socio in socios:
            print(f"   - {socio.get('nombre', 'N/A')} (ID: {socio.get('id', 'N/A')})")
    else:
        print(f" Error obteniendo socios: {response.status_code}")
except Exception as e:
    print(f" Error con socios: {e}")

print(" Refresca tu dashboard Streamlit para ver los datos")
print(" Si aún hay problemas, espera 1-2 minutos y vuelve a intentar")
