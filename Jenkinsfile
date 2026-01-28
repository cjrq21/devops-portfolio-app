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
                    sh "docker system prune -f"
                    sh "docker build --no-cache -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker build -t ${DOCKER_IMAGE}:latest ."
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
        stage('Update Manifest (GitOps)') {
            steps {
                script {
                    echo "--- Actualizando versión en Git ---"
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'GIT_TOKEN', usernameVariable: 'GIT_USER')]) {
                        sh '''
                            # Configurar identidad para el commit
                            git config user.email "jenkins-bot@example.com"
                            git config user.name "Jenkins GitOps Bot"
                            
                            # Actualizar el archivo yaml usando SED
                            # Busca "image: cjrq21/devops-portfolio:..." y lo reemplaza con el nuevo BUILD_NUMBER
                            sed -i "s|image: cjrq21/devops-portfolio:.*|image: cjrq21/devops-portfolio:${BUILD_NUMBER}|g" k8s/app.yaml
                            
                            # Verificar el cambio (opcional, para verlo en logs)
                            cat k8s/app.yaml | grep image:
                            
                            # Commit y Push
                            git add k8s/app.yaml
                            git commit -m "chore(release): update image tag to ${BUILD_NUMBER} [skip ci]"
                            
                            # Push autenticado usando las variables de entorno
                            git push https://${GIT_USER}:${GIT_TOKEN}@github.com/cjrq21/devops-portfolio-app.git HEAD:main
                        '''
                    }
                }
            }
        }
    }
}