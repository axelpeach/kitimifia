import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Лічильники мурчань
mur_counts = defaultdict(int)
last_mur_time = {}

# Завантаження токена
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Не знайдено змінної середовища TELEGRAM_TOKEN")


# Хендлер для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Команда /start отримана від {user.first_name} (ID: {user.id})")
    await update.message.reply_text("Воркаю 🐾")


# Хендлер для команди /murr
async def mur_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    now = datetime.now()

    logger.info(f"Команда /murr отримана від {user_first_name} ({user_id})")

    # Перевірка часу для обмеження мурчань
    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
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
async def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Додаємо хендлери
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", mur_handler))

    try:
        logger.info("Запуск бота в режимі полінгу")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Помилка при роботі бота: {e}")
    finally:
        await application.shutdown()  # Коректно завершуємо роботу


# Функція для запуску циклу
def start_bot():
    while True:
        try:
            asyncio.run(run_bot())
        except RuntimeError as e:
            logger.warning(f"RuntimeError: {e}")
            asyncio.set_event_loop(asyncio.new_event_loop())  # Встановлюємо новий цикл подій
        except Exception as e:
            logger.error(f"Непередбачена помилка: {e}")
        finally:
            logger.info("Чекаємо 5 секунд перед перезапуском...")
            asyncio.sleep(5)


if __name__ == "__main__":
    start_bot()
