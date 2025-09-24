
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# API ключ для курсов валют
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ В файле .env отсутствует TELEGRAM_BOT_TOKEN")

if not EXCHANGE_API_KEY:
    raise ValueError("❌ В файле .env отсутствует EXCHANGE_API_KEY")
