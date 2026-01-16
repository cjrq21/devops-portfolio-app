pipeline {
    agent any

    environment {
        // Asegúrate de que este sea tu usuario real
        DOCKER_IMAGE = 'cjrq21/devops-portfolio' 
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    echo "--- Construyendo y Testeando ---"
                    // --no-cache es opcional, pero ayuda si te da errores raros
                    sh "docker build --target builder -t test-image ."
                    sh "docker run --rm test-image pytest"
                }
            }
        }

        stage('Build Release') {
            steps {
                script {
                    echo "--- Generando Imagen Final ---"
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker build -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    echo "--- Subiendo a Docker Hub ---"
                    // Si te da error de 'toolName', borra la parte de ", toolName: 'docker'"
                    withDockerRegistry(credentialsId: DOCKER_CREDENTIALS_ID, toolName: 'docker') {
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }
}