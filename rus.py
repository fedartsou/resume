import telebot
import cherrypy
import sqlite3
import random
import requests
import json
import string
import time
import tests
from datetime import datetime
from telebot import types
from taxifunc import id_generator, bd, refresh_stat, time, API_KEY, bd_insert, destination_check, find_location
#↑↓
#☄
bot = telebot.TeleBot('406623693:AAGtViBaIYoUyPZAZ1_qkb2jrR5Wf5CHULM')

result = {}

change_car = {'car':'here is car',
			'color': 'here is color',
			'gosmun' : 'here is gosnum',
			'photo' : [],
			'inphoto' : []}

driver_data = {'phone' : 'here is phone',
				'first_name' : 'here is first name',
				'last_name' : 'here is last name',
				'third_name' : 'here is third name',
				'pasport' : 'here is pasport photo',
				'drive_id' : 'here is drive id',
				'selfie' : 'here is selfie',
				'license' : 'here is license',
				'gosnum' : 'here is gosnum',
				'car' : 'here is car',
				'color' : 'here is color',
				'photo' : [],
				'inphoto' : []}

def photos_in(chat_id, spisok, type):
	for i in spisok:
		bd('INSERT INTO car_photo(user, photo, type) VALUES("'+str(chat_id)+'","'+i+'","'+type+'")')

def markups(type, chat_id):
	reply_markup = types.InlineKeyboardMarkup()
	if type == 'drive':
		data = bd('SELECT * FROM drivers INNER JOIN cars using(user) WHERE user = "'+str(chat_id)+'"')[0]
		answer = data[4] +' '+ data[3]+' '+data[5]
		reply_markup.add(types.InlineKeyboardButton(text = 'Найти заказ »', callback_data = 'find_trip'),
						types.InlineKeyboardButton(text = 'Отложенные', callback_data = 'next_trips'))
		reply_markup.add(types.InlineKeyboardButton(text = 'История', callback_data = 'history'))
		reply_markup.add(types.InlineKeyboardButton(text = 'Помощь', callback_data = 'help'))
		reply_markup.add(types.InlineKeyboardButton(text = 'Информация', callback_data = 'info'))
		reply_markup.add(types.InlineKeyboardButton(text = 'Новости и общение', callback_data = 'news'))
		reply_markup.add(types.InlineKeyboardButton(text = data[8], callback_data = 'change_car'),
		types.InlineKeyboardButton(text = str(data[2]), callback_data = 'change_phone'))
	elif type == 'user':
		answer = 'Для поездок вам надо перейти в бота для пассажиров'
		reply_markup.add(types.InlineKeyboardButton(text = 'Перейти »', url = 'https://t.me/dyusyduysudysuydwrtrwtrbot'))
	elif type == 'first_time':
		answer = 'Вы здесь первый раз, кто вы?'
		reply_markup.add(types.InlineKeyboardButton(text = 'Я пассажир »', url = 'https://t.me/dyusyduysudysuydwrtrwtrbot'),
						types.InlineKeyboardButton(text = 'Я водитель', callback_data = 'driver'))
	elif type == 'not':
		answer = 'Мы не работаем в вашем городе'
	return [reply_markup, answer]

def question(markup, type, result_ans, mass_questions, chat_id, num, num1):
	l = 1
	answer = '<b>Вопрос ' + str(num)+'/'+str(len(tests.test))+'</b>'+'\n'+ tests.test[num1][0] + '\n'
	for i in tests.test[mass_questions][1]:
		markup.add(types.InlineKeyboardButton(text = str(l), callback_data = 'answer_'+str(i[1])))
		answer += '<b>'+str(l)+')</b> '+ i[0] + '\n'
		l += 1
	refresh_stat(chat_id, type)
	if result_ans is None:
		result.update({chat_id : 0})
	else:
		result[chat_id] += result_ans
	return answer

class WebhookServer(object):
	@cherrypy.expose
	def index(self):
		length = int(cherrypy.request.headers['content-length'])
		json_string = cherrypy.request.body.read(length).decode("utf-8")
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''

