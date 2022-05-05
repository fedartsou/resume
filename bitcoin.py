import telebot
import string
import json
import requests
import random
import cherrypy
import sqlite3
import time
import smtplib
from telebot import types
from telegraph import Telegraph
telegraph = Telegraph()

WEBHOOK_HOST = '68.183.160.11'
WEBHOOK_PORT = 88  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ('713926081:AAHlZWIjOV4_MDuujrS3CUme-SmUbJAYuUY')
wallet_work = {'full_wallet' : ['Выберите криптовалюту, которую хотите пополнить:', 'full_'], 'out_wallet' : ['Выберите криптовалюту, которую хотите вывести:', 'out_'], 'make_bill': ['Выберите криптовалюту для чека', 'check_'], 'create_type_buy' : ['Какую криптовалюту вы хотите купить?'], 'create_type_sell' : ['Какую криптовалюту вы хотите продать?']}
add_dic = {'btc' : 'Введите новый платежный адрес Bitcoin\n Пример адреса: 1Hv5RMDDZSfn69m2*******dsJzM386DPH',
			'eth' : 'Введите новый платежный адрес Ethereum\n Пример адреса: c5e6a28ff23a491********f3d28be75e4d65523'}
ADMIN = 625139398
dict_wallet_reverse = {'btc' : 'Bitcoin', 'eth' : 'Ethereum'}
dict_wallet = {'Bitcoin' : ['btc', 1], 'Ethereum' : ['eth', 2]}
triger_markup = {'1' : ['⚫️ Остановить', 'stop', '🔵'], '0' : ['⚪️ Возобновить', 'refresh', '⚪️'], 'sell' : '📕', 'buy' : '📘'}
sounds_dic = {'off' : ['🔕', 'on'], 'on' : ['🔔', 'off']}

lang_dic = {'ru' : ['Русский', 'eng'], 'eng' : ['English', 'ru']}
curr_dic = {'all' : ['Да', 'not'], 'not' : ['Нет', 'all']}
users_stat = {'nub' : 'Дух'}
deal_status = {'1' : ['⚪️ Выключить', 'off_', '🔵'], '0' : ['🔵 Включить', 'on_', '⚪️']}
dict_fiat_reverse = {'payer' : 'Payeer', 'ym' : 'YandexMoney', 'tinkof' : 'Tinkoff', 'qiwi' : 'Qiwi', 'sber' : 'Сбербанк', 'web': 'WebMoney'}
dict_fiat = {'Payeer' : 'payer', 'YandexMoney' : 'ym', 'Tinkoff' : 'tinkof', 'Qiwi' : 'qiwi', 'Сбербанк' : 'sber', 'WebMoney' : 'web'}

block_dict = {'0' : ['Заблокировать', 'block_', '1'], '1' : ['Разблокировать', 'unblock_', '0']}
reverse_type = {'sell' : 'buy', 'buy' : 'sell'}

wallet_dic = ['RUB', 'BYN', 'USD', 'EUR', 'UAH', 'KZT']
sources = {'cmc' : ['CoinMarketCap', 'coinmarketcap.com', 'cmc']}

sources_dic = [['CoinMarketCap', 'coinmarketcap.com', 'cmc']]

bot = telebot.TeleBot('713926081:AAHlZWIjOV4_MDuujrS3CUme-SmUbJAYuUY')

def id_generator(size = 10, chars = string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def back_markup(type, callback):
	reply_markup = types.InlineKeyboardMarkup()
	if type == 'markup':
		reply_markup.add(types.InlineKeyboardButton(text = '« Назад', callback_data = callback))
	elif type == 'button':
		reply_markup = types.InlineKeyboardButton(text = '« Назад', callback_data = callback)
	return reply_markup

def bd(sql):
	conn = sqlite3.connect('./bitcoin.sqlite3')
	curr = conn.cursor()
	data = curr.execute(sql).fetchall()
	conn.commit()
	conn.close()
	return data

#сделать чтоб сразу в функции отнимались все балансы и задолженности
#-
#Заблокировать#Перевести#Вывести
#-
#Выписка баланса не отобразило моей операции по зачислению средств.
#-
#И создать ордер может только тот, у кого положительный баланс. На пример если у него на балансе нет 1000₽. То он не может сделать ордер на такую сумму

def send_email(email, code):
	smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
	smtpObj.starttls()
	smtpObj.login('maksimfedartsou@gmail.com','5Chvpxjt')
	smtpObj.sendmail('maksimfedartsou@gmail.com', email, code)
	smtpObj.quit()

def refresh_stat(id, stat):
	conn = sqlite3.connect('./bitcoin.sqlite3')
	curr = conn.cursor()
	id = str(id)
	data = curr.execute('SELECT * FROM stats WHERE id = ?', (id,)).fetchall()
	print(data)
	if data == [] and stat is None:
		password = id_generator()+id_generator()+id_generator()
		btc = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567').json()['address']
		curr.execute('INSERT INTO balances(id, balance, fresh, type, balance_id, address, pass) VALUES(?,?,?,?,?,?,?)', (id, 0, 0, 'btc', id_generator(), btc, password))
		conn.commit()
		eth = requests.post('https://api.blockcypher.com/v1/eth/main/addrs?token=710a115882b646caab0d3d69ca46898c').json()
		print(eth)
		password = eth['private']+','+eth['public']
		eth = eth['address']
		curr.execute('INSERT INTO balances(id, balance, fresh, type, balance_id, address, pass) VALUES(?,?,?,?,?,?,?)', (id, 0, 0, 'eth', id_generator(), eth, password))
		conn.commit()
		curr.execute('INSERT INTO stats(id, stat, time) VALUES(?,?,?)', (id, stat, time.time()))
		conn.commit()
		curr.execute('INSERT INTO pay_settings(id, wallet, source) VALUES(?,?,?)', (id, 'RUB', 'cmc'))
		conn.commit()
		curr.execute('INSERT INTO orders_status(id, status) VALUES(?, ?)', (id, '1'))
		conn.commit()
		curr.execute('INSERT INTO settings(id, reit, language, notifications, curriences) VALUES(?,?,?,?,?)', (id, 0, 'ru', 'off', 'not'))
		conn.commit()
		curr.execute('INSERT INTO users(id, user_id, time, status) VALUES(?,?,?,?)', (id, id_generator(), time.time(), '0'))
		conn.commit()
	elif data == [] and (stat[:6] == 'start_' or stat == 'see_deal' or stat[:18] == 'send_verification_'):
		print(help)
		password = id_generator()+id_generator()+id_generator()
		btc = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/new_address?password=klopman567').json()['address']
		curr.execute('INSERT INTO balances(id, balance, fresh, type, balance_id, address, pass) VALUES(?,?,?,?,?,?,?)', (id, 0, 0, 'btc', id_generator(), btc, password))
		conn.commit()
		eth = requests.post('https://api.blockcypher.com/v1/eth/main/addrs?token=710a115882b646caab0d3d69ca46898c').json()
		print(eth)
		password = eth['private']+','+eth['public']
		eth = eth['address']
		curr.execute('INSERT INTO balances(id, balance, fresh, type, balance_id, address, pass) VALUES(?,?,?,?,?,?,?)', (id, 0, 0, 'eth', id_generator(), eth, password))
		conn.commit()
		curr.execute('INSERT INTO stats(id, stat, time) VALUES(?,?,?)', (id, stat, time.time()))
		conn.commit()
		curr.execute('INSERT INTO pay_settings(id, wallet, source) VALUES(?,?,?)', (id, 'RUB', 'cmc'))
		conn.commit()
		curr.execute('INSERT INTO orders_status(id, status) VALUES(?, ?)', (id, '1'))
		conn.commit()
		if stat[:6] == 'start_':
			print(stat[6:])
			curr.execute('INSERT INTO users(id, user_id, time, refer, status) VALUES(?,?,?,?,?)', (id, id_generator(), time.time(), stat[6:], '0'))
		else:
			curr.execute('INSERT INTO users(id, user_id, time, status) VALUES(?,?,?,?)', (id, id_generator(), time.time(), '0'))
		curr.execute('INSERT INTO settings(id, reit, language, notifications, curriences) VALUES(?,?,?,?,?)', (id, 0, 'ru', 'off', 'not'))
	elif stat != None:
		curr.execute('UPDATE stats SET stat = ? WHERE id = ?', (stat, id,))
		curr.execute('UPDATE stats SET time = ? WHERE id = ?', (time.time(), id,))
	conn.commit()
	conn.close()
	if data != []:
		return data[0]

def settings_markup(id):
	lang = lang_dic[bd('SELECT * FROM settings WHERE id = "'+str(id)+'"')[0][2]]
	sound = sounds_dic[bd('SELECT * FROM settings WHERE id = "'+str(id)+'"')[0][3]]
	cu = curr_dic[bd('SELECT * FROM settings WHERE id = "'+str(id)+'"')[0][4]]
	reply_markup = types.InlineKeyboardMarkup()
	settings_dic = [['🔐 Двухфакторная защита', 'two_factor'], ['🎁 Реферальная система', 'referal'], ['🔤 Сменить язык бота: '+lang[0], 'lang_'+lang[1]], ['📊 Ваша статистика', 'stat'],
	['Уведомления '+sound[0], 'sound_'+sound[1]],  ['💳 Реквизиты', 'pays'], ['❓ Помощь', 'https://t.me/seepayhelpbot']]
	reply_markup = types.InlineKeyboardMarkup(1)
	reply_markup.add(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in settings_dic[:6]])
	reply_markup.add(*[types.InlineKeyboardButton(text = i[0], url = i[1]) for i in settings_dic[6:]])
	return reply_markup

def menu_markup():
	reply_markup = types.InlineKeyboardMarkup()
	menu_markup = [['📘 Купить', 'create_type_buy'], ['📕 Продать', 'create_type_sell'], ['📓 Настройки', 'pay_settings'], ['📚 Мои ордера', 'my_orders']]
	reply_markup.add(types.InlineKeyboardButton(text = 'Как пользоваться маркетом?', url = 'https://telegra.ph/Instrukciya-po-ispolzovaniyu-servisa-Seepay-01-16'))
	reply_markup.add(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in menu_markup[:2]])
	reply_markup.add(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in menu_markup[2:]])
	return reply_markup

