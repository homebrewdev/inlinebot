import telebot
import config
import strings
import time
import settings
import smtplib
from telebot import types
from email.mime.text import MIMEText
from email.header    import Header
from mysql_save_user import saveUser
from mysql_save_order import saveOrder
from mysql_save_come_user import saveComeUser

# инициализируем нашего бота
bot = telebot.TeleBot(config.token)

# определяем класс заказа пользователя
class Customer(object):
    """ Класс Customer: несет всю информацию о заказе пользователя
        Поля:
            comb:     инфо о комбинезоне
            VIP:      тип напонителя
            rost:     рост
            razmer:   размер
            quantity: количество товара

        Методы:
            get_customer_complete_order
    """
    def __init__(self, comb, VIP, rost, razmer, quantity):
        """Constructor"""
        self.comb       = comb
        self.VIP        = VIP
        self.rost       = rost
        self.razmer     = razmer
        self.quantity   = quantity
    
    def get_customer_complete_order(self):
        return "Complete"


# определяем класс User - котрый будет нести всю инфу про нашего юзера, который стал пользоваться ботом
class User(object):
    """ Класс User: несет всю информацию о пользователе
        Поля:
            username:    никнейм в телеграмм
            name:        Имя
            family_name: Фамилия

        Методы: нет
    """
    def __init__(self, username, first_name, last_name, phone_number):
        """Constructor"""
        self.username       = username
        self.first_name     = first_name
        self.last_name      = last_name
        self.phone_number   = phone_number


# обработчик при старте команды - /start
@bot.message_handler(commands=["start"])
def start(message):
    start_dlg(message)


# обработчик при старте команды - /settings
@bot.message_handler(commands=["settings"])
def setting(message):
    bot.send_message(message.chat.id, strings.msg_help)
    start_dlg(message)


# обработчик при старте команды - /help
@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, strings.msg_help)
    start_dlg(message)


# на любую писанину пользователя берем и показываем опять главное меню
@bot.message_handler(content_types=["text"])
def any_msg(message):
    # Создаем клавиатуру и каждую из кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    url_button = types.InlineKeyboardButton(text="Посетите наш instagram", url="https://www.instagram.com/walk.moda/")
    callback_button = types.InlineKeyboardButton(text="Заказ комбинезона", callback_data="order")
    callback_button2 = types.InlineKeyboardButton(text="Отзывы наших клиентов", callback_data="feedback")
    callback_button3 = types.InlineKeyboardButton(text="Новинки сезона", callback_data="new_sales")

    keyboard.add(url_button, callback_button, callback_button2, callback_button3)

    bot.send_message(message.chat.id, strings.msg_hello)
    bot.send_message(message.chat.id, "Выбирай пункт меню для дальнейших действий:", reply_markup=keyboard)


# стартовый диалог с 3-мя кнопками, 3 категории товара
def start_dlg(message):
    # init()

    # записываем все данные о вошедшем пользователе
    user.username = message.chat.username
    user.first_name = message.chat.first_name
    user.last_name = message.chat.last_name
    
    print ("User:\n%s, %s, %s" % (user.username, user.first_name, user.last_name))

    # записываем зашедшего юзера в mysql БД
    saveComeUser(user.username, user.first_name, user.last_name, 'none_phone')

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    # начальное меню из 4 кнопок
    url_button = types.InlineKeyboardButton(text="Посетите наш instagram", url="https://www.instagram.com/walk.moda/")
    callback_button = types.InlineKeyboardButton(text="Заказ комбинезона", callback_data="order")
    callback_button2 = types.InlineKeyboardButton(text="Отзывы наших клиентов", callback_data="feedback")
    callback_button3 = types.InlineKeyboardButton(text="Новинки сезона", callback_data="new_sales")

    # размещаем кнопки
    keyboard.add(url_button, callback_button, callback_button2, callback_button3)

# логотип и первая фраза диалога о выборе категории
    bot.send_photo(message.chat.id, photo=open('res/logo2.png', 'rb'))
    msg_dialog = bot.send_message(message.chat.id, strings.msg_hello, reply_markup=keyboard)


