from flask import Flask, request
from telegram import Update
from telegram.ext import Dispatcher
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не вказано в змінних середовища")

dispatcher = None  # Ініціалізуйте свій Dispatcher тут

@app.route("/")
def home():
    return "Бот працює 🐾"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    global dispatcher
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), dispatcher.bot)
        dispatcher.process_update(update)
        return "OK", 200
    return "Метод не дозволений", 405
