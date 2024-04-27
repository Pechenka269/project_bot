from random import randint
import wikipedia
import requests
import math
from telebot import types
import telebot
import datetime
import threading

bot_token = "1972685095:AAEO56f9bxOARnFxwG-8mJYx5w9sYy5k_p4"

bot = telebot.TeleBot(bot_token)
wikipedia.set_lang("ru")

OWM_API_KEY = "585dfca480e94128dcfbb9983056fcff"
code_to_smile = {
    "clear": "Ясно \U00002600",
    "clouds": "Облачно \U00002601",
    "rain": "Дождь \U00002614",
    "drizzle": "Дождь \U00002614",
    "thunderstorm": "Гроза \U000026A1",
    "snow": "Снег \U0001F328",
    "mist": "Туман \U0001F32B"
}


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data["cod"] != 200:
        return "Город не найден"

    city = data["name"]
    cur_temp = round(data["main"]["temp"])
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    feels_like = round(data['main']['feels_like'])
    wind = data["wind"]["speed"]
    description = data["weather"][0]["description"]
    length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
        data["sys"]["sunrise"])
    sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
    sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
    if description.split()[0] in code_to_smile:
        wd = code_to_smile[description.split()[0]]
    else:
        wd = "Посмотри в окно, я не понимаю, что там за погода..."

    return f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n" \
           f"Погода в городе: {city}\n" \
           f"Температура: {cur_temp}°C\n" \
           f"Ощущается как {feels_like}°C\n" \
           f"Погода: {wd}\n" \
           f"Влажность: {humidity}%\n" \
           f"Давление: {math.ceil(pressure / 1.333)} мм.рт.ст\n" \
           f"Ветер: {wind} м/с \n" \
           f"Восход солнца: {sunrise_timestamp}\n" \
           f"Закат солнца: {sunset_timestamp}\n" \
           f"Продолжительность дня: {length_of_the_day}\n" \
           f"Хорошего дня!"


@bot.message_handler(commands=['weather'])
def weather(message):
    try:
        city = message.text.split()[1]
        if not city:
            bot.send_message(message.chat.id, "Введите название города")
            return
        weather_info = get_weather(city)
        bot.send_message(message.chat.id, weather_info)
    except:
        bot.send_message(message.chat.id, 'Введите название города корректно и на английском')


@bot.message_handler(commands=['reminder'])
def reminder_message(message):
    bot.send_message(message.chat.id, 'Введите название напоминания:')
    bot.register_next_step_handler(message, set_reminder_name)


def set_reminder_name(message):
    user_data = {}
    user_data[message.chat.id] = {'reminder_name': message.text}
    bot.send_message(message.chat.id,
                     'Введите дату и время, когда вы хотите получить напоминание в формате ГГГГ-ММ-ДД чч:мм:сс.')
    bot.register_next_step_handler(message, reminder_set, user_data)


def reminder_set(message, user_data):
    try:
        reminder_time = datetime.datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        delta = reminder_time - now
        if delta.total_seconds() <= 0:
            bot.send_message(message.chat.id, 'Вы ввели прошедшую дату, попробуйте еще раз.')
        else:
            reminder_name = user_data[message.chat.id]['reminder_name']
            bot.send_message(message.chat.id,
                             'Напоминание "{}" установлено на {}.'.format(reminder_name, reminder_time))
            reminder_timer = threading.Timer(delta.total_seconds(), send_reminder, [message.chat.id, reminder_name])
            reminder_timer.start()
    except ValueError:
        bot.send_message(message.chat.id, 'Вы ввели неверный формат даты и времени, попробуйте еще раз.')


def send_reminder(chat_id, reminder_name):
    bot.send_message(chat_id, 'Время получить ваше напоминание "{}"!'.format(reminder_name))


@bot.message_handler(commands=['find'])
def find(message):
    try:
        in_file = wikipedia.summary(message.text.split()[1])
        file_wiki = open('find_result.txt', 'w', encoding="utf-8")
        file_wiki.write(in_file)
        file_wiki.close()
        bot.send_message(message.chat.id, in_file)
        sending_file = open('find_result.txt', 'rb')
        bot.send_document(message.chat.id, sending_file)
        sending_file.close()
    except:
        bot.send_message(message.chat.id, 'Вы ввели неверное название, попробуйте еще раз.')


