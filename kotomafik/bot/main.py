import os
import logging
import random
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler

# Зберігаємо дані у словнику
user_data = {}

app = Flask(__name__)

# Тестові дані для зберігання інформації
user_data = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Перевіряємо, чи це валідний запит
    if not data or "data" not in data:
        return jsonify({"status": "error", "message": "Неправильний формат запиту"}), 400

    # Обробляємо транзакцію
    transaction = data["data"]
    account = transaction.get("account", "невідомий")
    amount = transaction.get("amount", 0) / 100  # Сума транзакції в гривнях
    user_id = account  # Наприклад, використовуємо рахунок як ідентифікатор

    # Знаходимо користувача та оновлюємо баланс
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "usik_length": 0}
    user_data[user_id]["balance"] += amount

    return jsonify({"status": "success"}), 200

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Завантаження імен користувачів
async def update_user_name(update, context):
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.first_name

    # Зберігаємо ім'я користувача в bot_data
    context.bot_data[user_id] = user_name

# Файл для збереження даних
DATA_FILE = "user_data.json"

# Дані про користувачів
user_data = {}

# Завантаження даних із JSON
def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            user_data = json.load(file)
    else:
        user_data = {}

# Збереження даних у JSON
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=6)

# Команда для початку поповнення
async def donate(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Генеруємо унікальний ID для доната
    unique_id = f"{user_id}-{random.randint(1000, 9999)}"

    # Додаємо користувача до словника, якщо його там ще немає
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "usik_length": 0, "donation_id": unique_id}
    else:
        user_data[user_id]["donation_id"] = unique_id



    await update.message.reply_text(
        f"Щоб задонатити, натисни на посилання нижче:\n\n"
        f"[Донат](<{monobank_link}>)\n\n"
        f"1 грн = 1 MurrCoin 🌟. Після оплати MurrCoins буде автоматично зараховано!",
        parse_mode="Markdown",
    )

# Замініть URL на адресу вашого сервера
WEBHOOK_URL = "https://kitimifia.onrender.com/webhook"

# Отримуємо токен з середовища
MONOBANK_TOKEN = os.getenv("MONOBANK_TOKEN")

# Перевірка, чи є токен
if MONOBANK_TOKEN is None:
    print("Токен Monobank не знайдено в змінних середовища!")
else:
    print("Токен успішно отримано!")

def register_webhook():
    headers = {
        "X-Token": MONOBANK_TOKEN,
    }
    data = {
        "webHookUrl": WEBHOOK_URL
    }

    response = requests.post("https://api.monobank.ua/personal/webhook", headers=headers, json=data)

    if response.status_code == 200:
        print("Webhook успішно зареєстрований!")
    else:
        print(f"Помилка реєстрації вебхука: {response.text}")

# Оновлення даних користувача
def update_user(user):
    user_id = str(user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "mur_count": 0,
            "usik_length": 0.0,
            "balance": 0,
            "is_donator": False,
            "first_name": user.first_name  # Зберігаємо ім'я користувача
        }

# Команда /balance
async def balance(update, context):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "usik_length": 0}

    balance = user_data[user_id]["balance"]

    await update.message.reply_text(f"Ваш баланс: {balance:.2f} MurrCoins 🌟")

# Команда /start
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name} 🐾\nТикни лапкою /help, щоб побачити список доступних команд."
    )

# Команда /help
async def help_command(update, context):
    commands = (
        "/start - Почати спілкування з ботом.\n"
        "/help - Показати список команд.\n"
        "/murr - Помурчати.\n"
        "/usik - Виростити котячі вуса.\n"
        "/balance - Перевірити свій баланс.\n"
        "/spend [сума] - Витратити MurrCoins.\n"
        "/donate - .\n"
        "/rating - ."
    )
    await update.message.reply_text(f"Доступні команди:\n{commands}")

