from fastapi import FastAPI
import redis
import os
import socket



app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Warning: Sin conexión a Redis: {e}")

@app.get("/")
def read_root():
    try:
        hits = r.incr("hits")
    except Exception:
        hits = "Error - Redis no disponible"
    
    return {
        "app": "DevOps Portfolio API",
        "version": "1.0.0",
        "hostname": socket.gethostname(),
        "visits": hits

    }

@app.get("/health")
def health_check():

    return {"status": "ok ahora con argocd", "redis": r.ping() if 'r' in globals() else False}