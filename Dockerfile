# --- ETAPA 1: Builder (Alpine) ---
FROM python:3.9-alpine as builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

# Instalamos dependencias en /app/libs
RUN pip install --no-cache-dir --target=/app/libs -r requirements.txt

# Instalamos pytest globalmente solo para esta etapa
RUN pip install pytest httpx

COPY ./app ./app
COPY ./tests ./tests

# Correr tests
ENV PYTHONPATH=/app/libs
RUN pytest

# --- ETAPA 2: Runtime (Alpine Limpio) ---
FROM python:3.9-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/libs

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiamos las librerías limpias
COPY --from=builder /app/libs /app/libs

# --- EL TRUCO DE MAGIA ESTÁ AQUÍ ---
# Desinstalamos las herramientas de build que traen vulnerabilidades
# Esto elimina setuptools (y su jaraco infectado) y pip
RUN pip uninstall -y setuptools pip

COPY --chown=appuser:appgroup ./app ./app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]