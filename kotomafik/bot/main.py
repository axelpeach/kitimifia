import os
import asyncio
from telegram.ext import Application, CommandHandler

# Зчитуємо змінні середовища
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в середовищі!")

# Створюємо екземпляр Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Обробник команди /start
async def start(update, context):
    await update.message.reply_text("Бот активований!")

# Реєструємо обробник команди
application.add_handler(CommandHandler("start", start))

async def main():
    # Запускаємо вебхук
    await application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=WEBHOOK_URL,
    )

# Запускаємо у вже існуючому циклі подій
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except RuntimeError as e:
        if str(e) == "This event loop is already running":
            asyncio.run(main())
        else:
            raise