@bot.message_handler(commands = ['start'])
def start(message):
	data = bd('SELECT * FROM users WHERE user = "'+str(message.chat.id)+'"')
	type = 'user'
	if data == []:
		data = bd('SELECT * FROM drivers WHERE user = "'+str(message.chat.id)+'"')
		if data == []:
			type = 'first_time'
		else:
			type = 'drive'
			bot.send_message(message.chat.id, 'Привет, '+str(message.chat.username), types.ReplyKeyboardMarkup(True, False).add('Выйти на линию'))
	elif type == 'not':
		answer = 'Мы не работаем в вашем городе'
	bot.send_message(
	chat_id = message.chat.id,
	text = markups(type, message.chat.id)[1],
	reply_markup = markups(type, message.chat.id)[0])

@bot.message_handler(content_types = ['photo'])
def photo(message):
	reply_markup = types.InlineKeyboardMarkup()
	if refresh_stat(message.chat.id, None)[6:] == 'drive_id':
		driver_data.update({'drive_id' : message.photo[-1].file_id})
		answer = 'Ваше селфи с водительским удостоверением в машине'
		type = 'photo_selfie'
	elif refresh_stat(message.chat.id, None)[6:] == 'selfie':
		driver_data.update({'selfie' : message.photo[-1].file_id})
		answer = 'Лицензию на такси при наличии'
		reply_markup.add(types.InlineKeyboardButton(text = 'Пропустить »', callback_data = 'skip_license'))
		type = 'photo_license'
	elif refresh_stat(message.chat.id, None)[6:] == 'license':
		driver_data.update({'license' : message.photo[-1].file_id})
		answer = 'Марку машины, цвет, и гос. номер для идентификации ее пассажиром в формате: <b>Honda Civic, черный, 111-11</b>'
		type = 'reg_car'
	elif refresh_stat(message.chat.id, None)[6:] == 'photo' or refresh_stat(message.chat.id, None) == 'change_car':
		print('change')
		if refresh_stat(message.chat.id, None)[6:] == 'photo':
			spisok = driver_data['photo']
			type = 'photo_photo'
		elif refresh_stat(message.chat.id, None) == 'change_car':
			type = 'change_car'
			spisok = change_car['photo']
		spisok.append(message.photo[-1].file_id)
		if len(spisok) < 4:
			answer = 'Пришлите еще фото '+str(len(spisok))+'/4 (минимум 4 фото со всех сторон)'
		else:
			answer = 'Если вы закончили - нажмите <i>"продолжить"</i>'
			reply_markup = types.ReplyKeyboardMarkup(True, True)
			reply_markup.add('Продолжить')
	elif refresh_stat(message.chat.id, None)[6:] == 'inphoto' or refresh_stat(message.chat.id, None) == 'change_incar':
		if refresh_stat(message.chat.id, None)[6:] == 'inphoto':
			spisok = driver_data['inphoto']
			type = 'photo_inphoto'
		else:
			type = 'change_incar'
			spisok = change_car['inphoto']
		spisok.append(message.photo[-1].file_id)
		if len(spisok) < 2:
			answer = 'Пришлите еще фото '+str(len(spisok))+'/2 (минимум 2 фото передние сиденья и задние)'
		else:
			answer = 'Если вы закончили - нажмите <i>"продолжить"</i>'
			reply_markup = types.ReplyKeyboardMarkup(True, True)
			reply_markup.add('Продолжить')
	bot.send_message(
	chat_id = message.chat.id,
	text = answer,
	reply_markup = reply_markup,
	parse_mode = 'HTML')
	refresh_stat(message.chat.id, type)

@bot.message_handler(content_types = ['contact'])
def contact(message):
	if refresh_stat(message.chat.id, None) == 'reg_drive':
		answer = 'Так же нам потребуется фото Вашего водительского удостоверения'
		driver_data.update({'phone' : message.contact.phone_number})
		refresh_stat(message.chat.id, 'photo_drive_id')
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = types.ReplyKeyboardRemove())

