import requests
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import os
import threading
from flask import Flask

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

if not TOKEN or not API_KEY:
    raise ValueError("TOKEN або API_KEY не задані!")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🔹 КНОПКИ
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton("🌅 Ранок"),
    KeyboardButton("☀️ День"),
    KeyboardButton("🌇 Вечір")
)

# 🔹 START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Обери час:", reply_markup=keyboard)


# 🔹 КНОПКИ → ПРОСИМО ГОДИНУ
@dp.message_handler(lambda message: message.text in ["🌅 Ранок", "☀️ День", "🌇 Вечір"])
async def ask_time(message: types.Message):
    await message.answer("Напиши годину (наприклад: 20)")


# 🔹 ОБРОБКА ГОДИНИ
@dp.message_handler(lambda message: message.text.isdigit())
async def weather_by_hour(message: types.Message):
    city = "Ternopil"
    hour = int(message.text)

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ua"
    response = requests.get(url).json()

    closest_hour = round(hour / 3) * 3
    if closest_hour == 24:
        closest_hour = 0

    target = f"{closest_hour:02d}:00:00"

    temp = None
    desc = None

    for item in response['list']:
        if target in item['dt_txt']:
            temp = item['main']['temp']
            desc = item['weather'][0]['description']
            break

    if temp is None:
        await message.answer("❌ Не знайдено прогноз")
        return

    await message.answer(
        f"🕒 Запит: {hour}:00\n"
        f"📊 Найближчий прогноз: {target[:5]}\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Погода: {desc}"
    )


# 🔹 WEB SERVER (щоб Render не падав)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"


def run_web():
    app.run(host="0.0.0.0", port=10000)


# 🔥 ГОЛОВНИЙ ФІКС (ВАЖЛИВО!)
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot started and webhook cleared")


# 🔹 ЗАПУСК
if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    print("🚀 Starting bot...")

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )
