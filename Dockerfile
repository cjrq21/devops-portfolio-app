# --- ETAPA 1: Builder (Alpine) ---
FROM python:3.9-alpine as builder

WORKDIR /app

# Compiladores básicos
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

# 1. Instalar dependencias de PRODUCCIÓN en una carpeta aislada (/app/libs)
#    Usamos --target para separarlas de las librerías del sistema
RUN pip install --no-cache-dir --target=/app/libs -r requirements.txt

# 2. Instalar dependencias de TESTING (pytest) en el sistema global
#    Esto instalará 'jaraco' aquí, pero como NO está en /app/libs, no se copiará al final
RUN pip install pytest httpx

COPY ./app ./app
COPY ./tests ./tests

# 3. Correr los tests
#    Le decimos a Python: "Busca librerías también en /app/libs"
ENV PYTHONPATH=/app/libs
RUN pytest

# --- ETAPA 2: Runtime (Alpine Limpio) ---
FROM python:3.9-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Importante: Añadimos nuestra carpeta de libs al path de Python
ENV PYTHONPATH=/app/libs

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 4. COPIAMOS SOLO LA CARPETA DE PRODUCCIÓN (/app/libs)
#    Aquí NO viene pytest, ni jaraco, ni vulnerabilidades.
COPY --from=builder /app/libs /app/libs

# Nota: Como instalamos en /app/libs, los ejecutables (uvicorn) están ahí dentro
# No copiamos /usr/local/bin para evitar traer basura

COPY --chown=appuser:appgroup ./app ./app

USER appuser

EXPOSE 8000

# Ejecutamos uvicorn como módulo de python (-m) para que use el PYTHONPATH correcto
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]