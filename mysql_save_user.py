import mysql.connector
from mysql.connector import Error
import datetime

# функция записи пользователя бота в БД его никнейма, имени, фамилии и номера телефона
def saveUser(username, first_name, last_name, phone_number):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='localhost', database='walkmodabot', user='database_login', password='db_pass')

        if conn.is_connected():
            print('... Connected to MySQL database ...')

        hash_string = username+first_name+last_name
        # вытаскиваем из базы данных поле hash
        cursor = conn.cursor()
        query = "SELECT hash FROM users"
        cursor.execute(query)
        row = cursor.fetchone()
        # и перебираем все хэш строки сравнивая: был ли такой пользователь зареган в БД, если он есть в БД row[0] == hash_string,
        #   тогда не пишем его в БД
        # если пользователь еще не записывался в БД: 
        #   тогда выполняется код запроса к БД query INSERT на запись полей этого нового пользователя в БД
        while row is not None:
            if row[0] == hash_string:
            # пользователь уже есть в базе по hashstring, выходим из цикла (break) ничего не записывая в БД 
            # закрывая соединение с БД conn.close()
                print("User with hash = %s is found!" % row[0])
                conn.close()
                break
            row = cursor.fetchone()

        # время совершения заказа пользователя
        today = datetime.datetime.today()
        user_time = today.strftime("%Y-%m-%d---%H:%M:%S")

        # если пользователя еще нет в БД, следовательно это новый юзер - записываем все его поля в БД users
        query = "INSERT INTO users (username, first_name, last_name, phone_number, hash, usertime) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"

        args = (username, first_name, last_name, phone_number, hash_string, user_time)

        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        print ('insert new user success!')

    except Error as e:
        print(e)

    finally:
        conn.close()
