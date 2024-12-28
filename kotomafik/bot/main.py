import os
import sys
import logging
from fastapi import FastAPI
from telegram.ext import Application, CommandHandler
import uvicorn
import asyncio

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# PID-файл
PID_FILE = "bot.pid"

# Створюємо FastAPI додаток
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Бот працює!"}

# Лічильники мурчань
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
        "/murr - Помурчати 🐾.\n"
        "/set_murr [число] - Встановити кількість мурчань.\n"
        "/status - Перевірити стан бота."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")

# Хендлер для команди /murr
async def murr(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

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

# Функція для запуску Telegram бота
async def start_telegram_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Не вказано TELEGRAM_TOKEN у змінних середовища!")
        return

    application = Application.builder().token(token).build()

    # Додаємо хендлери команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("set_murr", set_murr))
    application.add_handler(CommandHandler("status", status))

    logger.info("Запуск бота в режимі полінгу")
    await application.run_polling()

# Основний запуск
def main():
    if os.path.exists(PID_FILE):
        logger.error("Процес вже запущено! Вихід...")
        sys.exit()

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    try:
        # Запускаємо FastAPI сервер і Telegram бота
        loop = asyncio.get_event_loop()
        loop.create_task(start_telegram_bot())
        logger.info("Запуск FastAPI сервера")
        uvicorn.run(app, host="0.0.0.0", port=8080)

    except Exception as e:
        logger.error(f"Помилка: {e}")

    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

if __name__ == "__main__":
    main()
