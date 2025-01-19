import os
import logging
import random
import json
from datetime import datetime, timedelta
from telegram.ext import Application, CommandHandler

# Стани
SELECTING_RATING = 1

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

# Функція для генерації унікального ID для поповнення
def generate_donation_id():
    return str(random.randint(1000000000, 9999999999))

# Команда для початку поповнення
async def donate(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Генеруємо унікальний ID для поповнення
    donation_id = generate_donation_id()

    # Створюємо посилання для поповнення через Monobank (це приклад, реальне посилання може бути іншим)
    donation_link = f"https://monobank.ua/pay/{donation_id}"

    # Записуємо унікальний ID та посилання на поповнення в дані користувача
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "donations": {}}

    user_data[user_id]["donations"][donation_id] = {"status": "pending", "amount": 0}
    save_data()

    await update.message.reply_text(
        f"Для поповнення вашого балансу, використовуйте цей ID та перейдіть за посиланням: \n"
        f"Поповнити: {donation_link}\n"
        f"Ваш Donation ID: {donation_id}\n"
        f"Після поповнення на ваш баланс буде зараховано MurrCoins."
    )

# Оновлення даних користувача
def update_user(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "mur_count": 0,
            "usik_length": 0.0,
            "balance": 0,  # Додаємо баланс при створенні нового користувача
            "last_mur": None,
            "last_usik": None,
        }

def add_donation(user_id, amount):
    user_id = str(user_id)
    update_user(user_id)
    # Нараховуємо MurrCoins
    murrcoins = amount  # 1 грн = 1 MurrCoin
    user_data[user_id]["murr_balance"] += murrcoins
    # Покращення вусів (10 мм за 1 грн)
    user_data[user_id]["usik_length"] += amount * 10
    save_data()
    logger.info(f"Користувач {user_id} отримав {murrcoins} MurrCoins і {amount * 10} мм за донат {amount} грн.")

# Функція для оновлення статусу донатера
def update_donator_status(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"mur_count": 0, "usik_length": 0.0, "murrcoins": 0, "is_donator": False}

    if user_data[user_id]["murrcoins"] > 0:
        user_data[user_id]["is_donator"] = True
    else:
        user_data[user_id]["is_donator"] = False

    save_data()  # Зберігаємо зміни

# Команда /balance
async def balance(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Оновлюємо дані користувача, якщо необхідно
    update_user(user_id)

    # Отримуємо баланс користувача
    balance = user_data[user_id].get("balance", 0)

    # Виводимо баланс користувачу
    await update.message.reply_text(f"Твій баланс: {balance} Murrcoins 🐾")

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
        await update.message.reply_text("Наразі рейтинг мурчалок пустий 🐾")
        return

    sorted_murr = sorted(
        [(user_id, data["mur_count"], data.get("is_donator", False)) for user_id, data in user_data.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    leaderboard = "\n".join(
        [
            f"{i+1}. {'🌟' if is_donator else ''} Користувач {user_id} — {mur_count} мурчань"
            for i, (user_id, mur_count, is_donator) in enumerate(sorted_murr)
        ]
    )
    await update.message.reply_text(f"🏆 Топ-10 мурчунів 🐾:\n{leaderboard}")

# Команда /top_usik
async def top_usik(update, context):
    if not user_data:
        await update.message.reply_text("Наразі рейтинг довжини вусів пустий 🐾")
        return

    sorted_usik = sorted(
        [(user_id, data["usik_length"], data.get("is_donator", False)) for user_id, data in user_data.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    leaderboard = "\n".join(
        [
            f"{i+1}. {'🌟' if is_donator else ''} Користувач {user_id} — {usik_length:.2f} мм"
            for i, (user_id, usik_length, is_donator) in enumerate(sorted_usik)
        ]
    )
    await update.message.reply_text(f"🏆 Топ-10 вусанів 🐾:\n{leaderboard}")

# Команда /spend
async def spend(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Перевіряємо, чи вказана кількість MurrCoins для витрати
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Будь ласка, вкажи кількість MurrCoins, які ти хочеш витратити. Наприклад, /spend 10.")
        return

    amount = int(context.args[0])  # Сума, яку користувач хоче витратити

    # Оновлюємо дані користувача
    update_user(user_id)

    # Отримуємо поточний баланс користувача
    balance = user_data[user_id].get("balance", 0)

    # Перевіряємо, чи достатньо монет
    if balance < amount:
        await update.message.reply_text(
            f"У тебе недостатньо MurrCoins для цієї витрати. Твій баланс: {balance} MurrCoins."
        )
        return

    # Знімаємо монети з балансу та додаємо довжину вусів
    user_data[user_id]["balance"] -= amount
    user_data[user_id]["usik_length"] += amount * 5  # Додаємо 5 мм за кожен витрачений MurrCoin
    save_data()

    # Повідомляємо про успішну витрату
    await update.message.reply_text(
        f"Ти витратив {amount} MurrCoins і твої вуса виросли на {amount * 5} мм! 🐾\n"
        f"Тепер твій баланс: {user_data[user_id]['balance']} MurrCoins.\n"
        f"Загальна довжина твоїх вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )

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
    main()