###########################################################################################
# главный обработчик всех нажатий пользователя на кнопки диалога, для формирования заказа
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    # Если сообщение из чата с ботом
    if call.message:
        # Если нажата inline-кнопка "Заказ"
        if call.data == "order":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=strings.msg_category1)
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1)
            category1(call.message)

        # Если нажата inline-кнопка "Отзывы наших клиентов"
        if call.data == "feedback":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=strings.msg_category2)
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category2)
            category2(call.message)
            
        # Если нажата inline-кнопка "Новинки сезона"
        if call.data == "new_sales":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=strings.msg_category3)
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category3)
            category3(call.message)

         # Если нажата inline-кнопка "назад" в главном меню
        if call.data == "back_to_main_menu":
            start_dlg(call.message)

        # уровень диалога выбора цвета комбинезона
        if call.data == strings.msg_category1_1:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_1)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_1)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_1, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_2:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_2)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_2)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_2, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_3:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_3)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_3)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_3, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_4:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_4)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_4)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_4, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_5:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_5)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_5)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_5, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_6:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_6)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_6)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_6, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_7:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_7)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_7)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_7, 'rb'))
            VIP(call.message)

        if call.data == strings.msg_category1_8:
            # Уведомление в верхней части экрана
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_category1_8)
            customer.comb = ("Комбинезон: %s" % strings.msg_category1_8)
            bot.send_photo(call.message.chat.id, photo=open(strings.res_category1_8, 'rb'))
            VIP(call.message)

        # уровень выбора VIP
        if call.data == strings.msg_VIP_button1:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_VIP_button1)
            customer.VIP = ("Комплектация: %s" % strings.msg_VIP_button1)
            rost(call.message)

        if call.data == strings.msg_VIP_button2:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=strings.msg_VIP_button2)
            customer.VIP = ("Комплектация: %s" % strings.msg_VIP_button2)
            rost(call.message)

        if call.data == "back_to_combinez_menu":
            category1(call.message)

        # уровень выбора роста
        if call.data == strings.msg_rost1:
            customer.rost = ("Рост: %s" % strings.msg_rost1)
            razmer(call.message)

        if call.data == strings.msg_rost2: 
            customer.rost = ("Рост: %s" % strings.msg_rost2)
            razmer(call.message)

        if call.data == strings.msg_rost3: 
            customer.rost = ("Рост: %s" % strings.msg_rost3)
            razmer(call.message)

        if call.data == strings.msg_rost4: 
            customer.rost = ("Рост: %s" % strings.msg_rost4)
            razmer(call.message)

        if call.data == strings.msg_rost5: 
            customer.rost = ("Рост: %s" % strings.msg_rost5)
            razmer(call.message)

        if call.data == strings.msg_rost6: 
            customer.rost = ("Рост: %s" % strings.msg_rost6)
            razmer(call.message)

        if call.data == "back_to_VIP_menu":
            print (customer.comb + customer.VIP + customer.rost)
            VIP(call.message)

        # уровень выбора размера
        if call.data == strings.msg_razmer1:
            customer.razmer = ("Размер: %s" % strings.msg_razmer1)
            quantity(call.message)

        if call.data == strings.msg_razmer2: 
            customer.razmer = ("Размер: %s" % strings.msg_razmer2)
            quantity(call.message)

        if call.data == strings.msg_razmer3:
            customer.razmer = ("Размер: %s" % strings.msg_razmer3)
            quantity(call.message)

        if call.data == strings.msg_razmer4: 
            customer.razmer = ("Размер: %s" % strings.msg_razmer4)
            quantity(call.message)

        if call.data == strings.msg_razmer5: 
            customer.razmer = ("Размер: %s" % strings.msg_razmer5)
            quantity(call.message)

        if call.data == strings.msg_razmer6: 
            customer.razmer = ("Размер: %s" % strings.msg_razmer6)
            quantity(call.message)

        if call.data == "back_to_rost_menu":
            rost(call.message)

        # уровень выбора количества товара
        if call.data == strings.quantity1: 
            customer.quantity = ("Количество в шт.: %s" % strings.quantity1)
            complete(call.message)

        if call.data == strings.quantity2: 
            customer.quantity = ("Количество в шт.: %s" % strings.quantity2)
            complete(call.message)

        if call.data == strings.quantity3: 
            customer.quantity = ("Количество в шт.: %s" % strings.quantity3)
            complete(call.message)

        if call.data == strings.quantity4: 
            customer.quantity = ("Количество в шт.: %s" % strings.quantity4)
            complete(call.message)

        if call.data == strings.quantity5: 
            customer.quantity = ("Количество в шт.: %s" % strings.quantity5)
            complete(call.message)

        if call.data == "back_to_razmer_menu":
            razmer(call.message)

        # выбор пользователя - Все в заказе верно или вернуться назад
        if call.data == strings.btn_is_right_order1: 
            request_contact(call.message)

        # если нажали назад то идем в меню выбора комбеза
        if call.data == strings.btn_is_right_order2: 
            category1(call.message)

        # если нажали клавишу запроса контакта то все - после этого формируется заказ и отправляется на почту менеджору
        if call.data == strings.msg_request_tel_number:
            final_order_string = ("| %s\n| %s\n| %s\n| %s\n| %s") % (customer.comb, customer.VIP, customer.rost, customer.razmer, customer.quantity) 
            sendMail(final_order_string)


