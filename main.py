# import math
# import random
import telebot
from telebot import types
import psycopg2

from t_func import check_and_create_tables, my_characters_message, add_character_name, character_menu, character_choose, \
    character_edit, delete_character_check, delete_character_confirm

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


# Функция для обработки текстовых сообщений
@bot.message_handler(func=lambda message: message.text == 'Мои персонажи')
def text_my_characters(message):
    my_characters_message(message)

# Обработка кнопки 'Добавить персонажа'
@bot.callback_query_handler(func=lambda call: call.data == 'create_character')
def btn_add_character(call):
    # Запрашиваем у пользователя данные для добавления персонажа
    bot.send_message(call.message.chat.id, 'Введите имя персонажа:')
    bot.register_next_step_handler(call.message, add_character_name, bot)

# Обработка кнопки 'персонажа' из списка персонажей
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_character_'))
def btn_choose_character_callback(call):
    # Извлекаем ID персонажа из callback_data
    character_id = int(call.data[len("select_character_"):])
    character_menu(character_id, call.message.chat.id, bot)

# Обработка кнопки "выбрать персонажа"
@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_'))
def btn_choose(call):
    character_id = int(call.data[len("choose_"):])
    character_choose(character_id, call.from_user.id, call.message.chat.id, bot)

# Обработка кнопки "редактировать персонажа"
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def btn_choose(call):
    character_id = int(call.data[len("edit_"):])
    character_edit(character_id, call.message, bot)

# Обработка кнопки "удалить персонажа"
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def btn_choose(call):
    character_id = int(call.data[len("delete_"):])
    delete_character_check(character_id, call.message.chat.id, bot)
# Обработка кнопки "подтвердить удаление персонажа"
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_character(call):
    character_id = int(call.data[len("confirm_delete_"):])
    delete_character_confirm(character_id, call.message.chat.id, bot)







bot.infinity_polling(none_stop=True)
