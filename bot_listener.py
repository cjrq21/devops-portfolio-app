import time
import requests
import os
from dotenv import load_dotenv

# Cargamos configuración
print("📂 Cargando configuración segura...")
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")
JOB_NAME = os.getenv("JOB_NAME")

if not all([TELEGRAM_TOKEN, JENKINS_URL, JENKINS_USER, JENKINS_TOKEN, JOB_NAME]):
    print("❌ ERROR: Faltan variables en .env")
    exit(1)

TG_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
JENKINS_BUILD_URL = f"{JENKINS_URL}/job/{JOB_NAME}/build"

def get_updates(offset=None):
    """Consulta a Telegram por nuevos mensajes"""
    url = f"{TG_API_URL}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"⚠️ Error Telegram: {e}")
        return {}

def trigger_jenkins():
    """Dispara el job en Jenkins"""
    try:
        print(f"🚀 Llamando a Jenkins: {JOB_NAME}")
        response = requests.post(JENKINS_BUILD_URL, auth=(JENKINS_USER, JENKINS_TOKEN))
        
        if response.status_code == 201:
            return "🚀 ¡Recibido! Jenkins está trabajando."
        else:
            return f"⚠️ Error Jenkins ({response.status_code}). Revisa el token."
    except Exception as e:
        return f"❌ Error de conexión: {e}"

def send_message(chat_id, text):
    """Envía respuesta al usuario"""
    try:
        requests.post(f"{TG_API_URL}/sendMessage", data={'chat_id': chat_id, 'text': text})
    except Exception as e:
        print(f"⚠️ Error enviando mensaje: {e}")

def process_command(chat_id, text):
    """
    REFACTORIZACIÓN: Esta función maneja la lógica de comandos
    para reducir la complejidad de la función principal.
    """
    if text == "/deploy":
        send_message(chat_id, "⚙️ Procesando solicitud...")
        # FIX: Usamos '_' para indicar que no nos importa el primer valor (success)
        _, msg = trigger_jenkins() 
        send_message(chat_id, msg)
    
    elif text == "/status":
        send_message(chat_id, "✅ Bot activo. Jenkins operativo.")
    
    elif text == "/start":
        send_message(chat_id, "👋 Hola. Usa /deploy para desplegar.")

def main():
    print(f"🤖 Bot Listener iniciado para: {JOB_NAME}")
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        
        # Si no hay resultados, seguimos esperando
        if "result" not in updates or not updates["result"]:
            time.sleep(2)
            continue

        for item in updates["result"]:
            last_update_id = item["update_id"] + 1
            
            # Validamos que sea un mensaje de texto
            if "message" in item and "text" in item["message"]:
                chat_id = item["message"]["chat"]["id"]
                text = item["message"]["text"].lower().strip()
                
                print(f"📩 Comando: {text}")
                # Delegamos la lógica a la función auxiliar
                process_command(chat_id, text)

        time.sleep(2)

if __name__ == "__main__":
    main()