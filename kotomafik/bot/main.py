import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Налаштування логів
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо токен з оточення
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))  # Порт для UptimeRobot

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не заданий у змінних середовища!")

# Хендлер для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює через polling!")

# Маршрут для UptimeRobot
async def health_check(request):
    return web.Response(text="Бот працює!")

# Функція запуску бота
async def start_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Запускаємо polling у фоновому режимі
    logger.info("Запускаємо Telegram polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

# Функція запуску UptimeRobot сервера
async def start_uptimerobot():
    app = web.Application()
    app.router.add_get("/", health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    logger.info(f"UptimeRobot сервер запущено на порту {PORT}")
    await site.start()

# Основна функція
async def main():
    await start_bot()  # Запуск polling
    await start_uptimerobot()  # Запуск UptimeRobot сервера
    await web.AppRunner(web.Application()).cleanup()  # Чекаємо на завершення

if __name__ == "__main__":
    import asyncio

    # Запускаємо подіївий цикл
    asyncio.run(main())
