import time
import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
import requests
from bs4 import BeautifulSoup
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

        weather_all = soup.find_all('span', {'class': 'text text_block text_bold_medium margin_bottom_10'})
        condition_all = soup.find_all('span', {'class': 'text text_block text_light_normal text_fixed'})
        feels_like = soup.find_all('span', {'class': 'text text_block text_light_normal text_fixed color_gray'})

        return weather_all, condition_all, feels_like
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching weather data: {e}")
        return None, None, None

# Функция для форматирования сообщения о погоде
def get_message(weather_all, condition_all, feels_like):
    if not weather_all or not condition_all or not feels_like:
        return 'Сайтик лёг, пусть отдохнет немножечко)'

    result = ''
    times = ('ночью', 'утром', 'днем', 'вечером')
    for i, time_of_day in enumerate(times):
        result += f'Погода {time_of_day}: {weather_all[i].text}, {condition_all[i].text}, {feels_like[i].text}\n'

    return result

# Настройка бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name

    # Работа с кнопками:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Погода на сегодня", "Погода на завтра", "Погода на послезавтра")

    logging.info(f'{user_id=} {user_full_name=} {time.asctime()}')

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
async def today_weather(message: types.Message):
    weather_all, condition_all, feels_like = fetch_weather_data()
    await message.answer(get_message(weather_all[:4], condition_all[:4], feels_like[:4]))

@dp.message_handler(Text(equals='Погода на завтра'))
async def tomorrow_weather(message: types.Message):
    weather_all, condition_all, feels_like = fetch_weather_data()
    await message.answer(get_message(weather_all[4:8], condition_all[4:8], feels_like[4:8]))

@dp.message_handler(Text(equals='Погода на послезавтра'))
async def day_after_tomorrow_weather(message: types.Message):
    weather_all, condition_all, feels_like = fetch_weather_data()
    await message.answer(get_message(weather_all[8:12], condition_all[8:12], feels_like[8:12]))

if __name__ == '__main__':
    executor.start_polling(dp)