######################################################
# обработчики переходов по категориям

##########################################
# первая категория товаров:
def category1(message):

    # пишем все поля по пользователю в объект класса User
    user.username = message.chat.username
    user.first_name = message.chat.first_name
    user.last_name = message.chat.last_name
    
    print ("User:\n%s, %s, %s" % (user.username, user.first_name, user.last_name))

    # отсылаем логотип компании
    bot.send_photo(message.chat.id, photo=open('res/walkmoda_P.jpg', 'rb'))

    # разметка кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    callback_button = types.InlineKeyboardButton(text=strings.msg_category1_1, callback_data=strings.msg_category1_1)
    callback_button2 = types.InlineKeyboardButton(text=strings.msg_category1_2, callback_data=strings.msg_category1_2)
    callback_button3 = types.InlineKeyboardButton(text=strings.msg_category1_3, callback_data=strings.msg_category1_3)
    callback_button4 = types.InlineKeyboardButton(text=strings.msg_category1_4, callback_data=strings.msg_category1_4)
    callback_button5 = types.InlineKeyboardButton(text=strings.msg_category1_5, callback_data=strings.msg_category1_5)
    callback_button6 = types.InlineKeyboardButton(text=strings.msg_category1_6, callback_data=strings.msg_category1_6)
    callback_button7 = types.InlineKeyboardButton(text=strings.msg_category1_7, callback_data=strings.msg_category1_7)
    callback_button8 = types.InlineKeyboardButton(text=strings.msg_category1_8, callback_data=strings.msg_category1_8)
    # callback_button9 = types.InlineKeyboardButton(text=strings.msg_category1_9, callback_data=strings.msg_category1_9)
    # кнопка назад в главное меню
    callback_button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_main_menu")

    #размещаем кнопки для первой категории в данном случае для комбинезонов
    keyboard.add(callback_button, callback_button2, callback_button3, callback_button4, callback_button5, 
        callback_button6, callback_button7, callback_button8, callback_button_back)

    msg_dialog = bot.send_message(message.chat.id, strings.msg_category1_bot, reply_markup=keyboard)


#####################################################
# вторая категория(кнопка "отзывы наших клиентов"")
def category2(message):
    bot.send_photo(message.chat.id, photo=open('res/otzuv1.png', 'rb'))
    bot.send_message(message.chat.id, strings.msg_user_feedback)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_main_menu")

    # размещаем кнопки
    keyboard.add(button_back)
    msg_dialog = bot.send_message(message.chat.id, strings.msg_category2_1, reply_markup=keyboard)


#####################################################
# 3-ая категория(кнопка "новинки сезона"")
def category3(message):
    bot.send_photo(message.chat.id, photo=open('res/otzuv2.png', 'rb'))
    bot.send_message(message.chat.id, strings.msg_category3_bot)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_main_menu")

    # размещаем кнопки
    keyboard.add(button_back)
    msg_dialog = bot.send_message(message.chat.id, strings.msg_category3_1, reply_markup=keyboard)


