import os
from flask import Flask, request, jsonify
import requests
from datetime import datetime
import json
import random



app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PHRASES_URL = os.environ.get("PHRASES_URL")


PHRASES = {}

def load_phrases():
    global PHRASES
    try:
        r = requests.get(os.environ.get("PHRASES_URL"), timeout=5)
        r.raise_for_status()
        PHRASES = r.json()
        print("✅ Frases cargadas:", PHRASES.keys())
    except Exception as e:
        print("❌ Error cargando frases:", e)
        PHRASES = {
            "default": ["💪 Sigue adelante"]
        }

load_phrases()


def get_phrase_for_user(first_name):
    if first_name and first_name in PHRASES:
        return random.choice(PHRASES[first_name])
    return random.choice(PHRASES.get("default", ["💪 Sigue"]))


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)

    
    if response.status_code != 200:
        print("❌ Error enviando mensaje:", response.text)
    else:
        print("📨 Mensaje enviado correctamente")


@app.route("/")
def home():
    return "Servidor activo 🚀"


def get_file_url(file_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
    response = requests.get(url, params={"file_id": file_id})
    result = response.json()

    if not result.get("ok"):
        return None

    file_path = result["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

    return file_url

def create_notion_page(image_url, sender_first_name):
    current_week = datetime.utcnow().isocalendar().week
    title_name = f"Entrenamiento {sender_first_name} - Semana {current_week}"
    

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {os.environ.get('NOTION_TOKEN')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {
            "database_id": os.environ.get("NOTION_DATABASE_ID")
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title_name
                        }
                    }
                ]
            },
            "Fecha": {
                "date": {
                    "start": datetime.utcnow().isoformat()
                }
            },
            "Semana": {
                "number": current_week
            },
            "Participante": {
                "rich_text": [
                    {
                        "text": {
                            "content": sender_first_name
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code


@app.route("/webhook", methods=["POST"])

def webhook():
    data = request.json
    message = data.get("message")
    sender = message["from"]
    first_name = sender.get("first_name")
    phrase = get_phrase_for_user(first_name)
    chat_id = message["chat"]["id"]

    if not message:
        return jsonify({"ok": True})

    # 📸 Si es una foto
    if "photo" in message:
        photo_list = message["photo"]
        best_photo = photo_list[-1]
        file_id = best_photo["file_id"]

        file_url = get_file_url(file_id)
        

    user = message.get("from", {})
    first_name = user.get("first_name", "Usuario")
    

    
    print("📸 Foto recibida")
    print("File ID:", file_id)
    print("Emisor:", first_name)
    print("URL de la imagen:", file_url)
    status = create_notion_page(file_url, first_name)
    print("📘 Notion status:", status)
    send_telegram_message(chat_id, phrase)

    # 💬 Si es texto
    if "text" in message:
        print("💬 Texto recibido:", message["text"])

    return jsonify({"ok": True})
if __name__ == "__main__":
    app.run()
