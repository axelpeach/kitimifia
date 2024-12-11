from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
import random

# Змінні для лічильників
user_mur_count = {}
user_mustache_length = {}

# Обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply("Привіт! Я твій бот. Використовуй /murr для мурчання і /usik для вирощування вусів. няв")

# Обробник команди /murr
async def murr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Лічильник мурчань для цього користувача
    if user_id not in user_mur_count:
        user_mur_count[user_id] = 0
    user_mur_count[user_id] += 1

    # Відповідь на команду
    await update.message.reply(f"{user_name} помурчав! Загальна кількість мурчань: {user_mur_count[user_id]}")

# Обробник команди /mustache
async def mustache(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Зміна довжини вусів
    if user_id not in user_mustache_length:
        user_mustache_length[user_id] = 0.0  # Початковий розмір вусів

    # Рандомна зміна довжини вусів від -7 до +7 мм (з сотими)
    change = round(random.uniform(-7.0, 7.0), 2)
    user_mustache_length[user_id] += change

    # Відповідь на команду
    await update.message.reply(f"{user_name} ваі магьошь тваі усікь {('сталь больше' if change >= 0 else 'сталь мєньшє')} на {abs(change)} мм! Загальна довжина вусів: {user_mustache_length[user_id]:.2f} мм.")