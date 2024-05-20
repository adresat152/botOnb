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


#Подключение к боту по токену
from telebot import types;
bot = telebot.TeleBot('6647975314:AAFjVYqLhFLyIfuNZlRji_n4X2UU381g-r0');

admin = [883820247, 1108841817, 5403424801, 884863244, 757210002]


#Основные переменный
responseMenu = '';
responseRest = '';
host = '';
client_id = '';
client_secret = '';
grant_type = 'client_credentials';
scope = 'read write';
restId = '';
orderId = '';
response = '';

urlRest = host+'/restaurants'
urlMenu = host+'/menu/'+restId+'/composition'

def getToken(message):
    global response
    url = host+'/security/oauth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': grant_type,
        'scope': scope
    }
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
        response = requests.post(url, data=data)
        bot.send_message(message.chat.id, text="Креды проверил, все ок")


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("👋 Поздороваться")
        btn2 = types.KeyboardButton("Меню бота")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, text="Привет, {0.first_name}!\n\nЭтот бот доступен только узкому кругу лиц.".format(message.from_user), reply_markup=markup)
    else:
        print(message.from_user.id)
        bot.send_message(message.chat.id, text="Привет, {0.first_name}!\n\nЭтот бот доступен только узкому кругу лиц.".format(message.from_user))
        bot.send_message(message.chat.id, 'Извините, у вас нет доступа', reply_markup=types.ReplyKeyboardRemove())
