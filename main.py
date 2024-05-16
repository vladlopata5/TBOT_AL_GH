# import math
# import random
import telebot
from telebot import types
import psycopg2

from t_func import check_and_create_tables

bot = telebot.TeleBot('6889928482:AAGEDFlbcsLv9_r9Hjch6I6HtaXpPfxbUWY')

conn = psycopg2.connect(
    dbname='telegram_bot',
    user='postgres',
    password='Admin',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()


@bot.message_handler(commands=['start'])
def menu(message):
    check_and_create_tables()
    # Проверка наличия пользователя в базе данных
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    user_exists = cursor.fetchone()

    if user_exists:
        # Отправка приветственного сообщения
        bot.send_message(message.chat.id, "Привет, удачной игры!")
    else:
        # Добавление пользователя в таблицу
        cursor.execute("INSERT INTO users (telegram_id) VALUES (%s)", (message.from_user.id,))
        conn.commit()
        # Отправка приветственного сообщения
        bot.send_message(message.chat.id, "Привет, рад знакомству!")

    # Отправка клавиатуры с кнопками
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button_alchemy = types.KeyboardButton('Алхимия')
    button_characters = types.KeyboardButton('Мои персонажи')
    button_dice = types.KeyboardButton('Кубики')
    button_help = types.KeyboardButton('Помощь')
    keyboard.add(button_alchemy, button_dice, button_characters, button_help)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


bot.infinity_polling(none_stop=True)
