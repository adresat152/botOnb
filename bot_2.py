import telebot
import requests
import json

try:
    # python2
    from urlparse import urlparse
except ModuleNotFoundError:
    # python3
    from urllib.parse import urlparse

    #Функция проверки правильности URl
def url_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False
    
from telebot import types;
bot = telebot.TeleBot('6647975314:AAFjVYqLhFLyIfuNZlRji_n4X2UU381g-r0');

#Основные переменные
host = '';
client_id = '';
client_secret = '';
grant_type = 'client_credentials';
scope = 'read write';
restId = '';
orderId = '';
rep = ''; #Ответ response
admin = [883820247, 1108841817, 5403424801, 884863244, 757210002]
textCreds = '';
headers = '';

def pusin(host, client_id, client_secret, restId, orderId):
    global textCreds
    textCreds = "Я все записал!\nHost: "+host+"\nClinet ID: "+client_id+"\nClient Secret: "+client_secret+"\nRestID: "+restId+"\nЗаказ: "+orderId

helloWorld = 'Привет, {0.first_name}!\n\nЭтот бот доступен только узкому кругу лиц.'


#Функция получения токена
def getToken(message):
    url = host+'/security/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type,
        'scope': scope
    }
    if url_validator(host) == True:
        response = requests.post(url, data=data)
        if response.status_code == 400:
            print (response.status_code)
            bot.send_message(message.chat.id, text="❌Упс! Ошибка 400... Похоже неверные креды у тебя, дружок")
        elif response.status_code == 404:
            print (response.status_code)
            bot.send_message(message.chat.id, text="❌Тут уже 404 ошибка. Что-то с хостом. Стучимся не туда...")
        elif response.status_code == 401:
            print (response.status_code)
            bot.send_message(message.chat.id, text="❌Ошибка 401 авторизация. Хост ОК, смотри Client ID и Secret")
        else:
            global rep
            rep = response
            authToken = rep.json()['access_token']
            global headers
            headers = {'Authorization': 'Bearer '+authToken}
            return True
    else:
        bot.send_message(message.chat.id, text="Хост введен не верно...")

#Функция выгрузки чего-то в файл
def getFile(message):
    with open('place/file.json', 'w', encoding='utf-8') as outfile:  
        json.dump(rep.json(), outfile, ensure_ascii=False, sort_keys=True, indent=4)
    with open('place/file.txt', 'w', encoding='utf-8') as outfile:  
        json.dump(rep.json(), outfile, ensure_ascii=False)
    global file_json
    global file_txt
    file_json = open('place/file.json', 'rb')
    file_txt = open('place/file.txt', 'rb')

def getMenuCreds(message):
    pusin(host=host, client_id=client_id, client_secret=client_secret, restId=restId, orderId=orderId) #Сохраняем креды в переменные и заводит под одну переменную с текстом
    bot.send_message(message.chat.id, text=textCreds, reply_markup=types.ReplyKeyboardRemove()) #Отправляем переменную с текстом
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_place = telebot.types.InlineKeyboardButton(text="Рестораны", callback_data='load_place')
    button_menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='load_menu')
    button_order = telebot.types.InlineKeyboardButton(text="Получить заказ", callback_data='load_order')
    keyboard.add(button_place, button_menu, button_order)
    bot.send_message(message.chat.id, f'Что смотрим по кредам?', reply_markup=keyboard)

#Старт бота:
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menuButton = types.KeyboardButton("Меню бота")
        markup.add(menuButton)
        bot.send_message(message.chat.id, text=helloWorld.format(message.from_user), reply_markup=markup)
    else:
        print(message.from_user.id)
        bot.send_message(message.chat.id, text=helloWorld.format(message.from_user))
        bot.send_message(message.chat.id, 'Извините, у вас нет доступа', reply_markup=types.ReplyKeyboardRemove())

        
