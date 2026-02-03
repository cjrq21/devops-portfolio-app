import time
import requests
import os
from dotenv import load_dotenv

# 1. Cargamos las variables del archivo .env
print("📂 Cargando configuración segura...")
load_dotenv()

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
JOB_NAME = os.getenv("JOB_NAME")

# Verificación de seguridad: Si falta algo, el bot no arranca
if not all([TELEGRAM_TOKEN, JENKINS_URL, JENKINS_USER, JENKINS_TOKEN, JOB_NAME]):
    print("❌ ERROR CRÍTICO: Faltan variables en el archivo .env")
    print("Asegúrate de tener: TELEGRAM_TOKEN, JENKINS_URL, JENKINS_USER, JENKINS_TOKEN, JOB_NAME")
    exit(1)

# --- URLS ---
TG_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
# Esto maneja el nombre del job correctamente
JENKINS_BUILD_URL = f"{JENKINS_URL}/job/{JOB_NAME}/build"

def get_updates(offset=None):
    """Pregunta a Telegram si hay mensajes nuevos"""
    url = f"{TG_API_URL}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"⚠️ Error conectando a Telegram: {e}")
        return {}

def trigger_jenkins():
    """Da la orden a Jenkins para iniciar el pipeline"""
    try:
        print(f"🚀 Intentando disparar Jenkins en: {JENKINS_BUILD_URL}")
        # Autenticación segura con el Token API
        response = requests.post(JENKINS_BUILD_URL, auth=(JENKINS_USER, JENKINS_TOKEN))
        
        if response.status_code == 201:
            return True, "🚀 ¡Recibido! He ordenado a Jenkins que inicie el despliegue."
        else:
            return False, f"⚠️ Jenkins rechazó la orden. Código: {response.status_code}. Revisa tu Token/Usuario."
    except Exception as e:
        return False, f"❌ No pude conectar con Jenkins localmente: {e}"

def send_message(chat_id, text):
    """Envía la respuesta al usuario"""
    try:
        requests.post(f"{TG_API_URL}/sendMessage", data={'chat_id': chat_id, 'text': text})
    except Exception as e:
        print(f"⚠️ Error enviando mensaje: {e}")

def main():
    print(f"🤖 Bot Listener iniciado para el job: {JOB_NAME}")
    print("📡 Escuchando comandos en Telegram...")
    
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        
        if "result" in updates:
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1
                
                # Verificamos que sea un mensaje de texto
                if "message" in item and "text" in item["message"]:
                    chat_id = item["message"]["chat"]["id"]
                    # Convertimos a minúsculas para que de igual escribir /Deploy o /deploy
                    text = item["message"]["text"].lower().strip()
                    
                    print(f"📩 Comando recibido: {text}")

                    # --- ZONA DE COMANDOS ---
                    if text == "/deploy":
                        send_message(chat_id, "⚙️ Procesando solicitud...")
                        success, msg = trigger_jenkins()
                        send_message(chat_id, msg)
                    
                    elif text == "/status":
                        send_message(chat_id, "✅ Estoy activo y conectado a tu Jenkins local.")
                    
                    elif text == "/start":
                        send_message(chat_id, "👋 ¡Hola! Soy tu asistente DevOps.\n\nComandos disponibles:\n🚀 /deploy - Iniciar despliegue\nℹ️ /status - Verificar estado")

        # Esperamos 2 segundos antes de volver a preguntar (para no saturar)
        time.sleep(2)

if __name__ == "__main__":
    main()