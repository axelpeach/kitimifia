from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не вказано в змінних середовища")

# Ініціалізація Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

@app.route("/")
def home():
    return "Бот працює 🐾"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.update_queue.put(update)
        return "OK", 200
    return "Метод не дозволений", 405

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