def download(url, file_name):
	with open(file_name, "wb") as file:
		response = requests.get(url)
		file.write(response.content)

def koshelek_markup(id):
	user_data = bd('SELECT * FROM pay_settings WHERE id = "'+str(id)+'"')[0]
	balances = bd('SELECT * FROM balances WHERE id = "'+str(id)+'"')
	oma_balances = bd('SELECT * FROM oma_balances WHERE id = "'+str(id)+'"')[0][1]
	price_btc = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert='+user_data[1]+'&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote'][user_data[1]]['price']
	price_eth = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert='+user_data[1]+'&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][1]['quote'][user_data[1]]['price']
	print(str(price_btc)+' '+str(price_eth))
	btc_balance = check_btc_balance(balances[0][5])
	eth_balance = check_eth_balance(balances[1][5])
	answer = '🏧 Кошелёк:'
	answer += '\n\n<b>Bitcoin (BTC)</b>\nДоступно: <b>'+str(round(btc_balance, 6))+' BTC </b>('+str(round(btc_balance*price_btc, 2))+' '+user_data[1]+')\nУдержано: <b>'+str(round(float(balances[0][2])/price_btc, 6))+' BTC </b>('+str(balances[0][2])+' '+str(user_data[1])+')'
	answer += '\n\n<b>Ethereum (ETH)</b>\nДоступно: <b>'+str(round(eth_balance, 6))+' ETH </b>('+str(round(eth_balance*price_eth, 2))+' '+user_data[1]+')\nУдержано: <b>'+str(round(float(balances[1][2])/price_eth, 6))+' ETH </b>('+str(balances[1][2])+' '+str(user_data[1])+')'
	answer += '\n\n<b>Seepay Bonus (OMA)</b>\nДоступно: <b>'+str(oma_balances)+' OMA</b>'
	reply_markup = types.InlineKeyboardMarkup()
	koshelek_markup = [['➕ Пополнить', 'full_wallet'], ['➖ Вывести', 'out_wallet'],
	['🏷 Выписать чек', 'make_bill'], ['📑 Выписка', 'vipiska'], ['🔛 Обмен валют', 'wallet_change']]
	reply_markup.row(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in koshelek_markup[:2]])
	reply_markup.row(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in koshelek_markup[2:4]])
	reply_markup.row(*[types.InlineKeyboardButton(text = i[0], callback_data = i[1]) for i in koshelek_markup[4:]])
	return [reply_markup, answer]

def user_reit(id):
	users_num = len(bd('SELECT * FROM users WHERE refer = "'+id+'"'))
	if users_num >= 100 and users_num <= 500:
		reit = 0
		answer = ['Сержант', 0.25, 50, reit, users_num]
	elif users_num > 500 and users_num <= 1000:
		reit = 0
		answer = ['Солдат', 0.3, 100, reit, users_num]
	elif users_num > 1000 and users_num <= 5000:
		reit = 0
		answer = ['Эксперт', 0.35, 500, reit, users_num]
	elif users_num > 5000 and users_num <= 10000:
		reit = 0
		answer = ['Мастер', 0.4, 1000, reit, users_num]
	elif users_num > 10000:
		reit = 0
		answer = ['Легенда', 0.45, 2500, reit, users_num]
	else:
		reit = 0
		answer = ['Рядовой', 0.2, 0, reit, users_num]
	if id == '625139398':
		reit = 0
		answer = ['Легенда', 0.45, 2500, reit, users_num]
	return answer

def user_info(data):
	seller_data = bd('SELECT * FROM users INNER JOIN pay_settings using(id) WHERE id = "'+str(data[0])+'"')[0]
	seller_history = bd('SELECT * FROM history WHERE id = "'+str(data[0])+'"')
	good =  bd('SELECT * FROM reit WHERE id = "'+str(data[0])+'" AND type = "1"')
	bad =  bd('SELECT * FROM reit WHERE id = "'+str(data[0])+'" AND type = "0"')
	print(good)
	last_time = refresh_stat(data[0], None)[2]
	time_range = time.time() - float(last_time)
	if time_range > 86400:
		time_range = str(round((time.time() - float(last_time))/86400, 2)) + ' дней'
	elif time_range < 86400 and time_range > 3600:
		time_range = str(round((time.time() - float(last_time))/3600, 2)) + ' часов'
	elif time_range < 3600 and time_range > 300:
		time_range = str(round((time.time() - float(last_time))/60, 2)) + ' минут'
	else:
		time_range = 'только что'
	all_time = float(seller_data[2])
	all_range = time.time() - all_time
	if all_range > 86400:
		all_range = str(round((time.time() - float(all_time))/86400, 2)) + ' дней'
	elif all_range < 86400 and all_range > 3600:
		all_range = str(round((time.time() - float(all_time))/3600, 2)) + ' часов'
	elif all_range < 3600 and all_range > 300:
		all_range = str(round((time.time() - float(all_time))/60, 2)) + ' минут'
	else:
		all_range = 'только что'
	summ_sell = 0
	if len(seller_history) > 0:
		summ_sell = 0
		for i in seller_history:
			summ_sell += float(i[4])
		print(summ_sell)
	return [all_range, time_range, seller_data[1], seller_history, summ_sell, good, bad, seller_data[5]]

def user_smile(id):
	last_time = refresh_stat(str(id), None)[2]
	time_range = time.time() - float(last_time)
	smile = '🌕'
	if time_range > 86400:
		if round((time.time() - float(last_time))/86400) >= 7:
			smile = '🌑'
		elif round((time.time() - float(last_time))/86400) >= 5:
			smile = '🌘'
		elif round((time.time() - float(last_time))/86400) >= 3:
			smile = '🌗'
	elif time_range < 86400 and time_range > 3600:
		smile = '🌖'
	return smile

def user_information(id):
	last_time = refresh_stat(str(id), None)[2]
	time_range = time.time() - float(last_time)
	if time_range > 86400:
		time_range = str((time.time() - float(last_time))/86400) + ' дней назад'
	elif time_range < 86400 and time_range > 3600:
		time_range = str((time.time() - float(last_time))/3600) + ' часов назад'
	elif time_range < 3600 and time_range > 300:
		time_range = str((time.time() - float(last_time))/60) + ' минут назад'
	else:
		time_range = 'только что'
	reply_markup = types.InlineKeyboardMarkup()
	rows = bd('SELECT * FROM users AS a INNER JOIN stats ON stats.id = a.id INNER JOIN balances ON balances.id = a.id WHERE a.id = "'+str(id)+'"')
	print(rows)
	reply_markup.add(*[types.InlineKeyboardButton(text = dict_wallet_reverse[i[11]]+': '+str(i[9]), callback_data = 'balance_change_'+i[12]) for i in rows])
	reply_markup.add(types.InlineKeyboardButton(text = block_dict[str(rows[0][4])][0], callback_data = str(block_dict[str(rows[0][4])][1])+str(id)))
	reply_markup.add(back_markup('button', 'admin'))
	answer = '<a href = "tg://user?id='+str(id)+'">Написать сообщение</a>\n\n'+\
	'<b>Последний визит: </b>'+time_range
	return [answer, reply_markup]

def send_btc(to, amount, from_address):
	print(to+' '+str(amount)+' '+from_address)
	data = bd('SELECT * FROM admin')[0]
	fee = data[2]
	if data[3] != 0:
		percent = 1/float(data[3])
	else:
		percent = 1
	amount = float(amount) * 100000000# * percent
	print(amount)
	print(percent)
	final_ammount = int(amount - float(fee))
	print(final_ammount)
	response = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/payment?password=klopman567&to='+\
	str(to)+'&amount='+str(final_ammount)+'&from='+str(from_address)+'&fee='+str(fee))
	print(response.json())
	if 'success' in response.json():
		status = 'success'
	elif 'error' in response.json():
		status = 'error'
	return status

def check_btc_balance(address):
	balance = requests.get('http://localhost:3000/merchant/e91fcebd-ad39-44fd-94af-8cae0f22417e/address_balance?password=klopman567&address='+\
	str(address)).json()['balance']
	if balance != 0:
		balance /= 100000000
	return balance

def check_eth_balance(address):
	r = requests.get('https://api.blockcypher.com/v1/eth/main/addrs/'+address+'/balance').json()['final_balance'] / 1000000000000000000
	if r != 0:
		r /= 1000000000000000000
	return r

def send_eth(address, address1, value):
	#С которого адреса с того и signature
	data = bd('SELECT * FROM admin')[0]
	if data[3] != 0:
		percent = 1/float(data[3])
	else:
		percent = 1
	signatures = bd('SELECT * FROM balances WHERE address = "'+address+'"')[0][6].split(',')[1]
	data = '{"inputs":[{"addresses": ['+address+']}],"outputs":[{"addresses": ['+address1+'], "value": '+str(float(value) * percent)+'}]}'
	r = requests.post('https://api.blockcypher.com/v1/eth/main/txs/new?token=710a115882b646caab0d3d69ca46898c', params = params, data = data).json()
	print(r)
	tx = r['tx']
	data = '{"tx": '+tx+', "tosign": [ "'+tx['tosign']+'" ], "signatures": [ "'+signatures+'" ]}'
	response = requests.post('https://api.blockcypher.com/v1/eth/main/txs/send?token=710a115882b646caab0d3d69ca46898c', params=params, data=data)
	print(response.json())
	#201 code - success
	return response.status_code

