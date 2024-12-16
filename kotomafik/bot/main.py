import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Встановлення логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("воркаю")

# Команда /murr
async def murr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"{user.first_name} помурчав!🐾")

# Основна функція для запуску бота
async def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL вашого вебхука (домен Render)

    if not TELEGRAM_TOKEN or not WEBHOOK_URL:
        logger.error("TELEGRAM_TOKEN або WEBHOOK_URL не задані в середовищі!")
        return

    # Створення бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", murr))

    # Запуск вебхука
    await application.run_webhook(
        listen="0.0.0.0",  # Вказуємо, що приймаємо всі підключення
        port=8443,         # Порт для вебхука (Render відкриває 8443)
        webhook_url="https://kitimifia.onrender.com",  # Ваш вебхук URL
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
