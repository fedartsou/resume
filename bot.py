import telebot
from telebot import types
import cherrypy
import sqlite3
import random
import requests
import time
import json
import string

WEBHOOK_HOST = '82.202.204.83'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ('381314117:AAFIt9oMmW4r749drt4_uqbYb_rogAZWw2s')

bot = telebot.TeleBot('381314117:AAFIt9oMmW4r749drt4_uqbYb_rogAZWw2s')
token = 'Bearer 4560e5298d2d5a4c5943c238142a08a6'
qiwi = 79962319945

logi = {}
labele = []

choose_side = types.InlineKeyboardMarkup()
seller = types.InlineKeyboardButton(text = 'Продавец', callback_data = 'seller')
buyer = types.InlineKeyboardButton(text = 'Покупатель', callback_data = 'buyer')
back_side = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
choose_side.add(seller, buyer)
choose_side.add(back_side)

choose_value = types.InlineKeyboardMarkup()
bitcoins = types.InlineKeyboardButton(text = 'Bitcoin', callback_data = 'bitcoin')
qiwi = types.InlineKeyboardButton(text = 'Qiwi', callback_data = 'qiwi')
back_side = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
choose_value.add(bitcoins)
choose_value.add(qiwi)
choose_value.add(back_side)

reviews = types.InlineKeyboardMarkup()
mine = types.InlineKeyboardButton(text = 'Мой рейтинг', callback_data = 'mine')
back_reviews = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
reviews.add(mine)
reviews.add(back_reviews)

menu_kb = types.InlineKeyboardMarkup()
make_deal = types.InlineKeyboardButton(text = 'Оформить/войти в сделку', callback_data = 'make_deal')
lk = types.InlineKeyboardButton(text = 'Личный кабинет', callback_data = 'lk')
find_seller = types.InlineKeyboardButton(text = 'Найти продавца/продукт', callback_data = 'find_seller')
reviews = types.InlineKeyboardButton(text = 'Рейтинг пользователя', callback_data = 'reviews')
menu_kb.add(make_deal)
menu_kb.add(lk)
menu_kb.add(find_seller)
menu_kb.add(reviews)

percent_markup = types.InlineKeyboardMarkup()
seller_percent = types.InlineKeyboardButton(text = 'Я(продавец)', callback_data = 'iam')
buyer_percent = types.InlineKeyboardButton(text = 'Покупатель', callback_data = 'buyerpercent')
back_percent = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
percent_markup.add(seller_percent, buyer_percent)
percent_markup.add(back_percent)

lk_inside = types.InlineKeyboardMarkup()
sells = types.InlineKeyboardButton(text = 'История продаж', callback_data = 'sell_history')
bougth = types.InlineKeyboardButton(text = 'История покупок', callback_data = 'buy_history')
main_catalog = types.InlineKeyboardButton(text = 'Мой каталог', callback_data = 'main_catalog')
deals = types.InlineKeyboardButton(text = 'Текущие сделки', callback_data = 'deals')
pay_user = types.InlineKeyboardButton(text = 'Платежные реквизиты', callback_data = 'pay_user')
back_lk = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
lk_inside.add(sells, bougth)
lk_inside.add(main_catalog)
lk_inside.add(deals)
lk_inside.add(pay_user)
lk_inside.add(back_lk)

back_menu = types.InlineKeyboardMarkup()
back_lop_menu = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
back_menu.add(back_lop_menu)

class WebhookServer(object):
	@cherrypy.expose
	def index(self):
		if 'content-length' in cherrypy.request.headers and \
						'content-type' in cherrypy.request.headers and \
						cherrypy.request.headers['content-type'] == 'application/json':
			length = int(cherrypy.request.headers['content-length'])
			json_string = cherrypy.request.body.read(length).decode("utf-8")
			update = telebot.types.Update.de_json(json_string)
			bot.process_new_updates([update])
			return ''
		else:
			raise cherrypy.HTTPError(403)

def id_generator(size = 10, chars = string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def try_document(user_id, document_id):
	bot.send_chat_action(user_id, 'upload_document')
	bot.send_document(user_id, document_id)

def try_video(user_id, document_id):
	bot.send_chat_action(user_id, 'upload_video')
	bot.send_document(user_id, document_id)

def try_photo(user_id, document_id):
	bot.send_chat_action(user_id, 'upload_photo')
	bot.send_document(user_id, document_id)

@bot.message_handler(content_types=['document'])
def document(message):
	if logi[message.chat.id][:15] != 'upload_document':
		answer = 'Напиши сумму сделки в рублях'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		if logi[message.chat.id] == 'bitcoin':
			our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
			btc = our_pay.json()['address']
			lable = 0
		else:
			btc = '79962319945'
			lable = str(id_generator())
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, network_fee, our_fee, summ_rub, network_rub, our_fee_rub, note, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
		(message.chat.id, 0, message.document.file_id, btc, lable, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lable))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})
	else:
		answer = 'Файл загружен!'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('UPDATE sdelki SET document_code = ? WHERE id_sdelki = ?', (message.document.file_id, logi[message.chat.id][15:]))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

@bot.message_handler(content_types = ['video'])
def video(message):
	if logi[message.chat.id][:15] != 'upload_document':
		answer = 'Напиши сумму сделки в рублях'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		if logi[message.chat.id] == 'bitcoin':
			our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
			btc = our_pay.json()['address']
			lable = 0
		else:
			btc = '79962319945'
			lable = str(id_generator())
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, network_fee, our_fee, summ_rub, network_rub, our_fee_rub, note, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
		(message.chat.id, 0, message.video.file_id, btc, lable, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lable))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})
	else:
		answer = 'Файл загружен!'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('UPDATE sdelki SET document_code = ? WHERE id_sdelki = ?', (message.video.file_id, logi[message.chat.id][15:]))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

@bot.message_handler(content_types = ['audio'])
def video(message):
	answer = 'Пришли адуио в архиве'
	bot.send_message(
	chat_id = message.chat.id,
	text = answer,
	parse_mode = 'Markdown',
	reply_markup = back_menu)

@bot.message_handler(content_types = ['photo'])
def photo(message):
	if logi[message.chat.id] != 'upload_document':
		answer = 'Напиши сумму сделки в рублях'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		if logi[message.chat.id] == 'bitcoin':
			our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
			btc = our_pay.json()['address']
			lable = 0

		else:
			btc = '79962319945'
			lable = str(id_generator())
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, network_fee, our_fee, summ_rub, network_rub, our_fee_rub, note, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
		(message.chat.id, 0, message.photo[-1].file_id, btc, lable, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lable))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	else:
		answer = 'Файл загружен!'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('UPDATE sdelki SET document_code = ? WHERE id_sdelki = ?', (message.photo[-1].file_id, logi[message.chat.id][15:]))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

