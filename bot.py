# Вся логика тг бота по типу кнопок и команд
# Описание таблиц базы данных
import os
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot,types
from ai import text_to_dialogflow

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton(text="📂 Посмотреть все файлы")
    button_2 = types.KeyboardButton(text="📥 Загрузить файл")
    markup.row(button_1, button_2)
    return markup

#Начала точнее команда старт
@bot.message_handler(commands=["start"])
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    keyboard = create_main_keyboard()

#TODO Не забыть отображать имена пользователей
    cursor.execute('SELECT telegram_id FROM users WHERE telegram_id = ?', (user_id,))
    result = cursor.fetchone() 

    if result is None:
        bot.send_message(chat_id, "Hi, welcome to EDUVAULT!", reply_markup=keyboard)

        cursor.execute(
            'INSERT INTO users (telegram_id, username) VALUES (?, ?)', 
            (user_id, username)
        )
        connection.commit()
    else:
        bot.send_message(chat_id, "Welcome back!", reply_markup=keyboard)

    connection.close()

# Cохранение файлов в БД!
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    title = message.document.file_name
    file_id= message.document.file_id
    user_id = message.from_user.id

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO materials (title, file_id, uploaded_by) VALUES (?, ?, ?)', (title, file_id, user_id))

    connection.commit()
    connection.close()

    bot.send_message(message.chat.id, "Файл успешно сохранен!") # Я тут написал потому что если бд зависнет мы не отправляли ложное сообщение

# Выдача документов
@bot.message_handler(commands=["list"])
def show_docs(message):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT title, file_id FROM materials')
    files = cursor.fetchall()
    connection.close()

    if not files:
        bot.send_message(message.chat.id, "Пока что пусто, но вы можете добавить файлы!")
    else:
        bot.send_message(message.chat.id, "Вот все доступные материалы в EduVault:")
        for file_name, telegram_file_id in files:
            # Бот отправляет документ, используя его file_id, и подписывает его оригинальным именем
            bot.send_document(message.chat.id, telegram_file_id, caption=f"Название: {file_name}")

# Привяка кнопок к функциям
@bot.message_handler(func=lambda message: message.text == "📂 Посмотреть все файлы")
def handle_list_button(message):
    show_docs(message)


@bot.message_handler(func=lambda message: message.text == "📥 Загрузить файл")
def handle_upload_button(message):
    bot.send_message(message.chat.id, "📥Простоо перетащи или прикрепи любой документ (PDF, DOCX) в этот чат, и мы сохраним его в базу данных!.")

# Получение и отправка текста с dialogflow
@bot.message_handler(content_types=['text'])
def handle_ai_messages(message):
    chat_id = message.chat.id
    user_text = message.text

    PROJECT_ID = "eduvault-inoi" 
    SESSION_ID = str(message.from_user.id)

    try:
        ai_response = text_to_dialogflow(PROJECT_ID, SESSION_ID, user_text)
        bot.send_message(chat_id, ai_response)
        
    except Exception as e:
        print(f"Ошибка при работе с Dialogflow: {e}")
        bot.send_message(chat_id, "Извини, я призадумался. Попробуй спросить еще раз!")


if __name__ == "__main__":
    print("Бот Работает!")
    bot.infinity_polling()

