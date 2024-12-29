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

# Лічильники мурчань і час останнього мурчання
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
                f"не все одразу \n"
                f"спробуй через {minutes} хвилин та {seconds} секунд."
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
        f"{user_first}, твої вуса {'збільшились' if change > 0 else 'зменшились'} на {abs(change):.2f} мм.\n"
        f"Загальна довжина: {usik_lengths[user_id]:.2f} мм. 🧔‍♂️"
    )

# Хендлер для команди /start
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name} 🐾\n"
        "тикни лапкою /help, щоб побачити список доступних команд."
    )

# Хендлер для команди /help
async def help_command(update, context):
    commands = (
        "/start - не більше ніж старт.\n"
        "/help - показати список команд.\n"
        "/murr - помурчати.\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/about - про бота"
        "/usik - растіть усікі"
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
                f"твій мурчальник перегрівся 🐾 /nСпробуйте знову через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    last_mur_time[user_id] = now

    # Оновлення лічильника мурчань
    mur_counts[user_id] = mur_counts.get(user_id, 0) + 1
    await update.message.reply_text(f"{user_name} помурчав 🐾 /nВсього мурчань: {mur_counts[user_id]}.")

# Хендлер для команди /set_murr
async def set_murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if context.args and context.args[0].isdigit():
        mur_counts[user_id] = int(context.args[0])
        await update.message.reply_text(f"{user_first} чітір /nтепер кількість мурчань: {mur_counts[user_id]}.")
    else:
        await update.message.reply_text("ха ||лох|| будь ласка, введи коректне число. Наприклад: /set_murr 10")

# Хендлер для команди /status
async def status(update, context):
    await update.message.reply_text("придумйте самі що тут буде але краще б картка розробника")

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
    application.add_handler(CommandHandler("usik", usik))

    return application

# Основна функція запуску бота
def main():
    application = create_application()

    try:
        logger.info("Запуск бота через полінг")
        asyncio.run(application.run_polling())
    except Exception as e:
        logger.error(f"Помилка під час роботи бота: {e}")
    finally:
        logger.info("Бот завершив роботу.")

if __name__ == "__main__":
    main()
