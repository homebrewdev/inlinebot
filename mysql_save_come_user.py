import mysql.connector
from mysql.connector import Error
import datetime

# функция записи пользователя бота в БД его имя и тд
def saveComeUser(username, first_name, last_name, phone_number):
    """ Connect to MySQL database """
    try:
    	# инициализируем коннектор к mySQL
        conn = mysql.connector.connect(host='localhost', database='walkmodabot', user='database_login', password='db_pass')

        # записываем вошедших пользователей в таблицу come_users
        cursor = conn.cursor()
        # хеш строка = сумма полей username + Имя + Фамилия
        hash_string = username+first_name+last_name
        # время входа пользователя (когда он нажал старт или просто начал с ботом работать - нажимать кнопки)
        today = datetime.datetime.today()
        user_time = today.strftime("%Y-%m-%d---%H:%M:%S")
        # запрос SQL
        query = "INSERT INTO come_users (username, first_name, last_name, phone_number, hash, usertime) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        args = (username, first_name, last_name, phone_number, hash_string, user_time)
        # инжектнули SQL и подтвердили операцию commit
        cursor.execute(query, args)
        conn.commit()

    except Error as e:
        print(e)

    finally:
        conn.close()
