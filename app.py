from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor activo 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Datos recibidos:", data)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()