@bot.message_handler(content_types = ['text'])
def text(message):
	if message.text == 'Выйти на линию':
		reply_markup = types.ReplyKeyboardMarkup(True, True)
		answer = 'Начните трансляцию вашей локации на 8 часов'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup)
		refresh_stat(message.chat.id, 'start_working')

	elif message.text == 'Продолжить':
		reply_markup = types.InlineKeyboardMarkup()
		if refresh_stat(message.chat.id, None) == 'photo_photo' or refresh_stat(message.chat.id, None) == 'change_car':
			type = 'photo_inphoto'
			answer = 'Пришлите фото внутри машины. Задних и передних сидений(минимум два фото)'
			if refresh_stat(message.chat.id, None) == 'change_car':
				type = 'change_incar'
			refresh_stat(message.chat.id, type)
		elif refresh_stat(message.chat.id, None) == 'photo_inphoto' or refresh_stat(message.chat.id, None) == 'change_incar':
			if refresh_stat(message.chat.id, None) == 'photo_inphoto':
				answer = 'Вы сможете начать зарабатывать с помощью бота сразу после проверки, а пока пройдите тест!'
				reply_markup.row(types.InlineKeyboardButton(text = 'Пройти опрос', callback_data = 'start_answer'))
				bd('INSERT INTO drivers(user, username, phone, first_name, last_name, third_name) VALUES("'+\
				str(message.chat.id)+'","'+str(message.chat.username)+'","'+driver_data['phone']+'","'+driver_data['first_name']+'","'+driver_data['last_name']+'","'+driver_data['third_name']+'")')
				bd('INSERT INTO docs(user, pasport, drive_id, selfie, license) VALUES("'+str(message.chat.id)+'","'+driver_data['pasport']+'","'+driver_data['drive_id']+'","'+driver_data['selfie']+'","'+str(driver_data['license'])+'")')
				bd('INSERT INTO cars(user, gosnum, car, color, photo) VALUES("'+str(message.chat.id)+'","'+driver_data['gosnum']+'","'+driver_data['car']+'","'+driver_data['color']+'",Null)')
				spisok = driver_data['photo']
				spisok1 = driver_data['inphoto']
			else:
				bd('DELETE FROM cars WHERE user = "'+str(message.chat.id)+'"')
				bd('INSERT INTO cars(user, gosnum, car, color, photo) VALUES("'+str(message.chat.id)+'","'+change_car['gosnum']+'","'+change_car['car']+'","'+change_car['color']+'",Null)')
				reply_markup.row(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
				answer = 'Вы сменили машину'
				spisok = change_car['photo']
				spisok1 = change_car['inphoto']
			refresh_stat(message.chat.id, 'pop')
			photos_in(message.chat.id, spisok, 'car')
			photos_in(message.chat.id, spisok1, 'incar')
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup)

	elif refresh_stat(message.chat.id, None) == 'change_phone':
		bd('UPDATE drivers SET phone = "'+str(message.text)+'" WHERE user = "'+str(message.chat.id)+'"')
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Ваш телефон обновлен!',
		reply_markup = reply_markup)

	elif refresh_stat(message.chat.id, None)[:4] == 'reg_' or refresh_stat(message.chat.id, None) == 'change_car':
		reply_markup = types.ReplyKeyboardMarkup(True, True)
		if refresh_stat(message.chat.id, None)[4:] == 'drive':
			driver_data.update({'first_name' : message.text.split()[1], 'last_name' : message.text.split()[0], 'third_name' : message.text.split()[2]})
			reply_markup.add(types.KeyboardButton(text = 'Подтвердить телефон', request_contact = True))
			answer = 'Подтвердите ваш телефон, в случае отсутствия интернета пассажир будет связываться с Вами по телефону'
		elif refresh_stat(message.chat.id, None)[4:] == 'car' or refresh_stat(message.chat.id, None) == 'change_car':
			if len(message.text.split(',')) != 3:
				answer = 'Вы должны прислать марку машины, цвет, номер в следующем формате с соблюдением запятых: *марка машины, цвет, номер*'
			else:
				answer = 'Фото машины с четырех сторон'
				if refresh_stat(message.chat.id, None)[4:] == 'car':
					refresh_stat(message.chat.id, 'photo_photo')
					driver_data.update({'car' : message.text.split(',')[0], 'color' : message.text.split(',')[1], 'gosnum' : message.text.split(',')[2]})
				else:
					change_car.update({'car' : message.text.split(',')[0], 'color' : message.text.split(',')[1], 'gosnum' : message.text.split(',')[2]})
					refresh_stat(message.chat.id, 'change_car')
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'Markdown')

	elif refresh_stat(message.chat.id, None) == 'help':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Ваш вопрос задан, в скором времени вы получите на него ответ!\nБлагодарим Вас за проявленный интерес, Вы делаете нас лучше!',
		reply_markup = reply_markup)