def see_deal(id, user_id):
	see_dict = {'sell' : ' Продажа ', 'buy' : ' Покупка '}
	reply_markup = types.InlineKeyboardMarkup()
	data = bd('SELECT * FROM orders WHERE order_id = "'+str(id)+'"')[0]
	order_data = user_info(data)
	price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=RUB&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote']['RUB']['price']
	user_data = user_reit(str(data[0]))
	answer = '#'+data[1]+see_dict[data[2]]+dict_wallet_reverse[data[3]]+'⬅️ за '+dict_fiat_reverse[data[4]]
	if int(data[0]) == user_id:
		answer += '\n\nКурс '+dict_wallet_reverse[data[3]]+': <b>'+data[5]+'</b> '+order_data[7]+\
		'\n\nДопустимые лимиты ордера:'+\
		'\n<b>от </b>'+str(data[6])+' '+order_data[7]+'<b> до </b>'+str(data[7])+' '+order_data[7]+\
		'\n\nСсылка на сделку:'+\
		'\nhttps://t.me/seepaybot?start=D'+data[1]
		reply_markup.add(types.InlineKeyboardButton(text = deal_status[data[9]][0], callback_data = 'turn_'+deal_status[data[9]][1]+data[1]),
						types.InlineKeyboardButton(text = '📃 Условия', callback_data = 'create_description_'+data[1]))
		reply_markup.add(back_markup('button', 'my_orders'), types.InlineKeyboardButton(text = '❌ Удалить', callback_data = 'delete_'+data[1]))
	else:
		answer += '\n\nЗа '+str(order_data[0])+' /'+order_data[2]+' провел '+str(len(order_data[3]))+' успешных сделок на сумму '+str(round(order_data[4], 4))+' '+dict_wallet_reverse[data[3]]+\
		'\n\nРейтинг: '+str(user_data[0])+\
		'\nОтзывы: ('+str(len(order_data[5]))+')👍 ('+str(len(order_data[6]))+')👎'+\
		'\n\nБыл в сети: '+str(order_data[1])+' назад'+\
		'\n\n<pre>В этом объявлении вы можете купить '+dict_wallet_reverse[data[3]]+' по курсу '+str(data[5])+\
		'\nНа сумму от '+str(data[6])+' до '+str(data[7])+' '+order_data[7]+'</pre>'#+' или от '+str(round(float(data[6])/price, 4))+' до '+str(round(float(data[7])/price, 4))+' '+dict_wallet_reverse[data[3]]+'</pre>'
		reply_markup.add(types.InlineKeyboardButton(text = 'Открыть сделку', callback_data = 'open_deal_'+data[1]))
		reply_markup.add(types.InlineKeyboardButton(text = '✍ Связь с продавцом', callback_data = 'connect_'+data[0]))
		reply_markup.add(back_markup('button', 'fiat_back'))
	if data[8] is not None:
		answer += '\n\n<pre>'+str(data[8])+'</pre>'
	return [answer, reply_markup]

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

@bot.message_handler(commands = ['start'])
def start(message):
	start_markup = types.ReplyKeyboardMarkup(True, False)
	start_markup.add('🌐 Маркет')
	start_markup.add('🖥 Кабинет', '💼 Кошелёк')
	step = message.text[7:]
	if message.text[:6] == '/start' and message.text != '/start' and message.text[7:].isdigit() is False:
		if step[:11] == 'bill_obnal_':
			answer = 'Пришлите код'
			stat = 'send_verification_'+step[11:]
			reply_markup = back_markup('markup', 'menu')
		elif step[:1] == 'D':
			data = see_deal(step[1:], message.chat.id)
			answer = data[0]
			reply_markup = data[1]
			stat = 'see_deal'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, stat)
	else:
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Приветствую, '+message.chat.first_name+'!',
		reply_markup = start_markup)
		answer = '''seepaybot - P2P маркет криптовалют. Мультивалютный кошелек с возможностью обмена. Уникальный криптовалютный аукцион.\n'''+\
		'''Подписывайтесь на @Seepay, чтобы быть в курсе всех новостей бота.'''
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Support', url = 'https://t.me/SeepayHelpBot'),
						types.InlineKeyboardButton(text = 'FAQ', url = 'https://telegra.ph/Instrukciya-po-ispolzovaniyu-servisa-Seepay-01-16'))
		reply_markup.add(types.InlineKeyboardButton(text = '📘 Купить', callback_data = 'create_type_buy'),
						types.InlineKeyboardButton(text = '📕Продать', callback_data = 'create_type_sell'))
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup)
		refresh_stat(message.chat.id, None)
		if step.isdigit():
			stat = 'start_'+str(step)
			refresh_stat(message.chat.id, stat)

