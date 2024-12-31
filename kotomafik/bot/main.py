import os
import logging
from telegram.ext import Application, CommandHandler, ContextTypes, Updater
from datetime import datetime, timedelta
import random
import time
import signal
import sys

# Налаштування логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Лічильники мурчань і час останнього мурчання
mur_counts = {}
last_mur_time = {}

# Дані для вусів
usik_lengths = {}
last_usik_time = {}

# Команда /start
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name} 🐾\nТикни лапкою /help, щоб побачити список доступних команд."
    )

# Команда /help
async def help_command(update, context):
    commands = (
        "/start - Почати спілкування з ботом.\n"
        "/help - Показати список команд.\n"
        "/murr - Помурчати.\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/about - Інформація про бота.\n"
        "/usik - Виростити котячі вуса."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")

# Команда /murr
async def murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    # Перевірка часу останнього мурчання
    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Твій мурчальник перегрівся 🐾\nСпробуй знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлення часу останнього мурчання
    last_mur_time[user_id] = now
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    murr_count = mur_counts[user_id]

    # Перевірка, чи є повідомлення відповіддю на інше
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_name = f"{target_user.first_name} @{target_user.username}" if target_user.username else target_user.first_name
        await update.message.reply_text(
            f"{user_name} помурчав {target_name} на вушко! 🐾 Всього мурчань: {murr_count}"
        )
    else:
        await update.message.reply_text(
            f"{user_name} помурчав! 🐾 Всього мурчань: {murr_count}"
        )

# Команда /set_murr
async def set_murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_name}, тепер кількість мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("Будь ласка, введіть коректне число. Наприклад: /set_murr 10")

# Команда /about
async def about(update, context):
    await update.message.reply_text("бот для мурчання та вирощування вусів, автор приймає донати на картку.")

# Команда /usik
async def usik(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    if user_id in last_usik_time:
        elapsed_time = now - last_usik_time[user_id]
        if elapsed_time < timedelta(minutes=20):
            remaining_time = timedelta(minutes=20) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Не все одразу 🐾\nСпробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    last_usik_time[user_id] = now
    if user_id not in usik_lengths:
        usik_lengths[user_id] = 0.0

    change = round(random.uniform(-7, 7), 2)
    usik_lengths[user_id] = max(0.0, usik_lengths[user_id] + change)

    await update.message.reply_text(f"{user_name}, твої вуса {'збільшились' if change > 0 else 'зменшились'} на {abs(change):.2f} мм.\n"f"Загальна довжина: {usik_lengths[user_id]:.2f} мм."
    )

# Функція створення Telegram Application
def create_application():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Не вказано TELEGRAM_TOKEN у змінних середовища!")
        exit(1)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("set_murr", set_murr))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("usik", usik))
    return application

# Основна функція запуску бота з полінгом
def main():
    application = create_application()
    logger.info("Запуск бота через полінг")

    # Запуск полінгу
    application.run_polling(drop_pending_updates=True, allowed_updates=['message'])

# Функція для перезапуску бота
def restart_bot():
    logger.info("Перезапуск бота...")
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    main()
