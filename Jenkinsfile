pipeline {
    agent any

    tools {
        'hudson.plugins.sonar.SonarRunnerInstallation' 'sonar-scanner'
    }

    environment {
        DOCKER_IMAGE = 'cjrq21/devops-portfolio'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        
        // --- NUEVO: Credenciales para Telegram ---
        TELEGRAM_TOKEN = credentials('telegram-bot-token')
        TELEGRAM_CHAT_ID = credentials('telegram-chat-id')
        
        // URL de tu SonarQube (Ajusta la IP si cambió)
        SONAR_URL = 'http://192.168.250.100:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    echo "--- Iniciando Análisis de Código Estático ---"
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('sonarqube-server') {
                        sh """
                        "${scannerHome}/bin/sonar-scanner" \
                          -Dsonar.projectKey=devops-portfolio \
                          -Dsonar.projectName="DevOps Portfolio" \
                          -Dsonar.projectVersion=${BUILD_NUMBER} \
                          -Dsonar.sources=. \
                          -Dsonar.coverage.exclusions=bot_listener.py \
                          -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
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

        stage('Security Scan (Trivy)') {
            steps {
                script {
                    echo "--- Escaneando Vulnerabilidades con Trivy ---"
                    sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

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
                            git config user.email "jenkins-bot@example.com"
                            git config user.name "Jenkins GitOps Bot"
                            sed -i "s|image: cjrq21/devops-portfolio:.*|image: cjrq21/devops-portfolio:${BUILD_NUMBER}|g" k8s/app.yaml
                            git add k8s/app.yaml
                            git commit -m "chore(release): update image tag to ${BUILD_NUMBER} [skip ci]"
                            git push https://${GIT_USER}:${GIT_TOKEN}@github.com/cjrq21/devops-portfolio-app.git HEAD:main
                        '''
                    }
                }
            }
        }
    }

    // --- NUEVO: Bloque POST para notificaciones ---
    post {
        success {
            script {
                sendTelegramReport('SUCCESS', '🚀 Despliegue Exitoso')
            }
        }
        failure {
            script {
                sendTelegramReport('FAILURE', '❌ Fallo en el Pipeline')
            }
        }
    }
}

// --- FUNCIÓN PERSONALIZADA PARA TELEGRAM ---
def sendTelegramReport(buildStatus, title) {
    // Definimos el icono de SonarQube visualmente
    def sonarStatus = (buildStatus == 'SUCCESS') ? 'Passed ✅' : 'Check Logs ⚠️'
    
    // Construimos el mensaje en formato HTML
    // Nota: Jenkins inyecta las variables ${env.VAR} automáticamente
    def message = """
<b>${title}</b>

📦 <b>App Version:</b> v${env.BUILD_NUMBER}
🐙 <b>Git Repo:</b> <a href='${env.GIT_URL}'>Ver cambios</a>
🐳 <b>Docker Image:</b> <a href='https://hub.docker.com/r/${env.DOCKER_IMAGE}/tags'>${env.DOCKER_IMAGE}:${env.DOCKER_TAG}</a>

🛡️ <b>SonarQube:</b> ${sonarStatus}
<a href='${env.SONAR_URL}/dashboard?id=devops-portfolio'>Ver Reporte de Calidad</a>

⚙️ <b>Jenkins Build:</b> <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER} Console</a>
☸️ <b>ArgoCD:</b> Sincronizando en breve...
    """

    // Enviamos el mensaje usando curl a la API de Telegram
    sh """
        curl -s -X POST https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/sendMessage \
        -d chat_id=${env.TELEGRAM_CHAT_ID} \
        -d parse_mode=HTML \
        -d text="${message}"
    """
}