@bot.message_handler(content_types = ['text'])
def text(message):
	if message.text == '🌐 Маркет':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'В этом разделе вы можете покупать/продавать криптовалюту у других пользователей, используя наиболее удобную платежную систему.',
		reply_markup = menu_markup())

	elif message.text == '🖥 Кабинет':
		bot.send_message(
		chat_id = message.chat.id,
		text = '🛠 Выберите настройки, которые хотите изменить',
		reply_markup = settings_markup(message.chat.id))

	elif message.text == '💼 Кошелёк':
		email = bd('SELECT * FROM email WHERE id = "'+str(message.chat.id)+'"')
		reply_markup = back_markup('markup', 'menu')
		if email == []:
			data = koshelek_markup(message.chat.id)
			reply_markup = data[0]
			answer = data[1]
			stat = 'Complete'
		else:
			answer = 'Введите код верификации, отправленный на: ****'+email[0][1][4:]
			code = id_generator()[:4]
			send_email(email[0][1], code)
			stat = 'koshelek_'+code
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, stat)

	elif message.text == 'admin' and (message.chat.id == ADMIN or message.chat.id == 230952777):
		print(message.text)
		data = bd('SELECT * FROM admin')[0]
		admin_markup = types.InlineKeyboardMarkup()
		admin_markup.add(types.InlineKeyboardButton(text = 'Изменить комиссию: '+str(data[2]), callback_data = 'satoshi_change'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Информация о пользователе', callback_data = 'user_info'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Комиссия BTC: '+str(data[3])+'%', callback_data = 'btc_change'),
						types.InlineKeyboardButton(text = 'Комиссия ETH: '+str(data[4])+'%', callback_data = 'eth_change'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Рассылка всем', callback_data = 'send_message'),
						types.InlineKeyboardButton(text = 'Рассылка одному', callback_data = 'send_message_one'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Блокировка пользователя', callback_data = 'block_user'))
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Админка',
		reply_markup = admin_markup)

	elif message.text == '❌ Отмена':
		start_markup = types.ReplyKeyboardMarkup(True, False)
		start_markup.add('🌐 Маркет')
		start_markup.add('🖥 Кабинет', '💼 Кошелёк')
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Готово',
		reply_markup = start_markup,
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, 'Done')

	elif refresh_stat(message.chat.id, None)[1][:9] == 'koshelek_':
		code = refresh_stat(message.chat.id, None)[1][9:]
		reply_markup = back_markup('markup', 'menu')
		if code == message.text:
			data = koshelek_markup(message.chat.id)
			answer = data[1]
			reply_markup = data[0]
		else:
			answer = 'Код не верный'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif refresh_stat(message.chat.id, None)[1][:18] == 'send_verification_':
		id = refresh_stat(message.chat.id, None)[1][18:]
		data = bd('SELECT * FROM check_data WHERE check_id = "'+id+'"')[0]
		reply_markup = types.InlineKeyboardMarkup()
		if data[6] == '0':
			if data[4] == message.text:
				user_wallet = bd('SELECT * FROM balances WHERE id = "'+str(message.chat.id)+'" AND type = "'+data[2]+'"')[0]
				price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=RUB&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote']['RUB']['price']
				response = send_btc(user_wallet[5], float(data[3])/price, data[7])
				if response == 'success':
					answer = 'Средства в размере '+str(round(float(data[3])/price, 5))+'BTC переведены на ваш кошелек'
					reply_markup.add(types.InlineKeyboardButton(text = 'В кошелек »', callback_data = 'full_'+data[2]))
					refresh_stat(message.chat.id, 'Complete')
					bot.send_message(data[0], 'Ваш чек ID: '+data[1]+' обналичили', reply_markup = reply_markup)
					bd('UPDATE balances SET fresh = fresh - "'+str(data[3])+'" WHERE type = "'+str(data[2])+'" AND id = "'+str(data[0])+'"')
				else:
					answer = 'Упс, что-то пошло не так'
			else:
				answer = 'Неверный код, попробуйте еще раз'
				reply_markup.add(back_markup('button', 'menu'))
		elif data[6] == '1':
			answer = 'Упс, кажется кто-то другой обналичил чек'
			reply_markup.add(back_markup('button', 'menu'))
			refresh_stat(message.chat.id, 'Complete')
			bd('UPDATE users SET refer = "'+str(data[0])+'" WHERE id = "'+str(message.chat.id)+'"')
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif refresh_stat(message.chat.id, None)[1][:4] == 'add_':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Адресс <b>'+message.text+'</b> успешно добавлен',
		reply_markup = back_markup('markup', 'change_'+refresh_stat(message.chat.id, None)[1][4:]),
		parse_mode = 'HTML')
		bd('INSERT INTO user_pays(id, wallet_id, adress, type) VALUES("'+str(message.chat.id)+'","'+id_generator()+'","'+str(message.text)+'","'+refresh_stat(message.chat.id, None)[1][4:]+'")')

	elif refresh_stat(message.chat.id, None)[1] == 'block_user':
		bd('UPDATE users SET status = "1" WHERE id = "'+message.text+'"')
		data = user_information(message.text)
		reply_markup = data[1]
		bot.send_message(
		chat_id = message.chat.id,
		text = '<b>Пользователь заблокирован</b>\n\n'+data[0],
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif refresh_stat(message.chat.id, None)[1][:7] == 'create_':
		stap = refresh_stat(message.chat.id, None)[1][7:]
		reply_markup = types.InlineKeyboardMarkup()
		if stap[:5] == 'fiat_':
			if message.text.isdigit() and float(message.text) > 0:
				answer = 'Введите диапазон цен, с которыми вы готовы работать.\n<b>Пример: 1000-10000</b>'
				sql = 'UPDATE time_orders SET curs = "'+message.text+'" WHERE id = "'+str(message.chat.id)+'"'
				stat = 'create_range'
			else:
				answer = 'Введите допустимое значение для курса'
		elif stap[:5] == 'range':
			range = message.text.replace(' ', '')
			range = range.split('-')
			if len(range) == 2 and range[0].isdigit() and range[1].isdigit():
				answer = 'Ордер создан, вы можете перейти в него'
				stat = 'None'
				sql = 'DELETE FROM time_orders WHERE id = "'+str(message.chat.id)+'"'
				data = bd('SELECT * FROM time_orders WHERE id = "'+str(message.chat.id)+'"')[0]
				bd('INSERT INTO orders(id, order_id, type, cript, fiat, curs, range, range1, status) VALUES("'+data[0]+'", "'+data[1]+'", "'+data[2]+'", "'+data[3]+'", "'+data[4]+'", "'+data[5]+'", "'+range[0]+'", "'+range[1]+'", "1")')
				reply_markup.add(types.InlineKeyboardButton(text = 'К ордеру »', callback_data = 'see_'+data[1]))
				reply_markup.add(back_markup('button', 'menu'))
			else:
				'Введите допустимое значение диапазона цен в формате:  <b>100-10000</b>'
		elif stap[:12] == 'description_':
			answer = 'Описание ордера изменено на: <pre>'+message.text+'</pre>'
			sql = 'UPDATE orders SET description = "'+str(message.text)+'" WHERE order_id = "'+stap[12:]+'"'
			reply_markup.add(back_markup('button', 'my_orders'), types.InlineKeyboardButton(text = 'К ордеру »', callback_data = 'see_'+stap[12:]))
			stat = 'Complete!'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		print(sql)
		bd(sql)
		refresh_stat(message.chat.id, stat)

	elif refresh_stat(message.chat.id, None)[1] == 'two_factor':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Введите код отправленный вам на e-mail: <b>'+str(message.text)+'</b>',
		reply_markup = back_markup('markup', 'settings'),
		parse_mode = 'HTML')
		code = id_generator()[:4]
		send_email(message.text, code)
		refresh_stat(message.chat.id, 'code_'+code+','+str(message.text))

	elif refresh_stat(message.chat.id, None)[1].split(',')[0][:5] == 'code_':
		data = refresh_stat(message.chat.id, None)[1].split(',')
		if data[0][5:] == message.text:
			answer = 'Двухфакторная аутентификация включена'
			bd('INSERT INTO email(id, email) VALUES("'+str(message.chat.id)+'", "'+data[1]+'")')
			stat = 'Complete'
		else:
			answer = 'Неверный код'
			stat = None
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_markup('markup', 'settings'))

	elif refresh_stat(message.chat.id, None)[1][:4] == 'out_':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Введите сумму для вывода:',
		reply_markup = back_markup('markup', refresh_stat(message.chat.id, None)[1]))
		refresh_stat(message.chat.id, 'this_out_'+message.text)
		bd('UPDATE time_history SET to_addrr = "'+str(message.text)+'" WHERE id = "'+str(message.chat.id)+'"')

	elif refresh_stat(message.chat.id, None)[1][:9] == 'this_out_':
		data = bd('SELECT * FROM time_history WHERE id = "'+str(message.chat.id)+'"')[0]
		from_address = bd('SELECT * FROM balances WHERE id = "'+str(message.chat.id)+'" AND type = "'+data[1]+'"')[0]
		price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=RUB&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote']['RUB']['price']
		if data[1] == 'btc':
			final_summ = check_btc_balance(from_address[5])*price - from_address[2]
			if final_summ >= float(message.text):
				response = send_btc(data[2], float(message.text)/price, from_address[5])
			else:
				response = 666
		elif data[1] == 'eth':
			final_summ = (check_eth_balance(from_address[5]) - from_address[2])/price
			if final_summ >= float(message.text):
				response = send_eth(from_address[5], data[2], message.text)
			else:
				response = 666
		print(response)
		if response == 201 or response == 'success':
			answer = 'Средства в размере: '+str(message.text)+' переведены на '+dict_wallet_reverse[data[1]]+' кошелек <b>'+data[2]+'</b>'
			sql = 'UPDATE time_history SET summ = "'+str(message.text)+'" WHERE id = "'+str(message.chat.id)+'"'
		elif response == 666:
			answer = 'Сумма превышает доступную сумму на балансе'
			sql = 'SELECT * FROM users'
		else:
			answer = 'Средства не удалось перевести, попробуйте позже'
			sql = 'SELECT * FROM users'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_markup('markup', 'menu'),
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, 'Complete!')
		bd(sql)

	elif refresh_stat(message.chat.id, None)[1][:6] == 'check_':
		check_id = id_generator()
		code = id_generator()[:4]
		wallet = refresh_stat(message.chat.id, None)[1][6:]
		answer = 'Чек создан\n\n<b>Сумма: </b>'+str(message.text)+'\n<b>Валюта: </b>'+dict_wallet_reverse[wallet]+'\n<b>Код: </b>'+code+\
		'\n\n<b>Ссылка на чек: </b> https://t.me/seepaybot?start=bill_obnal_'+check_id+'\n\n<pre>Не сообщайте код, кроме лица которому предназначен этот чек - никому</pre>'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back_markup('markup', 'menu'),
		parse_mode = 'HTML')
		from_address = bd('SELECT * FROM balances WHERE id = "'+str(message.chat.id)+'" AND type = "'+wallet+'"')[0][5]
		bd('INSERT INTO check_data(id, check_id, wallet, summ, code, time, status, from_address) VALUES("'+str(message.chat.id)+'","'+check_id+'","'+wallet+'","'+str(message.text)+'","'+code+'","'+str(time.time())+'", "0", "'+from_address+'")')
		bd('UPDATE balances SET fresh = fresh + "'+str(message.text)+'" WHERE id = "'+str(message.chat.id)+'" AND type = "'+wallet+'"')
		refresh_stat(message.chat.id, 'Complete!')

	elif refresh_stat(message.chat.id, None)[1][:10] == 'open_deal_':
		data = bd('SELECT * FROM orders WHERE order_id = "'+refresh_stat(message.chat.id, None)[1][10:]+'"')[0]
		seller_data = bd('SELECT * FROM users WHERE id = "'+data[0]+'"')[0]
		user_data = bd('SELECT * FROM users WHERE id = "'+str(message.chat.id)+'"')[0]
		balance_cli_data = bd('SELECT * FROM balances WHERE id = "'+str(message.chat.id)+'" AND type = "'+data[3]+'"')[0]
		balance_ord_data = bd('SELECT * FROM balances WHERE id = "'+data[0]+'" AND type = "'+data[3]+'"')[0]
		reply_markup = types.InlineKeyboardMarkup()
		if (float(message.text) >= float(data[6])) and (float(message.text) <= float(data[7])):
			if data[3] == 'btc':
				final_balance = check_btc_balance(balance_cli_data[5]) - balance_cli_data[2]
				final_ord_balance = check_btc_balance(balance_ord_data[5]) - balance_cli_data[2]
				print(final_balance)
			elif data[3] == 'eth':
				final_balance = check_eth_balance(balance_cli_data[5]) - balance_cli_data[2]
				final_ord_balance = check_eth_balance(balance_ord_data[5]) - balance_cli_data[2]
				print(final_balance)
			if final_ord_balance >= final_balance:
				print('help')
				answer = 'Мы отправили пользователю /'+seller_data[1]+' преложение о вашей сделке на сумму: <b>'+str(message.text)+'</b>, сделка отменяется если он в течении 5 минут не появится'
				send_markup = types.InlineKeyboardMarkup()
				send_markup.add(types.InlineKeyboardButton(text = 'Принять »', callback_data = 'accept_'+data[1]),
				types.InlineKeyboardButton(text = 'Отклонить', callback_data = 'declaine_'+data[1]))
				bot.send_message(
				chat_id = data[0],
				text = 'Пользователь /'+user_data[1]+' хочет провести с вами сделку на сумму: <b>'+str(message.text)+'</b>, принять?',
				reply_markup = send_markup,
				parse_mode = 'HTML')
				reply_markup.add(types.InlineKeyboardButton(text = 'Отменить сделку', callback_data = 'cancel_deal_'+data[1]))
				reply_markup.add(back_markup('button', 'see_'+data[1]))
				bd('DELETE FROM deals WHERE order_id = "'+data[1]+'" AND first = "'+str(message.chat.id)+'" AND second = "'+data[0]+'"')
				bd('INSERT INTO deals(order_id, first, second, summ, fiat, cript) VALUES("'+data[1]+'", "'+str(message.chat.id)+'", "'+data[0]+'", "'+str(message.text)+'", "'+data[4]+'", "'+data[3]+'")')
			elif final_balance > final_ord_balance:
				answer = 'Ваша сумма превышает сумму на балансе партнера'
			else:
				answer = 'У вас недостаточно доступных средств'
		else:
			answer = 'Не в промежутке'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif refresh_stat(message.chat.id, None)[1] == 'user_info':
		data = user_information(message.text)
		bot.send_message(
		chat_id = message.chat.id,
		text = data[0],
		reply_markup = data[1],
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, 'Complete')

	elif refresh_stat(message.chat.id, None)[1] == 'send_message':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Сообщение скоро будет доставлено всем пользователям',
		reply_markup = back_markup('markup', 'admin'))
		refresh_stat(message.chat.id, 'Complete')
		bd('UPDATE admin SET send_status = "'+message.text+'"')

	elif refresh_stat(message.chat.id, None)[1][:15] == 'balance_change_':
		id = refresh_stat(message.chat.id, None)[1][15:]
		data = bd('SELECT * FROM balances WHERE balance_id = "'+id+'"')[0]
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Да, изменить', callback_data = 'yes_change_'+id),
						types.InlineKeyboardButton(text = 'Отмена', callback_data = 'no_cancel_'+id))
		reply_markup.add(back_markup('button', 'balance_change_'+id))
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Вы хотите изменить: '+str(data[1])+' на '+str(message.text)+'\n'+dict_wallet_reverse[data[3]]+' адресса: '+data[5],
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		refresh_stat(message.chat.id, message.text)

	elif refresh_stat(message.chat.id, None)[1] == 'send_message_one':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Пришлите сообщение, можете использовать HTML теги:\n*<b>Жирный</b>*\n_<i>Курсив</i>_\n`<pre>Код</pre>`',
		reply_markup = back_markup('markup', 'send_message_one'),
		parse_mode = 'Markdown')
		refresh_stat(message.chat.id, 'send_message_'+message.text)

	elif refresh_stat(message.chat.id, None)[1][:13] == 'send_message_':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Сообщение добавлено',
		reply_markup = back_markup('markup', 'admin'))
		data = refresh_stat(message.chat.id, None)[1][13:]
		bot.send_message(
		chat_id = data,
		text = message.text,
		parse_mode = 'HTML')

	elif refresh_stat(message.chat.id, None)[1] == 'satoshi_change':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Комиссия изменена на: '+str(message.text)+' сатошей',
		reply_markup = back_markup('markup', 'admin'))
		bd('UPDATE admin SET satoshi = "'+str(message.text)+'"')
		refresh_stat(message.chat.id, 'Complete')

	elif refresh_stat(message.chat.id, None)[1] == 'eth_change' or refresh_stat(message.chat.id, None)[1] == 'btc_change':
		sql_dict = {'eth_change' : 'UPDATE admin SET percent_eth = "'+str(message.text)+'"', 'btc_change' : 'UPDATE admin SET percent_btc = "'+message.text+'"'}
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Комиссия теперь составляет '+str(message.text)+'%',
		reply_markup = back_markup('markup', 'admin'))
		bd(sql_dict[refresh_stat(message.chat.id, None)[1]])
		refresh_stat(message.chat.id, 'Complete')

	elif refresh_stat(message.chat.id, None)[1][:8] == 'connect_':
		reply_markup = types.InlineKeyboardMarkup()
		seller_stat = refresh_stat(refresh_stat(message.chat.id, None)[1][8:], None)
		chat_id = refresh_stat(message.chat.id, None)[1][8:]
		if seller_stat[1] != 'connect_'+str(message.chat.id):
			answer = 'Вам сообщение: \n'+str(message.text)+'\nВступить в диалог?'
			reply_markup.add(types.InlineKeyboardButton(text = 'Да', callback_data = 'connect_'+str(message.chat.id)),
							types.InlineKeyboardButton(text = 'Нет', callback_data = 'hangdown_'+str(message.chat.id)))
		else:
			answer = str(message.text)
		bot.send_message(
		chat_id = chat_id,
		text = answer,
		reply_markup = reply_markup)

