import os
import logging
import random
import json
import requests
import atexit
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Налаштування Monobank API
MONOBANK_API_KEY = "азаза"


# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Файл для збереження даних
DATA_FILE = "user_data.json"

# Дані про користувачів
user_data = {}

# Список цитат
quotes = [
    "Без вусів і коту не жити.",
    "Кіт малий, а вуса ростуть.",
    "Де пахне MurrCoins, там багатий кіт.",
    "Хто рано мурчить, той більше MurrCoins має.",
    "Не відкладай мурчання на завтра, якщо можеш муркнути сьогодні.",
    "Не муркай багато, а MurrCoins збирай.",
    "Довгі вуса починаються з першого вирощування.",
    "Вусатий той, хто не забуває про свій вусик.",
    "Вусик без MurrCoin — як кіт без хвоста.",
    "За мурчанням і вусик не помітно, як росте.",
    "Кіт без вусика — як скарбниця без MurrCoins.",
    "Муркоїни водяться там, де коти знають їм ціну.",
    "Гроші не купують щастя, але муркоїни можуть купити вуса.",
    "Тільки той, хто ризикне втратити всі муркоїни, зможе відростити найдовші вуса.",
    "Час витрачати муркоїни – час подовжувати вуса.",
    "Світ належить тому, хто мурчить голосніше.",
    "Немає нічого неможливого, якщо у тебе достатньо муркоїнів.",
    "Якщо тобі складно – просто мурчи далі.",
    "З великими вусами приходить велика відповідальність.",
    "Великі вуса несуть велику відповідальність.",
    "Не питай, що муркоїни можуть зробити для тебе – питай, скільки мм вусів ти можеш купити за них.",
    "Я мурчу, отже, існую.",
    "Думай муркотливо, дій вусато.",
    "Муркоїни вуса не гріють, але без них вони не ростуть.",
    "Коти з довгими вусами мурчать впевненіше.",
    "Не все муркоїни, що блищить, але вуса без них не виростуть",
    "За муркоїни можна купити вуса, але не мурчання.",
    "Кіт багатий не мурчанням, а довгими вусами.",
    "Не економ на вусах – муркоїни для цього й створені.",
    "Це твій знак нарешті витратити муркоїни на розкішні вуса.",
    "Це твій знак перестати мурчати без користі й почати інвестувати в довжину вусів.",
    "Це твій знак, що твої вуса заслуговують на більше.",
    "Це твій знак зібрати всі муркоїни і зробити щось велике… наприклад, подовжити вуса.",
    "Це твій знак перестати відкладати та нарешті купити собі ще 5 мм вусів.",
    "Це твій знак, що без муркоїнів вуса не ростуть.",
    "Це твій знак, що настав час урочистого муркотіння.",
    "Це твій знак перестати дивитися на чужі вуса і почати працювати над своїми.",
    "Це твій знак, що сьогодні — ідеальний день для котячих інвестицій.",
    "Це твій знак, що вуса самі себе не відростять (але муркоїни допоможуть).",
    "Мурчання править світом.",
    "Не всі, хто блукає, загублені, можливо, вони просто шукають муркоїни.",
    "MurrCoin до MurrCoin’а — і будуть нові вуса."]

HELP_TEXT = """🐾 Важлива інформація про бота 🐾

✨ Цей бот створений для розваги, тож мурчи, рости вуса та збирай MurrCoins разом з іншими котиками!
🧹 Час від часу база даних очищається від неактивних користувачів (якщо ти не заходив більше 7 днів).
💰 MurrCoins можна заробити та витратити на вуса – але пам’ятай, що справжній багатій той, у кого довгі вуса!
На цьому все, пухнасті друзі, мур-мур! 😺

📜 Список команд:

🔹 Основне
/start – почати спілкування з ботом.
/help – показати це повідомлення.

🔹 Муркотіння та вуса
/murr – помурчати (раз на 10 хв, можна у відповідь іншому котику).
/top_murr – рейтинг мурчальників.
/usik – вирощування вусів (раз на годину).
/top_usik – рейтинг найдовших вусів.

🔹 MurrCoins
/balance – перевірити баланс.
/spend – витратити MurrCoins на вуса.
/get – отримати безкоштовні MurrCoins (раз на день).
/donate – купити MurrCoins (курс 1:1, підтримай розробника кавою).

🔹 Інше
/c – мудра цитата від Мудрого Кота.

📩 Зв’язок з розробником: @ghtipiq

Мур-мур, нехай твої вуса ростуть, а муркоїни множаться! 😺✨"""

