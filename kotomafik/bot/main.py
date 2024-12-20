import os
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в середовищі!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущено!")

async def handle(request):
    return web.Response(text="OK")

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # Запуск веб-сервера
    app = web.Application()
    app.router.add_post("/", application.update_queue.put)

    # Встановлення вебхука
    async with application:
        await application.bot.set_webhook(WEBHOOK_URL)
        runner = web.AppRunner(app)
        await runner.setup()

        port = int(os.environ.get("PORT", 443))  # Використовуємо стандартний HTTPS порт
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()

        print(f"Сервер запущено на порту {port}.")
        await application.start()
        await application.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
