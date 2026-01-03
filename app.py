import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/")
def home():
    return "Servidor activo 🚀"


@app.route("/webhook", methods=["POST"])

def get_file_url(file_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
    response = requests.get(url, params={"file_id": file_id})
    result = response.json()

    if not result.get("ok"):
        return None

    file_path = result["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

    return file_url

def webhook():
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"ok": True})

    # 📸 Si es una foto
    if "photo" in message:
        photo_list = message["photo"]
        best_photo = photo_list[-1]
        file_id = best_photo["file_id"]

        file_url = get_file_url(file_id)

        print("📸 Foto recibida")
        print("File ID:", file_id)
        print("URL de la imagen:", file_url)

    # 💬 Si es texto
    elif "text" in message:
        print("💬 Texto recibido:", message["text"])

    return jsonify({"ok": True})
if __name__ == "__main__":
    app.run()
