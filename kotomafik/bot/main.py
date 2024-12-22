import os
import asyncio
import logging
import logging
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler
from collections import defaultdict
from aiohttp import web

logging.basicConfig(level=logging.DEBUG)
# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mur_counts = defaultdict(int)

# Словник для зберігання часу останнього виклику команди кожним користувачем
last_mur_time = {}

# Завантажуємо токен із змінної середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")

PORT = int(os.getenv("PORT", 10000))  # Порт із середовища, або 10000 за замовчуванням

# Хендлер для команди /start
async def start(update, context):
    await update.message.reply_text("воркаю 🥺")

async def mur_handler(update, context):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name

    # Поточний час
    now = datetime.now()

    # Перевірка часу останнього виклику
    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            await update.message.reply_text(
                f"твой мурчальнік перегрівся, зачекай {remaining_time.seconds // 60} хвилин та {remaining_time.seconds % 60} секунд."
            )
            return

    # Оновлюємо час останнього виклику
    last_mur_time[user_id] = now

    # Обробка аргументів та мурчання
    if context.args:
        try:
            new_count = int(context.args[0])
            if new_count < 0:
                await update.message.reply_text("Кількість мурчань не може бути від'ємною.")
                return

            mur_counts[user_first_name] = new_count
            await update.message.reply_text(f"{user_first_name} чітер! Всього мурчань: {new_count}")
        except ValueError:
            await update.message.reply_text("Будь ласка, введіть число для оновлення кількості мурчань🐾.")
    else:
        mur_counts[user_first_name] += 1
        count = mur_counts[user_first_name]
        await update.message.reply_text(f"{user_first_name} помурчав 🐾. Всього мурчань: {count}.")
    
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
