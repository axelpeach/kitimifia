import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Отримання токена із секретів
TOKEN = os.getenv("TELEGRAM_TOKEN")

# URL-адреса для вебхука
WEBHOOK_URL = "https://your-app-name.onrender.com/webhook"

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