# Команда /murr
async def murr(update, context):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    update_user(user_id)  # Перевіряємо, чи є користувач у базі

    last_mur = user_data[user_id].get("last_mur")
    if last_mur:
        elapsed_time = now - datetime.fromisoformat(last_mur)
        if elapsed_time < timedelta(minutes=10):  # Раз на 10 хвилин
            remaining_time = timedelta(minutes=10) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Твій мурчальник перегрівся 🐾\nСпробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    user_data[user_id]["last_mur"] = now.isoformat()
    user_data[user_id]["mur_count"] += 1  # Збільшуємо лічильник мурчань
    save_data()  # Зберігаємо оновлені дані

    # Якщо команда відповідає на чиєсь повідомлення
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_first_name = target_user.first_name
        target_name = f"{target_first_name} @{target_user.username}" if target_user.username else target_first_name
        await update.message.reply_text(
            f"{user.first_name} помурчав на вушко {target_name} 🐾\n"
            f"Всього мурчань: {user_data[user_id]['mur_count']}."
        )
    else:
        await update.message.reply_text(
            f"{user.first_name} помурчав! 🐾\n"
            f"Всього мурчань: {user_data[user_id]['mur_count']}."
        )

# Команда /usik
async def usik(update, context):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    update_user(user_id)  # Перевіряємо, чи є користувач у базі

    last_usik = user_data[user_id].get("last_usik")
    if last_usik:
        elapsed_time = now - datetime.fromisoformat(last_usik)
        if elapsed_time < timedelta(hours=1):  # Раз на 60 хвилин
            remaining_time = timedelta(hours=1) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"твой усік устал расті 🐾\nСпробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    user_data[user_id]["last_usik"] = now.isoformat()

    # Вирощуємо або зменшуємо вуса
    change = round(random.uniform(-7, 7), 2)
    user_data[user_id]["usik_length"] += change
    save_data()  # Зберігаємо оновлені дані

    await update.message.reply_text(
        f"{user.first_name}, твої вуса {'збільшились' if change > 0 else 'зменшились'} на {abs(change):.2f} мм.\n"
        f"Загальна довжина вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )
    
# Команда /top_murr
async def top_murr(update, context):
    if not user_data:
        await update.message.reply_text("Наразі рейтинг мурчань пустий 🐾")
        return

    # Сортуємо користувачів за кількістю мурчань
    sorted_murr = sorted(
        user_data.items(),
        key=lambda x: x[1]["mur_count"],
        reverse=True
    )[:10]

    # Формуємо текст рейтингу
    leaderboard = "\n".join(
        [
            f"{i+1}. {data['first_name']} — {data['mur_count']} мурчань"
            for i, (user_id, data) in enumerate(sorted_murr)
        ]
    )

    await update.message.reply_text(f"🏆 Топ-10 мурчунів 🐾:\n{leaderboard}")


# Команда /top_usik
async def top_usik(update, context):
    if not user_data:
        await update.message.reply_text("Наразі рейтинг довжини вусів пустий 🐾")
        return

    # Сортуємо користувачів за довжиною вусів
    sorted_usik = sorted(
        user_data.items(),
        key=lambda x: x[1]["usik_length"],
        reverse=True
    )[:10]

    # Формуємо текст рейтингу
    leaderboard = "\n".join(
        [
            f"{i+1}. {data['first_name']} — {data['usik_length']:.2f} мм"
            for i, (user_id, data) in enumerate(sorted_usik)
        ]
    )

    await update.message.reply_text(f"🏆 Топ-10 вусанів 🐾:\n{leaderboard}")

# Команда /spend
async def spend(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Додаємо користувача до словника, якщо його там ще немає
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "usik_length": 0}

    # Перевіряємо, чи вказана кількість MurrCoins
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажи кількість MurrCoins, які ти хочеш витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])
    balance = user_data[user_id]["balance"]

    # Перевіряємо, чи достатньо монет
    if balance < amount:
        await update.message.reply_text(
            f"У тебе недостатньо MurrCoins для цієї витрати. Твій баланс: {balance} MurrCoins."
        )
        return

    # Знімаємо монети з балансу та додаємо довжину вусів
    user_data[user_id]["balance"] -= amount
    user_data[user_id]["usik_length"] += amount * 5

    response = (
        f"Ти витратив {amount} MurrCoins, і твої вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер твій баланс: {user_data[user_id]['balance']} MurrCoins.\n"
        f"Загальна довжина твоїх вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )

    # Додаємо позначку донатора
    if "🌟" not in user_data[user_id]:
        user_data[user_id]["donator"] = True
        response += "\nВітаємо! Ви отримали значок 🌟 за внесок у розвиток вусів!"

    await update.message.reply_text(response)

# Запуск бота
def main():
    load_data()
    token = os.getenv("TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("usik", usik))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("spend", spend))
    application.add_handler(CommandHandler("top_murr", top_murr))
    application.add_handler(CommandHandler("top_usik", top_usik))
    

    application.run_polling()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    main()
