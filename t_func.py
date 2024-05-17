import telebot
from telebot import types
import psycopg2

bot = telebot.TeleBot('6889928482:AAGEDFlbcsLv9_r9Hjch6I6HtaXpPfxbUWY')

conn = psycopg2.connect(
    dbname='telegram_bot',
    user='postgres',
    password='Admin',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

def get_user_id(user_tg_id):
    cursor.execute('SELECT id FROM users WHERE telegram_id = %s', (user_tg_id,))
    user_id = int(cursor.fetchone()[0])
    return user_id

# Функция для проверки и создания таблиц
def check_and_create_tables():
    # Проверка и создание таблиц
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        telegram_id INTEGER,
                        current_character_id INTEGER
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS characters (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        name VARCHAR(255),
                        skill INTEGER,
                        experience INTEGER,
                        known_recipes JSONB
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        character_id INTEGER REFERENCES characters(id),
                        ingredient_id INTEGER,
                        quantity INTEGER,
                        PRIMARY KEY (character_id, ingredient_id)
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        type VARCHAR(50),
                        value INTEGER,
                        description TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS potions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        type VARCHAR(50),
                        description TEXT,
                        difficulty INTEGER,
                        value INTEGER,
                        recipe JSONB
                      )''')

    conn.commit()

def my_characters_message(message):
    # Получаем Telegram ID пользователя
    user_id = get_user_id(message.from_user.id)
    # Проверяем, есть ли у пользователя выбранный персонаж
    cursor.execute("SELECT current_character_id FROM users WHERE id = %s", (user_id,))
    selected_character = cursor.fetchone()[0]
    # Отправляем сообщение с информацией о выбранном персонаже или о его отсутствии
    if selected_character:
        cursor.execute("SELECT name, skill FROM characters WHERE id = %s", (selected_character,))
        selected_character_data = cursor.fetchone()
        if selected_character_data:
            selected_character_name, selected_character_skill = selected_character_data
            bot.send_message(message.chat.id, f"Выбранный персонаж: \n{selected_character_name}, [{selected_character_skill}] - лвл алхимии.")
        else:
            bot.send_message(message.chat.id,f"Выбранный персонаж был удалён")
    else:
        bot.send_message(message.chat.id, "У тебя нет выбранного персонажа.")

    # Получаем список всех персонажей пользователя
    cursor.execute("SELECT name, skill, id FROM characters WHERE user_id = %s", (user_id,))
    characters = cursor.fetchall()

    # Если у пользователя есть персонажи, формируем сообщение с кнопками
    if characters:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for character in characters:
            character_name, character_skill, character_id = character
            button_text = f"{character_name} [{character_skill} лвл]"
            button = types.InlineKeyboardButton(text=button_text, callback_data=f"select_character_{character_id}")
            keyboard.add(button)

        # Добавляем кнопку "Создать нового персонажа"
        create_button = types.InlineKeyboardButton(text="Создать нового персонажа", callback_data="create_character")
        keyboard.add(create_button)

        bot.send_message(message.chat.id, "Твои персонажи:", reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        create_button = types.InlineKeyboardButton(text="Создать нового персонажа", callback_data="create_character")
        keyboard.add(create_button)
        bot.send_message(message.chat.id, "У тебя пока нет ни одного персонажа.", reply_markup=keyboard)

# добавление имени персонажа
def add_character_name(message, bot):
    # Сохраняем введенное имя и запрашиваем следующую информацию
    name = message.text
    bot.send_message(message.chat.id, 'Введите уровень навыка алхимии:\n'
                                      'от 1 до 20\n'
                                      'где 1 - совершенно не знаком с алхимией\n'
                                      '8 - может готовить простые зелья\n'
                                      '12 - профессиональный алхимик\n'
                                      '16 - мастер алхимии\n'
                                      '20 - топ 1 алхимик мира')
    bot.register_next_step_handler(message, lambda msg: add_character_skill(msg, bot, name))

# добавление уровня алхимии персонажа
def add_character_skill(message, bot, name):
    # Сохраняем скилл
    try:
        skill = int(message.text)
        user_id = get_user_id(message.from_user.id)
        cursor.execute(f'''
            INSERT INTO characters (user_id, name, skill, experience)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, name, skill, 0))
        conn.commit()
        bot.send_message(message.chat.id, 'Приятно познакомиться, герой.')
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка при добавлении героя. Error 902')

