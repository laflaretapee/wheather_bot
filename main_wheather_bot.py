import requests
import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import tg_token, open_weather_token
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
import asyncio

router = Router()

bot = Bot(token=tg_token)
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_location = State()
    waiting_for_city = State()

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Выбери способ получения погоды:", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Погода по местоположению", request_location=True)],
            [types.KeyboardButton(text="Погода по названию города")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))

@router.message(F.text == "Погода по названию города")
async def city_weather_cmd(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_city)
    await message.answer("Пожалуйста, введи название города.")

@router.message(Form.waiting_for_city)
async def city_weather_input(message: types.Message, state: FSMContext):
    city = message.text
    await get_weather_by_city(message, city)

@router.message(F.location)
async def location_cmd(message: types.Message, state: FSMContext):
    latitude = message.location.latitude
    longitude = message.location.longitude
    await get_weather(message, latitude, longitude)

def degrees_to_direction(degrees):
    directions = [
        "Северное", "Северо-восточное", "Восточное",
        "Юго-восточное", "Южное", "Юго-западное",
        "Западное", "Северо-западное"
    ]
    idx = round(degrees / 45) % 8
    return directions[idx]

async def get_weather(message: types.Message, latitude: float, longitude: float):
    await _get_weather(message, latitude=latitude, longitude=longitude)

async def get_weather_by_city(message: types.Message, city: str):
    await _get_weather(message, city=city)

async def _get_weather(message: types.Message, latitude: float = None, longitude: float = None, city: str = None):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Drizzle": "Дождь \U00002614",
        "Rain": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        params = {}
        if latitude and longitude:
            params = {"lat": latitude, "lon": longitude, "appid": open_weather_token, "units": "metric"}
        elif city:
            params = {"q": city, "appid": open_weather_token, "units": "metric"}

        r = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        r.raise_for_status()  # Проверка на ошибки HTTP
        data = r.json()

        if 'name' not in data:
            raise ValueError("Отсутствует ключ 'name' в ответе от API")

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Смотри сам на улицу!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]

        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        length_day = sunset_timestamp - sunrise_timestamp

        time_until_sunset = sunset_timestamp - datetime.datetime.now()

        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}***\n"
                            f"Погода в городе: {city}\nТемпература: {cur_weather} C° {wd}\n"
                            f"Влажность: {humidity} %\nДавление: {pressure} мм.рт.ст\nВетер: {wind['speed']} м/с\n"
                            f"Направление ветра: {degrees_to_direction(wind['deg'])}\n"
                            f"Восход: {sunrise_timestamp}\n"
                            f"Закат: {sunset_timestamp}\nПродолжительность дня: {length_day} ч\n"
                            f"Время до заката: {time_until_sunset}\n")

    except requests.exceptions.RequestException as e:
        await message.reply(f"\U00002620 Не удалось получить данные о погоде \U00002620\nОшибка HTTP: {str(e)}")
    except ValueError as e:
        await message.reply(f"\U00002620 Не удалось получить данные о погоде \U00002620\nОшибка данных: {str(e)}")
    except Exception as e:
        await message.reply(f"\U00002620 Не удалось получить данные о погоде \U00002620\nОшибка: {str(e)}")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())