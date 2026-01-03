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
    print("Mensaje recibido de Telegram:")
    print(data)

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
