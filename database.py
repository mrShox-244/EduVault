# Настройки подключения к БД
import sqlite3
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
telegram_id INTEGER UNIQUE,
id INTEGER,
username TEXT,
karma INTEGER,
role TEXT
    )
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS materials (
unique_id INTEGER UNIQUE,
title TEXT,
file_id TEXT,
subject TEXT,
uploaded_by INTEGER           
    )
''')

connection.commit()
connection.close()