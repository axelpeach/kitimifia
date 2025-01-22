import os
import sqlite3
import asyncio
import requests
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Завантаження змінних середовища
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL вашого сервера
JAR_LINK = "https://send.monobank.ua/jar/5yxJsnYG82"

# Ініціалізація Flask для обробки вебхуків
app = Flask(__name__)

# Ініціалізація бази даних
conn = sqlite3.connect("bot_data.db", check_same_thread=False)
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


# Реєстрація вебхука в Монобанку
def register_monobank_webhook():
    if not MONOBANK_API:
        print("Помилка: MONOBANK_API не встановлено у середовищі!")
        return

    headers = {"X-Token": MONOBANK_API, "Content-Type": "application/json"}
    data = {"webHookUrl": f"{WEBHOOK_URL}/monobank-webhook"}
    response = requests.post("https://api.monobank.ua/personal/webhook", json=data, headers=headers)

    if response.status_code == 200:
        print("Вебхук для Монобанку зареєстровано успішно!")
    else:
        print(f"Помилка реєстрації вебхука: {response.text}")


# Обробник для вебхука Монобанку
@app.route("/monobank-webhook", methods=["POST"])
def monobank_webhook():
    data = request.json

    if "data" in data:
        transaction = data["data"]
        comment = transaction.get("comment")
        amount = transaction.get("amount") // 100  # Переводимо копійки в гривні

        if comment and comment.isdigit():
            user_id = int(comment)
            cursor.execute(
                """
                INSERT INTO users (user_id, murrcoins)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET murrcoins = murrcoins + ?
                """,
                (user_id, amount, amount),
            )
            conn.commit()

    return jsonify({"status": "success"}), 200


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Додаємо користувача в базу, якщо його ще немає
    cursor.execute(
        """
        INSERT INTO users (user_id, username)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO NOTHING
        """,
        (user_id, username),
    )
    conn.commit()

    await update.message.reply_text(
        f"Вітаємо в боті я в говно! 🐾\n"
        f"Доступні команди:\n"
        f"/donate - Отримати посилання для донатів.\n"
        f"/balance - Перевірити баланс MurrCoins.\n"
        f"/spend <кількість> - Витратити MurrCoins на вуса.\n"
        f"/get <кількість> - Отримати MurrCoins вручну (для тестування).\n"
    )


# Команда /get
async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажіть кількість MurrCoins для нарахування. Наприклад, /get 10.")
        return

    amount = int(context.args[0])

    cursor.execute(
        """
        INSERT INTO users (user_id, murrcoins)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET murrcoins = murrcoins + ?
        """,
        (user_id, amount, amount),
    )
    conn.commit()

    await update.message.reply_text(f"Вам нараховано {amount} MurrCoins!")

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
async def start_telegram_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("start", start))  # Додано /start
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))
    application.add_handler(CommandHandler("get", get))  # Додано /get


    # Запуск бота
    await application.run_polling()


def run_flask():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    register_monobank_webhook()  # Реєстрація вебхука для Монобанку

    # Запуск Flask-сервера в окремому потоці
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запуск Telegram бота
    asyncio.run(start_telegram_bot())
# Основний код бота
async def start_telegram_bot():
