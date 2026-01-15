# DevOps Portfolio Project: Hit Counter App

Una aplicación Cloud-Native completa demostrando prácticas modernas de DevOps, desde el desarrollo hasta el despliegue automatizado.

## 🏗 Arquitectura

* **Backend:** Python FastAPI (Asíncrono, High Performance).
* **Database:** Redis (Para almacenamiento de estado y contadores).
* **Containerization:** Docker & Docker Compose (Multi-stage builds).
* **Orchestration:** Kubernetes (K8s/K3s) con despliegues declarativos.
* **CI/CD:** Jenkins Pipeline (Build, Test, Push, Deploy).
* **Observability:** Health Checks integrados para Liveness/Readiness probes.

## 🚀 Inicio Rápido (Local)

Para levantar el entorno de desarrollo con Hot-Reload activado:

```bash
# Levantar servicios
docker-compose up --build

# La app estará disponible en: http://localhost:8000
# Documentación API (Swagger): http://localhost:8000/docs