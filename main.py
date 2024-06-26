import requests
import datetime
from pprint import pprint
from config import open_weather_token


def degrees_to_direction(degrees):
    directions = [
        "Северное", "Северо-восточное","Восточное",
        "Юго-восточное", "Южное", "Юго-западное",
        "Западное","Северо-западное"
    ]
    idx = round(degrees / 45) % 8
    return directions[idx]

def get_weather(lon, lat, open_weather_token):


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
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        pprint(data)

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

        print(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}***\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather} C° {wd}\n"
              f"Влажность: {humidity} %\nДавление: {pressure} мм.рт.ст\nВетер: {wind['speed']} м/с\n"
              f"Направление ветра: {degrees_to_direction(wind['deg'])}\n"
              f"Восход: {sunrise_timestamp}\n"
              f"Закат: {sunset_timestamp}\nПродолжительность дня: {length_day} ч\n"
              f"Время до заката: {time_until_sunset}\n")

    except Exception as ex:
        print(ex)
        print("Не удалось получить данные о погоде.")

def main():
    try:
        lon = float(input("Введите долготу: "))
        lat = float(input("Введите широту: "))
        get_weather(lon, lat, open_weather_token)
    except ValueError:
        print("Некорректный формат координат.")

if __name__ == "__main__":
    main()