@bot.message_handler(content_types=['text'])
def text(message):
	global logi
	global back
	converter = {}
	response = requests.get('https://blockchain.info/ru/ticker/')
	koeff = 1/float(response.json()['RUB']['buy'])
	if message.text == '/start':
		logi.update({message.chat.id : 'start'})
		answer = 'Меню'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = menu_kb)

	elif logi[message.chat.id][0] == 'Пришли отзыв о пользователе':
		answer = 'Ваш отзыв: '+'\n'+message.text++'\n'+'О пользователе '+logi[message.chat.id][1]
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('UPDATE review SET review = ? WHERE leaver_id = ? AND review = ?', (message.text, message.chat.id, 0))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id][0] == 'Опишите суть диспута':
		answer = 'Диспут открыт :('
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = lk_inside)
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			for row in rows:
				if row[0] == message.chat.id or row[1] == message.chat.id and row[15] == logi[message.chat.id][1]:
					curr.execute('INSERT INTO disputs(manual_giver, money_giver, note, document_code, description) VALUES(?,?,?,?,?)', (row[0], row[1], message.text, logi[message.chat.id][1], row[7]))
					conn.commit()
					break
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id][0] == 'Каким будет ваше примечание?':
		answer = 'Примечание добавлено :)'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = lk_inside,
		parse_mode = 'Markdown')
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('UPDATE sdelki SET note = ? WHERE manual_giver = ? AND id_sdelki = ?',
					(message.text, message.chat.id, logi[message.chat.id][1],))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id][0] == 'Пришлите новый кошелек':
		answer = 'Кошелек изменен'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = lk_inside,
		parse_mode = 'Markdown')
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND money_giver = ?',
					(message.text, message.chat.id, logi[message.chat.id][1],))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Пришли nickname или ID пользователя. Можешь переслать сообщение с ним':
		reviews_about = []
		reviews_string = ''
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM review')
			rows = curr.fetchall()
			for row in rows:
				if str(row[0]) == message.forward_from.id:
					reviews_about.append(row[1])
				elif str(row[0]) == message.text:
					reviews_about.append(row[1])
				elif str(row[2]) == message.text or row[2] == message.text[1:]:
					reviews_about.append(row[1])

		for i in reviews_about:
			reviews_string += i + '\n' +'------------------------------' + '\n'

		if reviews_string == '':
			answer = 'Отзывов нету'
			bot.send_message(
			chat_id = message.chat.id,
			text = answer,
			reply_markup = back_menu,
			parse_mode = 'Markdown')
		else:
			answer = ''
			answer = reviews_string
			bot.send_message(
			chat_id = message.chat.id,
			text = reviews_string,
			reply_markup = back_menu,
			parse_mode = 'HTML')
		reviews_about.clear()
		reviews_string = ''
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Пришлите новый BTC кошелек':
		answer = 'Кошелек изменен :)'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('UPDATE users SET user_pay = ? WHERE user_id = ?', ('change_'+message.text, message.chat.id))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Пришлите новый QIWI кошелек':
		answer = 'Кошелек изменен :)'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('UPDATE users SET user_qiwi = ? WHERE user_id = ?', (str(message.text), message.chat.id))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Выберите прошлый кошелек или пришлите новый':
		answer = 'Напиши условия сделки'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		if message.chat.id in labele:
			curr.execute('UPDATE users SET user_qiwi = ? WHERE user_id = ?', (str(message.text), message.chat.id))
			curr.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND manual_giver_pay = ?', (str(message.text), message.chat.id, 0))
			labele.remove(message.chat.id)
		else:
			curr.execute('UPDATE users SET user_pay = ? WHERE user_id = ?', ('change_' + str(message.text), message.chat.id))
			curr.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND manual_giver_pay = ?', (str(message.text), message.chat.id, 0))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Пришли ID/nickname продавца или ID товара':
		n = 0
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM seller')
			rows = cur.fetchall()
			choose_good = types.InlineKeyboardMarkup()
			for row in rows:
				if str(row[0]) == message.text or row[1] == message.text or row[15] == message.text:
					if row[15] == message.text:
						list_data = types.InlineKeyboardButton(text = row[9]+': '+str(row[7])+'p.', callback_data = 'shop_'+row[15])
						choose_good.add(list_data)
						n += 1
					elif str(row[0]) == message.text or row[1] == message.text or row[1] == message.text[:1]:
						list_data = types.InlineKeyboardButton(text = row[9]+': '+str(row[7])+'p.', callback_data = 'shop_'+row[15])
						choose_good.add(list_data)
						n += 1

		back_choose_button = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
		choose_good.add(back_choose_button)
		if n == 0:
			answer = 'Товаров нету'
			bot.send_message(
			chat_id = message.chat.id,
			text = answer,
			parse_mode = 'Markdown',
			reply_markup = choose_good)

		else:
			answer = 'Выбирай:'
			bot.send_message(
			chat_id = message.chat.id,
			text = answer,
			parse_mode = 'Markdown',
			reply_markup = choose_good)
		logi.update({message.chat.id : answer})

	elif message.forward_from and logi[message.chat.id] == 'Перешли сообщение от покупателя мне в чат':
		try:
			bot.send_message(
			chat_id = message.forward_from.id,
			text = str(message.from_user.username) + ' пригласил Вас в сделку',
			parse_mode = 'Markdown',
			reply_markup = back_menu)
			conn = sqlite3.connect('./garant.sqlite3')
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			n = len(curr.fetchall())
			answer = 'Сделка №'+str(n)+' создана.'+'\n'+str(message.forward_from.username)+' пользовался ботом :)'
			bot.send_message(
			chat_id = message.chat.id,
			text = answer,
			parse_mode = 'Markdown',
			reply_markup = back_menu)
			logi.update({message.chat.id : answer})
			curr.execute('UPDATE sdelki SET money_giver = ? WHERE manual_giver = ?', (message.forward_from.id, message.chat.id,))
			conn.commit()
			conn.close()

		except Exception:
			conn = sqlite3.connect('./garant.sqlite3')
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			n = len(curr.fetchall())
			answer = 'Сделка №'+str(n)+' создана.'+'\n'+str(message.forward_from.username)+' не пользовался ботом.'
			bot.send_message(
			chat_id = message.chat.id,
			text = answer,
			parse_mode = 'Markdown',
			reply_markup = back_menu)
			logi.update({message.chat.id : answer})
			curr.execute('UPDATE sdelki SET money_giver = ? WHERE manual_giver = ?', (message.forward_from.id, message.chat.id,))
			conn.commit()
			conn.close()

	elif message.forward_from and logi[message.chat.id] == 'Перешли сообщение от продавца':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[0] == message.forward_from.id and row[1] == message.chat.id and row[7] is not None:
					menu_buyer = types.InlineKeyboardMarkup()
					agree = types.InlineKeyboardButton(text = 'Согласен', callback_data = 'agree_'+row[15])
					disagre = types.InlineKeyboardButton(text = 'Не согласен', callback_data = 'disagre_'+row[15])
					back_menu_buyer = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
					menu_buyer.add(agree, disagre)
					menu_buyer.add(back_menu_buyer)
					answer = 'условия'
					bot.send_message(
					chat_id = message.chat.id,
					text = 'Ознакомтесь с условиями сделки'+'\n'+
					'------------------------------'+'\n'+
					str(row[7])+'\n'+
					'------------------------------'+'\n'+
					'Процент оплачивает - '+str(row[8])+'\n'+
					'Сумма сделки: '+str(row[11])+' RUB'+'\n'+
					'Наш процент: '+str(row[13])+' RUB'+'\n'+
					'------------------------------'+'\n'+
					'Согласны?',
					parse_mode = 'Markdown',
					reply_markup = menu_buyer)
					logi.update({message.chat.id : answer})
					break

				elif row[0] == message.forward_from.id and row[1] == message.chat.id and row[7] is None:
					answer = 'Внесены не все данные, ожидайте'
					bot.send_message(
					chat_id = message.chat.id,
					text = answer,
					parse_mode = 'Markdown')
					logi.update({message.chat.id : answer})

		try:
			bot.send_message(
			chat_id = message.forward_from.id,
			text = str(message.from_user.username)+' присоединился к сделке',
			reply_markup = menu_kb,
			parse_mode = 'Markdown')
		except Exception:
			bot.send_message(
			chat_id = message.chat.id,
			text = 'Что-то явно пошло не так :|',
			reply_markup = menu_kb,
			parse_mode = 'Markdown')

	elif logi[message.chat.id] == 'Напиши условия сделки':
		conn = sqlite3.connect('./garant.sqlite3')
		cur = conn.cursor()
		cur.execute('UPDATE sdelki SET description = ? WHERE manual_giver = ? AND description = ?', (message.text, message.chat.id, 0))
		conn.commit()
		conn.close()
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()[::-1]
			for row in rows:
				if row[0] == message.chat.id and row[1] != 0:
					try:
						menu_buyer = types.InlineKeyboardMarkup()
						agree = types.InlineKeyboardButton(text = 'Согласен', callback_data = 'agree_'+row[15])
						disagre = types.InlineKeyboardButton(text = 'Не согласен', callback_data = 'disagre_'+row[15])
						back_menu_buyer = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
						menu_buyer.add(agree, disagre)
						menu_buyer.add(back_menu_buyer)
						answer = 'условия'
						bot.send_message(
						chat_id = row[1],
						text = 'Ознакомтесь с условиями сделки'+'\n'+
						'------------------------------'+'\n'+
						str(row[7])+'\n'+
						'------------------------------'+'\n'+
						'Процент оплачивает - '+str(row[8])+'\n'+
						'Сумма сделки: '+str(row[11])+' RUB'+'\n'+
						'Наш процент: '+str(row[13])+' RUB'+'\n'+
						'------------------------------'+'\n'+
						'Согласны?',
						parse_mode = 'Markdown',
						reply_markup = menu_buyer)
						answer = 'условия'
						bot.send_message(
						chat_id = message.chat.id,
						text = 'Сделка создана, покупатель получил условия сделки, ожидайте',
						parse_mode = 'Markdown',
						reply_markup = back_menu)
						logi.update({message.chat.id : answer})
						break
					except Exception:
						answer = 'Перешли сообщение от покупателя мне в чат'
						bot.send_message(
						chat_id = message.chat.id,
						text = answer,
						reply_markup = back_menu,
						parse_mode = 'Markdown')
						logi.update({message.chat.id : answer})
						break

				elif row[0] == message.chat.id and row[1] == 0:
					answer = 'Перешли сообщение от покупателя мне в чат'
					bot.send_message(
					chat_id = message.chat.id,
					text = answer,
					reply_markup = back_menu,
					parse_mode = 'Markdown')
					logi.update({message.chat.id : answer})
					break
		conn.close()

	elif logi[message.chat.id] == 'Пришли свой BTC кошелек' or logi[message.chat.id] == 'Пришли свой QIWI кошелек':
		answer = 'Напиши условия сделки'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		conn = sqlite3.connect('./garant.sqlite3')
		cur = conn.cursor()
		cur.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND manual_giver_pay = ?', (message.text, message.chat.id, 0))
		if logi[message.chat.id] == 'Пришли свой BTC кошелек':
			cur.execute('UPDATE users SET user_pay = ? WHERE user_id = ?', ('change_'+message.text, message.chat.id,))
		else:
			cur.execute('UPDATE users SET user_qiwi = ? WHERE user_id = ?', (message.text, message.chat.id,))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id][0] == 'Пришли новый вариант':
		answer = 'Изменения вступили в силу'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = lk_inside,
		parse_mode = 'Markdown')
		sql = 'UPDATE seller SET '+logi[message.chat.id][1]+' = ? WHERE seller_id = ? AND id_sdelki = ?'
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute(sql, (message.text, message.chat.id, logi[message.chat.id][2]))
		conn.commit()
		conn.close()
		logi.update({message.chat.id : answer})

	elif logi[message.chat.id] == 'Напиши сумму сделки в рублях' or logi[message.chat.id] == 'Сумма сделки должна быть больше или равна 1000 рублей!' and float(message.text) >= 1000:
		answer = 'Кто оплачивает процент?'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = percent_markup)
		logi.update({message.chat.id : [answer, message.text]})

	elif logi[message.chat.id] == 'Напиши сумму сделки в рублях' or logi[message.chat.id] == 'Сумма сделки должна быть больше или равна 1000 рублей!' and float(message.text) < 999:
		answer = 'Сумма сделки должна быть больше или равна 1000 рублей!'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({message.chat.id : answer})


