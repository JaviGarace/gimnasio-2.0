FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer puerto que Koyeb requiere
EXPOSE 8080

# Variable de entorno para el puerto
ENV PORT=8080

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
