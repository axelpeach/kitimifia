import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.DEBUG)  # Включаємо детальне логування

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # Використовуємо порт із змінних середовища
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в змінних середовища!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює!")

async def main():
    logging.info(f"Використовуємо порт: {PORT}")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    async def handle_update(request):
        json_data = await request.json()
        await application.update_queue.put(json_data)
        return web.Response()

    app = web.Application()
    app.router.add_post("/", handle_update)

    logging.info(f"Налаштовуємо вебхук на URL: {WEBHOOK_URL}")
    await application.bot.set_webhook(WEBHOOK_URL)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    logging.info(f"Запускаємо сервер на {PORT}...")
    await site.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