@bot.message_handler(content_types=['text'])
def func(message):
    if message.from_user.id in admin:
        if(message.text == "👋 Поздороваться"):
            bot.send_message(message.chat.id, text="Привеет.. Я создан ненормальным энтузиастом!")

        #Меню бота
        elif(message.text == "Меню бота"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Ввести креды 📥")
            btn2 = types.KeyboardButton("Получить Place'ы 🏠")
            btn3 = types.KeyboardButton("Выгрузить меню 📋")
            back = types.KeyboardButton("Вернуться в главное меню")
            markup.add(btn1, btn2, btn3, back)
            bot.send_message(message.chat.id, text="Выбери что проверяем", reply_markup=markup)
        #Ввести креды
        elif(message.text == "Ввести креды 📥"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Пропустить")
            markup.add(button1)
            bot.send_message(message.chat.id, text="Введи Host\n\nСБИС: api.sbis.ru/web-hook/req/yandex_food/new_host/[...]\nIikoWeb: [...].iikoweb.ru/api/integrations/yandex-food\nИ другие...", reply_markup=markup)
            bot.register_next_step_handler(message, get_cliet_id);
            
        #Выгрузка Ресторанов

        elif message.text == "Получить Place'ы 🏠":
            if url_validator(host) == True:
                #Авторизация и получение токена + проверка на статусы response
                if host == '':
                    bot.send_message(message.chat.id, text="Сначала введите креды")
                else:
                    url = host+'/security/oauth/token'
                    data = {
                        'client_id': client_id,
                        'client_secret': client_secret,
                        'grant_type': grant_type,
                        'scope': scope
                    }
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
                        #Выгружаем список рестов по токену полученному выше
                        AuthResponse = response.json()
                        accessToken = AuthResponse['access_token']

                        headers = {'Authorization': 'Bearer '+accessToken}
                        response = requests.get(host+'/restaurants', headers=headers)
                        if response.status_code == 404:
                            bot.send_message(message.chat.id, text="Партнер не поддерживает передачу списка ресторанов. \n\nЭто может быть Goulash.tech. Запрашиваем самостоятельно ID терминала.")
                        else: 
                            global responseRest
                            responseRest = response.json()
                            lenRest = len(responseRest['places'])
                            if lenRest > 15:
                                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                                button1 = types.KeyboardButton("Да")
                                button2 = types.KeyboardButton("Скачать файл")
                                markup.add(button1,button2)
                                bot.send_message(message.chat.id, text="Кол-во ресторанов на кредах превышает 15 штук. Выгрузить все? Их кол-во: "+str(lenRest), reply_markup=markup)
                                bot.register_next_step_handler(message, download_places);
                            else:
                                for txt in responseRest['places']:
                                        idRest = txt['id']
                                        titleRest = txt['title']
                                        adressRest = txt['address']
                                        bot.send_message(message.chat.id, idRest+'\n'+titleRest+'\n'+adressRest)
            else:
                bot.send_message(message.chat.id, text="Хост введен не верно")


        #Вернуться в главное меню

        elif (message.text == "Вернуться в главное меню"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("👋 Поздороваться")
            button2 = types.KeyboardButton("Меню бота")
            markup.add(button1, button2)
            bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)

        #Выгрузить меню

        elif (message.text == "Выгрузить меню 📋"):
            bot.send_message(message.chat.id, text="Введите, пожалуйста ID терминала или выберите по кнопке (Пока нереализовано)")
            bot.register_next_step_handler(message, get_menu_by_RestID);
        #Неизвестная команда
        elif message.text == "Получить заказ":
            getToken(message)
        else:
            bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован.. Давай попробуем сначала /start")
    else:
        bot.send_message(message.chat.id, 'Извините, у вас нет доступа', reply_markup=types.ReplyKeyboardRemove())

#Шаги записи кредов

def get_cliet_id(message): #Записываем host и получаем Client ID
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

def get_cliet_secret(message): #Записываем client_id и получаем Client Secret
    global client_id
    client_id = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Пропустить")
    markup.add(button1)
    bot.send_message(message.chat.id, text="Введи Client Secret", reply_markup=markup)
    bot.register_next_step_handler(message, saveCreds);

def saveCreds(message): # Записываем Secret и проверяем креды
    global client_secret
    client_secret = message.text
    if host == '':
        bot.send_message(message.chat.id, text="Сначала введите креды")
    else:
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
                bot.send_message(message.chat.id, text="✅Статус 200. Креды ок✅")
        else: 
            bot.send_message(message.chat.id, text="Хост введен не верно")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Ввести креды 📥")
        btn2 = types.KeyboardButton("Получить Place'ы 🏠")
        btn3 = types.KeyboardButton("Выгрузить меню 📋")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text="Я все записал!\nHost: "+host+"\nClinet ID: "+client_id+"\nClient Secret: "+client_secret+"\nRestID: "+restId+"\nЗаказ: "+orderId+"\n\nМожно выгрузить меню по кнопке", reply_markup=markup)

#Шаг выгрузки плейсов
def download_places(message):
    if message.text == "Да":
        for txt in responseRest['places']:
            idRest = txt['id']
            titleRest = txt['title']
            adressRest = txt['address']
            bot.send_message(message.chat.id, idRest+'\n'+titleRest+'\n'+adressRest)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Ввести креды 📥")
        btn2 = types.KeyboardButton("Получить Place'ы 🏠")
        btn3 = types.KeyboardButton("Выгрузить меню 📋")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text="Выбери что проверяем", reply_markup=markup)
    else:
        if host == '':
            bot.send_message(message.chat.id, text="Сначала введите креды")
        else:
            url = host+'/security/oauth/token'
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': grant_type,
                'scope': scope
            }
            response = requests.post(url, data=data)
            AuthResponse = response.json()
            accessToken = AuthResponse['access_token']
            headers = {'Authorization': 'Bearer '+accessToken}
            response = requests.get(host+'/restaurants', headers=headers)
            with open('place/place.json', 'w', encoding='utf-8') as outfile:  
                json.dump(response.json(), outfile, ensure_ascii=False, sort_keys=True, indent=4)
            with open('place/place.txt', 'w') as outfile:  
                json.dump(response.json(), outfile, ensure_ascii=False, )
            place_json = open('place/place.json', 'rb')
            place_txt = open('place/place.txt', 'rb')
            bot.send_document(message.from_user.id, place_txt);
            bot.send_document(message.from_user.id, place_json);
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Ввести креды 📥")
        btn2 = types.KeyboardButton("Получить Place'ы 🏠")
        btn3 = types.KeyboardButton("Выгрузить меню 📋")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text="Я все записал!\nHost: "+host+"\nClinet ID: "+client_id+"\nClient Secret: "+client_secret+"\nRestID: "+restId+"\nЗаказ: "+orderId+"\n\nМожно выгрузить меню по кнопке", reply_markup=markup)


