import os
import httpx
from groq import Groq
from flask import Flask, request, jsonify

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_KEY = os.environ["GROQ_KEY"]

SYSTEM_PROMPT = """Sei l'assistente virtuale di Capo Sud, il blog sul Sudafrica di Dario.
Rispondi sempre in italiano, con tono amichevole e diretto come un amico esperto.
Sei esperto di: viaggi in Sudafrica, Cape Town, safari, Kruger, Garden Route,
itinerari, costi, visti, cultura locale, vita quotidiana in Sudafrica.
Per consulenze personalizzate con Dario scrivi: [LINK CALENDLY]
Tieni le risposte brevi, utili e mai troppo formali."""

client = Groq(api_key=GROQ_KEY)
app = Flask(__name__)


def rispondi(testo):
    risposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": testo}
        ],
        max_tokens=500
    )
    return risposta.choices[0].message.content


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    with httpx.Client() as http:
        http.post(url, json={"chat_id": chat_id, "text": text})


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        testo = data["message"]["text"]
        risposta = rispondi(testo)
        send_message(chat_id, risposta)
    return jsonify({"ok": True})


@app.route("/")
def health():
    return "Bot Capo Sud attivo!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
