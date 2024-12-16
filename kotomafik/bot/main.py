import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Встановлення логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
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
    # Токен для доступу до вашого бота, можна використовувати секрети
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Створення додатку та додавання команд
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", murr))

    # Запуск polling для обробки повідомлень
    await application.run_polling()

# Запуск бота
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
