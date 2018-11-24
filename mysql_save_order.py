import mysql.connector
from mysql.connector import Error
import datetime

# функция записи пользователя бота в БД деталей заказа
def saveOrder(username, comb, VIP, rost, razmer, quantity, phone_number):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='localhost', database='walkmodabot', user='database_login', password='db_pass')

        # курсор к mySQL БД
        cursor = conn.cursor()

        # время совершения заказа пользователя
        today = datetime.datetime.today()
        ordertime = today.strftime("%Y-%m-%d---%H:%M:%S")
        
        # формируем запрос SQL
        query = "INSERT INTO orders (username, comb, VIP, rost, razmer, quantity, phone_number, ordertime) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        args = (username, comb, VIP, rost, razmer, quantity, phone_number, ordertime)

        # инжектнули SQL и подтвердили операцию commit
        cursor.execute(query, args)
        conn.commit()

        print ('save new order success!')

    except Error as e:
        print(e)

    finally:
        conn.close()
