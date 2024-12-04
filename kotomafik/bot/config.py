import os
from dotenv import load_dotenv

# Завантаження змінних середовища з .env (для локальної розробки)
load_dotenv()

# Токен Telegram бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# API-ключ для UptimeRobot
UPTIMEROBOT_API_KEY = os.getenv("UPTIMEROBOT_API_KEY")