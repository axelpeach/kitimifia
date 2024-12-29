import os
import logging
from telegram.ext import Application, CommandHandler
from datetime import datetime, timedelta
import asyncio

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Лічильники мурчань і час останнього мурчання
mur_counts = {}
last_mur_time = {}

# Хендлер для команди /start
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name}! 🐾\n"
        "Я ваш помічник. Введіть /help, щоб побачити список доступних команд."
    )

# Хендлер для команди /help
async def help_command(update, context):
    commands = (
        "/start - Почати спілкування з ботом.\n"
        "/help - Показати список команд і їх функціонал.\n"
        "/murr - Помурчати 🐾 (раз на 10 хвилин).\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/status - Перевірити стан бота."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")

# Хендлер для команди /murr
async def murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    # Перевірка на обмеження часу
    if user_id in last_mur_time:
        elapsed_time = now - last_mur_time[user_id]
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Ваш мурчальник перегрівся 🐾! Спробуйте знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    last_mur_time[user_id] = now

    # Оновлення лічильника мурчань
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    await update.message.reply_text(f"{user_name} помурчав 🐾! Всього мурчань: {mur_counts[user_id]}.")

# Хендлер для команди /set_murr
async def set_murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_name}, тепер кількість мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("Будь ласка, введіть коректне число. Наприклад: /set_murr 10")

# Хендлер для команди /status
async def status(update, context):
    await update.message.reply_text("Бот працює! 🐾")

# Функція створення Telegram Application
def create_application():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Не вказано TELEGRAM_TOKEN у змінних середовища!")
        exit(1)
    
    application = Application.builder().token(token).build()

    # Додаємо хендлери команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("set_murr", set_murr))
    application.add_handler(CommandHandler("status", status))

    return application

# Основна функція запуску бота
async def run_bot():
    application = create_application()
    logger.info("Запуск бота через полінг")
    await application.initialize()
    await application.start()
    try:
        await application.run_polling()
    except asyncio.CancelledError:
        logger.info("Зупинка полінгу")
    finally:
        await application.stop()
        await application.shutdown()
        logger.info("Бот завершив роботу.")

if __name__ == "__main__":
    # Отримуємо поточний цикл подій (підтримка середовищ із активним циклом)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Роботу бота перервано вручну.")
