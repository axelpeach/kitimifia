import os
import random
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import Updater
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Отримуємо токен бота з .env файлу
API_TOKEN = os.getenv('API_TOKEN')

# Логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення глобальної змінної для зберігання даних користувачів
user_data = {}

# Команда /donate для донатів
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)

    # Генерація випадкового значення для донату
    donation_amount = random.randint(10, 100)  # Можна змінити діапазон
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    # Додаємо MurrCoins до балансу
    user_data[user_id]['balance'] += donation_amount
    
    # Відповідаємо користувачу
    await update.message.reply_text(
        f"Дякуємо за донат! Ви отримали {donation_amount} MurrCoins! 🐾\n"
        f"Ваш новий баланс: {user_data[user_id]['balance']} MurrCoins."
    )

# Команда /balance для перегляду балансу
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    
    # Перевіряємо чи користувач має дані в user_data
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    balance = user_data[user_id]['balance']
    await update.message.reply_text(f"Ваш баланс: {balance} MurrCoins 🐾")

# Команда /spend для витрат
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    
    # Перевірка, чи вказана кількість монет
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажіть кількість MurrCoins, яку хочете витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])
    
    # Перевіряємо баланс користувача
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    balance = user_data[user_id]['balance']
    
    # Якщо баланс менший за витрату
    if balance < amount:
        await update.message.reply_text(f"У вас недостатньо MurrCoins для цієї витрати. Ваш баланс: {balance} MurrCoins.")
        return
    
    # Витрачаємо MurrCoins і додаємо вуса
    user_data[user_id]['balance'] -= amount
    user_data[user_id]['usik_length'] += amount * 5  # 5 мм за кожен витрачений MurrCoin
    
    # Повідомлення після витрати
    await update.message.reply_text(
        f"Ви витратили {amount} MurrCoins і ваші вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер ваш баланс: {user_data[user_id]['balance']} MurrCoins.\n"
        f"Загальна довжина ваших вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )

# Створення та запуск бота
async def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Реєстрація команд
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))
    
    # Запуск бота
    await application.run_polling()

if name == "__main__":
    import asyncio
    asyncio.run(main())import os
import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import Updater
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Отримуємо токен бота з .env файлу
API_TOKEN = os.getenv('API_TOKEN')

# Логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення глобальної змінної для зберігання даних користувачів
user_data = {}

# Команда /donate для донатів
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)

    # Генерація випадкового значення для донату
    donation_amount = random.randint(10, 100)  # Можна змінити діапазон
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    # Додаємо MurrCoins до балансу
    user_data[user_id]['balance'] += donation_amount
    
    # Відповідаємо користувачу
    await update.message.reply_text(
        f"Дякуємо за донат! Ви отримали {donation_amount} MurrCoins! 🐾\n"
        f"Ваш новий баланс: {user_data[user_id]['balance']} MurrCoins."
    )

# Команда /balance для перегляду балансу
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    
    # Перевіряємо чи користувач має дані в user_data
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    balance = user_data[user_id]['balance']
    await update.message.reply_text(f"Ваш баланс: {balance} MurrCoins 🐾")

# Команда /spend для витрат
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    
    # Перевірка, чи вказана кількість монет
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажіть кількість MurrCoins, яку хочете витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])
    
    # Перевіряємо баланс користувача
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0, 'usik_length': 0}
    
    balance = user_data[user_id]['balance']
    
    # Якщо баланс менший за витрату
    if balance < amount:
        await update.message.reply_text(f"У вас недостатньо MurrCoins для цієї витрати. Ваш баланс: {balance} MurrCoins.")
        return
    
    # Витрачаємо MurrCoins і додаємо вуса
    user_data[user_id]['balance'] -= amount
    user_data[user_id]['usik_length'] += amount * 5  # 5 мм за кожен витрачений MurrCoin
    
    # Повідомлення після витрати
    await update.message.reply_text(
        f"Ви витратили {amount} MurrCoins і ваші вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер ваш баланс: {user_data[user_id]['balance']} MurrCoins.\n"
        f"Загальна довжина ваших вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )

# Створення та запуск бота
async def main():
    application = Application.builder().token(TOKEN).build()
    
    # Реєстрація команд
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))
    
    # Запуск бота
    await application.run_polling()

if name == "__main__":
    asyncio.run(main())
