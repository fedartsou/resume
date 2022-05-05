import telebot
import cherrypy
import sqlite3
import random
import requests
import json
import string
import time
import telegramcalendar
import tests
from datetime import datetime
from telebot import types
from taxifunc import id_generator, bd, refresh_stat, time, API_KEY, bd_insert, destination_check, find_location
#@dyusyduysudysuydwrtrwtrbot
bot = telebot.TeleBot('597199791:AAGscOtf_zt3pJqX1ZwPZRIjoUOB3Xy7t1c')
current_shown_dates={}
user_data = {'phone' : 'here is phone',
			'first_name' : 'here is first name',
			'last_name' : 'here is last name',
			'third_name' : 'here is third name',
			'time' : 'here is time',
			'dat' : 'here is day'}
#		reply_markup.add(types.InlineKeyboardButton(text = 'Предстоящих поездок: '+str(len(bd('SELECT * FROM trips WHERE user = "'+str(chat_id)+'"')))))
#+str(len(bd('SELECT * FROM sends WHERE time IS NOT NULL')))
def markups(type, chat_id):
	reply_markup = types.InlineKeyboardMarkup()
	if type == 'user':
		data = bd('SELECT * FROM users WHERE user = "'+str(chat_id)+'"')[0]
		answer = 'Здравствуй, '+ data[3]+'!'
		reply_markup.add(types.InlineKeyboardButton(text = 'Срочный заказ »', callback_data = 'create_trip'))
		reply_markup.add(types.InlineKeyboardButton(text = 'Заказ на определенное время »', callback_data = 'next_trips'))
		reply_markup.add(types.InlineKeyboardButton(text = 'Предстоящих поездок: '+str(len(bd('SELECT * FROM trips WHERE user = "'+str(chat_id)+'"'))), callback_data = 'next_trips'))
		reply_markup.add(types.InlineKeyboardButton(text = 'История поездок', callback_data = 'history'))
	elif type == 'driver':
		answer = 'Для работы вам надо перейти в бота для водителей'
		reply_markup.add(types.InlineKeyboardButton(text = 'Перейти »', url = 'https://t.me/testmenbot'))
	elif type == 'first_time':
		answer = 'Вы здесь первый раз, кто вы?'
		reply_markup.add(types.InlineKeyboardButton(text = 'Я водитель »', url = 'https://t.me/testmenbot'),
						types.InlineKeyboardButton(text = 'Я пассажир', callback_data = 'user'))
	elif type == 'not':
		answer = 'Мы не работаем в вашем городе'
	print(answer)
	return [reply_markup, answer]

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
			type = 'driver'
	if data != [] and data[0][2] == None:
		data = bd('SELECT * FROM users WHERE user = "'+str(message.chat.id)+'"')
		type = 'not'
	elif data != [] and data[0][2] != None:
		type = 'user'
	bot.send_message(
	chat_id = message.chat.id,
	text = markups(type, message.chat.id)[1],
	reply_markup = markups(type, message.chat.id)[0])

@bot.message_handler(content_types = ['location'])
def location(message):
	if refresh_stat(message.chat.id, None) == 'user_location':
		find_location(message, 4)

	elif refresh_stat(message.chat.id, None)[:7] == 'adress_':
		find_location(message, 1)

