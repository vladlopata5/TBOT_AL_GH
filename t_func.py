import telebot
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
                        user_id INTEGER REFERENCES users(id),
                        ingredient_id INTEGER,
                        quantity INTEGER,
                        PRIMARY KEY (user_id, ingredient_id)
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