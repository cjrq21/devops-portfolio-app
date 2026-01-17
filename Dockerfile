# --- ETAPA 1: Builder (Alpine) ---
FROM python:3.9-alpine as builder

WORKDIR /app

# Instalamos compiladores básicos (necesarios para algunas libs de Python en Alpine)
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

# Instalamos las dependencias
# --no-cache-dir: Para que la imagen sea ligera
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./tests ./tests

# --- ETAPA 2: Runtime (Alpine) ---
FROM python:3.9-alpine

WORKDIR /app

# Evitamos archivos basura
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos usuario
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiamos las librerías desde el builder
# Nota: En Alpine la ruta suele ser la misma /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appgroup ./app ./app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]