@bot.callback_query_handler(func=lambda call: True)
def inline(call):
	print(call.data)
	global back
	global logi
	global lable
	global qiwi
	global token
	converter = {}
	response = requests.get('https://blockchain.info/ru/ticker/')
	koeff = 1/float(response.json()['RUB']['buy'])

	if call.data == 'seller':
		answer = 'Какой способ оплаты предпочитаете?'+'\n'+'<i>Биткоин-сеть взымает комиссию в районе 500р за перевод, учтите так же 5% гаранта</i>'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = choose_value,
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'bitcoin':
		cif = types.InlineKeyboardMarkup()
		cif_button = types.InlineKeyboardButton(text = 'Услуга', callback_data = 'cif_button')
		cif_back = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
		cif.add(cif_button)
		cif.add(cif_back)
		answer = 'Если это документ, то пришлите его. Если услуга выберите соответствующий пункт меню:'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = cif,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'bitcoin'})

	elif call.data == 'cif_button':
		answer = 'Напиши сумму сделки в рублях'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'Markdown',
		reply_markup = back_menu)
		if logi[call.message.chat.id] == 'bitcoin':
			our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
			btc = our_pay.json()['address']
			lable = 0
		else:
			btc = '79962319945'
			lable = str(id_generator())
		conn = sqlite3.connect('./garant.sqlite3')
		cursor = conn.cursor()
		cursor.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, network_fee, our_fee, summ_rub, network_rub, our_fee_rub, note, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
		(call.message.chat.id, 0, 'usluga', btc, lable, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, lable))
		conn.commit()
		conn.close()
		logi.update({call.message.chat.id : answer})

	elif call.data == 'qiwi':
		cif = types.InlineKeyboardMarkup()
		cif_button = types.InlineKeyboardButton(text = 'Услуга', callback_data = 'cif_button')
		cif_back = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
		cif.add(cif_button)
		cif.add(cif_back)
		answer = 'Если это документ, то пришлите его. Если услуга выберите соответствующий пункт меню:'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = cif,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'qiwi'})
		labele.append(call.message.chat.id)

	elif call.data == 'menu':
		answer = 'Меню'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = menu_kb,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'lk':
		answer = 'Личный кабиент'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = lk_inside,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'make_deal':
		answer = 'Выбери свою роль в сделке'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = choose_side,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'main_catalog':
		n = 0
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM seller')
			rows = cur.fetchall()
			choose_good = types.InlineKeyboardMarkup()
			for row in rows:
				if row[0] == call.message.chat.id:
					list_data = types.InlineKeyboardButton(text = str(row[9]), callback_data = 'edit_'+row[15])
					choose_good.add(list_data)
					n += 1
			back_choose_good = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
			choose_good.add(back_choose_good)
			if n != 0:
				answer = 'Выбери продукт для редактирования:'
				n = 0
			else:
				answer = 'У вас еще нету продуктов'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = choose_good,
			parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'leave_review':
		answer = 'Пришли отзыв о пользователе'
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM review')
			rows = curr.fetchall()
			for row in rows:
				if row[3] == call.message.chat.id and row[1] is None:
					logi.update({call.message.chat.id : [answer, row[2]]})
					break
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer + row[2],
		reply_markup = back_menu,
		parse_mode = 'Markdown')

	elif call.data == 'mine':
		reviews_about = []
		reviews_string = ''
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM review')
			rows = curr.fetchall()
			for row in rows:
				if row[0] == call.message.chat.id:
					reviews_about.append(row[1])
		for i in reviews_about:
			reviews_string += i + '\n' +'------------------------------' + '\n'

		if reviews_string != '':
			answer = ''
			answer = reviews_string
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = reviews_string,
			reply_markup = back_menu,
			parse_mode = 'Markdown')

		else:
			answer = 'Отзывов нету'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = back_menu,
			parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'buyerpercent' or call.data == 'iam' and logi[call.message.chat.id][0] == 'Кто оплачивает процент?':
		conn = sqlite3.connect('./garant.sqlite3')
		cur = conn.cursor()
		if call.data == 'buyerpercent':
			cur.execute('UPDATE sdelki SET summ = ? WHERE manual_giver = ? AND summ = ?', (round((float(logi[call.message.chat.id][1])+float(logi[call.message.chat.id][1])*6/100)*koeff, 5), call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET summ_rub = ? WHERE manual_giver = ? AND summ_rub = ? ', (round((float(logi[call.message.chat.id][1])+float(logi[call.message.chat.id][1])*6/100), 5), call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET oplata = ? WHERE manual_giver = ? AND oplata = ?', ('покупатель', call.message.chat.id, 0))
		else:
			cur.execute('UPDATE sdelki SET summ = ? WHERE manual_giver = ? AND summ = ?', (round(float(logi[call.message.chat.id][1])*koeff, 5), call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET summ_rub = ? WHERE manual_giver = ? AND summ_rub = ?', (round(float(logi[call.message.chat.id][1]), 5), call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET oplata = ? WHERE manual_giver = ? AND oplata = ?', ('продавец', call.message.chat.id, 0))
		conn.commit()
		cur.execute('SELECT * FROM users WHERE user_id = ?', (call.message.chat.id,))
		rows = cur.fetchall()
		for row in rows:
			btc = row[1]
			qiwi = row[4]
		if btc == 'change_Добавьте кошелек' and call.message.chat.id not in labele:
			answer = 'Пришли свой BTC кошелек'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			parse_mode = 'Markdown')

		elif call.message.chat.id in labele and qiwi is None:
			answer = 'Пришли свой Qiwi кошелек'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			parse_mode = 'Markdown')

		else:
			conn = sqlite3.connect('./garant.sqlite3')
			cur = conn.cursor()
			if qiwi is not None and call.message.chat.id in labele:
				cur.execute('SELECT * FROM users WHERE user_id = ?', (call.message.chat.id,))
				rows = cur.fetchall()
				choose_pay = types.InlineKeyboardMarkup()
				for row in rows:
					choose_qiwi = types.InlineKeyboardButton(text = 'QIWI - ' + str(row[4]), callback_data = 'choose_qiwi_'+ str(row[4]))
				choose_pay.add(choose_qiwi)

			elif call.message.chat.id not in labele and btc != 'change_Добавьте кошелек':
				cur.execute('SELECT * FROM users WHERE user_id = ?', (call.message.chat.id,))
				rows = cur.fetchall()
				choose_pay = types.InlineKeyboardMarkup()
				for row in rows:
					choose_btc = types.InlineKeyboardButton(text = 'BTC - ' + str(row[1][7:]), callback_data = 'choose_btc_'+ str(row[1][7:]))
				choose_pay.add(choose_btc)

			answer = 'Выберите прошлый кошелек или пришлите новый'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = choose_pay,
			parse_mode = 'Markdown')

			cur.execute('UPDATE sdelki SET our_fee_rub = ? WHERE manual_giver = ? AND our_fee_rub = ?',
						(float(logi[call.message.chat.id][1])/100*5, call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET our_fee = ? WHERE manual_giver = ? AND our_fee = ?',
						((float(logi[call.message.chat.id][1])*koeff/100*5), call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET our_fee_rub = ? WHERE manual_giver = ? AND our_fee_rub = ?',
						(float(logi[call.message.chat.id][1])/100*5, call.message.chat.id, 0))
			cur.execute('UPDATE sdelki SET our_fee = ? WHERE manual_giver = ? AND our_fee = ?',
						((float(logi[call.message.chat.id][1])*koeff/100*5), call.message.chat.id, 0))
			conn.commit()
			conn.close()
		logi.update({call.message.chat.id : answer})

	elif call.data[:12] == 'choose_qiwi_':
		answer = 'Напиши условия сделки'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		con = sqlite3.connect('./garant.sqlite3')
		cur = con.cursor()
		cur.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND manual_giver_pay = ?',
					(call.data[12:], call.message.chat.id, 0,))
		con.commit()
		con.close()
		labele.remove(call.message.chat.id)
		logi.update({call.message.chat.id : answer})

	elif call.data[:11] == 'choose_btc_':
		answer = 'Напиши условия сделки'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		con = sqlite3.connect('./garant.sqlite3')
		cur = con.cursor()
		cur.execute('UPDATE sdelki SET manual_giver_pay = ? WHERE manual_giver = ? AND manual_giver_pay = ?',
					(call.data[11:], call.message.chat.id, 0,))
		con.commit()
		con.close()
		logi.update({call.message.chat.id : answer})

	elif call.data == 'reviews':
		reviews_search_markup = types.InlineKeyboardMarkup()
		reviews_search_markup0 = types.InlineKeyboardButton(text = 'Отзывы обо мне', callback_data = 'mine')
		reviews_search_markup1 = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
		reviews_search_markup.add(reviews_search_markup0)
		reviews_search_markup.add(reviews_search_markup1)
		answer = 'Пришли nickname или ID пользователя. Можешь переслать сообщение с ним'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reviews_search_markup,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:13] == 'history_show_':
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('SELECT * FROM history WHERE id_sdelki = ?', (call.data[13:],))
		rows = curr.fetchall()
		for row in rows:
			if row[0] == call.message.chat.id or row[1] == call.message.chat.id and row[6] == call.data[13:]:
				answer = 'info'
				bot.edit_message_text(
				chat_id = call.message.chat.id,
				message_id = call.message.message_id,
				text = 'Информация по сделке '+'\n'+
				'------------------------------'+'\n'+
				'Покупатель - '+str(row[0])+'\n'+
				'Продавец - '+str(row[1])+'\n'+
				'Цена - '+str(row[5])+'BTC'+'\n'+
				'Описание: '+'\n'+str(row[4])+'\n'+
				'------------------------------'+'\n'+
				'ID - '+call.data[13:]+'\n'+
				'------------------------------',
				reply_markup = back_menu,
				parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'sell_history':
		n = 0
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('SELECT * FROM history WHERE manual_giver = ?', (call.message.chat.id,))
		rows = curr.fetchall()
		sell_markup = types.InlineKeyboardMarkup()
		for row in rows:
			sell_button = types.InlineKeyboardButton( text = str(row[3]), callback_data = 'history_show_'+row[6])
			sell_markup.add(sell_button)
			n += 1
		sell_back = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
		sell_markup.add(sell_back)
		if n == 0:
			answer = 'Сделок нету'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = back_menu,
			parse_mode = 'Markdown')
		else:
			answer = 'Выберите сделку:'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = sell_markup,
			parse_mode = 'Markdown')
		n = 0
		logi.update({call.message.chat.id : answer})

	elif call.data == 'buy_history':
		n = 0
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('SELECT * FROM history WHERE money_giver = ?', (call.message.chat.id,))
		rows = curr.fetchall()
		sell_markup = types.InlineKeyboardMarkup()
		for row in rows:
			sell_button = types.InlineKeyboardButton( text = str(row[3]), callback_data = 'history_show_'+row[6])
			sell_markup.add(sell_button)
			n += 1
		sell_back = types.InlineKeyboardButton( text = '<< В кабинет', callback_data = 'lk')
		sell_markup.add(sell_back)
		if n == 0:
			answer = 'Сделок нету'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = back_menu,
			parse_mode = 'Markdown')
		else:
			answer = 'Выберите сделку:'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = sell_markup,
			parse_mode = 'Markdown')
		n = 0
		logi.update({call.message.chat.id : answer})

	elif call.data[:12] == 'change_qiwi_':
		answer = 'Пришлите новый QIWI кошелек'
		back = types.InlineKeyboardMarkup()
		back_point = types.InlineKeyboardButton(text = 'Назад', callback_data = 'pay_user')
		back.add(back_point)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:7] == 'change_':
		answer = 'Пришлите новый BTC кошелек'
		back = types.InlineKeyboardMarkup()
		back_point = types.InlineKeyboardButton(text = 'Назад', callback_data = 'pay_user')
		back.add(back_point)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:11] == 'nower_open_':
		answer = 'Опишите суть диспута'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, call.data[11:]]})

	elif call.data[:13] == 'nower_adding_':
		answer = 'Каким будет ваше примечание?'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, call.data[13:]]})

	elif call.data[:11] == 'close_deal_':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki WHERE money_giver = ? and id_sdelki = ?', (call.message.chat.id, call.data[11:],))
			rows = cur.fetchall()
			for row in rows:
				if row[4] == 0:
					response = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/payment?password=klopman567&to='+str(row[5])+'&amount='+str(int(row[6]*100000000)-70000)+'&from='+str(row[3])+'&fee=70000')
					if 'success' in response.json():
						answer = 'Вы закрыли сделку'
						bot.edit_message_text(
						chat_id = call.message.chat.id,
						message_id = call.message.message_id,
						text = answer,
						reply_markup = back_menu,
						parse_mode = 'Markdown')
						logi.update({call.message.chat.id : answer})

						close_buyer = types.InlineKeyboardMarkup()
						back_buton = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
						blockchain_button = types.InlineKeyboardButton(text = 'Информация по транзакции', url = 'https://blockchain.info/ru/block/'+response.json()['tx_hash'])
						bot.send_message(
						chat_id = row[0],
						text = 'Покупатель закрыл сделку',
						reply_markup = back_menu,
						parse_mode = 'Markdown')
						cur.execute('INSERT INTO history(money_giver, manual_giver, document_id, name, description, price, id_sdelki) VALUES(?,?,?,?,?,?,?)', (row[1], row[0], row[2], row[7][:10], row[7], row[6], row[15]))
						cur.execute('INSERT INTO seller(seller_id, btc, document_id, opisanie, price, name, percent_pay, summ_rub, id_sdelki, lable) VALUES(?,?,?,?,?,?,?,?,?,?)', (row[0], row[5], row[2], row[7], row[6], row[7][:10]+'...', row[8], row[11], row[15], 'btc'))
						cur.execute('DELETE FROM sdelki WHERE id_sdelki = ?', (call.data[11:],))
					elif 'error' in response.json():
						answer = 'Возникли проблемы с закрытием сделки, попробуйте позже'
						bot.edit_message_text(
						chat_id = call.message.chat.id,
						message_id = call.message.message_id,
						text = answer,
						reply_markup = back_menu,
						parse_mode = 'Markdown')
						logi.update({call.message.chat.id : answer})

				elif row[4] != 0:
					answer = 'Покупатель закрыл сделку'+'\n'+'<i>Деньги переведены на ваш</i> <b>QIWI</b><i> кошелек</i>',
					answer1 = 'Сделка закрыта',
					if row[5][:1] == '+':
						account = row[5]
					elif row[5][:1] != '+' and row[5].isdigit():
						account = '+' + str(row[5])
					else:
						answer = 'Вы указали не верный кошелек!'+'\n'+'Измените его, перейдя в <i>Личный кабинет -> Текущие сделки -> Нужная сделка -> Редактировать кошелек</i>',
						answer1 = 'Продавец указал не верный кошелек, как только он его исправит вы сможете закрыть сделку',
					id_trans = int(time.time())*1000
					headers = {"Accept": "application/json", "Authorization" : token, "Content-type" : "application/json"}
					data = {"id" : str(id_trans),
							"sum": { "amount" : float(row[11])-float(row[11])/20, "currency":"643"},
							"paymentMethod": { "type":"Account", "accountId":"643"},
							"comment" : "Перевод от " + call.message.from_user.username,
							"fields": {"account": account}}
					url_pay = 'https://edge.qiwi.com/sinap/api/v2/terms/99/payments'
					r = requests.post(url_pay, data = json.dumps(data), headers = headers)

					bot.send_message(
					chat_id = row[0],
					text = answer,
					reply_markup = back_menu,
					parse_mode = 'HTML')

					bot.send_message(
					chat_id = call.message.chat.id,
					text = answer1,
					reply_markup = back_menu,
					parse_mode = 'HTML')
					cur.execute('INSERT INTO history(money_giver, manual_giver, document_id, name, description, price, id_sdelki) VALUES(?,?,?,?,?,?,?)', (row[1], row[0], row[2], row[7][:10], row[7], row[6], row[15]))
					cur.execute('INSERT INTO seller(seller_id, btc, document_id, opisanie, price, name, percent_pay, summ_rub, id_sdelki, lable) VALUES(?,?,?,?,?,?,?,?,?,?)', (row[0], row[5], row[2], row[7], row[6], row[7][:10]+'...', row[8], row[11], row[15], 'qiwi'))
					cur.execute('DELETE FROM sdelki WHERE id_sdelki = ?', (call.data[11:],))

		conn.commit()
		conn.close()

	elif call.data[:9] == 'get_dock_':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id or row[0] == call.message.chat.id and row[15] == call.data[9:]:
					try:
						try_document(call.message.chat.id, row[2])
					except Exception:
						try:
							try_photo(call.message.chat.id, row[2])
						except Exception:
							try_video(call.message.chat.id, row[2])
			answer = 'И такое бывает'
			bot.send_message(
			chat_id = call.message.chat.id,
			text = answer,
			reply_markup = back_menu,
			parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:16] == 'show_description':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id or row[0] == call.message.chat.id and row[15] == call.data[17:]:
					bot.answer_callback_query(call.id, show_alert=True, text=row[7])
		logi.update({call.message.chat.id : row[7]})

	elif call.data[:11] == 'update_pay_':
		answer = 'Пришлите новый кошелек'
		bot.send_message(
		chat_id = call.message.chat.id,
		text = answer,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, call.data[11:]]})

	elif call.data[:16] == 'upload_document_':
		answer = 'Пришлите документ в формате <b>.zip</b>'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'upload_document'+call.data[16:]})

	elif call.data[:6] == 'nower_':
		print(call.data)
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			nower_deal_markup = types.InlineKeyboardMarkup()
			for row in rows:
				if row[0] == call.message.chat.id or row[1] == call.message.chat.id and row[15] == call.data[6:]:
					nower_check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'check_'+row[15])
					nower_check0 = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'qiwi_check_'+row[15])
					nower_get = types.InlineKeyboardButton(text = 'Получить документ', callback_data = 'get_dock_'+row[15])
					nower_get0 = types.InlineKeyboardButton(text = 'Загрузить документ', callback_data = 'upload_document_'+row[15])
					nower_deal_button0 = types.InlineKeyboardButton(text = 'Примечаний нет', callback_data = 'nower_adding_'+row[15])
					nower_deal_button00 = types.InlineKeyboardButton(text = 'прим: '+str(row[14]), callback_data = 'nower_adding_'+row[15])
					nower_deal_button22 = types.InlineKeyboardButton(text = 'Условие сделки', callback_data = 'show_description_'+row[15])
					nower_deal_button2 = types.InlineKeyboardButton(text = 'Открыть диспут', callback_data = 'nower_open_'+row[15])
					nower_deal_button1 = types.InlineKeyboardButton(text = 'Закрыть сделку', callback_data = 'close_deal_'+row[15])
					nower_update_pay = types.InlineKeyboardButton(text = 'Редактировать кошелек', callback_data = 'update_pay_'+str(row[1]))
					if row[4] == 0:
						balance_deal = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/address_balance?password=klopman567&address='+str(row[3]))
						balance_deal = balance_deal.json()['balance'] / 100000000
						if round(float(balance_deal), 5) >= round(float(row[6]), 5):
							if row[1] == call.message.chat.id and row[2] != 'usluga':
								nower_deal_markup.add(nower_get)
								nower_deal_markup.add(nower_deal_button1)
							else:
								nower_deal_markup.add(nower_check)
					elif row[4] != 0:
						url_transaction = 'https://edge.qiwi.com/payment-history/v1/persons/'+str(qiwi)+'/payments?rows=50'
						r = requests.get(url_transaction, headers = {'Accept': 'application/json', 'Authorization' : token, 'Content-type' : 'application/json'})
						n = 0
						try:
							while True:
								if r.json()['data'][n]['comment'] == row[15]:
									balance_deal = r.json()['data'][n]['sum']['amount']
									if round(float(balance_deal), 5) >= round(float(row[6]), 5):
										if row[1] == call.message.chat.id and row[2] != 'usluga':
											nower_deal_markup.add(nower_get)
											nower_deal_markup.add(nower_deal_button1)
											break
								n += 1
						except Exception:
							balance_deal = 0
							nower_deal_markup.add(nower_check0)
					if str(row[14]) == '0':
						nower_deal_markup.add(nower_deal_button0)
					else:
						nower_deal_markup.add(nower_deal_button00)
					if row[0] == call.message.chat.id  and row[2] == 'usluga':
						nower_deal_markup.add(nower_update_pay)
						nower_deal_markup.add(nower_get0)
					nower_deal_markup.add(nower_deal_button2)
					back_nower = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
					nower_deal_markup.add(nower_deal_button22)
					nower_deal_markup.add(back_nower)
					answer = 'Нажмите, чтоб изменить'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = nower_deal_markup,
					parse_mode = 'Markdown')
					break
		answer = 'check'
		logi.update({call.message.chat.id : answer})

	elif call.data == 'deals':
		markup = []
		n = 0
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			deals_markup = types.InlineKeyboardMarkup()
			for row in rows:
				if row[0] == call.message.chat.id or row[1] == call.message.chat.id :
					deal_button = types.InlineKeyboardButton(text = row[7][:8] + ': ' + str(row[11]) + 'p', callback_data = 'nower_' + row[15])
					deals_markup.add(deal_button)
					n += 1
			back_deals = types.InlineKeyboardButton( text = '<< В кабинет', callback_data = 'lk')
			deals_markup.add(back_deals)
		if n > 0:
			answer = 'Текущие сделки'
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = deals_markup,
			parse_mode = 'Markdown')
		else:
			answer = 'Сделок нету :('
			bot.edit_message_text(
			chat_id = call.message.chat.id,
			message_id = call.message.message_id,
			text = answer,
			reply_markup = deals_markup,
			parse_mode = 'Markdown')
		n = 0
		logi.update({call.message.chat.id : answer})

	elif call.data == 'pay_user':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM users')
			rows = cur.fetchall()
			choose_btc = types.InlineKeyboardMarkup()
			for row in rows:
				if row[0] == call.message.chat.id:
					list_btc0 = types.InlineKeyboardButton( text = 'BTC для вывода: ' + row[1][7:], callback_data = row[1][:7])
					list_btc1 = types.InlineKeyboardButton( text = 'QIWI для вывода: ' + str(row[4]), callback_data = 'change_qiwi_' + str(row[4]))
					back_choose_btc = types.InlineKeyboardButton( text = 'В личный кабинет', callback_data = 'lk')
					choose_btc.add(list_btc0)
					choose_btc.add(list_btc1)
					choose_btc.add(back_choose_btc)
					break
		answer = 'Выберите операцию:'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = choose_btc,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:9] == 'edit_name':
		answer = 'Пришли новый вариант'
		print(call.data)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, 'name', call.data[10:]]})

	elif call.data[:13] == 'edit_opisanie':
		answer = 'Пришли новый вариант'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, 'opisanie', call.data[14:]]})

	elif call.data[:10] == 'edit_price':
		answer = 'Пришли новый вариант'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : [answer, 'price', call.data[11:]]})

	elif call.data[:4] == 'edit' and logi[call.message.chat.id] == 'Выбери продукт для редактирования:':
		change_markup = types.InlineKeyboardMarkup()
		sql = 'SELECT * FROM seller WHERE id_sdelki = ?'
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute(sql, [(call.data[5:])])
		rows = curr.fetchall()
		for row in rows:
			if row[15] == call.data[5:]:
				edit_name = types.InlineKeyboardButton(text = 'Название', callback_data = 'edit_name_'+row[15])
				edit_description = types.InlineKeyboardButton(text = 'Условие сделки', callback_data = 'edit_opisanie_'+row[15])
				edit_price = types.InlineKeyboardButton(text = 'Цену', callback_data = 'edit_price_'+row[15])
				back_change_markup = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
				verification = types.InlineKeyboardButton(text = 'Верифицировать товар', callback_data = 'verificate_'+row[15])
				delete = types.InlineKeyboardButton(text = 'Удалить товар', callback_data = 'delete_'+row[15])
				change_markup.add(edit_name)
				change_markup.add(edit_description)
				change_markup.add(edit_price)
				change_markup.add(verification)
				change_markup.add(back_change_markup)
				change_markup.add(delete)
				bot.edit_message_text(
				chat_id = call.message.chat.id,
				message_id = call.message.message_id,
				text = 'Что меняем?'+'\n'+
				'------------------------------'+'\n'+
				'Название - '+str(row[9])+'\n'+
				'Описание - '+str(row[6])+'\n'+
				'Цена - '+str(row[7])+'\n'+
				'------------------------------'+'\n'+
				'Верификация '+str(row[4])+'\n'+
				'ID товара: '+str(row[15]),
				reply_markup = change_markup,
				parse_mode = 'HTML')
				break
		logi.update({call.message.chat.id : 'change'})

	elif call.data[:7] == 'delete_':
		answer = 'Товар удален'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})
		conn = sqlite3.connect('./garant.sqlite3')
		curr = conn.cursor()
		curr.execute('DELETE FROM seller WHERE seller_id = ? AND id_sdelki = ?', (call.message.chat.id, call.data[7:]))
		conn.commit()
		conn.close()

	elif call.data[:4] == 'this':
		sql = 'SELECT * FROM seller WHERE id_sdelki = ?'
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute(sql, [(call.data[5:])])
			rows = curr.fetchall()
			for row in rows:
				if row[15] == call.data[5:]:
					our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
					btc = our_pay.json()['address']
					curr.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, our_fee, summ_rub, our_fee_rub, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
								(row[0], 0, row[5], btc, 0, row[2], row[5], row[6], row[7], row[11], row[13], row[14], row[15]))
				conn.commit()
		conn.close()
		answer = 'Перешли сообщение от покупателя'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:3] == 'buy' and call.data != 'buyerpercent' and call.data != 'buyer':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM seller WHERE id_sdelki = ?', (call.data[4:],))
			rows = curr.fetchall()
			for row in rows:
				print('hello')
				if row[16] == 'btc':
					our_pay = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567')
					btc = our_pay.json()['address']
					curr.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?)',
								(row[0], call.message.chat.id, row[5], btc, 0, row[2], row[7], row[6], row[10], row[15]))

					answer = 'Пополните BTC кошелек:'+'\n'+btc+'\n'+'На сумму: '+str(row[7])+' BTC'
					check_pay = types.InlineKeyboardMarkup()
					check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'check_'+row[15])
					back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
					check_pay.add(check)
					check_pay.add(back_check_pay)

				elif row[16] == 'qiwi':
					lable = id_generator()
					curr.execute('INSERT INTO sdelki(manual_giver, money_giver, document_code, our_pay, lable, manual_giver_pay, summ, description, oplata, id_sdelki) VALUES(?,?,?,?,?,?,?,?,?,?)',
								(row[0], call.message.chat.id, row[5], qiwi, lable, row[2], row[7], row[6], row[10], lable))

					answer = 'Пополните Qiwi кошелек:'+'\n'+str(qiwi)+'\n'+'С примечанием - '+lable+'\n'+'На сумму: '+str(row[11])+' p.'
					check_pay = types.InlineKeyboardMarkup()
					check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'qiwi_check_'+lable)
					back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
					check_pay.add(check)
					check_pay.add(back_check_pay)

				bot.edit_message_text(
				chat_id = call.message.chat.id,
				message_id = call.message.message_id,
				text = answer,
				reply_markup = check_pay,
				parse_mode = 'Markdown')
				logi.update({call.message.chat.id : answer})
				conn.commit()
		conn.close()


	elif call.data[:4] == 'shop':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM seller WHERE id_sdelki = ?', (call.data[5:],))
			rows = curr.fetchall()
			for row in rows:
				choose_buyer = types.InlineKeyboardMarkup()
				buy = types.InlineKeyboardButton(text = 'Купить', callback_data = 'buy_'+row[15])
				not_buy = types.InlineKeyboardButton(text = 'Отказаться', callback_data = 'menu')
				choose_buyer.add(buy, not_buy)
				bot.edit_message_text(
				chat_id = call.message.chat.id,
				message_id = call.message.message_id,
				text = 'Ознакомтесь с условиями сделки'+'\n'+
				'------------------------------'+'\n'+
				str(row[6])+'\n'+
				'------------------------------'+'\n'+
				'Процент оплачивает - '+str(row[10])+'\n'+
				'Сумма сделки: '+str(row[7])+' RUB'+'\n'+
				'Наш процент: '+str(float(row[7])/20)+' RUB'+'\n'+
				'------------------------------'+'\n'+
				'ID товара: '+str(row[15])+'\n'+
				'------------------------------',
				reply_markup = choose_buyer,
				parse_mode = 'HTML')

		answer = 'uslovie'
		logi.update({call.message.chat.id : answer})

	elif call.data == 'find_seller':
		answer = 'Пришли ID/nickname продавца или ID товара'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:5] == 'check' or call.data[:11] == 'qiwi_check_':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[15] == call.data[6:] and call.data[:11] != 'qiwi_check_':
					if row[3] is not None:
						check_pay = types.InlineKeyboardMarkup()
						check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'check_'+row[15])
						back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
						check_pay.add(check)
						check_pay.add(back_check_pay)
						balance = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/address_balance?password=klopman567&address='+str(row[3]))
						if float(balance.json()['balance']) == 0:
							answer = 'Закрыть пока нельзя 0 BTC'
							bot.answer_callback_query(call.id, text = answer)
							logi.update({call.message.chat.id : answer})

						elif round(float(balance.json()['balance']), 5) >= float(round(float(row[6]), 5)):
							if row[2] != 'usluga':
								try:
									try_document(call.message.chat.id, row[2])
								except Exception:
									try:
										try_photo(call.message.chat.id, row[2])
									except Exception:
										try_video(call.message.chat.id, row[2])
								check_dock = types.InlineKeyboardMarkup()
								true = types.InlineKeyboardButton(text = 'Верно', callback_data = 'true_'+row[15])
								not_true = types.InlineKeyboardButton(text = 'Не верно', callback_data = 'not_true_'+row[15])
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(true, not_true)
								check_dock.add(back_check_dock)
								answer = 'Проверьте следующий документ, соответствует ли он условиям выше?'
								answer1 = 'Пришла оплата, документ отправлен на проверку :)'
							else:
								check_dock = types.InlineKeyboardMarkup()
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(back_check_dock)
								answer = 'Оплата пришла, фрилансер приступил к работе'
								answer1 = 'Пришла оплата, приступайте к работе'
							bot.send_message(
							chat_id = call.message.chat.id,
							text = answer,
							reply_markup = check_dock,
							parse_mode = 'Markdown')

							bot.send_message(
							chat_id = row[0],
							text = answer1,
							parse_mode = 'Markdown',
							reply_markup = back_menu)
							logi.update({call.message.chat.id : answer})

						else:
							answer = 'Пополните счет на полную сумму сделки: '+str(row[6])
							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							reply_markup = check_pay,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

				elif row[0] == call.message.chat.id and row[15] == call.data[6:] and call.data[:11] != 'qiwi_check_':
					if row[2] is not None:
						check_pay = types.InlineKeyboardMarkup()
						check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'check_'+row[15])
						back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
						check_pay.add(check)
						check_pay.add(back_check_pay)
						balance = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/address_balance?password=klopman567&address='+str(row[3]))
						if float(balance.json()['balance']) == 0:
							answer = 'Закрыть пока нельзя 0 BTC'
							bot.answer_callback_query(call.id, text = answer)
							logi.update({call.message.chat.id : answer})

						elif round(float(balance.json()['balance']), 5) >= float(row[6]):
							if row[2] != 'usluga':
								check_dock = types.InlineKeyboardMarkup()
								true = types.InlineKeyboardButton(text = 'Верно', callback_data = 'true_'+row[15])
								not_true = types.InlineKeyboardButton(text = 'Не верно', callback_data = 'not_true_'+row[15])
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(true, not_true)
								check_dock.add(back_check_dock)
								answer1 = 'Проверьте следующий документ, соответствует ли он условиям выше?'
								answer = 'Пришла оплата, документ отправлен на проверку :)'
								try:
									try_document(row[1], row[2])
								except Exception:
									try:
										try_photo(row[1], row[2])
									except Exception:
										try_video(row[1], row[2])
							else:
								check_dock = types.InlineKeyboardMarkup()
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(back_check_dock)
								answer = 'Пришла оплата, можете приступать к работе'
								answer1 = 'Фрилансер приступил к работе'

							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							parse_mode = 'Markdown')

							bot.send_message(
							chat_id = row[1],
							text = answer1,
							reply_markup = check_dock,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

						else:
							answer = 'Пополните счет на полную сумму сделки: '+str(row[6])
							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							reply_markup = check_pay,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

				elif row[0] == call.message.chat.id and row[15] == call.data[11:] and call.data[:11] == 'qiwi_check_':
					print('hello')
					if row[2] is not None:
						check_pay = types.InlineKeyboardMarkup()
						check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'qiwi_check_'+row[15])
						back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
						check_pay.add(check)
						check_pay.add(back_check_pay)
						url_transaction = 'https://edge.qiwi.com/payment-history/v1/persons/79962319945/payments?rows=50'
						r = requests.get(url_transaction, headers = {'Accept': 'application/json', 'Authorization' : 'Bearer 4560e5298d2d5a4c5943c238142a08a6', 'Content-type' : 'application/json'})
						n = 0
						balance = 0
						try:
							while True:
								if r.json()['data'][n]['comment'] == row[15]:
									balance = r.json()['data'][n]['sum']['amount']
									break
								n += 1
						except Exception as err:
							print(err)
							balance = 0
						n = 0
						if float(balance) == 0:
							answer = 'Закрыть пока нельзя 0 p.'
							bot.answer_callback_query(call.id, text = answer)
							logi.update({call.message.chat.id : answer})

						elif round(float(balance), 5) >= float(row[6]):
							if row[2] != 'usluga':
								answer = 'Пришла оплата, документ отправлен на проверку :)'
								try:
									try_document(row[1], row[2])
								except Exception:
									try:
										try_photo(row[1], row[2])
									except Exception:
										try_video(row[1], row[2])
								check_dock = types.InlineKeyboardMarkup()
								true = types.InlineKeyboardButton(text = 'Верно', callback_data = 'true_'+row[15])
								not_true = types.InlineKeyboardButton(text = 'Не верно', callback_data = 'not_true_'+row[15])
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(true, not_true)
								check_dock.add(back_check_dock)
								answer1 = 'Проверьте следующий документ, соответствует ли он условиям выше?'
							else:
								check_dock = types.InlineKeyboardMarkup()
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(back_check_dock)
								answer1 = 'Оплата пришла, фрилансер приступил к работе'
								answer = 'Пришла оплата, приступайте к работе'

							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							parse_mode = 'Markdown')

							bot.send_message(
							chat_id = row[1],
							text = answer1,
							reply_markup = check_dock,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

						else:
							answer = 'Пополните счет на полную сумму сделки: '+str(row[6])
							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							reply_markup = check_pay,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

				elif row[1] == call.message.chat.id and row[15] == call.data[11:] and call.data[:11] == 'qiwi_check_':
					if row[2] is not None:
						check_pay = types.InlineKeyboardMarkup()
						check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'qiwi_check_'+row[15])
						back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
						check_pay.add(check)
						check_pay.add(back_check_pay)
						url_transaction = 'https://edge.qiwi.com/payment-history/v1/persons/79962319945/payments?rows=50'
						r = requests.get(url_transaction, headers = {'Accept': 'application/json', 'Authorization' : 'Bearer 4560e5298d2d5a4c5943c238142a08a6', 'Content-type' : 'application/json'})
						n = 0
						balance = 0
						try:
							while True:
								if r.json()['data'][n]['comment'] == row[15]:
									balance = r.json()['data'][n]['sum']['amount']
									break
								n += 1
						except Exception as err:
							print(err)
							balance = 0
						n = 0
						if float(balance) == 0:
							answer = 'Закрыть пока нельзя 0 p.'
							bot.answer_callback_query(call.id, text = answer)
							logi.update({call.message.chat.id : answer})

						elif round(float(balance), 5) >= float(row[6]):
							if row[2] != 'usluga':
								answer = 'Пришла оплата, документ отправлен на проверку :)'
								try:
									try_document(call.message.chat.id, row[2])
								except Exception:
									try:
										try_photo(call.message.chat.id, row[2])
									except Exception:
										try_video(call.message.chat.id, row[2])
								check_dock = types.InlineKeyboardMarkup()
								true = types.InlineKeyboardButton(text = 'Верно', callback_data = 'true_'+row[15])
								not_true = types.InlineKeyboardButton(text = 'Не верно', callback_data = 'not_true_'+row[15])
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(true, not_true)
								check_dock.add(back_check_dock)
								answer1 = 'Проверьте следующий документ, соответствует ли он условиям выше?'
							else:
								check_dock = types.InlineKeyboardMarkup()
								back_check_dock = types.InlineKeyboardButton(text = '<< В меню', callback_data = 'menu')
								check_dock.add(back_check_dock)
								answer1 = 'Пришла оплата, фрилансер приступил к работе'
								answer = 'Пришла оплата, приступайте к работе'

							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							parse_mode = 'Markdown')

							bot.send_message(
							chat_id = call.message.chat.id,
							text = answer1,
							reply_markup = check_dock,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

						else:
							answer = 'Пополните счет на полную сумму сделки: '+str(row[6])
							bot.edit_message_text(
							chat_id = call.message.chat.id,
							message_id = call.message.message_id,
							text = answer,
							reply_markup = check_pay,
							parse_mode = 'Markdown')
							logi.update({call.message.chat.id : answer})

	elif call.data[:10] == 'wait_deal_':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[0] == int(call.data[10:]):
					answer = 'Сделка не закрыта, как только ваш товар придет, закройте сделку в личном кабинете'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = menu_kb,
					parse_mode = 'Markdown')
					answer = 'Сделка не закрыта, вы получите деньги после того, как покупатель закроет сделку'
					bot.send_message(
					chat_id = row[0],
					text = answer,
					reply_markup = menu_kb,
					parse_mode = 'Markdown')
		conn.close()
		logi.update({call.message.chat.id : answer})

	elif call.data[:4] == 'true':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[15] == call.data[5:]:
					leav_reviews = types.InlineKeyboardMarkup()
					close_deal0 = types.InlineKeyboardButton(text = 'Закрыть сделку', callback_data = 'close_deal_'+str(row[15]))
					close_deal1 = types.InlineKeyboardButton(text = 'Не закрывать', callback_data = 'wait_deal_'+str(row[15]))
					leav_reviews.add(close_deal1)
					leav_reviews.add(close_deal0)
					answer = 'Закрыть сделку?'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = leav_reviews,
					parse_mode = 'Markdown')
					break
		logi.update({call.message.chat.id : answer})

	elif call.data[:8] == 'not_true':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[15] == call.data[9:]:
					answer = 'Рапорт по сделке'+'\n'+'---'+'\n'+'ID покупателя: '+str(call.message.chat.id)+'\n'+'ID продавца: '+str(row[0])
					bot.send_message(
					chat_id = 89366959,
					text = answer,
					parse_mode = 'Markdown')
					answer = 'Вопрос отправлен на рассмотрение модерации, вам напишет @markenstain'
					bot.send_message(
					chat_id = call.message.chat.id,
					text = answer,
					parse_mode = 'Markdown',
					reply_markup = back_menu)
					answer = 'Вопрос отправлен на рассмотрение модерации, вам напишет @markenstain'
					bot.send_message(
					chat_id = row[0],
					text = answer,
					parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data == 'buyer':
		answer = 'Перешли сообщение от продавца'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_menu,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : answer})

	elif call.data[:5] == 'agree':
		conn = sqlite3.connect('./garant.sqlite3')
		with conn:
			cur = conn.cursor()
			cur.execute('SELECT * FROM sdelki')
			rows = cur.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[3] is None and row[6] is None and row[15] == call.data[6:]:
					answer = 'Не все данные!'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					parse_mode = 'HTML')

				elif row[1] == call.message.chat.id and row[15] == call.data[6:] and row[3] == 0:
					check_pay = types.InlineKeyboardMarkup()
					check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'check_'+row[15])
					back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
					check_pay.add(check)
					check_pay.add(back_check_pay)
					answer = 'Пополните BTC кошелек:'+'\n'+str(row[3])+'\n'+'На сумму: '+str(row[6])+' BTC'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = check_pay,
					parse_mode = 'HTML')

				elif row[1] == call.message.chat.id and row[15] == call.data[6:] and row[3] is not None and row[3] != 0:
					check_pay = types.InlineKeyboardMarkup()
					check = types.InlineKeyboardButton(text = 'Проверить зачисление средств', callback_data = 'qiwi_check_'+row[15])
					back_check_pay = types.InlineKeyboardButton(text = '<< В кабинет', callback_data = 'lk')
					check_pay.add(check)
					check_pay.add(back_check_pay)
					answer = 'Пополните Qiwi кошелек:'+'\n'+str(row[3])+'\n'+'С примечанием - '+str(row[15])+'\n'+'На сумму: '+str(row[11])+' p.'
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = check_pay,
					parse_mode = 'HTML')

		logi.update({call.message.chat.id : answer})

	elif call.data[:8] == 'disagre_':
		conn = sqlite3.connec('./garant.sqlite3')
		with conn:
			curr = conn.cursor()
			curr.execute('SELECT * FROM sdelki')
			rows = curr.fetchall()
			for row in rows:
				if row[1] == call.message.chat.id and row[15] == call.data[8:]:
					answer = 'Сделка отменена :('
					bot.edit_message_text(
					chat_id = call.message.chat.id,
					message_id = call.message.message_id,
					text = answer,
					reply_markup = menu_kb,
					parse_mode = 'Markdown')

					answer = 'Сделка отменена покупателем :('
					bot.send_message(
					chat_id = row[0],
					text = answer,
					reply_markup = menu_kb,
					parse_mode = 'Markdown')
					break
			curr.execute('DELETE FROM sdelki WHERE id_sdelki = ?', (call.data[8:],))
			conn.commit()
		conn.close()
		logi.update({call.message.chat.id : answer})



bot.remove_webhook()

bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
				certificate = open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
	'server.socket_host': WEBHOOK_LISTEN,
	'server.socket_port': WEBHOOK_PORT,
	'server.ssl_module': 'builtin',
	'server.ssl_certificate': WEBHOOK_SSL_CERT,
	'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
