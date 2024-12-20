import os
import logging
import asyncio
from aiohttp import web
from telegram.ext import Application, CommandHandler

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Завантаження токена Telegram і порту
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8080))  # Render надає порт через змінну середовища

# Telegram команда /start
async def start(update, context):
    await update.message.reply_text("Бот працює!")

# Основна функція Telegram бота
async def run_telegram_bot():
    # Створення Telegram застосунку
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Реєстрація команди
    application.add_handler(CommandHandler("start", start))

    # Запуск Telegram polling
    logger.info("Запускаємо Telegram polling...")
    await application.run_polling()

# Основна функція UptimeRobot
async def run_uptime_server():
    async def handle_healthcheck(request):
        return web.Response(text="Бот працює!")

    app = web.Application()
    app.router.add_get("/", handle_healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    # Сервер слухає на вказаному порту
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    logger.info(f"UptimeRobot сервер запущено на порту {PORT}")
    await site.start()

# Головна функція
async def main():
    # Запускаємо два процеси паралельно
    await asyncio.gather(
        run_uptime_server(),
        run_telegram_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
