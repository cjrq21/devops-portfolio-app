pipeline {
    agent any

    environment {
        // OJO: Aquí pusimos un nombre temporal. 
        // No importa para el Build, pero para el Push (futuro) deberemos cambiarlo.
        DOCKER_IMAGE = 'cjrq21/devops-portfolio'
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
        
       stage('Push to Registry') {
            steps {
                script {
                    echo "--- Subiendo a Docker Hub ---"
                    // Esto usa el plugin 'Docker Pipeline' y las credenciales que guardaste
                    withDockerRegistry(credentialsId: DOCKER_CREDENTIALS_ID, toolName: 'docker') {
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
    }
}