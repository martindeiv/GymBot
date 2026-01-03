import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/")
def home():
    return "Servidor activo 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"ok": True})

    # 📸 Si es una foto
    if "photo" in message:
        photo_list = message["photo"]
        best_photo = photo_list[-1]  # mejor calidad
        file_id = best_photo["file_id"]

        print("📸 Foto recibida")
        print("File ID:", file_id)

    # 💬 Si es texto
    elif "text" in message:
        print("💬 Texto recibido:", message["text"])

    return jsonify({"ok": True})
if __name__ == "__main__":
    app.run()
