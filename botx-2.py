import telebot
from telebot import types
import pickle
#import cherrypy
import sqlite3
import random
import requests
import time
import json
import string

def id_generator(size = 10, chars = string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

bot = telebot.TeleBot('586528288:AAGUZ3AwAvvD19hXJhsfyp-FhXuNxMNKnd0')

BOOK = []
CHANELS = []
logi = {}
add_bot = {'name' : 'here is name', 'description' : 'here is description', 'api' : 'here is token'}

first_markup = types.InlineKeyboardMarkup()
first_markup.add(types.InlineKeyboardButton(text = 'Creator', callback_data = 'botanist'),
				types.InlineKeyboardButton(text = 'Advertiser', callback_data = 'advertiser'))
first_markup.add(types.InlineKeyboardButton(text = 'About Project »', callback_data = 'about'))

advertiser_markup = types.InlineKeyboardMarkup()
advertiser_markup.add(types.InlineKeyboardButton(text = 'Created Ads', callback_data = 'created_ad'),
					types.InlineKeyboardButton(text = 'Create Ad »', callback_data = 'create_anons'))
advertiser_markup.add(types.InlineKeyboardButton(text = 'Bot Catalog', callback_data = 'bot_catalog'))
advertiser_markup.add(types.InlineKeyboardButton(text = 'Chanel Catalog', callback_data = 'chanel_catalog'))
advertiser_markup.add(types.InlineKeyboardButton(text = 'BILL', callback_data = 'bill'))

botanist_markup = types.InlineKeyboardMarkup()
botanist_markup.add(types.InlineKeyboardButton(text = 'My Bots', callback_data = 'my_bots'),
					types.InlineKeyboardButton(text = 'Add Bot »', callback_data = 'add_bot'))
botanist_markup.add(types.InlineKeyboardButton(text = 'My Chanels', callback_data = 'my_chanels'),
					types.InlineKeyboardButton(text = 'Add Chanel »', callback_data = 'add_chanel'))
botanist_markup.add(types.InlineKeyboardButton(text = 'Announcement Applications', callback_data = 'applications'))
botanist_markup.add(types.InlineKeyboardButton(text = 'BILL', callback_data = 'bill'))

class WebhookServer(object):
    # index равнозначно /, т.к. отсутствию части после ip-адреса (грубо говоря)
    @cherrypy.expose
    def index(self):
        length = int(cherrypy.request.headers['content-length'])
        json_string = cherrypy.request.body.read(length).decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''

def add_user_type(call, user_type):
	conn = sqlite3.connect('./botx.sqlite3')
	curr = conn.cursor()
	curr.execute('UPDATE users SET type = ? WHERE id = ?', (user_type, call.message.chat.id))
	conn.commit()
	conn.close()

def list_markup(sql, name_row, call_row, calldata_row, back_call):
	conn = sqlite3.connect('./botx.sqlite3')
	curr = conn.cursor()
	with conn:
		markup = types.InlineKeyboardMarkup()
		rows = curr.execute(sql).fetchall()
		n = 0
		while True:
			try:
				markup.add(types.InlineKeyboardButton(text = rows[n][name_row], callback_data = calldata_row+rows[n][call_row]),
							types.InlineKeyboardButton(text = rows[n+1][name_row], callback_data = calldata_row+rows[n+1][call_row]),)
				n += 2
			except Exception:
				try:
					markup.add(types.InlineKeyboardButton(text = rows[n][name_row], callback_data = calldata_row+rows[n][call_row]))
					break
				except Exception:
					break
		markup.add(back(back_call, 'back_button', 'empty'))
		return markup

def back(back_to, keyboard_type, forward_to):
	keyboard = types.InlineKeyboardMarkup()
	back_button = types.InlineKeyboardButton(text = '«', callback_data = back_to)
	forward_button = types.InlineKeyboardButton(text = '»', callback_data = forward_to)
	if keyboard_type == 'all':
		if forward_to == 'finish':
			forward_button = types.InlineKeyboardButton(text = 'Done »', callback_data = forward_to)
		if forward_to[:12] == '1delete_bot_':
			forward_button = types.InlineKeyboardButton(text = 'Delete »', callback_data = forward_to)
		if forward_to[:14] == 'delete_chanel_':
			forward_button = types.InlineKeyboardButton(text = 'Delete »', callback_data = forward_to)
		else:
			forward_button = types.InlineKeyboardButton(text = '»', callback_data = forward_to)
		keyboard.add(back_button, forward_button)
		return keyboard
	elif keyboard_type == 'back_button':
		return back_button
	elif keyboard_type == 'back_markup':
		keyboard.add(back_button)
		return keyboard
	elif keyboard_type == 'forward_button':
		return forward_button
	else:
		keyboard.add(back_button)
		return keyboard

def pages_keyboard(start, stop, bot_id, category_id):
	keyboard = types.InlineKeyboardMarkup()
	btns = []
	if start > 0: btns.append(types.InlineKeyboardButton(
		text='«', callback_data='to_{}'.format(start - 1)))
	if stop < len(BOOK): btns.append(types.InlineKeyboardButton(
		text='»', callback_data='to_{}'.format(stop)))
	late = types.InlineKeyboardButton('Add To Favourite »', callback_data = 'add_favourite_{}'.format(bot_id))
	lk = types.InlineKeyboardButton(text = '« Other', callback_data = 'other_{}'.format(category_id))
	keyboard.add(*btns)
	keyboard.row(late)
	keyboard.row(lk)
	return keyboard

def pages_chanel(start, stop, bot_id, category_id):
	keyboard = types.InlineKeyboardMarkup()
	btns = []
	if start > 0: btns.append(types.InlineKeyboardButton(
		text='«', callback_data='chanel_to_{}'.format(start - 1)))
	if stop < len(CHANELS): btns.append(types.InlineKeyboardButton(
		text='»', callback_data='chanel_to_{}'.format(stop)))
	late = types.InlineKeyboardButton('Add To Favourite »', callback_data = 'add_fav_chanel_{}'.format(bot_id))
	lk = types.InlineKeyboardButton(text = '« Other', callback_data = 'chanel_other_{}'.format(category_id))
	keyboard.add(*btns)
	keyboard.row(late)
	keyboard.row(lk)
	return keyboard

@bot.message_handler(commands = ['start'])
def start(message):
	conn = sqlite3.connect('./botx.sqlite3')
	curr = conn.cursor()
	data = curr.execute('SELECT * FROM users WHERE id = ?', (message.chat.id,)).fetchall()
	start_markup = types.InlineKeyboardMarkup()
	if data == []:
		curr.execute('INSERT INTO users(id, type, bill, card) VALUES(?,?,?,?)', (message.chat.id, 0, 0, 0))
		conn.commit()
		answer = 'Whom you want to be?'
		start_markup = first_markup
	else:
		if data[0][1] == 'advertiser':
			start_markup = advertiser_markup
			logi.update({message.chat.id : 'advertiser'})
		elif data[0][1] == 'botanist':
			start_markup = botanist_markup
			logi.update({message.chat.id : 'botanist'})
		else:
			start_markup = first_markup
		answer = 'Wow, something went wrong?'
	conn.close()
	bot.send_message(
	chat_id = message.chat.id,
	text = answer,
	reply_markup = start_markup,
	parse_mode = 'Markdown')

@bot.message_handler(content_types=['text'])
def check(message):
	#logi.update({message.chat.id : 'text'})

	if logi[message.chat.id] == 'add_bot':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Can you describe in what his power? You can use HTML tegs to format text.',
		reply_markup = back('name', 'all', 'api'),
		parse_mode = 'Markdown')
		add_bot.update({'name' : message.text})
		logi.update({message.chat.id : 'description'})

	elif logi[message.chat.id] == 'description':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Send me his API Token, without It we will not be able to help you',
		reply_markup = back('description', 'all', 'api'),
		parse_mode = 'Markdown')
		logi.update({message.chat.id : 'api'})
		add_bot.update({'description' : message.text})

	elif logi[message.chat.id][:14] == 'on_remoderate_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM messages WHERE id = ?', (logi[message.chat.id][14:],)).fetchall()[0]
		curr.execute('UPDATE messages SET note = ? WHERE id = ?', (message.text, logi[message.chat.id][14:]))
		conn.commit()
		conn.close()
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Changes have taken effect',
		reply_markup = back('moderate_applications_for_bot_'+data[7], 'back_markup', 'empty'),
		parse_mode = 'Markdown')

	elif logi[message.chat.id] == 'api':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'All, right. Send me you user database in the next message. One id per line, it\'s important!',
		reply_markup = back('api', 'all', 'database'),
		parse_mode = 'Markdown')
		logi.update({message.chat.id: 'database'})
		add_bot.update({'api' : message.text})

	elif logi[message.chat.id] == 'database':
		bot_id = id_generator()
		answer = 'Hmmm, looks like it all. Check, is everything below true?'+'\n'+\
				'<b>Name: </b>'+add_bot['name']+'\n'+\
				'<b>Description: </b>'+add_bot['description']+'\n'+\
				'<b>Category: </b>'+add_bot['category']+'\n'+\
				'<b>API Token: </b>'+add_bot['api']
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back('database', 'all', 'finish'),
		parse_mode = 'HTML' )
		logi.update({message.chat.id : bot_id})
		with open(bot_id, "wb") as file:
			pickle.dump(message.text, file)

	elif logi[message.chat.id][:5] == 'edit_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		if logi[message.chat.id][5] == '0':
			curr.execute('UPDATE bots SET token = ? WHERE id = ?', (message.text, logi[message.chat.id][7:]))
			reply_markup = back('in_bot_'+logi[message.chat.id][7:], 'back_markup', 'empty')
		elif logi[message.chat.id][5] == '1':
			curr.execute('UPDATE bots SET name = ? WHERE id = ?', (message.text, logi[message.chat.id][7:]))
			reply_markup = back('in_bot_'+logi[message.chat.id][7:], 'back_markup', 'empty')
		elif logi[message.chat.id][5] == '2':
			curr.execute('UPDATE bots SET description = ? WHERE id = ?', (message.text, logi[message.chat.id][7:]))
			reply_markup = back('in_bot_'+logi[message.chat.id][7:], 'back_markup', 'empty')
		elif logi[message.chat.id][5] == '4':
			curr.execute('UPDATE bots SET price = ? WHERE id = ?', (message.text, logi[message.chat.id][7:]))
			reply_markup = back('in_bot_'+logi[message.chat.id][7:], 'back_markup', 'empty')
		elif logi[message.chat.id] == 'edit_card':
			curr.execute('UPDATE users SET card = ? WHERE id = ?', (message.text, message.chat.id))
			reply_markup = back('bill', 'back_markup', 'empty')
		else:
			with open(logi[message.chat.id][7:], "wb") as file:
				pickle.dump(message.text, file)
			reply_markup = back('in_bot_'+logi[message.chat.id][7:], 'back_markup', 'empty')
		conn.commit()
		conn.close()
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Changes have taken effect',
		reply_markup = reply_markup,
		parse_mode = 'Markdown')
		logi.update({message.chat.id : 'refresh'})

	elif logi[message.chat.id][0] == 'chanel_name':
		try:
			print(bot.get_chat_member('@'+message.text, message.chat.id))
			if bot.get_chat_member('@'+message.text, message.chat.id).status == 'admin' or\
			 bot.get_chat_member('@'+message.text, message.chat.id).status == 'creator':
				conn = sqlite3.connect('./botx.sqlite3')
				curr = conn.cursor()
				curr.execute('INSERT INTO chanels(id, name, user_id, price, category) VALUES (?,?,?,?,?)',
							(id_generator(), message.text, message.chat.id, 0, logi[message.chat.id][0]))
				conn.commit()
				conn.close()
				answer = 'Chanel had successfully added'
				logi.update({message.chat.id : 'chanel_added'})
			else:
				answer = 'You not admin in chanel: @'+str(message.text)+', send me another one.'
				logi.update({message.chat.id : 'chanel_name'})
		except Exception:
			answer = 'I not admin in chanel: @'+str(message.text)+'. Send me another one.'
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = back('botanist', 'back_markup', 'empty'),
		parse_mode = 'HTML')

	elif logi[message.chat.id] == 'out_bill':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM users WHERE id = ?', (call.message.chat.id,)).fetchall()[0]
		if message.text.isdigit():
			if data[2] >= int(message.text):
				answer = 'Money have sent on you card: <code>'+data[3][14:]+'</code>'
				##Отправка на карту##
				curr.execute('UPDATE users SET bill = bill - ? WHERE id = ?', (message.text, message.chat.id,))
				logi.update({call.message.chat.id, 'success'})
			else:
				answer = 'Don\'t try to still my money, try one more time!'
		else:
			answer = 'Wrong data, try one more time!'
		conn.commit()
		conn.close()
		bot.send_message(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back('bill', 'back_markup', 'empty'),
		parse_mode = 'Markdown')

	elif logi[message.chat.id][0] == 'send' or logi[message.chat.id][:5] == 'send_':
		botname = ''
		BOTNAME = []
		message.text += '\n'+'help'
		answer = 'Bots to promote: <pre>'+'\n'
		for i in message.text:
			if i == '\n':
				BOTNAME.append(botname)
				answer += botname + '\n'
				botname = ''
			else:
				botname += i
		answer += '</pre>'
		reply_markup = types.InlineKeyboardMarkup()
		if logi[message.chat.id][:5] == 'send_':
			reply_markup.add(types.InlineKeyboardButton(text = 'Yes', callback_data = 'aply_bots_'+logi[message.chat.id][5:]),
							types.InlineKeyboardButton(text = 'No', callback_data = 'declaine_bots_'+logi[message.chat.id][5:]))
			logi.update({message.chat.id : BOTNAME})
		else:
			reply_markup.add(types.InlineKeyboardButton(text = 'Yes', callback_data = 'aply_bots'),
							types.InlineKeyboardButton(text = 'No', callback_data = 'declaine_bots'))
			logi.update({message.chat.id : ['send', logi[message.chat.id][1], logi[message.chat.id][2], BOTNAME]})
		reply_markup.add(back('advertiser', 'back_button', 'empty'))
		bot.send_message(
		chat_id = message.chat.id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif logi[message.chat.id][:7] == 'redact_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		if logi[message.chat.id][:12] == 'redact_name_':
			curr.execute('UPDATE anons SET name = ? WHERE id = ?', (message.text, logi[message.chat.id][12:]))
			reply_markup = back('anons_more_'+logi[message.chat.id][12:], 'back_markup', 'empty')
		elif logi[message.chat.id][:19] == 'redact_description_':
			curr.execute('UPDATE anons SET message = ? WHERE id = ?', (message.text, logi[message.chat.id][19:]))
			reply_markup = back('anons_more_'+logi[message.chat.id][19:], 'back_markup', 'empty')
		elif logi[message.chat.id][:18] == 'redact_text_anons_':
			curr.execute('UPDATE messages SET mess_text = ? WHERE id = ?', (message.text, logi[message.chat.id][18:]))
			reply_markup = back('bot_anons_more_'+logi[message.chat.id][18:], 'back_markup', 'empty')
		conn.commit()
		conn.close()
		bot.send_message(
		chat_id = message.chat.id,
		text = 'I have done, come back to you anons',
		reply_markup = reply_markup,
		parse_mode = 'Markdown')
		logi.update({message.chat.id : 'success'})

	elif logi[message.chat.id][:12] == 'edit_chanel_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		if logi[message.chat.id][:17] == 'edit_chanel_name_':
			curr.execute('UPDATE chanels SET name = ? WHERE id = ?', (message.text, logi[message.chat.id][17:],))
			chanel_id = logi[message.chat.id][17:]
		elif logi[message.chat.id][:18] == 'edit_chanel_price_':
			curr.execute('UPDATE chanels SET price = ? WHERE id = ?', (message.text, logi[message.chat.id][18:],))
			chanel_id = logi[message.chat.id][18:]
		conn.commit()
		conn.close()
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Changes have taken effect',
		reply_markup = back('in_chanel_'+chanel_id, 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({message.chat.id : 'changes'})

	elif logi[message.chat.id] == 'create_anons':
		true_not_markup = types.InlineKeyboardMarkup()
		true_not_markup.add(types.InlineKeyboardButton(text = 'Yes', callback_data = 'right_anons'),
							types.InlineKeyboardButton(text = 'Not', callback_data = 'notright_anons'))
		true_not_markup.add(back('create_anons', 'back_button', 'empty'))
		try:
			bot.send_message(
			chat_id = message.chat.id,
			text = str(message.text),
			reply_markup = true_not_markup,
			parse_mode = 'HTML')
			logi.update({message.chat.id : message.text})
		except Exception:
			bot.send_message(
			chat_id = message.chat.id,
			text = 'Something wrong with you tags, try one more time'+'\n'+str(message.text),
			reply_markup = back('create_anons', 'back_markup', 'empty'),
			parse_mode = 'Markdown')
			logi.update({message.chat.id : 'create_anons'})

	elif logi[message.chat.id][0] == 'name_anons':
		bot.send_message(
		chat_id = message.chat.id,
		text = 'Send me the botnames in wich you want to promote you application. Message example: '+'\n'+\
		'<pre>'+'\n'+\
		'botname0'+'\n'+\
		'botname1'+'\n'+\
		'botname2'+'\n'+\
		'botname3'+'\n'+\
		'</pre>',
		reply_markup = back('advertiser', 'back_markup', 'empty'),
		parse_mode = 'HTML')
		logi.update({message.chat.id : ['send', logi[message.chat.id][1], message.text]})

@bot.callback_query_handler(func=lambda call: True)
def inline(call):
	#logi.update({call.message.chat.id : 'text'})
	print(call.data)
	if call.data == 'botanist':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Here is lonely yet',
		reply_markup = botanist_markup,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'botanist'})
		add_user_type(call, 'botanist')

	elif call.data == 'advertiser':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Here is lonely yet',
		reply_markup = advertiser_markup,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'advertiser'})
		add_user_type(call, 'advertiser')

	elif call.data == 'add_bot':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		with conn:
			rows = curr.execute('SELECT * FROM category').fetchall()
			category_list = types.InlineKeyboardMarkup()
			for row in rows:
				category_list.add(types.InlineKeyboardButton(text = row[1], callback_data = 'bot_choose_'+row[0]))
			category_list.add(back('botanist', 'back_button', 'empty'), back('empty', 'forward_button', 'name'))
		conn.close()
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Choose category for you bot below',
		reply_markup = category_list,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'add_bot'})

	elif call.data[:11] == 'bot_choose_' or call.data == 'name':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'How can I call him? Send me bot-username in such format <code>usernamebot</code>',
		reply_markup = back('add_bot', 'all', 'description'),
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'add_bot'})
		add_bot.update({'category': call.data[11:]})

	elif call.data == 'description':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Something changed in description?',
		reply_markup = back('name', 'all', 'api'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'description'})

	elif call.data == 'api':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Something wrong with old API Token?',
		reply_markup = back('description', 'all', 'database'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'api'})

	elif call.data == 'database':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'If something wrong with database you can send it in the nex message, one id per line, remember!',
		reply_markup = back('api', 'all', 'check_all'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'database'})

	elif call.data == 'check_all':
		answer = 'Hmmm, looks like it all. Check, is everything below true?'+'\n'+\
				'<b>Name: </b>'+add_bot['name']+'\n'+\
				'<b>Description: </b>'+add_bot['description']+'\n'+\
				'<b>Category: </b>'+add_bot['category']+'\n'+\
				'<b>API Token: </b>'+add_bot['api']
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back('database', 'all', 'finish'),
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'end'})

	elif call.data[:9] == 'aply_bots':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		if call.data == 'aply_bots':
			anons_id = id_generator()
			curr.execute('INSERT INTO anons(id, user_id, message, name) VALUES(?,?,?,?)',
						(anons_id, call.message.chat.id, logi[call.message.chat.id][1], logi[call.message.chat.id][2]))
			BOTS = logi[call.message.chat.id][3]
			answer = 'Here is info about you company:'+'\n'+\
			'<b>Name:</b> '+str(logi[call.message.chat.id][2])+'\n'+\
			'<b>Text:</b> '+'\n'+str(logi[call.message.chat.id][1])+'\n'+\
			'\n'+'BOTS: <pre>'
			anons_info = 0
		else:
			BOTS = logi[call.message.chat.id]
			anons_id = call.data[10:]
			answer = 'BOTS: <pre>'
			anons_info = curr.execute('SELECT * FROM anons WHERE id = ?', (call.data[10:],)).fetchall()[0]
		with conn:
			for botik in BOTS:
				bot_data = curr.execute('SELECT * FROM bots WHERE bot_name = ?', (botik,)).fetchall()
				if bot_data == []:
					answer += botik + ' -' +'\n'
				else:
					answer += bot_data[0][2] + ' +' +'\n'
					if anons_info == 0:
						curr.execute('INSERT INTO messages(id, anons_id, adv_id, name, mess_text, status, bot_name, bot_id, botanist_id, note)\
									VALUES(?,?,?,?,?,?,?,?,?,?)', (id_generator(), anons_id, call.message.chat.id, logi[call.message.chat.id][2],
									logi[call.message.chat.id][1], '-', bot_data[0][2], bot_data[0][0], bot_data[0][1], 0))
					else:
						curr.execute('INSERT INTO messages(id, anons_id, adv_id, name, mess_text, status, bot_name, bot_id, botanist_id, note)\
									VALUES(?,?,?,?,?,?,?,?,?,?)', (id_generator(), anons_id, call.message.chat.id, anons_info[3],
									anons_info[2], '-', bot_data[0][2], bot_data[0][0], bot_data[0][1], 0))
		answer += '</pre>'+'\n'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back('anons_more_'+anons_id, 'back_markup', 'empty'),
		parse_mode = 'HTML')

	elif call.data == 'finish':
		answer = 'It\'s all!'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back('botanist', 'all', 'in_bot_'+logi[call.message.chat.id]),
		parse_mode = 'HTML')
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		curr.execute('INSERT INTO bots(id, botanist_id, bot_name, description, token, category) VALUES(?,?,?,?,?,?)',
					(logi[call.message.chat.id], call.message.chat.id, add_bot['name'], add_bot['description'], add_bot['api'], add_bot['category']))
		conn.commit()
		conn.close()
		logi.update({call.message.chat.id : 'all'})

	elif call.data[:7] == 'in_bot_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM bots WHERE id = ?', (call.data[7:],)).fetchall()[0]
		conn.close()
		bot_panel = types.InlineKeyboardMarkup()
		bot_panel.add(types.InlineKeyboardButton(text = 'Edit Price: '+str(data[6]), callback_data = 'edit_price_'+call.data[7:]))
		bot_panel.add(types.InlineKeyboardButton(text = 'API Token', callback_data = 'edit_token_'+call.data[7:]),
						types.InlineKeyboardButton(text = 'Name', callback_data = 'edit_name_'+call.data[7:]))
		bot_panel.add(types.InlineKeyboardButton(text = 'Description', callback_data = 'edit_description_'+call.data[7:]),
						types.InlineKeyboardButton(text = 'User Database', callback_data = 'edit_database_'+call.data[7:]))
		bot_panel.add(back('my_bots', 'back_button', 'empty'), types.InlineKeyboardButton(text = 'Delete Bot', callback_data = 'delete_bot_'+call.data[7:]))
		answer = 'What do you want to do with '+data[2]+'?'+'<a href="https://t.me/'+str(data[2])+'">&#8203;</a>'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = bot_panel,
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'in_bot'})

	elif call.data == 'my_bots':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Choose a bot from the list below:',
		reply_markup = list_markup('SELECT * FROM bots WHERE botanist_id = '+str(call.message.chat.id), 2, 0, 'in_bot_', 'botanist'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'my_bots'})

	elif call.data[:11] == 'delete_bot_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Are you sure, that you want to delete bot?',
		reply_markup = back('in_bot_'+call.data[11:], 'all', '1delete_bot_'+call.data[11:]),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'first_delete'})

	elif call.data[:5] == 'edit_' and call.data[:12] != 'edit_chanel_':
		if call.data[:11] == 'edit_token_':
			reply_markup = back('in_bot_'+call.data[11:], 'back_markup', 'empty')
			logi.update({call.message.chat.id : 'edit_0_'+call.data[11:]})
			answer = 'Something wrong with old API Token? Send me a new one.'
		elif call.data[:10] == 'edit_name_':
			reply_markup = back('in_bot_'+call.data[10:], 'back_markup', 'empty')
			logi.update({call.message.chat.id : 'edit_1_'+call.data[10:]})
			answer = 'It\'s rather strange to rename you child, but send me a new name.'
		elif call.data[:17] == 'edit_description_':
			reply_markup = back('in_bot_'+call.data[17:], 'back_markup', 'empty')
			logi.update({call.message.chat.id : 'edit_2_'+call.data[17:]})
			answer = 'Alright, send me a new description.'
		elif call.data[:14] == 'edit_database_':
			reply_markup = back('in_bot_'+call.data[14:], 'back_markup', 'empty')
			logi.update({call.message.chat.id : 'edit_3_'+call.data[14:]})
			answer = 'Send me full database, but remember - one id per line!'
		elif call.data[:11] == 'edit_price_':
			reply_markup = back('in_bot_'+call.data[11:], 'back_markup', 'empty')
			logi.update({call.message.chat.id : 'edit_4_'+call.data[11:]})
			answer = 'Send me a new price per subsribe'
		elif call.data == 'edit_card':
			answer = 'Send me new one in format: <code>xxxx xxxx xxxx xxxx</code>'
			logi.update({call.message.chat.id : call.data})
			reply_markup = back('bill', 'back_markup', 'empty')
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'HTML')

	elif call.data[:12] == '1delete_bot_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		curr.execute('DELETE FROM bots WHERE id = ?', (call.data[12:],))
		conn.commit()
		conn.close()
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'My condolences, his gone...',
		reply_markup = back('in_bot_'+bot_id, 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'edit_'+str(num)+'_'+call.data[11:]})

	elif call.data == 'bot_catalog':
		bot.answer_callback_query(call.id, 'We just work about this part. It will be self-generated HTML page with whole catalog', show_alert = True)

	elif call.data == 'add_chanel':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		with conn:
			rows = curr.execute('SELECT * FROM category').fetchall()
			category_list = types.InlineKeyboardMarkup()
			for row in rows:
				category_list.add(types.InlineKeyboardButton(text = row[1], callback_data = 'chanel_choose_'+row[0]))
			category_list.add(back('botanist', 'back_button', 'empty'), back('empty', 'forward_button', 'chanel_name'))
		conn.close()
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Choose category for you bot from the list below:',
		reply_markup = category_list,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'chanel_category'})

	elif call.data[:14] == 'chanel_choose_' or call.data == 'chanel_name':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Make me admin in chanel you wanted to add and send me their name in such format <code>chanelname</code>.',
		reply_markup = back('add_chanel', 'back_markup', 'empty'),
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : ['chanel_name', call.data[14:]]})

	elif call.data == 'my_chanels':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Choose a chanel from the list below:',
		reply_markup = list_markup('SELECT * FROM chanels WHERE user_id = '+str(call.message.chat.id), 1, 4, 'in_chanel_', 'botanist'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'my_chanels'})

	elif call.data[:10] == 'in_chanel_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM chanels WHERE id = ?', (call.data[10:],)).fetchall()[0]
		conn.close()
		edit_chanel_markup = types.InlineKeyboardMarkup()
		edit_chanel_markup.add(types.InlineKeyboardButton(text = 'Edit Name', callback_data = 'edit_chanel_name_'+call.data[10:]),
								types.InlineKeyboardButton(text = 'Edit Price: '+str(data[3]), callback_data = 'edit_chanel_price_'+call.data[10:]))
		edit_chanel_markup.add(types.InlineKeyboardButton(text = 'Delete Chanel', callback_data = '1delete_chanel_'+call.data[10:]))
		edit_chanel_markup.add(back('my_chanels', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'What will be the next step?'+'<a href="https://t.me/'+str(data[1])+'">&#8203;</a>',
		reply_markup = edit_chanel_markup,
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'my_chanel'})

	elif call.data[:12] == 'edit_chanel_':
		if call.data[:17] == 'edit_chanel_name_':
			logi.update({call.message.chat.id : call.data})
			answer = 'Send me a new name for you chanel'
		elif call.data[:18] == 'edit_chanel_price_':
			logi.update({call.message.chat.id : call.data})
			answer = 'Send me a new post price for you chanel'
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = ('in_chanel_'+call.data[:12], 'back_markup', 'empty'),
		parse_mode = 'Markdown')

	elif call.data[:15] == '1delete_chanel_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Are you sure? Did you have time to think about?',
		reply_markup = back('in_chanel_'+call.data[15:], 'all', call.data[1:]),
		parse_mode = 'Markdown')

	elif call.data[:14] == 'delete_chanel_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		curr.execute('DELETE FROM chanels WHERE id = ?', (call.data[14:],))
		conn.commit()
		conn.close()
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'My condolences, his gone...',
		reply_markup = back('my_chanels', 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'success delete'})

	elif call.data == 'chanel_catalog':
		bot.answer_callback_query(call.id, 'We just work about this part. It will be self generated HTML page with whole catalog', show_alert = True)

	elif call.data == 'create_anons' or call.data == 'notright_anons':
		answer = 'Alright partner, keep on rolling baby, you know what time is it.'+'\n'+\
		'<b>*bold text*</b>'+'\n'+\
		'<i>_italic text_</i>'+'\n'+\
		'<a href = "http://example.com">[inline url](http://example.com)</a>'+'\n'+\
		'<a href="Past here photo link, it will be shown without tags">&#8203;</a>'+'\n'+\
		'<code>`inline fixed-width code`</code>'+'\n'+\
		'<pre>'+'\n'+\
		'```'+'\n'+\
		'pre-formatted fixed-width code block'+\
		'```'+\
		'</pre>'
		if call.data == 'notright_anons':
			answer += '\n'+str(logi[call.message.chat.id])
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = back('advertiser', 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : 'create_anons'})

	elif call.data == 'right_anons':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Give a name to you anons',
		reply_markup = back('create_anons', 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : ['name_anons', logi[call.message.chat.id]]})

	elif call.data == 'all_anons':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'All anons you had ever created',
		reply_markup = list_markup('SELECT * FROM anons WHERE user_id = '+str(call.message.chat.id), 3, 0, 'anons_more_', 'created_ad'),
		parse_mode = 'Markdown')

	elif call.data[:11] == 'anons_more_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM anons WHERE id = ?', (call.data[11:],)).fetchall()[0]
		conn.close()
		if '</' in data[2]:
			parse_mode = 'HTML'
			answer = '<b>Name: </b>'+str(data[3])+'\n'+\
			'<b>Text: </b>'+'\n'+\
			str(data[2])
		else:
			parse_mode = 'Markdown'
			answer = '*Name: *'+str(data[3])+'\n'+\
			'*Text: *'+'\n'+\
			str(data[2])
		anons_markup = types.InlineKeyboardMarkup()
		anons_markup.add(types.InlineKeyboardButton(text = 'Send »', callback_data = 'send_'+call.data[11:]))
		anons_markup.add(types.InlineKeyboardButton(text = 'Redact Name', callback_data = 'redact_name_'+call.data[11:]))
		anons_markup.add(types.InlineKeyboardButton(text = 'Redact Description', callback_data = 'redact_description_'+call.data[11:]))
		anons_markup.add(back('all_anons', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = anons_markup,
		parse_mode = parse_mode)

	elif call.data == 'declaine_bots' or call.data[:5] =='send_' or call.data[:14] == 'declaine_bots_':
		if call.data[:5] == 'send_':
			logi.update({call.message.chat.id : call.data})
		elif call.data[:14] == 'declaine_bots_':
			logi.update({call.message.chat.id : 'send_' + call.data[14:]})
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Send me the botnames in wich you want to promote you application. Message example: '+'\n'+\
		'<pre>'+'\n'+\
		'botname0'+'\n'+\
		'botname1'+'\n'+\
		'botname2'+'\n'+\
		'botname3'+'\n'+\
		'</pre>',
		reply_markup = back('advertiser', 'back_markup', 'empty'),
		parse_mode = 'HTML')
		#logi.update({call.message.chat.id : call.data})

	elif call.data[:7] == 'redact_':
		if call.data[:12] == 'redact_name_':
			id = call.data[7:]
		elif call.data[:19] == 'redact_description_':
			id = call.data[19:]
		elif call.data[:18] == 'redact_text_anons_':
			id = call.data[18:]
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Send me the new one!',
		reply_markup = back('anons_more_'+id, 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : call.data})

	elif call.data == 'created_ad':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		moderated = curr.execute('SELECT * FROM messages WHERE adv_id = ? AND status = ?', (call.message.chat.id, '+')).fetchall()
		on_moderate = curr.execute('SELECT * FROM messages WHERE adv_id = ? AND status = ?', (call.message.chat.id, '-')).fetchall()
		all = curr.execute('SELECT * FROM anons WHERE user_id = ?', (call.message.chat.id,)).fetchall()
		conn.close()
		created_markup = types.InlineKeyboardMarkup()
		created_markup.add(types.InlineKeyboardButton(text = 'Mdr('+str(len(moderated))+')', callback_data = 'moderated'),
							types.InlineKeyboardButton(text = 'On mdr('+str(len(on_moderate))+')', callback_data = 'on_moderate'))
		created_markup.add(types.InlineKeyboardButton(text = 'ALL('+str(len(all))+')', callback_data = 'all_anons'))
		created_markup.add(back('advertiser', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Go on!',
		reply_markup = created_markup,
		parse_mode = 'Markdown')

	elif call.data == 'on_moderate':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		markup = types.InlineKeyboardMarkup()
		with conn:
			company = []
			rows = curr.execute('SELECT * FROM messages WHERE adv_id = ? AND status = ?', (call.message.chat.id, '-')).fetchall()
			for row in rows:
				if row[1] not in company:
					markup.add(types.InlineKeyboardButton(text = row[3], callback_data = 'company_more_'+row[1]))
					company.append(row[1])
		markup.add(back('created_ad', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'All you company',
		reply_markup = markup,
		parse_mode = 'Markdown')

	elif call.data[:13] == 'company_more_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		markup = types.InlineKeyboardMarkup()
		with conn:
			rows = curr.execute('SELECT * FROM messages WHERE anons_id = ?', (call.data[13:],)).fetchall()
			for row in rows:
				markup.add(types.InlineKeyboardButton(text = row[3] + ' for ' + row[6], callback_data = 'bot_anons_more_'+row[0]))
		conn.close()
		if rows[0][5] == '-':
			markup.add(back('on_moderate', 'back_button', 'empty'))
		else:
			markup.add(back('moderated', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Anons for every bot',
		reply_markup = markup,
		parse_mode = 'Markdown')

	elif call.data[:15] == 'bot_anons_more_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM messages WHERE id = ?', (call.data[15:],)).fetchall()[0]
		conn.close()
		markup = types.InlineKeyboardMarkup()
		answer = '<b>Name: </b>'+str(data[3])+' '+data[5]+'\n'+\
		'<b>Text: </b>'+str(data[4])+'\n'+\
		'<b>BOT: </b>'+data[6]+'\n'
		if data[2] == call.message.chat.id:
			if data[9] != 0:
				answer += 'Botanist note: <pre>'+str(data[9])+'</pre>'
				markup.add(types.InlineKeyboardButton(text = 'On moderate »', callback_data = 'moderate_send_'+data[0]))
			if data[5] == '-':
				markup.add(types.InlineKeyboardButton(text = 'Redact Text', callback_data = 'redact_text_anons_'+data[0]))
			markup.add(back('company_more_'+data[1], 'back_button', 'empty'))
		else:
			if data[5] == '-':
				markup.add(types.InlineKeyboardButton(text = 'Accept', callback_data = 'accept_'+data[0]))
				markup.add(types.InlineKeyboardButton(text = 'On Remoderate', callback_data = 'on_remoderate_'+data[0]))
				markup.add(back('moderate_applications_for_bot_'+data[7], 'back_button', 'empty'))
			elif data[5] == '+':
				markup.add(types.InlineKeyboardButton(text = 'Send »', callback_data = 'bot_send_'+data[0]))
				markup.add(types.InlineKeyboardButton(text = 'Declaine', callback_data = 'declaine_'+data[0]))
				markup.add(back('execution_applications_for_bot_'+data[7], 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = markup,
		parse_mode = 'HTML')

	elif call.data[:9] == 'bot_send_':
		bot.answer_callback_query(call.id, text = 'This function in progress', show_alert = True)

	elif call.data[:14] == 'on_remoderate_':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Specify the reason for the revision',
		reply_markup = back('bot_anons_more_'+call.data[14:], 'back_markup', 'empty'),
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : call.data})

	elif call.data[:7] == 'accept_' or call.data[:9] == 'declaine_':
		bot.answer_callback_query(call.id, 'Done!')
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		if call.data[:7] == 'accept_':
			data = curr.execute('SELECT * FROM messages WHERE id = ?', (call.data[7:],)).fetchall()[0]
			curr.execute('UPDATE messages SET status = ? WHERE id = ?', ('+', call.data[7:]))
		elif call.data[:9] == 'declaine_':
			data = curr.execute('SELECT * FROM messages WHERE id = ?', (call.data[9:],)).fetchall()[0]
			curr.execute('DELETE FROM messages WHERE id = ?', (call.data[9:],))
		conn.commit()
		conn.close()
		bot.edit_message_reply_markup(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		reply_markup = back('moderate_applications_for_bot_'+data[7], 'back_markup', 'empty'))

	elif call.data[:14] == 'moderate_send_':
		bot.answer_callback_query(call.id, 'Done!')
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM messages WHERE id = ?', (call.data[14:],)).fetchall()[0]
		curr.execute('UPDATE messages SET note = ? WHERE id = ?', (0, call.data[14:],))
		conn.commit()
		conn.close()
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton(text = 'Redact Text', callback_data = 'redact_text_anons_'+call.data[14:]))
		markup.add(back('company_more_'+data[1], 'back_button', 'empty'))
		bot.edit_message_reply_markup(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		reply_markup = markup)

	elif call.data == 'bill':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM users WHERE id = ?', (call.message.chat.id,)).fetchall()[0]
		conn.close()
		answer = 'Bill information'
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Balance: '+str(data[2]), callback_data = 'balance_show_'+str(data[2])))
		if data[1] == 'botanist':
			if data[3] == 0:
				reply_markup.add(types.InlineKeyboardButton(text = 'Bind Card', callback_data = 'bind_card'))
			else:
				reply_markup.add(types.InlineKeyboardButton(text = 'xxxx - xxxx - xxxx -' + str(data[3])[14:], callback_data = 'edit_card'))
				if data[2] > 0:
					reply_markup.add(types.InlineKeyboardButton(text = 'Out Money', callback_data = 'out_bill'))
			reply_markup.add(back('botanist', 'back_button', 'empty'))
		if data[1] == 'advertiser':
			reply_markup.add(types.InlineKeyboardButton(text = 'Full Bill', callback_data = 'full_bill'))
			reply_markup.add(back('advertiser', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = reply_markup,
		parse_mode = 'Markdown')

	elif call.data == 'bind_card':
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Send me you card number in format: <code>XXXX XXXX XXXX XXXX</code>',
		reply_markup = back('bill', 'back_markup', 'empty'),
		parse_mode = 'HTML')
		logi.update({call.message.chat.id : 'edit_card'})

	elif call.data == 'out_bill':
		reply_markup = types.InlineKeyboardMarkup()
		reply_markup.add(types.InlineKeyboardButton(text = 'Out All', callback_data = 'out_all'))
		reply_markup.add(back('bill', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Send me summ or may be out all',
		reply_markup = reply_markup,
		parse_mode = 'Markdown')
		logi.update({call.message.chat.id : call.data})

	elif call.data == 'out_all':
		bot.answer_callback_query(call.id, 'Done!')
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		data = curr.execute('SELECT * FROM users WHERE id = ?', (call.message.chat.id,)).fetchall()[0]
		curr.execute('UPDATE users SET bill = ? WHERE id = ?', (0, call.message.chat.id,))
		conn.commit()
		conn.close()
		##Отправка денег на карту##
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'All mone have sent on you card: <code>'+data[3]+'</code>',
		reply_markup = back('back', 'back_markup', 'empty'),
		parse_mode = 'Markdown')

	elif call.data[:13] == 'balance_show_':
		bot.answer_callback_query(call.id, 'You balance: '+call.data[13:])

	elif call.data == 'applications':
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton(text = 'For Execution', callback_data = 'for_execution'),
					types.InlineKeyboardButton(text = 'For Moderate', callback_data = 'for_moderate'))
		markup.add(back('botanist', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'What kind of aplications?',
		reply_markup = markup,
		parse_mode = 'Markdown')

	elif call.data == 'for_moderate' or call.data == 'for_execution':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		markup = types.InlineKeyboardMarkup()
		with conn:
			bots_apl = []
			if call.data == 'for_moderate':
				rows = curr.execute('SELECT * FROM messages WHERE status = ? AND note = ? AND botanist_id = ?', ('-', 0, call.message.chat.id,)).fetchall()
			elif call.data == 'for_execution':
				rows = curr.execute('SELECT * FROM messages WHERE status = ? AND botanist_id = ?', ('+', call.message.chat.id,)).fetchall()
			for row in rows:
				if row[7] not in bots_apl:
					if call.data == 'for_moderate':
						markup.add(types.InlineKeyboardButton(text = str(row[6]), callback_data = 'moderate_applications_for_bot_'+row[7]))
					elif call.data == 'for_execution':
						markup.add(types.InlineKeyboardButton(text = str(row[6]), callback_data = 'execution_applications_for_bot_'+row[7]))
					bots_apl.append(row[7])
		conn.close()
		markup.add(back('applications', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = 'Choose applications for special bot',
		reply_markup = markup,
		parse_mode = 'Markdown')

	elif call.data[:30] == 'moderate_applications_for_bot_' or call.data[:31] == 'execution_applications_for_bot_':
		conn = sqlite3.connect('./botx.sqlite3')
		curr = conn.cursor()
		markup = types.InlineKeyboardMarkup()
		with conn:
			if call.data[:30] == 'moderate_applications_for_bot_':
				rows = curr.execute('SELECT * FROM messages WHERE bot_id = ? AND note = ? AND status = ?', (call.data[30:], 0, '-')).fetchall()
			elif call.data[:31] == 'execution_applications_for_bot_':
				rows = curr.execute('SELECT * FROM messages WHERE bot_id = ? AND status = ?', (call.data[31:], '+')).fetchall()
			for row in rows:
				markup.add(types.InlineKeyboardButton(text = str(row[3]), callback_data = 'bot_anons_more_'+row[0]))
		conn.close()
		if len(rows) > 0:
			answer = 'Applications for '+rows[0][6]
		else:
			answer = 'Here is lonely yet'
		if call.data[:30] == 'moderate_applications_for_bot_':
			markup.add(back('for_moderate', 'back_button', 'empty'))
		elif call.data[:31] == 'execution_applications_for_bot_':
			markup.add(back('for_execution', 'back_button', 'empty'))
		bot.edit_message_text(
		chat_id = call.message.chat.id,
		message_id = call.message.message_id,
		text = answer,
		reply_markup = markup,
		parse_mode = 'Markdown')

#YandexMoney
##########################

#bot.polling()
#with open(FILENAME, "rb") as file:
	#name = pickle.load(file)
if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 7774,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