# Завантаження даних із JSON
def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                user_data = json.load(file)
        except (json.JSONDecodeError, IOError):
            user_data = {}  # Якщо помилка, просто створюємо пустий словник
    else:
        user_data = {}

# Збереження даних у JSON
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

# Оновлення даних користувача
def update_user(user):
    user_id = str(user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "first_name": user.first_name,
            "balance": 0,
            "mur_count": 0,
            "usik_length": 0.0,
            "last_mur": None,
            "last_usik": None,
            "last_get": None,
            "last_active": datetime.now().isoformat(),  # Оновлення активності
        }
    else:
        user_data[user_id]["first_name"] = user.first_name
        user_data[user_id]["last_active"] = datetime.now().isoformat()  # Оновлення активності

    save_data()  # Зберігаємо зміни в файлі


def remove_inactive_users():
    global user_data
    now = datetime.now()

    # Список користувачів, яких потрібно видалити
    to_remove = []

    for user_id, data in user_data.items():
        last_active = data.get("last_active")
        
        # Якщо у користувача є поле "last_active"
        if last_active:
            last_active = datetime.fromisoformat(last_active)
            if now - last_active > timedelta(days=7):  # Якщо не активний більше 7 днів
                to_remove.append(user_id)

    # Видаляємо неактивних користувачів
    for user_id in to_remove:
        del user_data[user_id]
        logger.info(f"Видалено неактивного користувача {user_id}")

    # Зберігаємо оновлені дані
    save_data()


# Команда /start
async def start(update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привіт, {user.first_name} 🐾\nТикни лапкою /help, щоб побачити список доступних команд."
    )

# Команда /help
async def help_command(update, context):
    await update.message.reply_text(HELP_TEXT)


# Функція для отримання випадкової цитати
async def random_quote(update: Update, context):
    quote = random.choice(quotes)
    await update.message.reply_text(f'"{quote}"\n— Мудрий Кіт')

# Команда /murr
async def murr(update, context):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    # Оновлюємо або додаємо користувача в JSON
    update_user(user)

    # Перевіряємо, чи можна мурчати (раз на 10 хвилин)
    last_mur = user_data[user_id].get("last_mur")
    if last_mur:
        elapsed_time = now - datetime.fromisoformat(last_mur)
        if elapsed_time < timedelta(minutes=10):
            remaining_time = timedelta(minutes=10) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Твій мурчальник перегрівся 🐾\nСпробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього мурчання
    user_data[user_id]["last_mur"] = now.isoformat()
    user_data[user_id]["mur_count"] += 1  # Збільшуємо лічильник мурчань
    save_data()  # Зберігаємо зміни

    # Якщо команда відповідає на чиєсь повідомлення
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_first_name = target_user.first_name or "Користувач"
        await update.message.reply_text(
            f"{user_data[user_id]['first_name']} помурчав на вушко {target_first_name} 🐾\n"
            f"Всього мурчань: {user_data[user_id]['mur_count']}."
        )
    else:
        await update.message.reply_text(
            f"{user_data[user_id]['first_name']} помурчав! 🐾\n"
            f"Всього мурчань: {user_data[user_id]['mur_count']}."
        )

# Команда /usik
async def usik(update, context):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    # Оновлюємо або додаємо користувача в JSON
    update_user(user)

    # Перевіряємо, чи можна вирощувати вуса (раз на 60 хвилин)
    last_usik = user_data[user_id].get("last_usik")
    if last_usik:
        elapsed_time = now - datetime.fromisoformat(last_usik)
        if elapsed_time < timedelta(hours=1):
            remaining_time = timedelta(hours=1) - elapsed_time
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await update.message.reply_text(
                f"Твій вусик втомився рости 😿\nспробуй через {minutes} хвилин та {seconds} секунд."
            )
            return

    # Оновлюємо час останнього росту вусів
    user_data[user_id]["last_usik"] = now.isoformat()

    # Змінюємо довжину вусів (з випадковою зміною)
    change = round(random.uniform(-7, 7), 2)  # Довжина змінюється від -7 до 7 мм
    user_data[user_id]["usik_length"] += change
    save_data()  # Зберігаємо зміни

    # Повідомляємо про результат
    await update.message.reply_text(
        f"{user_data[user_id]['first_name']}, твій вусик {'збільшився' if change > 0 else 'зменшився'} на {abs(change):.2f} мм.\n" 
        f"Загальна довжина вусів: {user_data[user_id]['usik_length']:.2f} мм."
    )
    
