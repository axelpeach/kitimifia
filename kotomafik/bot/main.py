import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Зчитуємо змінні середовища
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в середовищі!")

# Створюємо Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Обробник для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущений і працює через вебхук!")

# Додаємо обробник
application.add_handler(CommandHandler("start", start))

async def main():
    # Запускаємо вебхук
    await application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
