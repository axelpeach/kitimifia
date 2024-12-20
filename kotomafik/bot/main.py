import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web
import asyncio

# Налаштування логів
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо токен з оточення
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не заданий в середовищі!")

# Хендлер для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот працює через polling!")

# Маршрут для UptimeRobot
async def health_check(request):
    return web.Response(text="Бот працює!")

# Основна функція
async def main():
    # Створюємо застосунок
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))

    # Запускаємо сервер для UptimeRobot
    app = web.Application()
    app.router.add_get("/", health_check)  # Кореневий маршрут для перевірки
    runner = web.AppRunner(app)
    await runner.setup()

    # Динамічно визначаємо порт для сервера
    port = int(os.getenv("PORT", 8080))  # Render зазвичай використовує PORT
    site = web.TCPSite(runner, "0.0.0.0", port)
    logger.info(f"UptimeRobot сервер запущено на порту {port}")
    await site.start()

    # Запускаємо polling у фоновому режимі
    asyncio.create_task(application.run_polling())
    await asyncio.Event().wait()  # Тримаємо подіївий цикл активним

if __name__ == "__main__":
    asyncio.run(main())
