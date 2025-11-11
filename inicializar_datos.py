# inicializar_datos.py
import requests
import time

print(" Inicializando base de datos con datos de prueba...")

# URL base de tu API
BASE_URL = "https://gimnasio-2-0-1.onrender.com"

# 1. Crear datos de prueba (esto inicializará toda la base de datos)
try:
    print(" Creando datos de prueba...")
    response = requests.post(f"{BASE_URL}/datos-prueba/notificaciones")
    if response.status_code == 200:
        print(" Datos de prueba creados exitosamente")
        print(response.json())
    else:
        print(f" Error creando datos de prueba: {response.status_code}")
except Exception as e:
    print(f" Error: {e}")

# Esperar un momento para que se procesen los datos
time.sleep(3)

# 2. Verificar que los planes estén disponibles
try:
    print("\n Verificando planes...")
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
    print("\n Verificando socios...")
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

# 4. Verificar clases (ahora debería funcionar)
try:
    print("\n Verificando clases...")
    response = requests.get(f"{BASE_URL}/clases/")
    if response.status_code == 200:
        clases = response.json()
        print(f" Clases disponibles: {len(clases)}")
        for clase in clases:
            print(f"   - {clase.get('nombre', 'N/A')} ({clase.get('dia_semana', 'N/A')} a las {clase.get('hora_inicio', 'N/A')})")
    else:
        print(f" Error obteniendo clases: {response.status_code}")
except Exception as e:
    print(f" Error con clases: {e}")

print("\n Inicialización completada!")
print(" Refresca tu dashboard Streamlit para ver los datos")
print(" Todos los datos de prueba están listos para usar")