@bot.message_handler(content_types=['text'])
def menu(message):
    if message.from_user.id in admin:
        if(message.text == "Меню бота"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            credsButton = types.KeyboardButton("Ввести креды 📥")
            back = types.KeyboardButton("Вернуться в главное меню")
            markup.add(credsButton, back)
            bot.send_message(message.chat.id, text="Выбери что проверяем", reply_markup=markup)
            bot.register_next_step_handler(message, creds);
    else:
        bot.send_message(message.chat.id, 'Извините, у вас нет доступа', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def creds(message):
    if message.from_user.id in admin:
        if(message.text == "Ввести креды 📥"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            skip = types.KeyboardButton("Пропустить")
            markup.add(skip)
            bot.send_message(message.chat.id, text="Введи Host", reply_markup=markup)
            bot.register_next_step_handler(message, get_cliet_id);
    else:
        bot.send_message(message.chat.id, 'Извините, у вас нет доступа', reply_markup=types.ReplyKeyboardRemove())

#Записываем host и получаем Client ID
def get_cliet_id(message):
    global host
    host = message.text
    checkHost = host[-1]
    if checkHost == '/':
        host = host[:-1]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Пропустить")
    markup.add(button1)
    bot.send_message(message.chat.id, text="Введи Client ID", reply_markup=markup)
    bot.register_next_step_handler(message, get_cliet_secret);
#Записываем client_id и получаем Client Secret
def get_cliet_secret(message):
    global client_id
    client_id = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Пропустить")
    markup.add(button1)
    bot.send_message(message.chat.id, text="Введи Client Secret", reply_markup=markup)
    bot.register_next_step_handler(message, saveCreds);
# Записываем Secret и проверяем креды
def saveCreds(message):
    global client_secret
    client_secret = message.text
    if host == '':
        bot.send_message(message.chat.id, text="Сначала введите креды")
    else:
        #Рестораны
        @bot.callback_query_handler(func=lambda call: call.data == 'load_place')
        def save_btn(call):
            message = call.message
            chat_id = message.chat.id
            message_id = message.message_id  
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Получаю токен...')
            getToken(message)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Токен получил, проверяю хост...')
            global rep
            rep = requests.get(host+'/restaurants', headers=headers)
            if rep.status_code == 404:
                bot.send_message(message.chat.id, text="Партнер не поддерживает передачу списка ресторанов. \n\nЭто может быть Goulash.tech. Запрашиваем самостоятельно ID терминала.")
            else:
                @bot.callback_query_handler(func=lambda call: call.data == 'load_in_chat')
                def save_btn(call):
                    message = call.message
                    chat_id = message.chat.id
                    message_id = message.message_id  
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Все ок, держи список ✅')
                    for txt in responseRest['places']:
                        idRest = txt['id']
                        titleRest = txt['title']
                        adressRest = txt['address']
                        bot.send_message(message.chat.id, idRest+'\n'+titleRest+'\n'+adressRest)
                    getMenuCreds(message)

                @bot.callback_query_handler(func=lambda call: call.data == 'load_file')
                def save_btn(call):
                    message = call.message
                    chat_id = message.chat.id
                    message_id = message.message_id  
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Скачиваю файл...')
                    getFile(message)
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Отправляю файл...')
                    bot.send_document(chat_id, file_json);
                    bot.send_document(chat_id, file_txt);
                    getMenuCreds(message)
                
                global responseRest
                responseRest = rep.json()
                lenRest = len(responseRest['places'])
                if lenRest >= 15:
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button_in_chat = telebot.types.InlineKeyboardButton(text="Выгрузить", callback_data='load_in_chat')
                    button_file = telebot.types.InlineKeyboardButton(text="Скачать файл", callback_data='load_file')
                    keyboard.add(button_in_chat, button_file)
                    bot.send_message(message.chat.id, f'Список рестов привышает 15 на кредах. Выгрузить все?', reply_markup=keyboard)
                else:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Все ок, держи список ✅')
                    for txt in responseRest['places']:
                        idRest = txt['id']
                        titleRest = txt['title']
                        adressRest = txt['address']
                        bot.send_message(message.chat.id, idRest+'\n'+titleRest+'\n'+adressRest)
                    getMenuCreds(message)
        
        #Меню
        @bot.callback_query_handler(func=lambda call: call.data == 'load_menu')
        def save_btn(call):
            def Get_id_rest(message):
                bot.send_message(message.chat.id, text="Введи ID ресторана")
                bot.register_next_step_handler(message, download_rest);
            def download_rest(message):
                global restId
                restId = message.text
                global rep
                rep = requests.get(host+'/menu/'+restId+"/composition", headers=headers)
                responseMenu = rep.json()
                if len(responseMenu) == 1:
                    bot.send_message(message.chat.id, text="Что-то пошло не так... Возможно неверный ID терминала\nОшибка:")
                    bot.send_message(message.chat.id, text=str(responseMenu), parse_mode='html')
                else:
                    @bot.callback_query_handler(func=lambda call: call.data == 'load_in_chat_menu')
                    def save_btn(call):
                        message = call.message
                        chat_id = message.chat.id
                        message_id = message.message_id  
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Все ок, держи список ✅')
                        for txt in responseMenu['items']:
                            NamePos = txt['name']
                            DesPos = txt['description']
                            PricePos = txt['price']
                            MeaUnitPos = txt['measureUnit']
                            if len(txt['images']) > 0:
                                ImgPos = txt['images'][0]['url']
                            else:
                                ImgPos = txt['images']
                            bot.send_message(message.chat.id, NamePos+'\n'+DesPos+'\n'+str(PricePos)+'\n'+MeaUnitPos+'\n'+str(ImgPos))
                        getMenuCreds(message);
                    @bot.callback_query_handler(func=lambda call: call.data == 'load_file_menu')
                    def save_btn(call):
                        message = call.message
                        chat_id = message.chat.id
                        message_id = message.message_id  
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Скачиваю файл...')
                        getFile(message)
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Отправляю файл...')
                        bot.send_document(chat_id, file_json);
                        bot.send_document(chat_id, file_txt);
                        getMenuCreds(message);
                    
                    if len (responseMenu['items']) > 10:
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        button_in_chat = telebot.types.InlineKeyboardButton(text="Выгрузить", callback_data='load_in_chat_menu')
                        button_file = telebot.types.InlineKeyboardButton(text="Скачать файл", callback_data='load_file_menu')
                        keyboard.add(button_in_chat, button_file)
                        bot.send_message(message.chat.id, f'Список блюд привышает 10. Выгрузить все?', reply_markup=keyboard)
                    else:
                        for txt in responseMenu['items']:
                            NamePos = txt['name']
                            DesPos = txt['description']
                            PricePos = txt['price']
                            MeaUnitPos = txt['measureUnit']
                            if len(txt['images']) > 0:
                                ImgPos = txt['images'][0]['url']
                            else:
                                ImgPos = txt['images']
                            bot.send_message(message.chat.id, NamePos+'\n'+DesPos+'\n'+str(PricePos)+'\n'+MeaUnitPos+'\n'+str(ImgPos))
                        getMenuCreds(message)

            message = call.message
            chat_id = message.chat.id
            message_id = message.message_id  
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Здесь будет выгрузка меню')
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Получаю токен...')
            getToken(message)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Токен получил, необходимо ID ресторана')
            bot.register_next_step_handler(message, Get_id_rest);
        
        #Заказы
        @bot.callback_query_handler(func=lambda call: call.data == 'load_order')
        def save_btn(call):
            def Get_order(message):
                bot.register_next_step_handler(message, download_order);
            def download_order(message):
                @bot.callback_query_handler(func=lambda call: call.data == 'yes_status')
                def save_btn(call):
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Получаю токен...')
                    getToken(message)
                    rep = requests.get(host+'/order/'+orderId+'/status', headers=headers)
                    responseOrder = rep.json()
                    bot.send_message(message.chat.id, text=str(responseOrder))
                    getMenuCreds(message)
                @bot.callback_query_handler(func=lambda call: call.data == 'no_status')
                def save_btn(call):
                    getMenuCreds(message)
                global orderId
                orderId = message.text
                global rep
                rep = requests.get(host+'/order/'+orderId, headers=headers)
                responseOrder = rep.json()
                bot.send_message(message.chat.id, text=str(responseOrder))
                keyboard = telebot.types.InlineKeyboardMarkup()
                button_yes_status = telebot.types.InlineKeyboardButton(text="Да", callback_data='yes_status')
                button_no_status = telebot.types.InlineKeyboardButton(text="Нет", callback_data='no_status')
                keyboard.add(button_yes_status, button_no_status)
                bot.send_message(message.chat.id, f'Выгрузить его статус у партнера?', reply_markup=keyboard)
            message = call.message
            chat_id = message.chat.id
            message_id = message.message_id  
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Получаю токен...')
            getToken(message)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Токен получил, необходимо ввести номер заказа')
            bot.register_next_step_handler(message, Get_order);
        
        if getToken(message) == True:
            pusin(host=host, client_id=client_id, client_secret=client_secret, restId=restId, orderId=orderId) #Сохраняем креды в переменные и заводит под одну переменную с текстом
            bot.send_message(message.chat.id, text=textCreds, reply_markup=types.ReplyKeyboardRemove()) #Отправляем переменную с текстом
            keyboard = telebot.types.InlineKeyboardMarkup()
            button_place = telebot.types.InlineKeyboardButton(text="Рестораны", callback_data='load_place')
            button_menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='load_menu')
            button_order = telebot.types.InlineKeyboardButton(text="Получить заказ", callback_data='load_order')
            keyboard.add(button_place, button_menu, button_order)
            bot.send_message(message.chat.id, f'Что смотрим по кредам?', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, f'Что-то пошло не так... Начнем с начала /start')


bot.polling()