import os
import sqlite3
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    JobQueue,
)

# Завантаження змінних середовища
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK_API")
JAR_LINK = "https://send.monobank.ua/jar/5yxJsnYG82"

# Підключення до SQLite
DB_NAME = "bot_data.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# Ініціалізація таблиці
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0,
        usik_length REAL DEFAULT 0
    )
    """
)
conn.commit()


# Додати користувача
def add_user(user_id: int, username: str):
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
        (user_id, username),
    )
    conn.commit()


# Отримати користувача
def get_user(user_id: int):
    cursor.execute(
        "SELECT username, balance, usik_length FROM users WHERE id = ?", (user_id,)
    )
    return cursor.fetchone()


# Оновити баланс
def update_balance(user_id: int, amount: int):
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id)
    )
    conn.commit()


# Оновити довжину вусів
def update_usik_length(user_id: int, length: float):
    cursor.execute(
        "UPDATE users SET usik_length = usik_length + ? WHERE id = ?", (length, user_id)
    )
    conn.commit()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "невідомий котик")
    await update.message.reply_text("Привіт! Я в говно 🐾")


# Команда /donate
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "невідомий котик")
    code = str(user.id)
    await update.message.reply_text(
        f"Щоб задонатити, переходь за посиланням {JAR_LINK} і додай цей код у коментар: {code}"
    )


# Команда /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user.id)
    if data:
        username, balance, usik_length = data
        await update.message.reply_text(
            f"Твій баланс: {balance} MurrCoins 🪙\n"
            f"Довжина вусів: {usik_length:.2f} мм 🐾"
        )
    else:
        await update.message.reply_text("Тебе не знайдено в системі!")


# Команда /spend
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Вкажи кількість MurrCoins. Наприклад, /spend 10")
        return

    amount = int(context.args[0])
    data = get_user(user.id)
    if data:
        username, balance, usik_length = data
        if balance >= amount:
            update_balance(user.id, -amount)
            update_usik_length(user.id, amount * 5)
            await update.message.reply_text(
                f"Ти витратив {amount} MurrCoins! Твої вуса виросли на {amount * 5} мм 🐾"
            )
        else:
            await update.message.reply_text("Недостатньо MurrCoins!")
    else:
        await update.message.reply_text("Тебе не знайдено в системі!")


# Перевірка донатів
async def check_donations(context: CallbackContext):
    headers = {"X-Token": MONOBANK_API}
    response = requests.get("https://api.monobank.ua/personal/statement/0", headers=headers)
    if response.status_code == 200:
        transactions = response.json()
        for transaction in transactions:
            if "comment" in transaction and transaction["comment"].isdigit():
                user_id = int(transaction["comment"])
                amount = transaction["amount"] // 100
                update_balance(user_id, amount)


# Запуск бота
def main():
    application = ApplicationBuilder().token(TOKEN).build()

# Додати команди
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))

    # Налаштування JobQueue
    job_queue = application.job_queue
    job_queue.run_repeating(check_donations, interval=60, first=10)

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
