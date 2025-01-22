import os
import sqlite3
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Завантаження змінних середовища
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK")
JAR_LINK = "https://send.monobank.ua/jar/5yxJsnYG82"

# Ініціалізація бази даних
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        murrcoins INTEGER DEFAULT 0,
        usik_length INTEGER DEFAULT 0
    )
    """
)
conn.commit()


# Перевірка донатів
async def check_donations(application):
    while True:
        try:
            response = requests.get(
                "https://api.monobank.ua/personal/statement/0",
                headers={"X-Token": MONOBANK_API},
            )
            if response.status_code == 200:
                transactions = response.json()
                for transaction in transactions:
                    if "comment" in transaction:
                        comment = transaction["comment"]
                        amount = transaction["amount"] // 100  # сума в гривнях
                        user_id = int(comment) if comment.isdigit() else None

                        if user_id:
                            cursor.execute(
                                "UPDATE users SET murrcoins = murrcoins + ? WHERE user_id = ?",
                                (amount, user_id),
                            )
                            conn.commit()
        except Exception as e:
            print(f"Error checking donations: {e}")
        await asyncio.sleep(60)  # Перевіряти кожну хвилину


# Команда /donate
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Щоб задонатити, перейдіть за посиланням {JAR_LINK}.\n"
        f"У коментарі до платежу вкажіть ваш Telegram ID: {update.effective_user.id}."
    )


# Команда /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT murrcoins FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"Ваш баланс: {result[0]} MurrCoins.")
    else:
        await update.message.reply_text("У вас ще немає MurrCoins. Зробіть донат, щоб отримати їх!")


# Команда /spend
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Вкажіть кількість MurrCoins, які хочете витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])
    cursor.execute("SELECT murrcoins, usik_length FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result or result[0] < amount:
        await update.message.reply_text("Недостатньо MurrCoins для витрати.")
        return

    new_balance = result[0] - amount
    new_usik_length = result[1] + (amount * 5)

    cursor.execute(
        "UPDATE users SET murrcoins = ?, usik_length = ? WHERE user_id = ?",
        (new_balance, new_usik_length, user_id),
    )
    conn.commit()

    await update.message.reply_text(
        f"Ви витратили {amount} MurrCoins і ваші вуса виросли на {amount * 5} мм!\n"
        f"Новий баланс: {new_balance} MurrCoins.\n"
        f"Загальна довжина вусів: {new_usik_length} мм."
    )


# Ініціалізація бота
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))

    # Запуск перевірки донатів у фоновому режимі
    asyncio.create_task(check_donations(application))

    # Запуск бота
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
