import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler
from collections import defaultdict

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mur_counts = defaultdict(int)
last_mur_time = {}

# Завантажуємо токен і домен із змінних середовища
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # Порт сервера

if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")

# Хендлер для команди /start
async def start(update, context):
    logger.info(f"Команда /start отримана від {update.message.from_user.first_name}")
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Воркаю"
        )
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
            logger.info(f"Від {user_first_name}: залишилось часу для наступного мурчання: {remaining_time}")
            await update.message.reply_text(
                f"Твой мурчальнік перегрівся, зачекай {remaining_time.seconds // 60} хвилин та {remaining_time.seconds % 60} секунд."
            )
            return

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

# Функція для запуску Telegram бота
async def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", mur_handler))

    # Запуск полінгу
    await application.run_polling()

# Головна функція
def main():
    # Запуск бота (полінг)
    asyncio.run(run_telegram_bot())

if __name__ == "__main__":
    try:
        main()  # Тепер викликаємо без asyncio.run() в основній функції
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинено.")
