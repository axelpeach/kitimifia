import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Зчитуємо змінні середовища
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8443"))

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в середовищі!")

# Створюємо Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Обробник для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює через вебхук!")

# Додаємо обробник
application.add_handler(CommandHandler("start", start))

# Створюємо HTTP-сервер для Render
async def health_check(request):
    return web.Response(text="Бот працює!")

app = web.Application()
app.router.add_get("/", health_check)

async def main():
    # Запускаємо Telegram Application
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )
    print(f"Бот запущено на вебхуку: {WEBHOOK_URL}")

    # Запускаємо HTTP-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# Запускаємо
import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
