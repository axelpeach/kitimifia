import logging
from telegram.ext import Application
from bot.config import TELEGRAM_TOKEN
from bot.handlers import start, murr, mustache

# Логування для налагодження
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Ініціалізуємо бота з токеном
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("murr", murr))
    application.add_handler(CommandHandler("usik", mustache))

    # Запускаємо бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())  # Запускаємо основну функцію