# Команда /top_murr
async def top_murr(update, context):
    if not user_data:
        await update.message.reply_text("Наразі рейтинг мурчалок пустий 🐱")
        return

    sorted_murr = sorted(
        [(data["first_name"], data["mur_count"]) for data in user_data.values()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    leaderboard = "\n".join(
        [f"{i+1}. {first_name} — {mur_count} мурчань" for i, (first_name, mur_count) in enumerate(sorted_murr)]
    )
    await update.message.reply_text(f"🏆 Топ-10 мурчалок 🐱:\n{leaderboard}")

# Команда /top_usik
async def top_usik(update, context):
    if not user_data:
        await update.message.reply_text("Наразі рейтинг довжини вусанів пустий 🐱")
        return

    sorted_usik = sorted(
        [(data["first_name"], data["usik_length"]) for data in user_data.values()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    leaderboard = "\n".join(
        [f"{i+1}. {first_name} — {usik_length:.2f} мм" for i, (first_name, usik_length) in enumerate(sorted_usik)]
    )
    await update.message.reply_text(f"🏆 Топ-10 вусанів 🐱:\n{leaderboard}")


# Команда для отримання муркоїнів
async def get(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Оновлюємо інформацію про користувача
    update_user(user)

    # Завантажуємо дані користувача
    user_info = user_data.get(user_id, {})
    current_time = datetime.now()

    # Перевіряємо, коли востаннє користувач виконував команду /get
    last_get = user_info.get("last_get")
    if last_get:
        last_get_time = datetime.fromisoformat(last_get)
        if current_time - last_get_time < timedelta(hours=24):
            remaining_time = timedelta(hours=24) - (current_time - last_get_time)
            hours, minutes = divmod(remaining_time.seconds, 3600)
            minutes //= 60
            await update.message.reply_text(
                f"Є в глечику MurrCoin та голова не влазить...\nСпробуй ще раз через {hours} годин {minutes} хвилин."
            )
            return

    
    # Генерація випадкової кількості муркоїнів (від 1 до 10)
    random_coins = random.randint(1, 2)
    user_data[user_id]["balance"] += random_coins

    # Оновлюємо час останнього використання команди /get
    user_info["last_get"] = current_time.isoformat()

    # Зберігаємо оновлені дані
    user_data[user_id] = user_info
    save_data()

    # Відповідь користувачу
    await update.message.reply_text(
        f"Ти отримав {random_coins} муркоїнів! \nТвій баланс тепер: {user_info['balance']} муркоїнів."
    )

# Команда для витрати муркоїнів
async def spend(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    # Оновлення даних користувача
    update_user(user)

    # Якщо користувач НЕ вказав число, бот чекає одне повідомлення
    if not context.args:
        await update.message.reply_text("Скільки муркоїнів ти хочеш витратити? Відправ число.")
        context.user_data["awaiting_spend"] = True  # Встановлюємо флаг очікування
        return
    
    # Якщо користувач одразу ввів число
    await process_spend(update, context, context.args[0])

# Функція для обробки витрати муркоїнів
async def process_spend(update: Update, context: CallbackContext, spend_amount):
    user = update.effective_user
    user_id = str(user.id)

    # Якщо введене значення не є числом
    if not spend_amount.isdigit():
        await update.message.reply_text("Ти мав ввести число, спробуй ще раз командою /spend.")
        context.user_data.pop("awaiting_spend", None)  # Скидаємо стан очікування
        return
    
    spend_amount = int(spend_amount)

    # Перевіряємо баланс
    balance = user_data[user_id].get("balance", 0)

    if spend_amount > balance:
        await update.message.reply_text("У тебе недостатньо MurrCoins на балансі 😿\nПеревір баланс командою /balance")
        return

    # Віднімаємо муркоїни та додаємо вуса
    user_data[user_id]["balance"] -= spend_amount
    usik_increase = spend_amount * 5
    user_data[user_id]["usik_length"] += usik_increase

    save_data()  # Зберігаємо зміни

    await update.message.reply_text(
        f"Ти витратив {spend_amount} MurrCoins. Тепер у тебе {user_data[user_id]['balance']} MurrCoins.\n"
        f"Ти отримав {usik_increase} мм вусів. Загальна довжина вусів: {user_data[user_id]['usik_length']} мм."
    )

    # Скидаємо стан очікування
    context.user_data.pop("awaiting_spend", None)

# Обробник тексту після /spend (тільки один раз)
async def handle_text(update: Update, context: CallbackContext):
    if context.user_data.pop("awaiting_spend", None):  # Видаляємо флаг після першого повідомлення
        await process_spend(update, context, update.message.text)

# Команда /balance
async def balance(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Оновлюємо дані користувача
    update_user(user)

    # Отримуємо поточний баланс
    balance = user_data[user_id].get("balance", 0)

    # Якщо баланс пустий
    if balance == 0:
        await update.message.reply_text(
            "Твій баланс пустий... 😿\n"
            "Але не сумуй! Напиши /get і зароби свої перші MurrCoins! 🐾\n"
            "Або купи розробнику каву викоставши команду /donate" 
        )
    else:
        # Виведення поточного балансу
        await update.message.reply_text(
            f"Твій баланс: {balance} MurrCoins 🐾\n"
            "Пам'ятай, що MurrCoins можна витратити через /spend!"
        )

# Команда /donate
async def donate(update, context):
    user = update.effective_user
    user_id = str(user.id)

    # Надсилаємо повідомлення з ID користувача для використання у коментарі
    await update.message.reply_text(
        f"Зробіть донат на картку Monobank 4441111026523120. Використовуйте наступний коментар до переказу:\n\n"
        f"ID для коментаря: {user_id}\nКурс 1 до 1"
    )


# Перевірка транзакцій
def check_transactions():
    headers = {"X-Token": MONOBANK_API_KEY}
    url = "https://api.monobank.ua/personal/statement/0/{}".format(
        int((datetime.now() - timedelta(minutes=5)).timestamp())
    )
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            transactions = response.json()

            for transaction in transactions:
                # Переконуємося, що є коментар до платежу
                if "comment" in transaction:
                    user_id = transaction["comment"].strip()

                    # Перевіряємо, чи коментар є числом (ID користувача)
                    if user_id.isdigit():
                        amount = transaction["amount"] / 100  # Перетворюємо копійки у гривні
                        add_murkoins(user_id, amount)
                        logger.info(f"Нараховано {amount} муркоїнів користувачу {user_id}")

            return transactions
        else:
            logger.error(f"Помилка отримання транзакцій: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка запиту до Monobank: {e}")
        return None

# Нарахування муркоїнів
def add_murkoins(user_id: str, amount: float):
    if user_id in user_data:
        user_data[user_id]["balance"] += amount
    else:
        user_data[user_id] = {"balance": amount, "mur_count": 0}
    
    logger.info(f"Користувач {user_id} отримав {amount} муркоїнів. Новий баланс: {user_data[user_id]['balance']}")
    save_data()

# Запуск бота
def main():
    load_data()
    token = "токен"
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("usik", usik))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("top_murr", top_murr))
    application.add_handler(CommandHandler("top_usik", top_usik))
    application.add_handler(CommandHandler("spend", spend))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CommandHandler("get", get))
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("c", random_quote))
    
    # Створюємо асинхронний планувальник
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: check_transactions(), 'interval', minutes=5)
    scheduler.add_job(remove_inactive_users, 'interval', days=1)  
    scheduler.start()
    
    # Функція для закриття планувальника при завершенні бота
    atexit.register(lambda: scheduler.shutdown(wait=False))
    
    application.run_polling() #міша не ругай не плач 


if __name__ == "__main__":
    main()
