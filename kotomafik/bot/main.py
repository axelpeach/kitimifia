import os
import logging
from telegram.ext import Application, CommandHandler
from datetime import datetime, timedelta
import nest_asyncio
import asyncio
import random  # Для генерації випадкових значень

# Патч для асинхронного циклу
nest_asyncio.apply()

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Лічильники мурчань, довжина вусів і часи останньої дії
mur_counts = {}
last_mur_time = {}
usik_lengths = {}
last_usik_time = {}


async def usik(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    now = datetime.now()

    # Перевірка на обмеження часу
    if user_id in last_usik_time:
        elapsed_time = now - last_usik_time[user_id]
        if elapsed_time < timedelta(minutes=20):
            remaining_time = timedelta(minutes=20) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Не все одразу! 🐾\n"
                f"Спробуйте знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього вирощування вусів
    last_usik_time[user_id] = now

    # Ініціалізація довжини вусів, якщо користувач ще не починав
    if user_id not in usik_lengths:
        usik_lengths[user_id] = 0.0

    # Генерація зміни довжини вусів (-7 до +7 мм)
    change = round(random.uniform(-7, 7), 2)
    usik_lengths[user_id] = max(0.0, usik_lengths[user_id] + change)  # Вуса не можуть бути менше 0

    # Відправка повідомлення користувачу
    await update.message.reply_text(
        f"{user_name}, твої вуса {'збільшились' if change > 0 else 'зменшились'} на {abs(change):.2f} мм.\n"
        f"Загальна довжина: {usik_lengths[user_id]:.2f} мм."
    )


async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name}! 🐾\n"
        "Тикни лапкою /help, щоб побачити список доступних команд."
    )


async def help_command(update, context):
    commands = (
        "/start - Почати роботу з ботом.\n"
        "/help - Показати список команд.\n"
        "/murr - Помурчати.\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/about - Про бота.\n"
        "/usik - Виростити котячі вуса."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")


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
                f"Твій мурчальник перегрівся! 🐾\n"
                f"Спробуйте знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    last_mur_time[user_id] = now

    # Оновлення лічильника мурчань
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    await update.message.reply_text(f"{user_name} помурчав! 🐾\nВсього мурчань: {mur_counts[user_id]}.")


async def set_murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_name}, тепер кількість мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("Будь ласка, введіть коректне число. Наприклад: /set_murr 10")


async def status(update, context):
    await update.message.reply_text("Бот працює! 🐾")


# Функція створення Telegram Application
def create_application():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:logger.error("Не вказано TELEGRAM_TOKEN у змінних середовища!")
        exit(1)

    application = Application.builder().token(token).build()

    # Додаємо хендлери команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("set_murr", set_murr))
    application.add_handler(CommandHandler("about", status))
    application.add_handler(CommandHandler("usik", usik))

    return application


# Основна функція запуску бота
def main():
    application = create_application()
    try:
        logger.info("Запуск бота через полінг")
        application.run_polling()
    except Exception as e:
        logger.error(f"Помилка під час роботи бота: {e}")
    finally:
        logger.info("Бот завершив роботу.")


if __name__ == "__main__":
    main()
