import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram.ext import Application, CommandHandler
import asyncio

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Лічильники мурчань
mur_counts = defaultdict(int)
last_mur_time = {}

# Завантаження токена
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")

# Хендлер для команди /start
async def start(update, context):
    user = update.effective_user
    logger.info(f"Команда /start отримана від {user.first_name} (ID: {user.id})")
    try:
        await update.message.reply_text("Воркаю")
        logger.info("Відповідь на команду /start успішно надіслана.")
    except Exception as e:
        logger.error(f"Помилка під час відправки повідомлення: {e}")

# Хендлер для команди /murr
async def mur_handler(update, context):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    now = datetime.now()

    logger.info(f"Команда /murr отримана від {user_first_name} ({user_id})")

    # Перевірка часу для обмеження мурчань
    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            logger.info(f"{user_first_name} спробував помурчати занадто рано.")
            await update.message.reply_text(
                f"Твой мурчальнік перегрівся, зачекай {remaining_time.seconds // 60} хвилин та {remaining_time.seconds % 60} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    last_mur_time[user_id] = now

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

# Основна функція для запуску бота
async def main():
    # Створюємо об'єкт програми
    application = Application.builder().token(TOKEN).build()

    # Додаємо хендлери
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", mur_handler))

    logger.info("Запуск бота в режимі полінгу")
    # Запускаємо polling з коректним закриттям
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await application.updater.idle()  # Чекаємо зупинки
    finally:
        logger.info("Завершення роботи бота...")
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинено.")