@bot.callback_query_handler(func = lambda call : True)
def callback(call):
	print(call.data)
	if call.data == 'buy':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = i, callback_data = 'buy_'+dict_wallet[i][0]) for i in dict_wallet])
		reply_markup.add(back_markup('button', 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Выберите криптовалюту, которую хотите купить:',
		reply_markup = reply_markup)

	elif call.data == 'my_orders' or call.data[:7] == 'delete_':
		if call.data[:7] == 'delete_':
			bd('DELETE FROM orders WHERE order_id = "'+call.data[7:]+'"')
		reply_markup = types.InlineKeyboardMarkup(1)
		rows = bd('SELECT * FROM orders_status INNER JOIN orders using(id) WHERE id = "'+str(call.message.chat.id)+'"')
		if len(rows) == 0:
			rows = bd('SELECT * FROM orders_status WHERE id = "'+str(call.message.chat.id)+'"')
		else:
			reply_markup.add(*[types.InlineKeyboardButton(text = triger_markup[i[10]][2]+' '+dict_wallet_reverse[i[4]]+' '+triger_markup[i[3]]+' '+dict_fiat_reverse[i[5]]+' '+i[6], callback_data = 'see_'+i[2]) for i in rows])
		print(rows)
		reply_markup.row(types.InlineKeyboardButton(text = triger_markup[rows[0][1]][0], callback_data = triger_markup[rows[0][1]][1]),
						types.InlineKeyboardButton(text = '➕ Создать ордер', callback_data = 'create_order'))
		reply_markup.row(types.InlineKeyboardButton(text = '⚙️ Настройки', callback_data = 'pay_settings'), back_markup('button', 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Внизу отображается список ваших ордеров покупки(📘) и продажи(📕) криптовалюты.',
		reply_markup = reply_markup)

	elif call.data == 'eth_change' or call.data == 'btc_change':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите процент для переводов',
		reply_markup = back_markup('markup', 'admin'))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data == 'admin' and (call.message.chat.id == ADMIN or call.message.chat.id == 230952777):
		print(call.data)
		data = bd('SELECT * FROM admin')[0]
		admin_markup = types.InlineKeyboardMarkup()
		admin_markup.add(types.InlineKeyboardButton(text = 'Изменить комиссию: '+str(data[2]), callback_data = 'satoshi_change'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Информация о пользователе', callback_data = 'user_info'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Комиссия BTC: '+str(data[3])+'%', callback_data = 'btc_change'),
						types.InlineKeyboardButton(text = 'Комиссия ETH: '+str(data[4])+'%', callback_data = 'eth_change'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Рассылка всем', callback_data = 'send_message'),
						types.InlineKeyboardButton(text = 'Рассылка одному', callback_data = 'send_message_one'))
		admin_markup.add(types.InlineKeyboardButton(text = 'Блокировка пользователя', callback_data = 'block_user'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Админка',
		reply_markup = admin_markup)

	elif call.data == 'satoshi_change':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Сейчас комиссия составляет: '+str(bd('SELECT * FROM admin')[0][2])+' сатошей, сколько она будет введите ниже',
		reply_markup = back_markup('markup', 'admin'))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data == 'full_wallet' or call.data == 'out_wallet' or call.data == 'make_bill':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = i, callback_data = wallet_work[call.data][1]+dict_wallet[i][0]) for i in dict_wallet])
		reply_markup.add(back_markup('button', 'koshelek'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = wallet_work[call.data][0],
		reply_markup = reply_markup)

	elif call.data == 'user_info':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите ID пользователя',
		reply_markup = back_markup('markup', 'admin'))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:8] == 'connect_':
		reply_markup = types.ReplyKeyboardMarkup(True, True)
		reply_markup.row('❌ Отмена')
		bot.send_message(
		chat_id = call.message.chat.id,
		text = 'Напишите ваше сообщение',
		reply_markup = reply_markup)
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:9] == 'hangdown_':
		reply_markup = back_markup('markup', 'menu')
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Готово',
		reply_markup = reply_markup)
		bot.send_message(
		chat_id = call.data[9:],
		text = 'Пользователь отказал вам в диалоге',
		reply_markup = reply_markup)

	elif call.data == 'send_message_one':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите ID человека',
		reply_markup = back_markup('markup', 'admin'))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:10] == 'user_info_':
		print(call.data)
		data = user_information(call.data[10:])
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = data[0],
		reply_markup = data[1],
		parse_mode = 'HTML')

	elif call.data == 'send_message':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Удалить предыдущее', callback_data = 'delete_last'))
		reply_markup.add(back_markup('button', 'admin'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите сообщение, можете использовать HTML теги:\n*<b>Жирный</b>*\n_<i>Курсив</i>_\n`<pre>Код</pre>`',
		reply_markup = reply_markup,
		parse_mode = 'Markdown')
		refresh_stat(call.message.chat.id, call.data)

	elif call.data == 'settings':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = '🛠 Выберите настройки, которые хотите изменить',
		reply_markup = settings_markup(call.message.chat.id))

	elif call.data == 'two_factor':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите ваш <b>e-mail</b>, чтоб включить двухфакторную аутентификацию',
		reply_markup = back_markup('markup', 'settings'),
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, call.data)

	elif call.data == 'delete_last':
		bot.answer_callback_query(call.id, 'Готово!')
		bd('UPDATE admin SET delete_status = "1"')

	elif call.data[:4] == 'yes_' or call.data[:3] == 'no_':
		balance_new = refresh_stat(call.message.chat.id, None)[1]
		if call.data[:11] == 'yes_change_':
			id = call.data[11:]
			answer = 'Баланс изменен на '+balance_new
			bd('UPDATE balances SET balance = "'+balance_new+'" WHERE balance_id = "'+call.data[11:]+'"')
		else:
			id = call.data[10:]
			answer = 'Баланс остался прежним'
		data = bd('SELECT * FROM balances WHERE balance_id = "'+id+'"')[0]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_markup('markup', 'user_info_'+data[0]),
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, 'Complete')

	elif call.data[:15] == 'balance_change_':
		data = bd('SELECT * FROM balances WHERE balance_id = "'+call.data[15:]+'"')[0]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = '<b>Текущий баланс: </b>'+str(data[1])+'\n<b>Удержано средств: </b>'+str(data[2])+'\n<b>'+dict_wallet_reverse[data[3]]+' адресс: </b>'+data[5]+'<pre>Пришлите новую сумму, чтоб обновить баланс</pre>',
		reply_markup = back_markup('markup', 'user_info_'+data[0]),
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:6] == 'block_' or call.data[:8] == 'unblock_':
		print(call.data)
		if call.data[6:] == 'user':
			answer = 'Пришлите ID пользователя'
			reply_markup = back_markup('markup', 'admin')
		elif call.data[:8] == 'unblock_':
			data = bd('UPDATE users SET status = "0" WHERE id = "'+call.data[8:]+'"')
			data = user_information(call.data[8:])
			answer = '<b>Пользователь разблокирован</b>\n\n'+data[0]
			reply_markup = data[1]
		else:
			data = bd('UPDATE users SET status = "1" WHERE id = "'+call.data[6:]+'"')
			data = user_information(call.data[6:])
			answer = '<b>Пользователь зблокирован</b>\n\n'+data[0]
			reply_markup = data[1]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:6] == 'check_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Введите сумму для чека',
		reply_markup = back_markup('markup', 'make_bill'))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:4] == 'out_':
		bd('DELETE FROM time_history WHERE id = "'+str(call.message.chat.id)+'"')
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.row(*[types.InlineKeyboardButton(text = i[2], callback_data = 'this_out_'+i[1]) for i in bd('SELECT * FROM user_pays WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+call.data[4:]+'"')])
		reply_markup.add(back_markup('button', 'out_wallet'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Введите '+dict_wallet_reverse[call.data[4:]]+' кошелек для вывода или выберите ниже:',
		reply_markup = reply_markup)
		refresh_stat(call.message.chat.id, call.data)
		bd('INSERT INTO time_history(id, out) VALUES("'+str(call.message.chat.id)+'", "'+call.data[4:]+'")')

	elif call.data[:10] == 'open_deal_':
		data = bd('SELECT * FROM orders WHERE order_id = "'+str(call.data[10:])+'"')[0]
		price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=RUB&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote']['RUB']['price']
		answer = 'Выберите сумму, на которую хотите совершить сделку.\n\nСумма должна быть от\n <b>'+str(data[6])+'</b> до <b>'+str(data[7])+' '+\
		dict_wallet_reverse[data[3]]+'</b> или \nот <b>'+str(round(float(data[6])/price, 4))+'</b> до <b>'+str(round(float(data[7]), 4))+' RUB</b>'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_markup('markup', 'see_'+call.data[10:]),
		parse_mode = 'HTML')
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:7] == 'accept_':
		data = bd('SELECT * FROM orders WHERE order_id = "'+call.data[7:]+'"')[0]
		cli_data = bd('SELECT * FROM deals WHERE order_id = "'+call.data[7:]+'"')[0]
		deal_data = bd('SELECT * FROM deals WHERE order_id = "'+call.data[7:]+'"')[0]
		edit_markup = types.InlineKeyboardMarkup()
		send_markup = types.InlineKeyboardMarkup()
		if data[2] == 'sell':
			sender_id = cli_data[1]
			bills = bd('SELECT * FROM user_pays WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+data[4]+'"')[0]
			answer_send = 'Пользователь /'+data[1]+' согласен провести с вами сделку\n\nПополните реквизиты: <b>'+bills[2]+'</b>\n\n<pre>Средства на время сделки замораживается, на кошельке продавца</pre>'
			answer_edit = 'Средства в размере: <b>'+str(cli_data[3])+'</b> заморожены на вашем счете. \n\nРеквизиты по которым поступит платеж: <b>'+bills[2]+'</b> '+dict_fiat_reverse[bills[3]]
			bd('UPDATE balances SET fresh = fresh + '+deal_data[3]+', balance = balance - '+deal_data[3]+' WHERE type = "'+cli_data[5]+'" AND id = "'+str(call.message.chat.id)+'"')
			send_markup.add(types.InlineKeyboardButton(text = 'Пополнил »', callback_data = 'fulled_'+data[1]))
		elif data[2] == 'buy':
			sender_id = deal_data[1]
			bills = bd('SELECT * FROM user_pays WHERE id = "'+str(sender_id)+'" AND type = "'+data[4]+'"')[0]
			answer_send = 'Средства в размере: <b>'+str(deal_data[3])+'</b> заморожены на вашем счете. \n\nРеквизиты по которым поступит платеж: <b>'+bills[2]+'</b> '+dict_fiat_reverse[bills[3]]
			answer_edit = 'Пополните реквизиты: <b>'+bills[2]+'</b>\n\n<pre>Средства на время сделки замораживается, на кошельке продавца</pre>'
			bd('UPDATE balances SET balance =  balance - '+deal_data[3]+', fresh = fresh + '+deal_data[3]+' WHERE type = "'+deal_data[5]+'" AND id = "'+sender_id+'"')
			edit_markup.add(types.InlineKeyboardButton(text = 'Пополнил »', callback_data = 'fulled_'+data[1]))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer_edit,
		reply_markup = edit_markup,
		parse_mode = 'HTML')
		bot.send_message(
		chat_id = sender_id,
		text = answer_send,
		reply_markup = send_markup,
		parse_mode = 'HTML')

	elif call.data[:7] == 'fulled_':
		order_data = bd('SELECT * FROM orders WHERE order_id = "'+call.data[7:]+'"')[0]
		data = bd('SELECT * FROM deals WHERE order_id = "'+call.data[7:]+'"')[0]
		send_markup = types.InlineKeyboardMarkup()
		edit_markup = types.InlineKeyboardMarkup()
		if order_data[2] == 'sell':
			bills = bd('SELECT * FROM user_pays WHERE id = "'+str(data[2])+'" AND type = "'+data[4]+'"')[0]
			answer_send = 'Пользователь пополнил счет на сумму: '+data[3]+' по вашим реквизитам: <b>'+bills[2]+'</b> '+dict_fiat_reverse[bills[3]]+'\nПодтвердите получение средств'
			answer_edit = 'Ждем подтверждения от продавца...'
			send_markup.add(types.InlineKeyboardButton(text = 'Получил', callback_data = 'granted_'+call.data[7:]))
			send_markup.add(types.InlineKeyboardButton(text = 'Долго, не получил', callback_data = 'notgranted_'+call.data[7:]))
			sender_id = data[2]
		elif order_data[2] == 'buy':
			bills = bd('SELECT * FROM user_pays WHERE id = "'+str(data[1])+'" AND type = "'+data[4]+'"')[0]
			answer_send = 'Пользователь пополнил счет на сумму: '+data[3]+' по вашим реквизитам: <b>'+bills[2]+'</b> '+dict_fiat_reverse[bills[3]]+'\nПодтвердите получение средств'
			answer_edit = 'Ждем подтверждения от продавца...'
			send_markup.add(types.InlineKeyboardButton(text = 'Получил', callback_data = 'granted_'+call.data[7:]))
			send_markup.add(types.InlineKeyboardButton(text = 'Долго, не получил', callback_data = 'notgranted_'+call.data[7:]))
			sender_id = data[1]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer_edit,
		reply_markup = edit_markup)
		bot.send_message(
		chat_id = sender_id,
		text = answer_send,
		reply_markup = send_markup,
		parse_mode = 'HTML')

	elif call.data[:8] == 'granted_':
		edit_markup = types.InlineKeyboardMarkup()
		send_markup = types.InlineKeyboardMarkup()
		data = bd('SELECT * FROM deals INNER JOIN orders using(order_id) WHERE order_id = "'+call.data[8:]+'"')[0]
		first_balance = bd('SELECT * FROM balances WHERE id = "'+data[1]+'" AND type = "'+data[5]+'"')[0]
		second_balance = bd('SELECT * FROM balances WHERE id = "'+data[2]+'" AND type = "'+data[5]+'"')[0]
		price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert=RUB&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote']['RUB']['price']
		response = ''
		if data[7] == 'sell':
			sender_id = data[1]
			bd('UPDATE balances SET fresh =  fresh - '+data[3]+' WHERE id = "'+data[2]+'" AND type = "'+data[5]+'"')
			if data[5] == 'btc':
				response = send_btc(first_balance[5], float(data[3])/price, second_balance[5])
			elif data[5] == 'eth':
				response = send_eth(first_balance[5], second_balance[5], data[3])
			print(response)
			if response == 'success' or response == 201:
				answer_edit = 'Средства списаны с вашего кошелька'
				answer_send = 'Средства переведены на ваш кошелек'
				send_markup.add(types.InlineKeyboardButton(text = 'В кошелек »', callback_data = 'full_'+first_balance[3]))
				edit_markup.add(types.InlineKeyboardButton(text = '« В меню', callback_data = 'menu'))
			else:
				answer_edit = 'Проблема с платежной системой, попробуйте позже'
				answer_send = 'Проблема с платежной системой, попробуйте позже'
				edit_markup.add(types.InlineKeyboardButton(text = 'Еще раз', callback_data = call.data))
				send_markup.add(types.InlineKeyboardButton(text = 'Еще раз', callback_data = call.data))
		elif data[7] == 'buy':
			sender_id = data[2]
			bd('UPDATE balances SET fresh =  fresh - '+data[3]+' WHERE id = "'+data[1]+'" AND type = "'+data[5]+'"')
			if data[5] == 'btc':
				response = send_btc(second_balance[5], float(data[3])/price, first_balance[5])
			elif data[5] == 'eth':
				response = send_eth(second_balance[5], first_balance[5], data[3])
			print(response)
			if response == 'success' or response == 201:
				answer_send = 'Средства переведены на ваш кошелек'
				answer_edit = 'Средства списаны с вашего кошелька'
				send_markup.add(types.InlineKeyboardButton(text = 'В кошелек »', callback_data = 'full_'+second_balance[3]))
				edit_markup.add(types.InlineKeyboardButton(text = '« В меню', callback_data = 'menu'))
			else:
				answer_send = 'Проблемы с платежной системой, попробуйте позже'
				answer_edit = 'Проблемы с платежной системой, попробуйте позже'
				edit_markup.add(types.InlineKeyboardButton(text = 'Еще раз', callback_data = call.data))
				send_markup.add(types.InlineKeyboardButton(text = 'Еще раз', callback_data = call.data))
		if response == 'success' or response == 201:
			edit_markup.row(types.InlineKeyboardButton(text = '👍', callback_data = 'mark_5_'+str(sender_id)),types.InlineKeyboardButton(text = '😌', callback_data = 'mark_4_'+str(sender_id)),
						types.InlineKeyboardButton(text = '😫', callback_data = 'mark_3_'+str(sender_id)),types.InlineKeyboardButton(text = '😡', callback_data = 'mark_2_'+str(sender_id)),
						types.InlineKeyboardButton(text = '💩', callback_data = 'mark_1_'+str(sender_id)))
			send_markup.row(types.InlineKeyboardButton(text = '👍', callback_data = 'mark_5_'+str(call.message.chat.id)),types.InlineKeyboardButton(text = '😌', callback_data = 'mark_4_'+str(call.message.chat.id)),
						types.InlineKeyboardButton(text = '😫', callback_data = 'mark_3_'+str(call.message.chat.id)),types.InlineKeyboardButton(text = '😡', callback_data = 'mark_2_'+str(call.message.chat.id)),
						types.InlineKeyboardButton(text = '💩', callback_data = 'mark_1_'+str(call.message.chat.id)))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer_edit,
		reply_markup = edit_markup,
		parse_mode = 'HTML')
		bot.send_message(
		chat_id = sender_id,
		text = answer_send,
		reply_markup = send_markup,
		parse_mode = 'HTML')

	elif call.data[:11] == 'notgranted_':
		reply_markup = back_markup('markup', 'admin')
		data = bd('SELECT * FROM deals INNER JOIN orders using(order_id) WHERE order_id = "'+call.data[11:]+'"')[0]
		user_pays = bd('SELECT * FROM user_pays WHERE id = "'+data[2]+'" AND type = "'+data[4]+'"')[0]
		answer = 'Диспут направлен администратору'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		bot.send_message(
		chat_id = data[1],
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		disput_markup = types.InlineKeyboardMarkup()
		disput_markup.add(types.InlineKeyboardButton(text = 'Ср-ва переведены', callback_data = 'funds_granted_'+call.data[11:]))
		disput_markup.add(types.InlineKeyboardButton(text = 'Ср-ва не переведены', callback_data = 'funds_not_granted_'+call.data[11:]))
		answer = 'Открыт диспут: \n\n'
		if data[7] == 'buy':
			answer += '<b>Продавец: </b><a href = "tg://user?id='+str(data[2])+'">Написать сообщение</a>'
			answer += '\n<b>Покупатель: </b><a href = "tg://user?id='+str(data[1])+'">Написать сообщение</a>'
		elif data[7] == 'sell':
			answer += '<b>Продавец: </b><a href = "tg://user?id='+str(data[1])+'">Написать сообщение</a>'
			answer += '\n<b>Покупатель: </b><a href = "tg://user?id='+str(data[2])+'">Написать сообщение</a>'
		answer += '\n\n<b>Сумма: </b>'+str(data[3])
		answer += '\n<b>Крипта: </b>'+dict_wallet_reverse[data[5]]
		answer += '\n<b>Счет получателя: </b>'+data[2]+' '+dict_fiat_reverse[data[4]]
		if data[13] is not None:
			answer += '\n<b>Условия:</b>\n'
			andwer += data[13]
		bot.send_message(
		chat_id = ADMIN,
		text = answer,
		reply_markup = disput_markup,
		parse_mode = 'HTML')

	elif call.data[:6] == 'funds_':
		reply_markup = types.InlineKeyboardMarkup()
		if call.data[:14] == 'funds_granted_':
			data = bd('SELECT * FROM deals INNER JOIN orders using(order_id) WHERE order_id = "'+call.data[14:]+'"')[0]
			#ср-ва переведены:
			if data[7] == 'sell':
				#sell - btc переводятся покупателю то есть тот который в deal first
				bd('UPDATE balances SET fresh = fresh - "'+data[3]+'" WHERE id = "'+data[2]+'"')
				to_address = bd('SELECT * FROM balances WHERE id = "'+data[1]+'" AND type = "'+data[5]+'"')[0][5]
				from_address = bd('SELECT * FROM balances WHERE id = "'+data[2]+'" AND type = "'+data[5]+'"')[0][5]
			else:
				#buy - btc переводятся тому кто в ордере
				bd('UPDATE balances SET fresh = fresh - "'+data[3]+'" WHERE id = "'+data[1]+'"')
				from_address = bd('SELECT * FROM balances WHERE id = "'+data[1]+'" AND type = "'+data[5]+'"')[0][5]
				to_address = bd('SELECT * FROM balances WHERE id = "'+data[2]+'" AND type = "'+data[5]+'"')[0][5]
			response = send_btc(from_address, float(data[3])/float(data[10]), to_address)
			if response == 'success' or response == 201:
				answer = 'Средства переведены'
				reply_markup.add(back_markup('button', 'admin'))
			else:
				answer = 'Попробуйте позже'
				reply_markup.add(types.InlineKeyboardButton(text = 'Еще раз', callback_data = call.data))
		elif call.data[:18] == 'funds_not_granted_':
			data = bd('SELECT * FROM deals INNER JOIN orders using(order_id) WHERE order_id = "'+call.data[18:]+'"')[0]
			#ср-ва не переведены:
			answer = 'Готово'
			if data[7] == 'sell':
				#sell - btc размораживаются со счета кто в orders
				bd('UPDATE balances SET fresh = fresh - "'+data[3]+'" WHERE id = "'+data[1]+'"')
			else:
				#buy - btc размораживаются на счете того кто в deals first
				bd('UPDATE balances SET fresh = fresh - "'+data[3]+'" WHERE id = "'+data[2]+'"')
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_markup('markup', 'admin'))

	elif call.data[:5] == 'turn_':
		bot.answer_callback_query(call.id, 'Готово!')
		if call.data[5:8] == 'on_':
			sql = 'UPDATE orders SET status = "1" WHERE order_id = "'+call.data[8:]+'"'
			id = call.data[8:]
		else:
			sql = 'UPDATE orders SET status = "0" WHERE order_id = "'+call.data[9:]+'"'
			id = call.data[9:]
		print(id)
		bd(sql)
		data = bd('SELECT * FROM orders WHERE order_id = "'+id+'"')[0]
		print(data)
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = deal_status[data[9]][0], callback_data = 'turn_'+deal_status[data[9]][1]+id),
						types.InlineKeyboardButton(text = '📃 Условия', callback_data = 'create_description_'+data[1]))
		reply_markup.add(back_markup('button', 'my_orders'), types.InlineKeyboardButton(text = '❌ Удалить', callback_data = 'delete_'+data[1]))
		bot.edit_message_reply_markup(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		reply_markup = reply_markup)

	elif call.data[:4] == 'see_':
		data = see_deal(call.data[4:], call.message.chat.id)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = data[0],
		reply_markup = data[1],
		parse_mode = 'HTML')

	elif call.data[:9] == 'this_out_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Введите сумму для вывода:',
		reply_markup = back_markup('markup', refresh_stat(call.message.chat.id, None)))
		bd('UPDATE time_history SET to_addrr = "'+call.data[9:]+'" WHERE id = "'+str(call.message.chat.id)+'"')
		refresh_stat(call.message.chat.id, call.data)


	elif call.data[:5] == 'full_':
		data = bd('SELECT * FROM balances WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+call.data[5:]+'"')[0]
		user_wallet = bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0][1]
		if call.data[5:] == 'eth':
			balance = str(check_eth_balance(data[5]))
			quer = 'https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=ethereum:'+data[5]
			price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert='+user_wallet+'&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][0]['quote'][user_wallet]['price']
		else:
			balance = str(check_btc_balance(data[5]))
			quer = 'https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl=bitcoin:'+data[5]
			price = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?&convert='+user_wallet+'&CMC_PRO_API_KEY=39f0b609-7dbd-4577-81dd-6d89676c5a77').json()['data'][1]['quote'][user_wallet]['price']
		filename = './qr/'+id_generator()+'.png'
		download(quer, filename)
		send_file = open(filename, 'rb')
		bot.send_chat_action(call.message.chat.id, 'upload_photo')
		bot.send_photo(call.message.chat.id, send_file, disable_notification = True)
		answer = 'Для пополнения счета '+dict_wallet_reverse[call.data[5:]]+' используйте многоразовый адрес ниже:\n\n<b>'+\
		data[5]+'</b>\n\n<pre>Средства будут зачислены на ваш счет после 2 подтверждений сети.</pre>'
		answer += '\n\n<b>Доступно: </b>'+balance+' '+dict_wallet_reverse[call.data[5:]]+'\n<b>Удержано: </b>'+str(round(float(data[2])/price, 4))+' '+dict_wallet_reverse[call.data[5:]]
		bot.send_message(
		chat_id = call.message.chat.id,
		text = answer,
		reply_markup = back_markup('markup', 'full_wallet'),
		parse_mode = 'HTML')

	elif call.data == 'create_order':
		bd('DELETE FROM time_orders WHERE id = "'+str(call.message.chat.id)+'"')
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = '📘 Купить', callback_data = 'create_type_buy'),
						types.InlineKeyboardButton(text = '📕 Продать', callback_data = 'create_type_sell'))
		reply_markup.add(back_markup('button', 'my_orders'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Выберите тип ордера:',
		reply_markup = reply_markup)

	elif call.data == 'koshelek':
		data = koshelek_markup(call.message.chat.id)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = data[1],
		reply_markup = data[0],
		parse_mode = 'HTML')

	elif call.data[:7] == 'create_' or call.data == 'fiat_back':
		step = call.data[7:]
		reply_markup = types.InlineKeyboardMarkup(1)
		if step[:5] == 'type_':
			reply_markup.add(*[types.InlineKeyboardButton(text = i+'('+str(len(bd('SELECT * FROM orders WHERE type = "'+reverse_type[step[5:]]+'" AND cript = "'+dict_wallet[i][0]+'" AND status = "1" AND id IS NOT "'+str(call.message.chat.id)+'"')))+')', callback_data = 'create_wallet_'+dict_wallet[i][0]) for i in dict_wallet])
			answer = wallet_work[call.data]
			sql = 'INSERT INTO time_orders(id, order_id, type) VALUES("'+str(call.message.chat.id)+'", "'+id_generator()+'", "'+step[5:]+'")'
			refresh_stat(call.message.chat.id, step[5:])
		elif step[:7] == 'wallet_':
			result = bd('SELECT * FROM balances WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+step[7:]+'"')[0][5]
			if step[7:] == 'btc':
				response = check_btc_balance(result)
			else:
				response = check_eth_balance(result)
			if response == 0:
				answer = 'У вас на балансе нет '+dict_wallet_reverse[step[7:]]+'.'
				reply_markup.add(types.InlineKeyboardButton(text = '➕ Пополнить ', callback_data = 'full_'+step[7:]))
				refresh_stat(call.message.chat.id, 'Compete')
				sql = 'SELECT * FROM users'
			else:
				search_fiat = dict_fiat
				user_pays = bd('SELECT * FROM user_pays WHERE id = "'+str(call.message.chat.id)+'"')
				if refresh_stat(call.message.chat.id, None)[1] == 'sell':
					search_fiat = {dict_fiat_reverse[i[3]] : i[3] for i in user_pays}
					print(search_fiat)
				reply_markup.add(*[types.InlineKeyboardButton(text = i+'('+str(len(bd('SELECT * FROM orders WHERE type = "'+reverse_type[refresh_stat(call.message.chat.id, None)[1]]+'" AND cript = "'+step[7:]+'" AND fiat = "'+dict_fiat[i]+'" AND status = "1" AND id IS NOT "'+str(call.message.chat.id)+'"')))+')', callback_data = 'create_fiat_'+dict_fiat[i]) for i in search_fiat])
				answer = 'Выберите фиатную платёжную систему по которой вы будете работать при создании этого ордера.'
				sql = 'UPDATE time_orders SET cript = "'+step[7:]+'" WHERE id = "'+str(call.message.chat.id)+'"'
				refresh_data = refresh_stat(call.message.chat.id, None)[1]+','+step[7:]
				if refresh_stat(call.message.chat.id, None)[1] == 'sell' and len(user_pays) == 0:
					answer = 'Вам надо добавить платежные реквизиты, прежде чем вы сможете создавать или принимать участие в ордерах.'
					refresh_data = 'complete'
					sql = 'SELECT * FROM users'
					reply_markup.add(types.InlineKeyboardButton(text = '💳 Реквизиты', callback_data = 'pays'))
				refresh_stat(call.message.chat.id, refresh_data)
		elif step[:12] == 'description_':
			print(step[12:])
			answer = 'Пришлите новое описание для ордера'
			sql = 'SELECT * FROM users'
			reply_markup.add(back_markup('button', 'see_'+step[12:]))
			refresh_stat(call.message.chat.id, call.data)
		elif step[:5] == 'fiat_' or call.data == 'fiat_back':
			reply_markup = types.InlineKeyboardMarkup(1)
			user_pays = bd('SELECT * FROM user_pays WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+step[5:]+'"')
			user_curr = bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0]
			if call.data == 'fiat_back':
				order_data = bd('SELECT * FROM time_orders WHERE id = "'+str(call.message.chat.id)+'"')[0]
				reply_markup.add(*[types.InlineKeyboardButton(text = user_smile(i[0])+' '+i[5]+' '+bd('SELECT * FROM pay_settings WHERE id = "'+str(i[0])+'"')[0][1]+'('+i[6]+'-'+i[7]+' '+bd('SELECT * FROM pay_settings WHERE id = "'+str(i[0])+'"')[0][1]+')', callback_data = 'see_'+i[1]) for i in bd('SELECT * FROM orders WHERE type = "'+reverse_type[order_data[2]]+'" AND cript = "'+order_data[3]+'" AND fiat = "'+order_data[4]+'" AND status = "1" AND id IS NOT "'+str(call.message.chat.id)+'"')])
				print(order_data)
			else:
				order_data = refresh_stat(call.message.chat.id, None)[1].split(',')
				print(order_data)
				reply_markup.add(*[types.InlineKeyboardButton(text = user_smile(i[0])+' '+i[5]+' '+bd('SELECT * FROM pay_settings WHERE id = "'+str(i[0])+'"')[0][1]+'('+i[6]+'-'+i[7]+' '+bd('SELECT * FROM pay_settings WHERE id = "'+str(i[0])+'"')[0][1]+')', callback_data = 'see_'+i[1]) for i in bd('SELECT * FROM orders WHERE type = "'+reverse_type[order_data[0]]+'" AND cript = "'+order_data[1]+'" AND fiat = "'+step[5:]+'" AND status = "1" AND id IS NOT "'+str(call.message.chat.id)+'"')])
			answer = 'Введите свое значение курса для монеты'
			sql = 'UPDATE time_orders SET fiat = "'+step[5:]+'" WHERE id = "'+str(call.message.chat.id)+'"'
			refresh_stat(call.message.chat.id, call.data)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')
		bd(sql)

	elif call.data == 'menu':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'В этом разделе вы можете покупать/продавать криптовалюту у других пользователей, используя наиболее удобную платежную систему.',
		reply_markup = menu_markup())

	elif call.data == 'pays':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = i, callback_data = 'change_'+dict_fiat[i]) for i in dict_fiat])
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = '💳 Выберите валюту для добавления платежных реквизитов.',
		reply_markup = reply_markup)

	elif call.data[:7] == 'change_':
		reply_markup = types.InlineKeyboardMarkup()
		data = bd('SELECT * FROM user_pays WHERE id = "'+str(call.message.chat.id)+'" AND type = "'+call.data[7:]+'"')
		reply_markup.add(*[types.InlineKeyboardButton(text = i[2], callback_data = 'delete_'+i[1]) for i in data])
		answer = 'Список ваших адресов для <b>'+dict_fiat_reverse[call.data[7:]]+'</b>: \nЧтобы удалить адрес, нажмите на него.'
		reply_markup.add(types.InlineKeyboardButton(text = '➕ Добавить', callback_data = 'add_'+call.data[7:]))
		reply_markup.add(back_markup('button', 'pays'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data[:4] == 'add_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Пришлите новый адрес '+dict_fiat_reverse[call.data[4:]],
		reply_markup = back_markup('markup', 'change_'+call.data[7:]))
		refresh_stat(call.message.chat.id, call.data)

	elif call.data[:7] == 'wallet_':
		if call.data[:12] == 'wallet_this_':
			bot.answer_callback_query(call.id, 'Готово!')
			bd('UPDATE pay_settings SET wallet = "'+call.data[12:]+'" WHERE id = "'+str(call.message.chat.id)+'"')
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = '✅ '+i, callback_data = 'wallet_this_'+i) for i in wallet_dic if i == bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0][1]])
		reply_markup.add(*[types.InlineKeyboardButton(text = i, callback_data = 'wallet_this_'+i) for i in wallet_dic if i != bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0][1]])
		reply_markup.add(back_markup('button', 'pay_settings'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Выберете фиатную валюту, с которой вы работаете:',
		reply_markup = reply_markup)

	elif call.data[:6] == 'source':
		sourc = call.data[7:]
		if call.data[:12] == 'source_this_':
			bot.answer_callback_query(call.id, 'Готово!')
			bd('UPDATE pay_settings SET source = "'+call.data[12:]+'" WHERE id = "'+str(call.message.chat.id)+'"')
			sourc = call.data[12:]
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = '✅ '+i[0], callback_data = 'source_this_'+i[2]) for i in sources_dic if i[2] == bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0][2]])
		reply_markup.add(*[types.InlineKeyboardButton(text = i[0], callback_data = 'source_this_'+i[2]) for i in sources_dic if i[2] != bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0][2]])
		reply_markup.add(back_markup('button', 'pay_settings'))
		answer = 'Сейчас вы используете\n🔺 '+sources[sourc][0]+'\n'+sources[sourc][1]+'\nВыбрать источник актуального курса криптовалюты:'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup)

	elif call.data == 'pay_settings':
		data = bd('SELECT * FROM pay_settings WHERE id = "'+str(call.message.chat.id)+'"')[0]
		reply_markup = types.InlineKeyboardMarkup()
		print(data[2])
		reply_markup.add(types.InlineKeyboardButton(text = '💱 Ваша валюта ('+data[1]+')', callback_data = 'wallet_choose'))
		reply_markup.add(types.InlineKeyboardButton(text = '📶 Источник курсов ('+sources[data[2]][0]+')', callback_data = 'source_'+data[2]))
		reply_markup.add(back_markup('button', 'menu'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'В этом разделе вы можете настроить источник курсов и выбрать валюту.',
		reply_markup = reply_markup)

	elif call.data == 'vipiska':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(*[types.InlineKeyboardButton(text = i, callback_data = 'vipiska_'+dict_wallet[i][0]) for i in dict_wallet])
		reply_markup.add(back_markup('button', 'koshelek'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Последние операции по вашему аккаунту:',
		reply_markup = reply_markup)

	elif call.data[:8] == 'vipiska_':
		bot.answer_callback_query(call.id, 'Wait...')
		answer = ''
		for row in bd('SELECT * FROM history WHERE id = "'+str(call.message.chat.id)+'" AND out = "'+call.data[8:]+'"'):
			answer += '<p><b>ID: </b>'+row[1]+\
			'<b>Кошелек: </b>'+row[3]+'</p>'+\
			'<p><b>Сумма: </b>'+row[4]+\
			'<b>Время: </b>'+time.strftime('%H:%M:%S', time.gmtime(row[5]))+'</p>'
			n += 1
		telegraph.create_account(short_name = call.message.chat.first_name)
		if answer != '':
			response = telegraph.create_page(dict_wallet_reverse[call.data[8:]], html_content = answer)
			answer = 'Выписка по счету: \n<a href = "http://telegra.ph/{}">'+dict_wallet_reverse[call.data[8:]]+'</a>'.format(response['path'])
		else:
			answer = 'У вас не было операций по счету '+dict_wallet_reverse[call.data[8:]]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_markup('markup', 'vipiska'))

	elif call.data == 'wallet_change':
		bot.answer_callback_query(call.id, 'В разработке...')

	elif call.data[:5] == 'lang_' or call.data[:6] == 'sound_' or call.data[:5] == 'curr_':
		if call.data[:5] == 'lang_':
			sql = 'UPDATE settings SET language = "'+call.data[5:]+'" WHERE id = "'+str(call.message.chat.id)+'"'
		elif call.data[:6] == 'sound_':
			sql = 'UPDATE settings SET notifications = "'+call.data[6:]+'" WHERE id = "'+str(call.message.chat.id)+'"'
		elif call.data[:5] == 'curr_':
			sql = 'UPDATE settings SET curriences = "'+call.data[5:]+'" WHERE id = "'+str(call.message.chat.id)+'"'
		bd(sql)
		bot.edit_message_reply_markup(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		reply_markup = settings_markup(call.message.chat.id))

	elif call.data == 'referal':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Ваша реферальная ссылка:\n https://t.me/seepaybot?start='+str(call.message.chat.id),
		reply_markup = back_markup('markup', 'settings'))

	elif call.data == 'stat':
		user_data = user_reit(str(call.message.chat.id))
		answer = 'Ваш статус: '+user_data[0]+'\n<b>Всего c маркета: </b>'+str(user_data[2])+' OMA\n<b>У вас в команде:  </b>⚪️ '+str(user_data[4])+'\n\n<b>Реферальная ссылка: </b>https://t.me/seepaybot?start='+str(call.message.chat.id)
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back_markup('markup', 'settings'),
		parse_mode = 'HTML')


bot.remove_webhook()

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
				certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
	'server.socket_host': WEBHOOK_LISTEN,
	'server.socket_port': WEBHOOK_PORT,
	'server.ssl_module': 'builtin',
	'server.ssl_certificate': WEBHOOK_SSL_CERT,
	'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
