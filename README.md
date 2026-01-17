# 🚀 DevOps Portfolio App: Full Stack CI/CD Automation

![Python](https://img.shields.io/badge/Python-3.9-blue?style=flat&logo=python)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=flat&logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?style=flat&logo=kubernetes)
![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins-red?style=flat&logo=jenkins)
![Trivy](https://img.shields.io/badge/Security-Trivy-aquamarine?style=flat&logo=aquasec)
![Alpine](https://img.shields.io/badge/OS-Alpine_Linux-blue?style=flat&logo=alpine-linux)

Este repositorio contiene una implementación completa de un ciclo de vida **DevOps**. Muestra cómo una aplicación web (FastAPI + Redis) viaja desde el entorno de desarrollo local hasta un clúster de Kubernetes en producción, pasando por un pipeline automatizado de CI/CD.

---

## 🏗️ Arquitectura del Sistema

El proyecto simula un entorno empresarial real utilizando las siguientes capas:

1.  **Código:** API REST en Python (FastAPI) con base de datos en memoria (Redis) para persistencia de datos.
2.  **Containerización Segura:** Imágenes basadas en **Alpine Linux** (Hardened), ejecutadas con usuarios no-root y sin herramientas de construcción en producción.
3.  **CI (Integración Continua):** Jenkins automatiza el testing (utilizando Mocks para aislar dependencias) y la construcción de artefactos.
4.  **Registry:** Publicación segura y versionada de imágenes en **Docker Hub**.
5.  **Orquestación:** Despliegue en **Kubernetes** con configuración de Alta Disponibilidad, Balanceo de Carga y Auto-healing.
6.  **DevSecOps:** Escaneo automático de vulnerabilidades (CVEs) en cada build utilizando **Trivy**, con política de tolerancia cero para vulnerabilidades críticas.

---

## 🛡️ Estrategia DevSecOps (Image Hardening)

Este proyecto implementa estrictos controles de seguridad en la construcción de contenedores:

1.  **Base Minimalista:** Migración de Debian a **Alpine Linux**, reduciendo la superficie de ataque y el tamaño de la imagen (~50MB).
2.  **Segregación de Dependencias:**
    * Librerías de desarrollo (`pytest`, `setuptools`) se instalan solo en la etapa de `builder`.
    * Solo las librerías estrictamente necesarias viajan a la imagen final.
3.  **Limpieza en Runtime:** Se eliminan gestores de paquetes (`pip`, `apk`) y herramientas de construcción en la imagen final para evitar la inyección de malware.
4.  **Escaneo Automatizado:**
    * Integración de **Trivy** en el Pipeline de Jenkins.
    * El pipeline falla si detecta vulnerabilidades `CRITICAL` o `HIGH` no resueltas.

---

## 📋 Guía de Replicación (Paso a Paso)

Si deseas replicar este laboratorio en tu propia máquina, sigue estas instrucciones detalladas.

### 1. Prerrequisitos
Necesitas tener instalado el siguiente software:
* **Git** (Para control de versiones).
* **Docker Desktop** (Para Windows/Mac/Linux).
* **VS Code** (Recomendado como editor de código).

### 2. Configuración del Entorno

#### A. Habilitar Kubernetes Local
1.  Abre el panel de **Docker Desktop**.
2.  Ve a **Settings (⚙️)** -> **Kubernetes**.
3.  Marca la casilla **"Enable Kubernetes"** y haz clic en "Apply & Restart".

#### B. Levantar Jenkins (Con acceso a Docker)
Para que Jenkins pueda construir imágenes Docker desde dentro de su contenedor, debe tener acceso al socket del host. Ejecuta este comando en tu terminal:

```bash
docker run -d -p 8080:8080 -p 50000:50000 --name devops-jenkins -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts

#### C. Configuración Inicial de Jenkins
1.  Accede a `http://localhost:8080` en tu navegador.
2.  Para obtener la contraseña de administrador inicial, ejecuta en tu terminal:
    ```bash
    docker exec devops-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
    ```
3.  Pega la contraseña en la web y sigue el asistente de instalación (selecciona **"Install suggested plugins"**).
4.  Una vez dentro, ve a **Manage Jenkins** -> **Plugins** -> **Available plugins**, busca e instala:
    * `Docker Pipeline`
    * `Docker`

#### D. Configurar Credenciales de Docker Hub
1.  Ve a [Docker Hub](https://hub.docker.com) -> **Account Settings** -> **Security** -> **New Access Token**.
2.  Genera un token con permisos de lectura/escritura y **cópialo**.
3.  En Jenkins, ve a **Manage Jenkins** -> **Credentials** -> **System** -> **Global credentials (unrestricted)** -> **Add Credentials**.
    * **Kind:** Username with password.
    * **Username:** Tu usuario de Docker Hub.
    * **Password:** El Token que acabas de generar (NO tu contraseña habitual).
    * **ID:** `docker-hub-credentials` (Es vital que uses este ID exacto).

---

## 🚀 Despliegue del Proyecto

### 1. Clonar el repositorio
```bash
git clone [https://github.com/cjrq21/devops-portfolio-app.git](https://github.com/cjrq21/devops-portfolio-app.git)
cd devops-portfolio-app

### 2. Ejecutar el Pipeline (CI)

1.  En el panel principal de Jenkins, haz clic en **New Item** (Nueva Tarea).
2.  Ingresa un nombre (ej: `portfolio-pipeline`), selecciona **Pipeline** y haz clic en OK.
3.  Desplázate hasta la sección **Pipeline** y en **Definition** selecciona **Pipeline script from SCM**.
4.  Configura los siguientes campos:
    * **SCM:** Git
    * **Repository URL:** `https://github.com/cjrq21/devops-portfolio-app.git`
    * **Branch Specifier:** `*/main`
5.  Haz clic en **Save** y luego presiona **Build Now** en el menú izquierdo.

**Lo que sucederá automáticamente:**
* ✅ **Checkout:** Jenkins descargará tu código.
* ✅ **Test:** Se ejecutarán las pruebas unitarias con `pytest` (usando mocks para Redis).
* 🛡️ **Security Scan:** Trivy analiza la imagen en busca de CVEs.
* ✅ **Build:** Se construirá la imagen Docker optimizada.
* ✅ **Push:** La imagen se subirá a tu repositorio en Docker Hub.

### 3. Desplegar en Kubernetes (CD)

Una vez que el Pipeline finalice con éxito (bola verde o azul), tu imagen ya estará en la nube. Ahora, despliega la infraestructura en tu clúster local:

```bash
# Aplica los manifiestos de Base de Datos y Aplicación
kubectl apply -f k8s/

```bash
kubectl get pods

Finalmente, accede a la aplicación desde tu navegador: 👉 http://localhost

📂 Estructura del Repositorio
Este proyecto sigue una estructura profesional organizada por capas de infraestructura:

.
├── app/                 # Código fuente de la aplicación (FastAPI)
│   └── main.py          # Lógica principal y endpoints
├── k8s/                 # Infrastructure as Code (Kubernetes Manifests)
│   ├── app.yaml         # Definición del Deployment, Service y LoadBalancer de la App
│   └── redis.yaml       # Definición del Deployment y Service de la Base de Datos
├── tests/               # Tests automatizados
│   └── test_main.py     # Unit Testing con Pytest y Mocks
├── Jenkinsfile          # Pipeline Declarativo de CI/CD (Groovy)
├── Dockerfile           # Instrucciones de empaquetado (Multi-stage)
├── docker-compose.yml   # Entorno de desarrollo local (Legacy/Rápido)
└── requirements.txt     # Dependencias de Python

## 🧪 Pruebas de Resiliencia (Chaos Engineering)

Gracias a la orquestación de Kubernetes, el sistema cuenta con **Alta Disponibilidad**. Puedes probar la capacidad de **Auto-healing** (auto-curación) simulando un fallo crítico:

1.  **Identifica un pod:**
    ```bash
    kubectl get pods
    ```

2.  **Elimínalo manualmente:**
    ```bash
    kubectl delete pod devops-portfolio-xxxxxx-xxxx
    ```

3.  **Observa la recuperación:**
    Vuelve a ejecutar `kubectl get pods`. Verás que Kubernetes detectó la "muerte" del contenedor e inició una nueva réplica instantáneamente para mantener el servicio activo.

---
**Autor:** Carlos Javier