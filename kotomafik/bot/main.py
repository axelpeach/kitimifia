import os
import sqlite3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Завантажуємо змінні середовища безпосередньо з Render
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK_API")

# Налаштування логування
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення та підключення до бази даних SQLite
def create_db():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        usik_length REAL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

# Додавання або оновлення користувача
def add_user(user_id, balance, usik_length):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, balance, usik_length)
    VALUES (?, ?, ?)
    """, (user_id, balance, usik_length))

    conn.commit()
    conn.close()

# Отримання даних користувача
def get_user_data(user_id):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

# Команда /donate
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Повідомлення з посиланням на банку
    donate_link = "https://send.monobank.ua/jar/5yxJsnYG82"
    await update.message.reply_text(f"Щоб зробити донат, використай це посилання: {donate_link}. У коментарі вкажи свій ID: {user_id}.")

# Команда /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    # Отримуємо дані користувача з бази
    data = get_user_data(user_id)

    if data:
        balance = data[1]
        usik_length = data[2]
        await update.message.reply_text(f"Твій баланс: {balance} MurrCoins.\nДовжина вусів: {usik_length:.2f} мм.")
    else:
        await update.message.reply_text("Ти ще не зробив донатів, будь ласка, зроби це через команду /donate.")

# Команда /spend
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    # Перевірка наявності аргументу з кількістю MurrCoins для витрати
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажи кількість MurrCoins, які ти хочеш витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])

    # Отримуємо дані користувача з бази
    data = get_user_data(user_id)

    if not data:
        await update.message.reply_text("У тебе немає жодних муркоїнів. Спершу зроби донат.")
        return

    balance = data[1]

    # Перевіряємо, чи достатньо монет
    if balance < amount:
        await update.message.reply_text(f"У тебе недостатньо MurrCoins для цієї витрати. Твій баланс: {balance} MurrCoins.")
        return

    # Знімаємо монети з балансу та додаємо довжину вусів
    usik_length = data[2]
    new_usik_length = usik_length + (amount * 5)  # Додаємо 5 мм за кожен витрачений MurrCoin
    new_balance = balance - amount

    # Оновлюємо дані користувача в базі
    add_user(user_id, new_balance, new_usik_length)

    # Повідомлення про успішну витрату
    await update.message.reply_text(
        f"Ти витратив {amount} MurrCoins і твої вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер твій баланс: {new_balance} MurrCoins.\n"
        f"Загальна довжина твоїх вусів: {new_usik_length:.2f} мм."
    )

# Запуск бота
def main():
    # Створюємо базу даних, якщо її ще немає
    create_db()

    # Налаштовуємо бота
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))

    # Запуск бота
    application.run_polling()

# Запуск бота
if __name__ == "__main__":
    main()
