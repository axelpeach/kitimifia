import logging
import asyncio
from datetime import datetime
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Змінна для збереження лічильника мурчань
mur_counts = {}

# Хендлер для команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Команда /start отримана від {update.message.from_user.first_name}")
        await update.message.reply_text(f"Привіт, {update.message.from_user.first_name}! Вітаю на борту! 🥳")
    except Exception as e:
        logger.error(f"Помилка при обробці команди /start: {e}")

# Хендлер для команди /murr
async def mur_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_first_name = update.effective_user.first_name
        now = datetime.now()

        logger.info(f"Команда /murr отримана від {user_first_name} ({user_id})")

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
    except Exception as e:
        logger.error(f"Помилка при обробці команди /murr: {e}")

# Функція для обробки вебхука
async def handle_webhook(request):
    try:
        data = await request.json()
        logger.info(f"Отримано дані вебхука: {data}")
        await application.update_queue.put(data)  # ставимо оновлення у чергу
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Помилка при обробці вебхука: {e}")
        return web.Response(text="Error", status=500)

# Налаштування та запуск бота
async def run_telegram_bot():
    try:
        application = Application.builder().token("YOUR_BOT_TOKEN").build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("murr", mur_handler))

        # Запуск бота
        await application.initialize()
        logger.info("Бот запущений та готовий до роботи.")
        await application.start_polling()
    except Exception as e:
        logger.error(f"Помилка при запуску Telegram бота: {e}")

# Запуск UptimeRobot сервісу
async def run_uptime_robot():
    try:
        # Тут ваш код для моніторингу сервісу через UptimeRobot
        pass
    except Exception as e:
        logger.error(f"Помилка при запуску UptimeRobot: {e}")

# Основна функція
async def main():
    try:
        await asyncio.gather(
            run_telegram_bot(),
            run_uptime_robot()
        )
    except Exception as e:
        logger.error(f"Помилка в основній функції: {e}")

# Запуск сервера
if name == '__main__':
    try:
        logger.info("Запуск сервісу...")
        asyncio.run(main())  # викликаємо основну функцію
    except Exception as e:
        logger.error(f"Помилка при запуску сервісу: {e}")