@bot.edited_message_handler(func = lambda edited_message : True, content_types = ['location'])
def edit(message):
	bd('UPDATE location SET lng = "'+str(message.location.longitude)+'", lat = "'+str(message.location.latitude)+'" WHERE user = "'+str(message.chat.id)+'" AND type = "drive"')
	data = bd('SELECT * FROM trips WHERE drive = "'+str(message.chat.id)+'"')
	if data != []:
		bd('INSERT INTO distance(id, lng, lat) VALUES("'+data[0][1]+'","'+message.location.longitude+'","'+message.location.latitude+'")')

@bot.message_handler(content_types = ['location'])
def location(message):
	if refresh_stat(message.chat.id, None) == 'start_working' or refresh_stat(message.chat.id, None) == 'continue_working':
		if refresh_stat(message.chat.id, None) == 'continue_working':
			answer = 'Вы продолжили смену'
		else:
			answer = 'Вы вышли на смену, ближайшая от вас заявка придет Вам'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer)
		bd('DELETE FROM location WHERE user = "'+str(message.chat.id)+'" AND type = "drive"')
		bd('INSERT INTO location(user, lng, lat, type, data, notification) VALUES("'+str(message.chat.id)+'", "'\
		+str(message.location.longitude)+'", "'\
		+str(message.location.latitude)+'", "drive", "'\
		+datetime.strftime(datetime.now(), '''%H%M%S''')+'", "-")')
		refresh_stat(message.chat.id, 'pop')

