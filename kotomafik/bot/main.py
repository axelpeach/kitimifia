import random
import string
import requests
import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Отримуємо змінні середовища для токенів
TOKEN = os.getenv("TOKEN")
MONOBANK_API = os.getenv("MONOBANK")
MONOBANK_CARD_NUMBER = os.getenv("MONOBANK_CARD_NUMBER")

# Зміст даних користувачів
user_data = {}
donations = {}

# Генерація випадкового коду для коментаря
def generate_comment_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Команда /donate
async def donate(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Генерація випадкового коду для коментаря
    comment_code = generate_comment_code()

    # Генеруємо посилання на Monobank
    monobank_url = f"https://api.monobank.ua/p2p/{MONOBANK_CARD_NUMBER}?amount={{amount}}&comment={comment_code}"

    # Зберігаємо код для моніторингу
    donations[user_id] = {"comment_code": comment_code, "amount_donated": 0}

    await update.message.reply_text(
        f"Дякуємо за бажання зробити донат! 🤝\n"
        f"Будь ласка, зроби переказ на банківську картку Monobank за посиланням нижче:\n"
        f"{monobank_url}\n"
        f"Не забудь вказати код коментаря: {comment_code}"
    )

# Команда /balance
async def balance(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Отримуємо поточний баланс муркоїнів
    balance = user_data.get(user_id, {}).get("balance", 0)

    await update.message.reply_text(
        f"Твій поточний баланс муркоїнів: {balance} MurrCoins."
    )

# Команда /spend
async def spend(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Перевіряємо, скільки муркоїнів користувач хоче витратити
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажіть кількість MurrCoins для витрати. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])

    # Отримуємо поточний баланс користувача
    balance = user_data.get(user_id, {}).get("balance", 0)

    if balance < amount:
        await update.message.reply_text(f"У тебе недостатньо MurrCoins для цієї витрати. Твій баланс: {balance} MurrCoins.")
        return

    # Зменшуємо баланс і збільшуємо довжину вусів
    user_data[user_id]["balance"] -= amount
    user_data[user_id]["usik_length"] += amount * 5  # 5 мм за кожен витрачений MurrCoin

    await update.message.reply_text(
        f"Ти витратив {amount} MurrCoins, і твої вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер твій баланс: {user_data[user_id]['balance']} MurrCoins.\n"
        f"Загальна довжина твоїх вусів: {user_data[user_id]['usik_length']} мм."
    )

# Функція для моніторингу донатів
def monitor_donations():
    while True:
        for user_id, donation in donations.items():
            comment_code = donation["comment_code"]

            # Отримуємо дані про транзакції з Monobank API
            response = requests.get(f"https://api.monobank.ua/p2p/{MONOBANK_CARD_NUMBER}/transactions",
                                    headers={"Authorization": f"Bearer {MONOBANK_API}"})
            transactions = response.json()

            for transaction in transactions:
                if transaction.get('comment') == comment_code:
                    # Якщо сума донату збігається з коментарем, додаємо MurrCoins
                    amount = transaction['amount'] / 100  # Переводимо в гривні (Monobank API дає копійки)
                    if user_id not in user_data:
                        user_data[user_id] = {"balance": 0, "usik_length": 0}

                    user_data[user_id]["balance"] += amount
                    donations[user_id]["amount_donated"] += amount

                    # Повідомляємо користувача про поповнення
                    context.bot.send_message(user_id, f"Ти отримав {amount} MurrCoins за донат на {comment_code}.")
                    break

        # Чекаємо 10 секунд перед наступною перевіркою
        time.sleep(10)

# Налаштування бота
def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Додаємо обробники команд
    dispatcher.add_handler(CommandHandler('donate', donate))
    dispatcher.add_handler(CommandHandler('balance', balance))
    dispatcher.add_handler(CommandHandler('spend', spend))

    # Запускаємо бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Запуск моніторингу донатів у фоновому режимі
    import threading
    donation_thread = threading.Thread(target=monitor_donations)
    donation_thread.daemon = True
    donation_thread.start()

    # Запуск бота
    start_bot()
