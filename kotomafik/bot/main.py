import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler
from aiohttp import web

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Завантажуємо токен із змінної середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")

PORT = int(os.getenv("PORT", 10000))  # Порт із середовища, або 10000 за замовчуванням

# Хендлер для команди /start
async def start(update, context):
    await update.message.reply_text("Привіт! Я твій бот.")

# Функція для запуску Telegram-бота
async def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    logger.info("Запускаємо Telegram polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Запускаємо polling
    await asyncio.Event().wait()  # Блокуючий виклик для утримання програми активною

# Функція для UptimeRobot
async def handle_uptime(request):
    return web.Response(text="UptimeRobot працює!")

async def run_uptime_robot():
    app = web.Application()
    app.router.add_get("/", handle_uptime)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"UptimeRobot сервер запущено на порту {PORT}")
    while True:
        await asyncio.sleep(3600)  # Утримуємо сервер активним

# Головна функція
async def main():
    await asyncio.gather(
        run_telegram_bot(),
        run_uptime_robot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинено.")
