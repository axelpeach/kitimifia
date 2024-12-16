import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Отримання токена із секретів
TOKEN = os.getenv("TELEGRAM_TOKEN")

# URL-адреса для вебхука
WEBHOOK_URL = "https://kitimifia.onrender.com"

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привіт! Бот працює.")

# Основний код
def main():
    # Перевірка наявності токена
    if not TOKEN:
        logger.error("Токен Telegram не знайдено. Перевірте змінну оточення TELEGRAM_TOKEN.")
        return

    # Створення застосунку
    application = Application.builder().token(TOKEN).build()

    # Додавання обробника команди /start
    application.add_handler(CommandHandler("start", start))

    # Запуск вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