@bot.message_handler(content_types = ['text'])
def text(message):
	if refresh_stat(message.chat.id, None) == 'reg_user':
		reply_markup = types.ReplyKeyboardMarkup(True, True)
		user_data.update({'first_name' : message.text, 'last_name' : 'Null', 'third_name' : 'Null'})
		reply_markup.add(types.KeyboardButton(text = 'Подтвердить телефон', request_contact = True))
		answer = 'Подтвердите ваш телефон, в случае отсутствия интернета водитель будет связываться с Вами по телефону'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup)

	elif refresh_stat(message.chat.id, None) == 'send_city':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Пока мы не работаем в Вашем городе')
		bd('INSERT INTO users(user, username, city) VALUES("'+str(message.chat.id)+'", "'+str(message.chat.username)+'", "'+str(message.text)+'")')
		refresh_stat(message.chat.id, 'pop')

	elif refresh_stat(message.chat.id, None)[:7] == 'adress_':
		find_location(message, 0)

	elif refresh_stat(message.chat.id, None)[:12] == 'add_comment_':
		id = refresh_stat(message.chat.id, None)[12:]
		if user_data['time'] != None:
			refresh_stat(message.chat.id, datetime.strftime(datetime.now(), '%H%M%S')[:2]+','+datetime.strftime(datetime.now(), '%H%M%S')[2:4]+','+refresh_stat(message.chat.id, None)[12:])
			answer = 'Выберите время'
			reply_markup = time(id, message.chat.id)
		else:
			answer = 'Поездка создана. Ищем водителя...'
			reply_markup = types.InlineKeyboardMarkup()
			reply_markup.add(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
			bd_insert(id, None, message.chat.id, None, None)
			refresh_stat(message.chat.id, 'pop')
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		bd('INSERT INTO comments(id, comment) VALUES("'+id+'","'+message.text+'")')

	elif refresh_stat(message.chat.id, None) == 'user_location':
		find_location(message, 2)

@bot.message_handler(content_types = ['contact'])
def contact(message):
	if refresh_stat(message.chat.id, None) == 'reg_user':
		data = bd('SELECT * FROM users WHERE user = "'+str(message.chat.id)+'"')
		bd('INSERT INTO users(user, username, phone, first_name, last_name, third_name, city) VALUES("'+\
		str(message.chat.id)+'","'+message.chat.username+'","'+message.contact.phone_number+'","'+\
		user_data['first_name']+'","'+user_data['last_name']+'","'+user_data['third_name']+'", "Москва")')
		refresh_stat(message.chat.id, 'pop')
	bot.send_message(
	chat_id = message.chat.id,
	text = markups('user', message.chat.id)[1],
	reply_markup = markups('user', message.chat.id)[0])

@bot.message_handler(content_types = ['photo'])
def photo(message):
	pass

@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
	user_data.update({'day' : call.data[13:]})
	refresh_stat(call.message.chat.id, datetime.strftime(datetime.now(), '%H%M%S')[:2]+','+datetime.strftime(datetime.now(), '%H%M%S')[2:4]+','+refresh_stat(call.message.chat.id, None)[12:])
	bot.edit_message_text(
	chat_id = call.message.chat.id,
	message_id = call.message.message_id,
	text = 'Выберите время',
	reply_markup = time(refresh_stat(call.message.chat.id, None)[12:], call.message.chat.id))

@bot.callback_query_handler(func = lambda call: True)
def call(call):
	if call.data == 'user':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Да', callback_data = 'moscow'),
		types.InlineKeyboardButton(text = 'Нет', callback_data = 'other'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Вы из Москвы?',
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data == 'moscow' or call.data == 'other':
		if call.data == 'moscow':
			answer = 'Ваше имя?'
			refresh_stat(call.message.chat.id, 'reg_user')
		else:
			answer = 'Напишите Ваш город'
			refresh_stat(call.message.chat.id, 'send_city')
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'HTML')

	elif call.data == 'menu':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = markups('user', call.message.chat.id)[1],
		reply_markup = markups('user', call.message.chat.id)[0],
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, 'pop')

	elif call.data == 'history':
		bot.answer_callback_query(call.id, 'Эта функция в разработке', show_alert = True)

	elif call.data[:4] == 'yes_' or call.data == 'yes' or call.data[:3] == 'no_' or call.data == 'no':
		reply_markup = types.InlineKeyboardMarkup()
		if call.data == 'yes':
			answer = 'Напишите конечный адрес или пришлите локацию'
			refresh_stat(call.message.chat.id, 'adress_'+refresh_stat(call.message.chat.id, None))
		elif call.data == 'no':
			answer = 'Пришлите новый адрес подачи'
			bd('DELETE FROM trips WHERE id = "'+refresh_stat(call.message.chat.id, None)+'"')
			refresh_stat(call.message.chat.id, 'user_location')
		if call.data[:4] == 'yes_':
			print(call.data[4:])
			reply_markup.add(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'),
							types.InlineKeyboardButton(text = 'Пропустить »', callback_data = 'skip_comment_'+call.data[4:]))
			answer = 'Добавьте комментарий к поездке или пропустите это шаг'
			refresh_stat(call.message.chat.id, 'add_comment_'+call.data[4:])
		elif call.data[:3] == 'no_':
			answer = 'Пришлите новый конечный адрес'
			reply_markup.row(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup)
