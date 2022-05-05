import telebot
from telebot import types
import json
import time
import random
import string
import random
import requests
import sqlite3
import math

#объект нашего бота с токеном
bot = telebot.TeleBot('227057823:AAGHEIVDbb-e3DVOTOE_09OO_X_YT7mamjQ')

#через этот словарь в последующем будем добавлять новые отели
logi = {}

#здесь задаем наш ID
ADMIN = 230952777

#расстояние которое будем высчитывать изначально и потом с ним сравнивать
destination0 = 0

#первое ID отеля
ID = 0

#широта первая
longitude = 0

#долгота первая
latitude = 0

#имя выведенного отеля, при добавлении в избранное, чтоб не делать лишний запрос
name = 'name'

#словарь в который будем добавлять отель
add_new = {'name' : 'here is name',
            'description' : 'here is description',
            'city' : 'here is city',
            'adress' : 'here is adress',
            'phone' : 'here is phone',
            'price' : 'here is price',
            'note' : 'here is note',
            'photo_link' : 'here is photo'}

#генератор id для отелей, просто вызываем его и получаем 10 значное епонятно что, заменяем 10 на другое число и получаем другого размера
def id_generator(size = 10, chars = string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

#чтоб постоянно не создавать клавиатуру или кнопку с одинаковым содержанием будем передавать
#этой функции туда куда нам надо вернуться в callback и тип: клавиатура(markup) или кнопка(button)
def back_markup(callback, type):
	back_markup = types.InlineKeyboardMarkup()
	back_button = types.InlineKeyboardButton(text = '« Back', callback_data = callback)
	back_markup.add(back_button)
	if type == 'markup':
		return back_markup
	elif type == 'button':
		return back_button

#эта функция выдает понравившиеся отели, первый раз она вызывается /myplaces а второй раз
#когда назад возвращаемся
def like_hotels(user_id):
    conn = sqlite3.connect('./rent.sqlite3')
    curr = conn.cursor()
    reply_markup = types.InlineKeyboardMarkup()
    with conn:
        rows = curr.execute('SELECT * FROM favourites WHERE user_id = ?', (user_id,)).fetchall()
        for row in rows:
            reply_markup.add(types.InlineKeyboardButton(text = row[2], callback_data = 'hotel_more_'+row[0]))
    conn.close()
    return reply_markup

#админская клавиатура
admin_markup = types.InlineKeyboardMarkup()
admin_markup.add(types.InlineKeyboardButton(text = 'Добавить новый', callback_data = 'add_new'))

#отсылаем локацию при добавлении отеля
send_location = types.ReplyKeyboardMarkup(True, True)
button_yes = types.KeyboardButton(text = 'Да', request_location = True)
send_location.add(button_yes)

#отсылаем локацию при поиске отеля
request_location = types.ReplyKeyboardMarkup(True, True)
button = types.KeyboardButton(text = 'Find me', request_location = True)
request_location.add(button)

#хэндлер на обработку, когда отсылается локация
#все локации будут обрабатываться здесь
@bot.message_handler(content_types = ['location'])
def location(message):
    #чтоб могли изменять переменные объявленные вне функции делаем их глобальными, так сказать
    global destination0
    global ID
    global longitude
    global latitude
    global name
    conn = sqlite3.connect('./rent.sqlite3')
    curr = conn.cursor()
    #определяем админ отсылает локацию при добавлении или нет
    if logi[message.chat.id] == 'adminsend_yes':
        reply_markup = back_markup('admin', 'markup')
        answer = 'Добавление закончено'
        curr.execute('INSERT INTO main(id, name, description, longitude, latitude, city, adress, phone, price, note, photo_link)\
        VALUES(?,?,?,?,?,?,?,?,?,?,?)', (id_generator(), add_new['name'], add_new['description'], message.location.longitude,
        message.location.latitude, add_new['city'], add_new['adress'], add_new['phone'], add_new['price'], add_new['note'], add_new['photo_link']))
        conn.commit()
        #изменяем значение, чтоб при повторной отправке снова не добавилось одно и то же место
        logi.update({message.chat.id : 'success'})
    else:
        longitude = message.location.longitude
        latitude = message.location.latitude
        #радиус земли
        R = 6371
        with conn:
            rows = curr.execute('SELECT * FROM main').fetchall()
            for row in rows:
                #все что дальше - формула гаверсинуса
                #взял из инета, особо не разбирался
                #но, я так понимаю есть SQL запрос, который достанет ближайшую локацию
                sin1 = math.sin(latitude - (row[4]) / 2)
                sin2 = math.sin(longitude - (row[3]) / 2)
                destination1 = 2 * R * math.asin(math.sqrt(sin1 ** 2 + sin2 ** 2 * math.cos(latitude) * math.cos(row[4])))
                if destination0 == 0:
                    name = row[1]
                    destination0 = destination1
                    ID = row[0]
                elif destination1 < destination0:
                    name = row[1]
                    destination0 = destination1
                    ID = row[0]
            #как только закончились все сравнения достаем отель с наименьшим расстоянием
            data = curr.execute('SELECT * FROM main WHERE id = ?', (ID,)).fetchall()[0]
        #оформляем вывод parse_mode = HTML
        answer = '<a href ="'+data[10]+'">&#8203;</a>'+\
        '<b>'+data[1]+'</b>'+'\n'+\
        data[2]+'\n'+\
        '<b>Adress: </b>'+data[6]+'\n'+\
        '<b>Phone: </b>'+str(data[7])+'\n'+\
        '<b>Degre price: </b>'+data[8]+'\n'+\
        '<pre>'+data[9]+'</pre>'
        reply_markup = types.InlineKeyboardMarkup()
        #Поиск другого
        reply_markup.add(types.InlineKeyboardButton(text = 'Find Another »', callback_data = 'find_another'))
        #добавление в понравившееся
        reply_markup.add(types.InlineKeyboardButton(text = 'Add to Favourites', callback_data = 'add_to_favourites'))
    conn.close()
    bot.send_message(
    chat_id = message.chat.id,
    text = answer,
    reply_markup = reply_markup,
    parse_mode = 'HTML')

@bot.message_handler(commands = ['start'])
def start(message):
    #реагируем на /start
    bot.send_message(
    chat_id = message.chat.id,
    text = 'Hello, World'+'\n'+\
    '/findplace - If you want found nearest hotel'+'\n'+\
    '/myplaces - Places you liked',
    parse_mode = 'HTML')
    conn = sqlite3.connect('./rent.sqlite3')
    curr = conn.cursor()
    #если юзера нет в нашей бд - добавляем его
    curr.execute('SELECT * FROM users WHERE id = ?', (message.chat.id,))
    if curr.fetchall() == []:
        curr.execute('INSERT INTO users(id, username) VALUES(?,?)', (message.chat.id, message.chat.username,))
        conn.commit()
    conn.close()

@bot.message_handler(commands = ['findplace'])
def find(message):
    #реагируем на /findplace
    bot.send_message(
    chat_id = message.chat.id,
    text = 'I need you location, let me know it',
    reply_markup = request_location,
    parse_mode = 'Markdown')

@bot.message_handler(commands = ['myplaces'])
def places(message):
    bot.send_message(
    chat_id = message.chat.id,
    text = 'Hotels you like',
    #вызвали функцию like_hotels и передали в нее id пользователя
    reply_markup = like_hotels(message.chat.id),
    parse_mode = 'Markdown')

@bot.message_handler(content_types = ['text'])
def text(message):
    if message.text == 'admin' and message.chat.id == ADMIN:
        #админка
        bot.send_message(
        chat_id = message.chat.id,
        text = 'Admin',
        reply_markup = admin_markup,
        parse_mode = 'Markdown')

    elif logi[message.chat.id][:4] == 'add_':
        #здесь мы обрабатываем сообщения, когда добавляем отель, чтоб сократить кодик, меняем только значение, которое будем ждать от пользователя и ответ
        #так как в логах у нас add_name или add_description, по add_ мы определяем что юзер че-то добавляет
        #но ключ у нас в add_new без add_, поэтому делаем так logi[message.chat.id][4:] - и у нас будет с 4-ой позиции все
        add_new.update({logi[message.chat.id][4:] : message.text})
        reply_markup = back_markup('admin', 'markup')
        if logi[message.chat.id] == 'add_name':
            #вот тут мы ждем от пользователя имя, следущее должно быть описание
            answer = 'Пришли описание'
            adding = 'add_description'
        elif logi[message.chat.id] == 'add_description':
            answer = 'Пришли город'
            adding = 'add_city'
        elif logi[message.chat.id] == 'add_city':
            answer = 'Пришли адрес'
            adding = 'add_adress'
        elif logi[message.chat.id] == 'add_adress':
            answer = 'Пришли телефон заведения'
            adding = 'add_phone'
        elif logi[message.chat.id] == 'add_phone':
            answer = 'Введите среднюю цену'
            adding = 'add_price'
        elif logi[message.chat.id] == 'add_price':
            answer = 'Пришлите примечание'
            adding = 'add_note'
        elif logi[message.chat.id] == 'add_note':
            answer = 'Пришлите ссылку на фото'
            adding = 'add_photo_link'
        elif logi[message.chat.id] == 'add_photo_link':
            answer = 'Местоположение где вы находитесь является местом где находится заведение?'
            reply_markup = send_location
            adding = 'adminsend_yes'
        bot.send_message(
        chat_id = message.chat.id,
        text = answer,
        reply_markup = reply_markup,
        parse_mode = 'Markdown')
        logi.update({message.chat.id : adding})

@bot.callback_query_handler(func = lambda call : True)
def call(call):
    global destination0
    global ID
    global longitude
    global latitude
    global name
    if call.data == 'add_new':
        #начинаем добавлять новый отель
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Пришлите имя',
        reply_markup = back_markup('admin', 'markup'),
        parse_mode = 'Markdown')
        #юзер пришлет сообщение, мы должны знать на что он ответил
        #поэтому как ключ добавляем его ID а значение будет то, что мы ждем
        #в данном случае имя
        logi.update({call.message.chat.id : 'add_name'})

    elif call.data == 'admin':
        #снова админка, если мы нажмем на кнопку назад
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Admin',
        reply_markup = admin_markup,
        parse_mode = 'Markdown')

    elif call.data[:11] == 'hotel_more_':
        #когда выведем список понравившихся отелей надо сделать возможность просматривать инфу о них
        #поэтому когда мы создавали эту клавиатуру сделали значение callback_data = 'hotel_more_'+IDотеля
        conn = sqlite3.connect('./rent.sqlite3')
        curr = conn.cursor()
        #поэтому здесь и достаем отель по call.data[11:], 'hotel_more_' отбрасывается и у нас только ID отеля
        data = curr.execute('SELECT * FROM main WHERE id = ?', (call.data[11:],)).fetchall()[0]
        conn.close()
        answer = '<b>'+data[1]+'</b>'+'\n'+\
        data[2]+'\n'+\
        '<b>Adress: </b>'+data[6]+'\n'+\
        '<b>Phone: </b>'+str(data[7])+'\n'+\
        '<b>Degre price: </b>'+data[8]+'\n'+\
        '<pre>'+data[9]+'</pre>'+'\n'+\
        #здесь скрывается картинка, бот не может отредактировать текст и фотку в оодном сообщении
        '<a href ="'+data[10]+'">&#8203;</a>'
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = answer,
        reply_markup = back_markup('favourites_hotel', 'markup'),
        parse_mode = 'HTML')

    elif call.data == 'favourites_hotel':
        #тут если мы вышли из отеля который нам понравился назад, тож та функция вызывается
        #зачем дважды одно и то же писать?
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = 'Hotels you like',
        reply_markup = like_hotels(call.message.chat.id),
        parse_mode = 'Markdown')

    elif call.data == 'add_to_favourites':
        #добавляем в понравившееся, просто выскочет и добавится в бд
        bot.answer_callback_query(call.id, 'Done!')
        conn = sqlite3.connect('./rent.sqlite3')
        curr = conn.cursor()
        curr.exeucte('SELECT * FROM favourites WHERE id = ? AND user_id = ?', (ID, call.message.chat.id,))
        #смотрим есть ли такая запись а только потом добавляем
        if curr.fetchall() == []:
            curr.execute('INSERT INTO favourites(id, user_id, name) VALUES (?,?,?)', (ID, call.message.chat.id, name,))
            conn.commit()
        conn.close()

    elif call.data == 'find_another':
        R = 6371
        old_destination = destination0
        old_id = ID
        conn = sqlite3.connect('./rent.sqlite3')
        curr = conn.cursor()
        with conn:
            rows = curr.execute('SELECT * FROM main').fetchall()
            for row in rows:
                sin1 = math.sin((latitude - row[4]) / 2)
                sin2 = math.sin((longitude - row[3]) / 2)
                destination1 = 2 * R * math.asin(math.sqrt(sin1 ** 2 + sin2 ** 2 * math.cos(latitude) * math.cos(row[4])))
                #тут только исключаем прошлый ID, а логика все та же
                if destination0 == 0 and old_id != row[0]:
                    name = row[1]
                    destination0 = destination1
                    ID = row[0]
                elif (destination1 < destination0 and old_destination < destination1) and old_id != row[0]:
                    name = row[1]
                    destination0 = destination1
                    ID = row[0]
            data = curr.execute('SELECT * FROM main WHERE id = ?', (ID,)).fetchall()[0]
        answer = '<a href ="'+data[10]+'">&#8203;</a>'+\
        '<b>'+data[1]+'</b>'+'\n'+\
        data[2]+'\n'+\
        '<b>Adress: </b>'+data[6]+'\n'+\
        '<b>Phone: </b>'+str(data[7])+'\n'+\
        '<b>Degre price: </b>'+data[8]+'\n'+\
        '<pre>'+data[9]+'</pre>'
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(types.InlineKeyboardButton(text = 'Find Another »', callback_data = 'find_another'))
        reply_markup.add(types.InlineKeyboardButton(text = 'Add to Favourites', callback_data = 'add_to_favourites'))
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = answer,
        reply_markup = reply_markup,
        parse_mode = 'HTML')

#опрашиваем сервера на наличие новых сообщений
#но лучше использовать webhooks, так как этот способ иногда выдает ошибку и бот ложится
bot.polling()