#####################################################
# для обработки выбора VIP или простой наполнитель
def VIP(message):
    bot.send_message(message.chat.id, strings.msg_VIP_info)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text=strings.msg_VIP_button1, callback_data=strings.msg_VIP_button1)
    button2 = types.InlineKeyboardButton(text=strings.msg_VIP_button2, callback_data=strings.msg_VIP_button2)
    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_combinez_menu")

    # размещаем кнопки
    keyboard.add(button1, button2, button_back)
    msg_dialog = bot.send_message(message.chat.id, strings.msg_VIP_info2, reply_markup=keyboard)


#####################################################
# кнопки и меню по выбору роста
def rost(message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton(text=strings.msg_rost1, callback_data=strings.msg_rost1)
    button2 = types.InlineKeyboardButton(text=strings.msg_rost2, callback_data=strings.msg_rost2)
    button3 = types.InlineKeyboardButton(text=strings.msg_rost3, callback_data=strings.msg_rost3)
    button4 = types.InlineKeyboardButton(text=strings.msg_rost4, callback_data=strings.msg_rost4)
    button5 = types.InlineKeyboardButton(text=strings.msg_rost5, callback_data=strings.msg_rost5)
    button6 = types.InlineKeyboardButton(text=strings.msg_rost6, callback_data=strings.msg_rost6)

    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_VIP_menu")

    # размещаем кнопки
    keyboard.add(button1, button2, button3, button4, button5, button6, button_back)

    bot.send_message(message.chat.id, strings.msg_rost_info, reply_markup=keyboard)


##########################################################################################################
# кнопки и меню по выбору роста
def razmer(message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton(text=strings.msg_razmer1, callback_data=strings.msg_razmer1)
    button2 = types.InlineKeyboardButton(text=strings.msg_razmer2, callback_data=strings.msg_razmer2)
    button3 = types.InlineKeyboardButton(text=strings.msg_razmer3, callback_data=strings.msg_razmer3)
    button4 = types.InlineKeyboardButton(text=strings.msg_razmer4, callback_data=strings.msg_razmer4)
    button5 = types.InlineKeyboardButton(text=strings.msg_razmer5, callback_data=strings.msg_razmer5)
    button6 = types.InlineKeyboardButton(text=strings.msg_razmer6, callback_data=strings.msg_razmer6)

    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_rost_menu")

    # размещаем кнопки
    keyboard.add(button1, button2, button3, button4, button5, button6, button_back)

    bot.send_message(message.chat.id, strings.msg_razmer_info, reply_markup=keyboard)
    

##########################################################################################################
# кнопки и меню по выбору количества товара
def quantity(message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton(text=strings.quantity1, callback_data=strings.quantity1)
    button2 = types.InlineKeyboardButton(text=strings.quantity2, callback_data=strings.quantity2)
    button3 = types.InlineKeyboardButton(text=strings.quantity3, callback_data=strings.quantity3)
    button4 = types.InlineKeyboardButton(text=strings.quantity4, callback_data=strings.quantity4)
    button5 = types.InlineKeyboardButton(text=strings.quantity5, callback_data=strings.quantity5)

    button_back = types.InlineKeyboardButton(text=strings.msg_button_back, callback_data="back_to_razmer_menu")

    # размещаем кнопки
    keyboard.add(button1, button2, button3, button4, button5, button_back)

    bot.send_message(message.chat.id, strings.msg_quantity, reply_markup=keyboard)


##########################################################################################################
# выводим пользователю финальный заказ с учетом всех выбранных характеристик
def complete(message):
    bot.send_message(message.chat.id, strings.msg_complete)
    final_order_string = ("| %s\n| %s\n| %s\n| %s\n| %s") % (customer.comb, customer.VIP, customer.rost, customer.razmer, customer.quantity)
    bot.send_message(message.chat.id, final_order_string)

    is_order_right(message)


##########################################################################################################
# запрашиваем пользователя - заказ верный? либо вернуться назад в меню выбора комбинезона
def is_order_right(message):
    # размещаем клавиатуру с кнопками Верно и Назад
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text=strings.btn_is_right_order1, callback_data=strings.btn_is_right_order1)
    button2 = types.InlineKeyboardButton(text=strings.btn_is_right_order2, callback_data=strings.btn_is_right_order2)

    keyboard.add(button1, button2)

    bot.send_message(message.chat.id, strings.msg_is_right_order, reply_markup=keyboard)


###########################################################################################################
# всё в заказе теперь верно и можно запросить у пользователя контакт с номером телефона
def request_contact(message):

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(text=strings.btn_request_tel_number, request_contact=True)

    keyboard.add(button1)
    msg_dialog = bot.send_message(message.chat.id, strings.msg_request_tel_number, reply_markup=keyboard)
    bot.register_next_step_handler(msg_dialog, final_order)


###############################################################################################
# заказ полностью подтвержден и получено согласие пользователя, а также контакт телефон юзера
def final_order(message):
    user.phone_number = message.contact.phone_number
    print("Номер тел = %s" % user.phone_number)

    user_string = ("Имя пользователя: %s\nИмя: %s Фамилия: %s\nНомер телефона: %s" % (user.username, user.first_name, user.last_name, user.phone_number))

    final_order_string = ("\n| %s\n| %s\n| %s\n| %s\n| %s") % (customer.comb, customer.VIP, customer.rost, customer.razmer, customer.quantity)

    # телефон юзера у нас уже получен, так что пишем юзера в БД
    #    если юзер есть в БД, то метод saveUser не будет его лишний раз записывать в БД таблицу users
    saveUser(user.username, user.first_name, user.last_name, user.phone_number)

    # пишем детали заказа в БД заказов orders saveOrder(username, comb, VIP, rost, razmer, quantity, phone_number):
    saveOrder(user.username, customer.comb, customer.VIP, customer.rost, customer.razmer, customer.quantity, user.phone_number)

    # отправляем детали заказа менеджору на почту
    mail_order = user_string + final_order_string
    sendMail(mail_order, message)


###############################################################################################
# функция пересылки письма с заказом на почтовый ящик менеджора
def sendMail(message_to_send, message):
    smtp_host = settings.SMTPAgent # gmail smtp server SMTPAgent = "smtp.gmail.com" или yandex.ru - smtp.yandex.ru
    # почта для менеджора  info.walkmoda@gmail.com  pass: менеджернасвязи (en)
    login, password = settings.MailAgentBotLogin, settings.MailAgentBotPassword
    #recipients_emails = [login]
    recipient = settings.MailAgentLogin_2send

    msg = MIMEText(message_to_send, 'plain', 'utf-8')
    msg['Subject'] = Header('Zakaz Walkmoda bot', 'utf-8')
    msg['From'] = login
    #msg['To'] = ", ".join(recipients_emails)
    msg['To'] = recipient

    s = smtplib.SMTP(smtp_host, 587, timeout=10)
    s.set_debuglevel(1)
    try:
        s.starttls()
        s.login(login, password)
        s.sendmail(msg['From'], recipient, msg.as_string())
    finally:
        print("Send mail status to address %s = OK!" % recipient)
    s.quit()

    # Все ок ваш заказ отправлен на почту менеджору и он вам позвонит! и 2 секунды sleep чтобы прочитал юзер инфу
    bot.send_message(message.chat.id, strings.msg_success_zakaz)
    time.sleep(2)
    # и вернулись в главное меню
    start_dlg(message)


###############################################################################################
# самое основное тут - точка входа)
if __name__ == '__main__':
# создаем объекты customer и user - экземпляры классов Customer и User, который содержит поля заказа и обнуляем на старте
    customer = Customer("null", "null", "null", "null", "null")
    user = User("null", "null", "null", "null")

# делаем так, чтобы наш бот не падал, когда сервер api.telegram.org выкидывает нашего бота)
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            print(str(e)) # или просто print(e) если у вас логгера нет,
            # или import traceback; traceback.print_exc() для печати полной инфы
            time.sleep(15)


        # для прерывания процесса по нажатию на клавишу в терминале
        except KeyboardInterrupt as keyExc:
            exit(0)