#«»
	elif call.data == 'create_trip' or call.data == 'next_trips':
		user_data.update({'time' : None})
		user_data.update({'date' : None})
		if call.data == 'next_trips':
			user_data.update({'time' : 'Not null'})
			user_data.update({'date' : 'Not null'})
		bot.send_message(call.message.chat.id, text = 'Напишите адрес подачи или пришлите локацию', reply_markup = types.ReplyKeyboardMarkup(True, True).row(types.KeyboardButton(text = 'Прислать локацию', request_location = True)))
		refresh_stat(call.message.chat.id, 'user_location')

	elif call.data[:5] == 'skip_' or call.data == 'time_done':
		bot.answer_callback_query(call.id, 'Готово')
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.row(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
		answer = 'Поездка создана. Ищем водителя...'
		if call.data[:13] == 'skip_comment_':
			if user_data['time'] != None:
				answer = 'Когда забирать?'
				now = datetime.now()
				reply_markup = telegramcalendar.create_calendar(now.year, now.month)
			else:
				id, date, day = call.data[13:], None, None
		else:
			data = refresh_stat(call.message.chat.id, None).split(',')
			id, date, day = data[2], data[0]+data[1]+'00', user_data['day']
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		bd_insert(id, date, call.message.chat.id, None, day)

	elif call.data[:6] == 'hours_' or call.data[:8] == 'minutes_':
		bot.answer_callback_query(call.id, 'Wait')
		data = refresh_stat(call.message.chat.id, None).split(',')
		if call.data[:9] == 'hours_up_':
			id = call.data[9:]
			refresh_stat(call.message.chat.id, str(int(data[0])+1)+','+str(data[1])+','+call.data[9:])
		elif call.data[:11] == 'hours_down_':
			id = call.data[11:]
			refresh_stat(call.message.chat.id, str(int(data[0])-1)+','+str(data[1])+','+call.data[11:])
		elif call.data[:11] == 'minutes_up_':
			id = call.data[11:]
			refresh_stat(call.message.chat.id, str(data[0])+','+str(int(data[1])+10)+','+call.data[11:])
		elif call.data[:13] == 'minutes_down_':
			id = call.data[13:]
			refresh_stat(call.message.chat.id, str(data[0])+','+str(int(data[1])-10)+','+call.data[13:])
		reply_markup = time(id, call.message.chat.id)
		reply_markup.row(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Когда забирать?',
		reply_markup = time(id, call.message.chat.id),
		parse_mode = 'HTML')

	elif call.data[:13] == 'cancel_order_':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.row(types.InlineKeyboardButton(text = '« Меню', callback_data = 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Поездка отменена, вас никто не повезет')
		bd('DELETE FROM sends WHERE id = "'+call.data[13]+'"')
		data = bd('SELECT * FROM trips WHERE id = "'+call.data[13:]+'"')[0]
		bd('INSERT INTO history(id, drive, user, ot, kuda, cost) VALUES("'+data[0]+'","'+data[1]+'","'+data[2]+'","'+data[3]+'","'+data[4]+'","'+data[5]+'")')
		if data[1] != None:
			bot.send_message(
			chat_id = data[1],
			text = 'Пассажир больше не хочет ехать с: '+data[3])
		bd('DELETE FROM trips WHERE id = "'+call.data[13:]+'"')
		bd('DELETE FROM messages WHERE id = "'+call.data[13:]+'"')
		bd('DELETE FROM distance WHERE id = "'+call.data[13:]+'"')
		bd('DELETE FROM comments WHERE id = "'+call.data[13:]+'"')




if __name__ == '__main__':
	cherrypy.config.update({
		'server.socket_host': '127.0.0.1',
		'server.socket_port': 7774,
		'engine.autoreload.on': False
	})
	cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
