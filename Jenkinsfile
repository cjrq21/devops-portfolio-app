pipeline {
    agent any

    environment {
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
                    sh "docker build --target builder -t test-image ."
                    sh "docker run --rm test-image pytest"
                }
            }
        }

        stage('Build Release') {
            steps {
                script {
                    echo "--- Generando Imagen Final ---"
                    sh "docker build --no-cache -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker build --no-cache -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        // --- NUEVO STAGE AQUÍ ---
        stage('Security Scan (Trivy)') {
            steps {
                script {
                    echo "--- Escaneando Vulnerabilidades con Trivy ---"
                    sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
        // ------------------------

        stage('Push to Registry') {
            steps {
                script {
                    echo "--- Subiendo a Docker Hub ---"
                    withDockerRegistry(credentialsId: DOCKER_CREDENTIALS_ID, toolName: 'docker') {
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }
}