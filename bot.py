import os
import asyncio
import httpx
from groq import Groq

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_KEY = os.environ["GROQ_KEY"]
OFFSET = 0

SYSTEM_PROMPT = """Sei l'assistente virtuale di Capo Sud, il blog sul Sudafrica di Dario.
Rispondi sempre in italiano, con tono amichevole e diretto come un amico esperto.
Sei esperto di: viaggi in Sudafrica, Cape Town, safari, Kruger, Garden Route,
itinerari, costi, visti, cultura locale, vita quotidiana in Sudafrica.
Per consulenze personalizzate con Dario scrivi: [LINK CALENDLY]
Tieni le risposte brevi, utili e mai troppo formali."""

client = Groq(api_key=GROQ_KEY)

async def get_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    async with httpx.AsyncClient(timeout=35) as http:
        r = await http.get(url, params={"offset": offset, "timeout": 30})
        return r.json().get("result", [])

async def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as http:
        await http.post(url, json={"chat_id": chat_id, "text": text})

async def rispondi(testo):
    risposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": testo}
        ],
        max_tokens=500
    )
    return risposta.choices[0].message.content

async def main():
    global OFFSET
    print("Bot avviato!")
    while True:
        updates = await get_updates(OFFSET)
        for update in updates:
            OFFSET = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                testo   = update["message"]["text"]
                risposta = await rispondi(testo)
                await send_message(chat_id, risposta)
        await asyncio.sleep(1)

asyncio.run(main())
