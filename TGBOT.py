import requests
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8669565510:AAGTiinEDUerA8kUF2I9cVPXl8qEJ0e_FYw"
API_KEY = "778dce10acdc408b31b87ede8f8e60c1"

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

    # 🔥 знаходимо найближчий час (кратний 3)
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

    now = datetime.now().strftime("%H:%M")

    await message.answer(
        f"🕒 Запит: {hour}:00\n"
        f"📊 Найближчий прогноз: {target[:5]}\n"
        # f"🕓 Зараз: {now}\n"
        f"🌡 Температура в {target[:5]}: {temp}°C\n"
        f"☁️ Погода: {desc}"
    )


# 🔹 ЗАПУСК
if __name__ == "__main__":
    executor.start_polling(dp)