def get_data_from_file(day):
    f = open(day, "r", encoding='utf-8')
    data = f.read()
    f.close()
    return data


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "Вот список команд: /roll (случайное число), /timetable (расписание уроков и звонков),"
                     " /find и запрос из википедии,"
                     " /coin, /weather и название города на английском,"
                     " /joke(анекдоты про чака нориса), /reminder (напоминалка)")


@bot.message_handler(commands=['timetable'])
def timetable(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Понедельник", callback_data='4'),
               types.InlineKeyboardButton("Вторник", callback_data='5'))
    markup.add(types.InlineKeyboardButton("Среда", callback_data='6'),
               types.InlineKeyboardButton("Четверг", callback_data='7'))

    markup.add(types.InlineKeyboardButton("Пятница", callback_data='8'),
               types.InlineKeyboardButton("Звонки", callback_data='9'))

    bot.reply_to(message, 'Выбери день недели или расписание звонков', reply_markup=markup)


@bot.message_handler(commands=['joke'])
def get_joke(message):
    response = requests.get('https://api.chucknorris.io/jokes/random')
    joke = response.json()['value']
    bot.send_message(message.chat.id, joke)


@bot.message_handler(commands=["MMM"])
def inline(message):
    bot.send_message(message.chat.id, 'Пирамида')
    img = open("Mavrodi.jpg", 'rb')
    bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['roll'])
def roll(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("10", callback_data='1'))
    markup.add(types.InlineKeyboardButton("100", callback_data='2'))
    markup.add(types.InlineKeyboardButton("1000", callback_data='3'))
    bot.reply_to(message, 'Выбери крайнее число генерации', reply_markup=markup)


@bot.message_handler(commands=['coin'])
def coin(message):
    b = randint(0, 1)
    if b > 0:
        bot.send_message(message.chat.id, 'Орел')
    else:
        bot.send_message(message.chat.id, 'Решка')


@bot.callback_query_handler(func=lambda callback: True)
def button(callback):
    if callback.data == "1":
        bot.send_message(callback.message.chat.id, str(randint(0, 10)))
    elif callback.data == "2":
        bot.send_message(callback.message.chat.id, str(randint(0, 100)))
    elif callback.data == "3":
        bot.send_message(callback.message.chat.id, str(randint(0, 1000)))
    elif callback.data == "4":
        bot.send_message(callback.message.chat.id, get_data_from_file("mon.txt"))
    elif callback.data == "5":
        bot.send_message(callback.message.chat.id, get_data_from_file("tue.txt"))
    elif callback.data == "6":
        bot.send_message(callback.message.chat.id, get_data_from_file("wed.txt"))
    elif callback.data == "7":
        bot.send_message(callback.message.chat.id, get_data_from_file("thu.txt"))
    elif callback.data == "8":
        bot.send_message(callback.message.chat.id, get_data_from_file("fri.txt"))
    elif callback.data == "9":
        bot.send_message(callback.message.chat.id, get_data_from_file("bel.txt"))
    # если выбрано первое, открывается следующее меню из кнопок со "стилями"
    elif callback.text == "первое":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("стиль1")
        btn2 = types.KeyboardButton("стиль2")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(callback.chat.id, text="Направление 1", reply_markup=markup)

    # если выбрано второе, открывается следующее меню из кнопок со "стилями"
    elif callback.text == "второе":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("стиль3")
        btn2 = types.KeyboardButton("стиль4")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(callback.chat.id, "Направление 2", reply_markup=markup)

    # если выбрано третье, возврат в главное меню
    elif callback.text == "Вернуться в главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Начать обработку")
        markup.add(button1)
        bot.send_message(callback.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)

    # иначе, принудительный возврат в главное меню
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Начать обработку")
        markup.add(button1)
        bot.send_message(callback.chat.id, text="Такой команды нет. Вы возвращены в главное меню", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать обработку")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот помощник, для списка команд введите /help".format(
                         message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Начать обработку":
        bot.send_message(message.chat.id, text="Жду твою фотографию")


@bot.message_handler(content_types=['photo'])
def photo(message):
    # меню из кнопок с выбором направления обработки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("первое")
    btn2 = types.KeyboardButton("второе")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="Выбери направление".format(message.from_user), reply_markup=markup)


bot.polling(none_stop=True)
