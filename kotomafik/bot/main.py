import logging
import os
import asyncio
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

    # Створення бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", murr))

    # Запуск бота через polling
    await application.run_polling()

# Перевірка та запуск event loop
if __name__ == "__main__":
    try:
        # Якщо event loop уже існує, використовуємо його
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # Якщо event loop не існує, створюємо новий
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Запускаємо основну функцію
    loop.run_until_complete(main())
