import os
import requests
import sqlite3
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import asyncio

# Налаштування для роботи з Monobank API та Telegram
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK")
DATABASE_PATH = 'user_data.db'  # шлях до бази даних

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Підключення до бази даних SQLite
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

# Функція для отримання даних користувача з бази
def get_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Функція для додавання нового користувача в базу
def add_user(user_id, balance, usik_length):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, balance, usik_length) VALUES (?, ?, ?)", 
                   (user_id, balance, usik_length))
    conn.commit()
    conn.close()

# Функція для оновлення балансу користувача
def update_balance(user_id, balance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance, user_id))
    conn.commit()
    conn.close()

# Функція для отримання транзакцій з Monobank API
def get_transactions():
    url = "https://api.monobank.ua/personal/statement"
    headers = {
        "X-Token": MONOBANK_API
    }

    params = {
        "from": "2025-01-01",  # Наприклад, з 1 січня
        "to": "2025-01-22",  # до сьогодні
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("Error fetching transactions: %s", response.text)
        return []

# Функція для обробки донатів
def process_donations():
    transactions = get_transactions()

    for transaction in transactions:
        if transaction['comment']:
            user_id = transaction['comment']  # Коментар містить ID користувача
            if user_id.isdigit():
                amount = transaction['sum'] // 10  # 10 грн = 1 муркоїн

                # Оновлюємо баланс користувача
                user_data = get_user_data(user_id)
                if user_data:
                    new_balance = user_data[1] + amount
                    update_balance(user_id, new_balance)
                    logger.info(f"User {user_id} has been credited {amount} MurrCoins.")
                else:
                    logger.info(f"User {user_id} not found in the database.")

# Функція для запуску періодичного моніторингу транзакцій
async def check_donations():
    while True:
        process_donations()
        await asyncio.sleep(60)  # Перевірка кожні 60 секунд

# Команда /donate для генерації посилання на Monobank
def donate(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Генерація посилання для донату
    link = "https://send.monobank.ua/jar/5yxJsnYG82"
    comment = f"Ваш коментар: {user_id}"  # ID користувача у коментарі

    response_text = f"Для того, щоб зробити донат, використовуйте це посилання:\n{link}\n\n" \
                    f"Не забудьте вказати свій ID користувача ({user_id}) в коментарі до платежу."

    update.message.reply_text(response_text)

# Команда /balance для перегляду балансу користувача
def balance(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    user_data = get_user_data(user_id)
    if user_data:
        balance = user_data[1]
        update.message.reply_text(f"Ваш баланс: {balance} MurrCoins.")
    else:
        update.message.reply_text("Ви ще не зробили жодного донату. Спробуйте це зробити через /donate.")

# Команда /spend для витрат муркоїнів на вуса
def spend(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Перевіряємо, чи вказана кількість MurrCoins для витрати
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Будь ласка, вкажіть кількість MurrCoins, які ви хочете витратити.")
        return

    amount = int(context.args[0])

    user_data = get_user_data(user_id)
    if user_data and user_data[1] >= amount:
        new_balance = user_data[1] - amount
        new_usik_length = user_data[2] + (amount * 5)

        # Оновлюємо базу даних
        update_balance(user_id, new_balance)
        update_user_length(user_id, new_usik_length)

        update.message.reply_text(f"Ви витратили {amount} MurrCoins і ваші вуса виросли на {amount * 5} мм!")
    else:
        update.message.reply_text("У вас недостатньо MurrCoins для цієї витрати.")

# Основна функція для запуску бота
def start_bot():
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("donate", donate))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("spend", spend))

    # Запускаємо бота
    updater.start_polling()
    updater.idle()

# Запуск моніторингу донатів
async def main():
    await check_donations()

if __name__ == '__main__':
    start_bot()
    asyncio.run(main())
