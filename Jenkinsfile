pipeline {
    agent any

    environment {
        // OJO: Aquí pusimos un nombre temporal. 
        // No importa para el Build, pero para el Push (futuro) deberemos cambiarlo.
        DOCKER_IMAGE = 'tu-usuario-dockerhub/devops-portfolio'
        DOCKER_TAG = "${BUILD_NUMBER}" 
    }

    stages {
        stage('Checkout') {
            steps {
                // Descarga el código de GitHub
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    // TRUCO DEVOPS:
                    // 1. Construimos la imagen hasta la etapa "builder" (donde están las herramientas de compilación)
                    sh "docker build --target builder -t test-image ."
                    
                    // 2. Corremos los tests DENTRO de ese contenedor temporal.
                    // Si los tests fallan aquí, el pipeline se detiene y no pasa a producción.
                    sh "docker run --rm test-image pytest"
                }
            }
        }

        stage('Build Release') {
            steps {
                script {
                    // Si los tests pasaron, construimos la imagen final ligera y segura
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
        
        // El stage 'Push' lo teníamos comentado o pendiente de credenciales
    }
}