@bot.callback_query_handler(func = lambda call: True)
def call(call):
	if call.data[:4] == 'yes_' or call.data[:3] == 'no_':
		reply_markup = types.InlineKeyboardMarkup()
		if call.data[:4] == 'yes_':
			reply_markup.add(types.InlineKeyboardButton(text = 'Пропустить »', callback_data = 'skip_comment_'+call.data[4:]))
			answer = 'Добавьте комментарий к поездке или пропустите это шаг'
			refresh_stat(call.message.chat.id, 'add_comment_'+call.data[4:])
		else:
			answer = 'Пришлите новый адрес'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup)

	elif call.data == 'menu':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = markups('drive', call.message.chat.id)[1],
		reply_markup = markups('drive', call.message.chat.id)[0])

	elif call.data[:7] == 'change_':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		if call.data == 'change_car':
			answer = 'Пришлите марку, цвет, номер машины. Соблюдая запятые в формате: <b>марка машины, цвет, номер</b>'
			type = 'change_car'
		elif call.data == 'change_phone':
			answer = 'Пришлите номер'
			type = 'change_phone'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, type)

	elif call.data == 'news':
		reply_markup = types.InlineKeyboardMarkup()
		data = bd('SELECT * FROM links')
		for row in data:
			reply_markup.add(types.InlineKeyboardButton(text = row[1], url = row[2]))
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Новости и чаты',
		reply_markup = reply_markup)

	elif call.data == 'info':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'О боте', callback_data = 'about'),
						types.InlineKeyboardButton(text = 'Тарифы', callback_data = 'tarif'))
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Что вас интересует?',
		reply_markup = reply_markup)

	elif call.data == 'tarif':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'info'))
		data = bd('SELECT * FROM tarif')
		answer = 'Информация о тарифах'
		for row in data:
			answer += '\n\n<b>'+row[1]+'</b>'+\
			'\n<i>Стоимость км: </i>'+str(row[2])+\
			'\n<i>Стоимость мин: </i>'+str(row[3])+\
			'\n<i>Бесплатные км: </i>'+str(row[4])+\
			'\n<i>Бесплатные мин: </i>'+str(row[5])+\
			'\n<i>Минималка: </i>'+str(row[6])
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data == 'about':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'info'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = bd('SELECT * FROM admin')[0][0],
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data == 'help':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пожалйста, напишите и отправьте ваш вопрос',
		reply_markup = reply_markup)
		refresh_stat(call.message.chat.id, 'help')

	elif call.data == 'history':
		reply_markup = types.InlineKeyboardMarkup()
		data = bd('SELECT * FROM history WHERE drive = "'+str(call.message.chat.id)+'"')
		if len(data) == 0:
			answer = 'Вы совершили ни одной поездки'
		else:
			answer = 'История поездок'
			for row in data:
				reply_markup.add(types.InlineKeyboardButton(text = row[3], callback_data = 'more_history_'+row[0]))
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup)

	elif call.data == 'find_trip' or call.data == 'next_trips':
		reply_markup = types.InlineKeyboardMarkup()
		answers = {'find_trip' : ['Нет отложенных поездок, загляните сюда позже', 'На данный момент доступны следующие поездки'],
				'next_trips' : ['Вы не взяли ни одной поездки', 'Предстоящие для вас поездки']}
		if call.data == 'find_trip':
			data = bd('SELECT * FROM sends WHERE driver is Null')
		else:
			data = bd('SELECT * FROM sends WHERE driver = "'+str(call.message.chat.id)+'"')
		if len(data) == 0:
			answer = answers[call.data][0]
		else:
			answer = answers[call.data][1]
			for row in data:
				print(row[0])
				print(row[3])
				more_data = bd('SELECT * FROM trips WHERE id = "'+row[0]+'"')[0]
				reply_markup.add(types.InlineKeyboardButton(text = more_data[3]+' - '+more_data[4], callback_data = 'more_info_'+row[0]))
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup)

	elif call.data[:10] == 'more_info_' or call.data[:13] == 'more_history_':
		reply_markup = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton(text = ' ', callback_data = 'empty')
		if call.data[:10] == 'more_info_':
			data = bd('SELECT * FROM trips INNER JOIN sends using(id) WHERE id = "'+call.data[10:]+'"')[0]
			comment = bd('SELECT * FROM comments WHERE id = "'+call.data[10:]+'"')
		else:
			data = bd('SELECT * FROM history WHERE id = "'+call.data[13:]+'"')[0]
		answer = '__Информация о поездке:__ \n\n'+\
		'[Пассажир](tg://user?id='+str(data[2])+')'+\
		'\n*Место подачи:* '+data[3]+\
		'\n*Точка назначения:* '+data[4]+\
		'\n*Стоимость:* '+str(data[5])
		if call.data[:10] == 'more_info_':
			if data[8] != None:
				answer += '\n*Дата поездки:* '+str(data[8])
			answer += '\n*Время подачи:* '+str(data[7])[:2]+':'+str(data[7])[2:4]
			if comment != []:
				answer += '\n*Комментарий:* '+\
				'`'+comment[0][1]+'`'
			back = 'find_trip'
			if data[9] == str(call.message.chat.id):
				back = 'next_trips'
			else:
				button = types.InlineKeyboardButton(text = 'Взять поездку', callback_data = 'take_trip_'+data[0])
		else:
			back = 'history'
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = back), button)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'Markdown')

	elif call.data == 'driver':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Как к вам обращаться?: <b>Фамилия Имя Отчество</b>',
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, 'reg_drive')

	elif call.data[:5] == 'skip_' or call.data == 'time_done':
		reply_markup = types.InlineKeyboardMarkup()
		bot.answer_callback_query(call.id, 'Готово')
		if call.data == 'skip_license':
			answer = 'Марку машины, цвет, и гос. номер для идентификации ее пассажиром в формате: <b>Honda Civic, черный, 111-11</b>'
			driver_data.update({'license' : None})
			refresh_stat(call.message.chat.id, 'reg_car')
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data == 'leave_job':
		bot.answer_callback_query(call.id, 'Вам больше не будут приходить заявки о поездках!', show_alert = True)
		bd('DELETE FROM location WHERE user = "'+str(call.message.chat.id)+'"')

	elif call.data[:12] == 'finish_trip_':
		#Выссчитывается стоимость##
		destination = destination_check(call.data[12:]) / 1000
		data = bd('SELECT * FROM trips WHERE id = "'+call.data[12:]+'"')
		time = (time.time() - int(data[0][6]))/60
		tarif = bd('SELECT * FROM tarif WHERE id = "'+str(1)+'"')[0]
		min_km, koef_km, min_time, koef_time = tarif[4], tarif[2], tarif[5], tarif[3]
		cost = ((destination/1000 - min_km)  * koef_km) + ((time - min_time) * koef_time)
		if cost < tarif[6]:
			cost = tarif[6]
		print(cost)
		data_mess = bd('SELECT * FROM messages WHERE id = "'+call.data[12:]+'"')[0]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Поездка закончилась, стоимость = '+str(cost))
		bot.send_message(
		chat_id = data_mess[1],
		text = 'Поездка закончилась, стоимость = '+str(cost))
		bd('INSERT INTO history(id, drive, user, ot, kuda, cost) VALUES("'+data[0][0]+'","'+data[0][1]+'","'+data[0][2]+'","'+data[0][3]+'","'+data[0][4]+'","'+data[0][5]+'")')
		bd('DELETE FROM trips WHERE id = "'+call.data[12:]+'"')
		bd('DELETE FROM messages WHERE id = "'+call.data[12:]+'"')

	elif call.data[:11] == 'start_trip_':
		bd('UPDATE trips SET drive = "'+str(call.message.chat.id)+'" WHERE id = "'+call.data[11:]+'"')
		bd('UPDATE trips SET status = "'+str(time.time())+'" WHERE id = "'+call.data[11:]+'"')
		data = bd('SELECT * FROM messages WHERE id = "'+call.data[11:]+'"')[0]
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Закончить поездку »', callback_data = 'finish_trip_'+call.data[11:]))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Поездка началась',
		reply_markup = reply_markup)
		bot.send_message(
		chat_id = data[1],
		text = 'Поездка началась')

	elif call.data[:7] == 'accept_' or call.data[:9] == 'declaine_':
		if call.data[:7] == 'accept_':
			bd('UPDATE trips SET status = "+" WHERE id = "'+call.data[7:]+'"')
			data = bd('SELECT * FROM trips INNER JOIN messages using(id) WHERE id = "'+call.data[7:]+'"')[0]
			reply_markup = types.InlineKeyboardMarkup()
			nickname = bd('SELECT * FROM users WHERE user = "'+data[2]+'"')[0][0]
			reply_markup.row(types.InlineKeyboardButton(text = 'Начать заказ »', callback_data = 'start_trip_'+call.data[7:]))
			answer = 'Информация о пассажире:\n\n[Связаться](tg://user?id='+str(nickname)+')\n*Пункт отправления: *'+data[3]+'\n*Пункт прибытия: *'+data[4]+'\n'+\
			'*Примерная прибыль: *'+data[5]
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = reply_markup,
			parse_mode = 'Markdown')
			driver_dt = bd('SELECT * FROM drivers INNER JOIN cars using(user) WHERE user = "'+str(call.message.chat.id)+'"')
			print(driver_dt)
			driver_dt = driver_dt[0]
			reply_markup = types.InlineKeyboardMarkup()
			reply_markup.row(types.InlineKeyboardButton(text = 'Отменить поездку »', callback_data = 'cancel_order_'+data[0]))
			bot.send_message(
			chat_id = data[7],
			text = 'Ура, __'+driver_dt[3]+' '+driver_dt[4]+'__ вас повезет!\n\n[Связаться](tg://user?id='+str(driver_dt[0])+')\n'+\
			'*Машина: *'+str(driver_dt[6])+'\t*Цвет: *'+str(driver_dt[7])+'\n*Номер: *'+str(driver_dt[5]),
			reply_markup = reply_markup,
			parse_mode = 'Markdown')
		else:
			bot.answer_callback_query(call.id, 'Заказ передан')
			bot.edit_message_reply_markup(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			reply_markup = types.InlineKeyboardMarkup())

	elif call.data[:7] == 'answer_' or call.data == 'start_answer':
		reply_markup = types.InlineKeyboardMarkup()
		message_id = call.message.message_id
		if call.data == 'start_answer':
			answer = question(reply_markup, 1, None, 0, call.message.chat.id, 1, 0)
		elif len(tests.test) >= refresh_stat(call.message.chat.id, None) + 1:
			answer = question(reply_markup, refresh_stat(call.message.chat.id, None) + 1, int(call.data[7:]),
			refresh_stat(call.message.chat.id, None), call.message.chat.id, str(refresh_stat(call.message.chat.id, None) + 1),
			refresh_stat(call.message.chat.id, None))
		else:
			result[call.message.chat.id] += int(call.data[7:])
			#answer = '<b>Ваш результат: </b>'+str(result[call.message.chat.id])
			reply_markup = types.ReplyKeyboardMarkup(True, False)
			reply_markup.add('Выйти на линию')
			bot.send_message(call.message.chat.id, 'Привет, '+str(call.message.chat.username), reply_markup = reply_markup)
			r = bot.send_message(call.message.chat.id, 'Еще раз')
			message_id = r.message_id
			answer = 'Меню'
			reply_markup = markups('drive', call.message.chat.id)[0]
			refresh_stat(call.message.chat.id, 'pop')
			result.pop(call.message.chat.id)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

if __name__ == '__main__':
	cherrypy.config.update({
		'server.socket_host': '127.0.0.1',
		'server.socket_port': 7773,
		'engine.autoreload.on': False
	})
	cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
