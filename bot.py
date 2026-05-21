import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_KEY = os.environ["GROQ_KEY"]

SYSTEM_PROMPT = """Sei l'assistente virtuale di Capo Sud, il blog sul Sudafrica di Dario.
Rispondi in italiano, amichevole e diretto.
Sei esperto di viaggi in Sudafrica, Cape Town, safari, itinerari, costi, visti, cultura locale.
Per consulenze personalizzate con Dario manda: [LINK CALENDLY]
Risposte brevi e utili."""

client = Groq(api_key=GROQ_KEY)

async def rispondi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo = update.message.text
    risposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": testo}
        ],
        max_tokens=500
    )
    await update.message.reply_text(risposta.choices[0].message.content)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rispondi))
app.run_polling()