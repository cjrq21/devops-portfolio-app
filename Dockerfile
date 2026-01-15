# Usamos una imagen base ligera de Python
FROM python:3.9-slim

# Evitamos que Python genere archivos .pyc y logs en buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo
WORKDIR /app

# --- CORRECCIÓN DE SEGURIDAD ---
# 1. Creamos el usuario PRIMERO
RUN useradd -m appuser

# 2. Copiamos los requirements
COPY requirements.txt .

# 3. Instalamos las dependencias GLOBALMENTE (System-wide)
#    Esto las pone en /usr/local/lib/python..., donde 'appuser' SÍ puede leerlas.
#    Ya no usamos '--user'
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos el código de la aplicación
#    Usamos '--chown' para que los archivos pertenezcan al usuario correcto desde el inicio
COPY --chown=appuser:appuser ./app ./app

# 5. Cambiamos al usuario seguro
USER appuser

# Exponemos el puerto
EXPOSE 8000

# Comando por defecto (Producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]