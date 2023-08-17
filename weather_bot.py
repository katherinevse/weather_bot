import time
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text


TOKEN = "6013011791:AAGSYCm8Qeo94l9pqGApyS2lkTRRVcbrzUM"
MSG = "Я могу рассказать вам про погоду только в Москве!"

WEATHER_URL = 'https://pogoda.mail.ru/prognoz/moskva/extended/'

# Функция для получения данных о погоде с сайта
def fetch_weather_data():
    try:
        response = requests.get(WEATHER_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        weather_blocks = soup.find_all('div', {'class': 'day__temperature'})
        condition_blocks = soup.find_all('div', {'class': 'day__description'})
        feels_like_blocks = soup.find_all('div', {'class': 'day__feels-like'})

        return weather_blocks, condition_blocks, feels_like_blocks
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching weather data: {e}")
        return None, None, None

# Функция для форматирования сообщения о погоде
def format_weather_message(time_of_day, weather, condition, feels_like):
    return f'Погода {time_of_day}: {weather}, {condition}, {feels_like}'

# Настройка бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Работа с кнопками:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Погода на сегодня", "Погода на завтра", "Погода на послезавтра")

    current_time = datetime.now()
    if current_time.hour >= 17:
        greeting = "Добрый вечер"
    elif current_time.hour >= 12:
        greeting = "Добрый день"
    else:
        greeting = "Доброе утро"

    await message.reply(f"{greeting}, {user_name}")
    await message.answer("В какой день вы хотите узнать погоду в Москве?", reply_markup=keyboard)

@dp.message_handler(Text(equals="Погода на сегодня"))
@dp.message_handler(Text(equals='Погода на завтра'))
@dp.message_handler(Text(equals='Погода на послезавтра'))
async def weather_by_day(message: types.Message):
    day = message.text.replace("Погода на ", "")
    weather_blocks, condition_blocks, feels_like_blocks = fetch_weather_data()

    if not weather_blocks or not condition_blocks or not feels_like_blocks:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        return

    day_indices = {'сегодня': 0, 'завтра': 1, 'послезавтра': 2}
    index = day_indices.get(day)

    if index is not None:
        start = index * 4
        end = start + 4
        weather_data = zip(weather_blocks[start:end], condition_blocks[start:end], feels_like_blocks[start:end])
        messages = [format_weather_message(time_of_day, weather.text, condition.text, feels_like.text)
                    for time_of_day, weather, condition, feels_like in weather_data]

        await message.answer("\n".join(messages))
    else:
        await message.answer("Извините, не могу предоставить погоду на выбранный день.")

if __name__ == '__main__':
    executor.start_polling(dp)
