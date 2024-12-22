import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler
from collections import defaultdict
from aiohttp import web

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mur_counts = defaultdict(int)

# Завантажуємо токен із змінної середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")

PORT = int(os.getenv("PORT", 10000))  # Порт із середовища, або 10000 за замовчуванням

# Хендлер для команди /start
async def start(update, context):
    await update.message.reply_text("воркаю 🥺")

async def mur_handler(update, context):
    user_first_name = update.effective_user.first_name

    # Якщо передані аргументи до команди
    if context.args:
        try:
            # Перевіряємо, чи є аргумент числом
            new_count = int(context.args[0])
            if new_count < 0:
                await update.message.reply_text("Кількість мурчань не може бути від'ємною.")
                return

            mur_counts[user_first_name] = new_count
            await update.message.reply_text(f"Мурчання оновлено, {user_first_name}! Тепер ви мурчали {new_count} разів.")
        except ValueError:
            await update.message.reply_text("Будь ласка, введіть число для оновлення кількості мурчань.")
    else:
        # Збільшення мурчань, якщо аргументів немає
        mur_counts[user_first_name] += 1
        count = mur_counts[user_first_name]
        await update.message.reply_text(f"Муррр, {user_first_name}! Ви мурчали {count} разів.")
    
# Функція для запуску Telegram-бота
async def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", mur_handler))
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
