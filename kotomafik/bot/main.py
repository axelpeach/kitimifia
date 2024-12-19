import os
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Зчитуємо TELEGRAM_TOKEN і порт з оточення
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # За замовчуванням порт 8000, якщо змінна PORT не задана
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL вебхука (потрібно налаштувати в Telegram)

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise ValueError("TELEGRAM_TOKEN або WEBHOOK_URL не задані в змінних середовища!")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює!")

# Основна функція
async def main():
    # Створюємо додаток Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Реєструємо команду /start
    application.add_handler(CommandHandler("start", start))

    # Створюємо веб-сервер
    async def handle_update(request):
        json_data = await request.json()
        await application.update_queue.put(json_data)
        return web.Response()

    # Налаштовуємо веб-сервер
    app = web.Application()
    app.router.add_post("/", handle_update)

    # Встановлюємо вебхук
    await application.bot.set_webhook(WEBHOOK_URL)

    # Запускаємо веб-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"Бот запущено. Слухаємо порт {PORT}...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
