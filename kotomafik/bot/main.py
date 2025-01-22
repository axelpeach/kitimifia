import os
import sqlite3
import asyncio
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ініціалізація Flask
app = Flask(__name__)

# Маршрут для головної сторінки
@app.route("/")
def index():
    return "Bot is running!"


# Завантаження змінних середовища
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL вашого сервера
JAR_LINK = "https://send.monobank.ua/jar/5yxJsnYG82"

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

# Ініціалізація Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

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
        amount = transaction.get("amount")

        if amount is None:
            return jsonify({"status": "error", "message": "Invalid transaction data"}), 400

        amount = amount // 100  # Переводимо копійки в гривні

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


# Telegram Webhook (синхронний)
@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, application.bot)
    application.update_queue.put(update)  # Додаємо в чергу оновлень
    return jsonify({"status": "ok"})


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


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "я хочу пітсу Використовуйте команди:\n"
        "/donate - щоб задонатити та отримати MurrCoins\n"
        "/balance - щоб перевірити ваш баланс\n"
        "/get <кількість> - щоб додати MurrCoins вручну (адміністративна команда)"
    )


# Команда /spend
async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Перевіряємо, чи є аргумент, який вказує кількість MurrCoins для витрати
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Вкажіть кількість MurrCoins, яку хочете витратити. Наприклад: /spend 10")
        return

    amount = int(context.args[0])
    user_id = update.effective_user.id

    # Отримуємо поточний баланс користувача
    cursor.execute("SELECT murrcoins FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        await update.message.reply_text("У вас немає MurrCoins. Поповніть свій баланс!")
        return

    current_balance = result[0]

    # Перевіряємо, чи вистачає балансу
    if current_balance < amount:
        await update.message.reply_text(
            f"Недостатньо коштів! Ваш баланс: {current_balance} MurrCoins, а потрібно: {amount}."
        )
        return

    # Знімаємо MurrCoins з балансу
    cursor.execute(
        "UPDATE users SET murrcoins = murrcoins - ? WHERE user_id = ?",
        (amount, user_id),
    )
    conn.commit()

    await update.message.reply_text(f"Ви витратили {amount} MurrCoins. Ваш новий баланс: {current_balance - amount} MurrCoins.")


# Команда /get
async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Вкажіть кількість MurrCoins, яку хочете отримати. Наприклад: /get 10")
        returnamount = int(context.args[0])
    user_id = update.effective_user.id

    cursor.execute(
        """
        INSERT INTO users (user_id, murrcoins)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET murrcoins = murrcoins + ?
        """,
        (user_id, amount, amount),
    )
    conn.commit()

    await update.message.reply_text(f"Вам додано {amount} MurrCoins!")


# Запуск Telegram бота
async def start_telegram_bot():
    # Реєстрація команд
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spend", spend))
    application.add_handler(CommandHandler("get", get))

# Запуск Flask-сервера
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Реєстрація вебхука для Монобанку
    register_monobank_webhook()

    # Запуск Flask у окремому потоці
    threading.Thread(target=run_flask, daemon=True).start()

    # Запуск Telegram бота
    asyncio.run(start_telegram_bot())
