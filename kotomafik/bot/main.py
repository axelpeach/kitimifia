import os
import logging
from telegram.ext import Application, CommandHandler
from datetime import datetime, timedelta
import nest_asyncio

# Патч для асинхронного циклу (усуває проблему "RuntimeError: Cannot close a running event loop")
nest_asyncio.apply()

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
        f"привіт, {user.first_name} 🐾\n"
        "натисни /help, щоб побачити список доступних команд."
    )

# Хендлер для команди /help
async def help_command(update, context):
    commands = (
        "/start - не більше ніж старт \n"
        "/help - список команд \n"
        "/murr - мурчання раз на 10хв \n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/about - про бота \n"
        "/usik - coming soon"
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
                f"ndsq мурчальник перегрівся 🐾! \n спробуй ще через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    last_mur_time[user_id] = now

    # Оновлення лічильника мурчань
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    await update.message.reply_text(f"{user_name} помурчав 🐾!\n Всього мурчань: {mur_counts[user_id]}.")

# Хендлер для команди /set_murr
async def set_murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_name} чітер. \n всього мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("Будь ласка, введіть коректне число. Наприклад: /set_murr 10")

# Хендлер для команди /status
async def status(update, context):
    await update.message.reply_text("накидайте ідей що написати сюди в розділ про бота")

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
    application.add_handler(CommandHandler("about", status))

    return application

# Основна функція запуску бота
async def main():
    application = create_application()
    try:
        logger.info("Запуск бота через полінг")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Помилка під час роботи бота: {e}")
    finally:
        logger.info("Бот завершив роботу.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