def character_menu(character_id, chat_id, bot):
    # Получаем имя персонажа и навыки для вывода на кнопках
    cursor.execute('SELECT name, skill FROM characters WHERE ID = %s', (character_id,))
    character_data = cursor.fetchone()
    if character_data:
        character_name, character_skill = character_data
        # Создаем инлайн-кнопки с командами 'Выбрать', 'Редактировать', 'Удалить'
        keyboard = types.InlineKeyboardMarkup()
        button_choose = types.InlineKeyboardButton('Выбрать', callback_data=f'choose_{character_id}')
        button_edit = types.InlineKeyboardButton('Редактировать', callback_data=f'edit_{character_id}')
        button_delete = types.InlineKeyboardButton('Удалить', callback_data=f'delete_{character_id}')
        keyboard.add(button_choose, button_edit, button_delete)

        # Отправляем сообщение с информацией о персонаже и кнопками
        message_text = f'Имя: {character_name}\nНавык алхимии: {character_skill}'
        bot.send_message(chat_id, message_text, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, 'Произошла ошибка при получении данных о персонаже.')

def character_choose(character_id, tg_id, chat_id, bot):
    cursor.execute('UPDATE users SET current_character_id = %s WHERE telegram_id = %s', (character_id, tg_id))
    conn.commit()
    bot.send_message(chat_id, 'Персонаж выбран как текущий.')

def character_edit(character_id, message, bot):
    cursor.execute('SELECT name, skill FROM characters WHERE ID = %s',
                (character_id,))
    character_data = cursor.fetchone()

    if character_data:
        # Распаковываем данные персонажа
        character_name, character_skill = character_data

        # Запрашиваем новые данные у пользователя
        bot.send_message(message.chat.id, f'Введите новые данные для персонажа {character_name} в формате:\n'
                                          f'Имя, Уровень алхимии\n'
                                          f'Пример: НовыйПерсонаж, 8')

        # Устанавливаем статус для ожидания новых данных
        bot.register_next_step_handler(message, lambda msg: edit_character_data(msg, character_id, bot))
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка при получении данных о персонаже.')

def edit_character_data(message, character_id, bot):
    new_data = message.text.split(',')
    try:
        new_name = new_data[0].strip()
        new_skill = int(new_data[1].strip())
        # Обновляем данные о персонаже в базе данных
        cursor.execute(
            'UPDATE characters SET name = %s, skill = %s WHERE ID = %s',
            (
                new_name, new_skill, character_id))
        conn.commit()
        bot.send_message(message.chat.id, 'Данные о персонаже успешно обновлены.')
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректный формат данных.')

def delete_character_check(character_id, chat_id, bot):
    keyboard = types.InlineKeyboardMarkup()
    button_delete_yes = types.InlineKeyboardButton('Подтверждаю', callback_data=f'confirm_delete_{character_id}')
    button_delete_no = types.InlineKeyboardButton('НЕТ!', callback_data=f'dismiss_delete_{character_id}')
    keyboard.add(button_delete_yes, button_delete_no)
    bot.send_message(chat_id, 'Вы точно хотите удалить своего персонажа?\n'
                              'Это действие нельзя отменить', reply_markup=keyboard)


def delete_character_confirm(character_id, chat_id, bot):
    cursor.execute('DELETE FROM characters WHERE ID = %s', (character_id,))
    conn.commit()
    #cursor.execute('DELETE FROM cauldron WHERE id_character = %s', (character_id,))
    #conn.commit()
    cursor.execute('DELETE FROM inventory WHERE character_id = %s', (character_id,))
    conn.commit()
    bot.send_message(chat_id, 'Персонаж удален.')
    bot.send_animation(chat_id, 'https://c.tenor.com/2bAKt_bnAYMAAAAd/press-f-mg.gif')





