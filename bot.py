# Вся логика тг бота по типу кнопок и команд
# Описание таблиц базы данных
import os
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)

#Начала точнее команда старт
@bot.message_handler(commands=["start"])
def register_user(message):

    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

#TODO Не забыть отображать имена пользователей
    cursor.execute('SELECT telegram_id FROM users WHERE telegram_id = ?', (user_id,))
    result = cursor.fetchone() 

    if result is None:
        bot.send_message(chat_id, "Hi, welcome to EDUVAULT!")

        cursor.execute(
            'INSERT INTO users (telegram_id, username) VALUES (?, ?)', 
            (user_id, username)
        )
        connection.commit()
    else:
        bot.send_message(chat_id, "Welcome back!")

    connection.close()

if __name__ == "__main__":
    print("Бот успешно запущен и слушает команды...")
    bot.infinity_polling()