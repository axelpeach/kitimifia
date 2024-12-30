import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request
from datetime import datetime, timedelta
import nest_asyncio
import random
import asyncio
import httpx
from threading import Thread

# Патч для асинхронного циклу
nest_asyncio.apply()

# Налаштування логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Лічильники мурчань і час останнього мурчання
mur_counts = {}
last_mur_time = {}

# Дані для вусів
usik_lengths = {}
last_usik_time = {}

# Flask додаток для UptimeRobot
app = Flask(__name__)

@app.route("/")
def home():
    return "Бот працює! 🐾"

@app.route("/webhook/<token>", methods=["POST"])
def webhook(token):
    if token != os.getenv("TELEGRAM_TOKEN"):
        return "Unauthorized", 403

    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, application.bot)

    application.process_update(update)
    return "OK"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Команда /usik
async def usik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    if user_id in last_usik_time:
        elapsed_time = now - last_usik_time[user_id]
        if elapsed_time < timedelta(minutes=20):
            remaining_time = timedelta(minutes=20) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Не все одразу 🐾\nСпробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    last_usik_time[user_id] = now
    if user_id not in usik_lengths:
        usik_lengths[user_id] = 0.0

    change = round(random.uniform(-7, 7), 2)
    usik_lengths[user_id] = max(0.0, usik_lengths[user_id] + change)

    await update.message.reply_text(
        f"{user_name}, твої вуса {'збільшились' if change > 0 else 'зменшились'} на {abs(change):.2f} мм.\n"
        f"Загальна довжина: {usik_lengths[user_id]:.2f} мм."
    )

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name} 🐾\nТикни лапкою /help, щоб побачити список доступних команд."
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = (
        "/start - Почати спілкування з ботом.\n"
        "/help - Показати список команд.\n"
        "/murr - Помурчати.\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/about - Інформація про бота.\n"
        "/usik - Виростити котячі вуса."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")

# Команда /murr
async def murr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Твій мурчальник перегрівся 🐾\nСпробуй знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    last_mur_time[user_id] = now
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    await update.message.reply_text(f"{user_name} помурчав 🐾\nВсього мурчань: {mur_counts[user_id]}.")

# Команда /set_murr
async def set_murr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_name}, тепер кількість мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("Будь ласка, введіть коректне число. Наприклад: /set_murr 10")

# Команда /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Це бот, який допомагає котам мурчати та ростити вуса 🐾.")

# Функція створення Telegram Application
def create_application():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Не вказано TELEGRAM_TOKEN у змінних середовища!")
        exit(1)

    application = Application.builder(). token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("set_murr", set_murr))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("usik", usik))
    return application

# Основна функція запуску бота
def main():
    global application
    application = create_application()

    # Запуск Flask серверу в окремому потоці
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    logger.info("Запуск бота через вебхуки")
 application.run_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path=f"webhook/{os.getenv('TELEGRAM_TOKEN')}",
    webhook_url="https://kitimifia.onrender.com/webhook/{os.getenv('TELEGRAM_TOKEN')}"  # Замість HTTP на HTTPS
)

if __name__ == "__main__":
    main()