def get_menu_by_RestID(message):
    global restId
    restId = message.text
    #Авторизация и получение токена
    if host == '':
        bot.send_message(message.chat.id, text="Сначала введите креды")
    else:
        if url_validator(host) == True:
            url = host+'/security/oauth/token'
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': grant_type,
                'scope': scope
            }
            response = requests.post(url, data=data)
            AuthResponse = response.json()
            accessToken = AuthResponse['access_token']
            headers = {'Authorization': 'Bearer '+accessToken}
            urlMenu = host+'/menu/'+restId+'/composition'
            response = requests.get(urlMenu, headers=headers)
            global responseMenu
            responseMenu = response.json()
            if len(responseMenu) == 1:
                bot.send_message(message.chat.id, text="Что-то пошло не так... Возможно неверный ID терминала\nОшибка:")
                bot.send_message(message.chat.id, text=str(responseMenu), parse_mode='html')
            else:
                lenMenu = len(responseMenu['items'])
                if lenMenu > 10:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button1 = types.KeyboardButton("Да")
                    button2 = types.KeyboardButton("Скачать файл")
                    markup.add(button1,button2)
                    bot.send_message(message.chat.id, text="Кол-во блюд на ресторана превышает 10 штук. Выгрузить все? Общнн кол-во: "+str(lenMenu), reply_markup=markup)
                    bot.register_next_step_handler(message, download_menu);
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
        else:
            bot.send_message(message.chat.id, text="Хост введен не верно")


def download_menu(message):
    if message.text == "Да":
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
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Ввести креды 📥")
            btn2 = types.KeyboardButton("Получить Place'ы 🏠")
            btn3 = types.KeyboardButton("Выгрузить меню 📋")
            back = types.KeyboardButton("Вернуться в главное меню")
            markup.add(btn1, btn2, btn3, back)
    else:
        url = host+'/security/oauth/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': grant_type,
            'scope': scope
        }
        response = requests.post(url, data=data)
        AuthResponse = response.json()
        accessToken = AuthResponse['access_token']
        headers = {'Authorization': 'Bearer '+accessToken}
        response = requests.get(host+'/menu/'+restId+'/composition', headers=headers)
        with open('menu/menu.json', 'w', encoding='utf-8') as outfile:  
            json.dump(response.json(), outfile, ensure_ascii=False, sort_keys=True, indent=4)
        with open('menu/menu.txt', 'w') as outfile:  
            json.dump(response.json(), outfile, ensure_ascii=False, )
        menu_json = open('menu/menu.json', 'rb')
        menu_txt = open('menu/menu.txt', 'rb')
        bot.send_document(message.from_user.id, menu_txt);
        bot.send_document(message.from_user.id, menu_json);
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Ввести креды 📥")
    btn2 = types.KeyboardButton("Получить Place'ы 🏠")
    btn3 = types.KeyboardButton("Выгрузить меню 📋")
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(btn1, btn2, btn3, back)
    bot.send_message(message.chat.id, text="Я все записал!\nHost: "+host+"\nClinet ID: "+client_id+"\nClient Secret: "+client_secret+"\nRestID: "+restId+"\nЗаказ: "+orderId+"\n\nМожно выгрузить меню по кнопке", reply_markup=markup)
    


# def telegram_polling():
#     try:
#         bot.polling()
#     except:
#         bot
#         traceback_error_string=traceback.format_exc()
#         with open("Error.Log", "a") as myfile:
#             myfile.write("\r\n\r\n" + time.strftime("%c")+"\r\n<<ERROR polling>>\r\n"+ traceback_error_string + "\r\n<<ERROR polling>>")
#         bot.stop_polling()
#         time.sleep(10)
#         telegram_polling()

# telegram_polling()
bot.polling()