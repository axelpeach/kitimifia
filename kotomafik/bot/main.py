import sys
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Додаємо шлях до імпорту
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Словники для збереження даних користувачів
user_mur_count = {}
user_mustache_length = {}

async def mur(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /mur."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Збільшуємо кількість мурчань
    user_mur_count[user_id] = user_mur_count.get(user_id, 0) + 1
    mur_count = user_mur_count[user_id]

    response = f"{user_name} помурчав {mur_count} разів!"
    await update.message.reply_text(response)

async def mustache(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /mustache."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Генеруємо випадкову зміну довжини вусів
    change = round(random.uniform(-7, 7), 2)
    user_mustache_length[user_id] = user_mustache_length.get(user_id, 0) + change
    total_length = user_mustache_length[user_id]

    change_text = f"твої вуса {'збільшились' if change > 0 else 'зменшились'} на {change} мм."
    response = f"{user_name}, {change_text} Загальна довжина: {total_length:.2f} мм."
    await update.message.reply_text(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Відповідає на команду /start."""
    await update.message.reply_text("Привіт! Я ваш котик-бот. Використовуйте /murr або /usik!")

async def main() -> None:
    """Запускає бота."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", mur))
    application.add_handler(CommandHandler("usik", mustache))

    # Запускаємо бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())