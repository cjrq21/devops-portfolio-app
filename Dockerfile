# --- ETAPA 1: Builder (Para compilar y testear) ---
# Le ponemos nombre "builder" para que Jenkins pueda llamarlo
#FROM python:3.9-slim as builder
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# Copiamos requirements
COPY requirements.txt .

# Instalamos todo (incluyendo pytest y httpx)
# Lo hacemos en /usr/local para que sea accesible globalmente
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código (Necesario para correr tests en esta etapa)
COPY ./app ./app
COPY ./tests ./tests

# --- ETAPA 2: Runtime (La imagen final ligera) ---
FROM python:3.11-slim-bookworm

WORKDIR /app

# Evitamos archivos basura de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Creamos el usuario
RUN useradd -m appuser

# 2. Copiamos las librerías instaladas desde la etapa 'builder'
#    Esto es magia de Docker: copiamos de una imagen a otra
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Copiamos solo el código de la app (No copiamos los tests a producción)
COPY --chown=appuser:appuser ./app ./app

# 4. Cambiamos al usuario seguro
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]