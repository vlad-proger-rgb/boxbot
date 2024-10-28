import telebot
from telebot import types

import random as rm
import db_use as use
import datetime

from settings import TELEGRAM_BOT_TOKEN, MYID

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def not_admin(message):
	bot.send_message(message.from_user.id, "Нет, нельзя!")

@bot.message_handler(commands=["start"])
def start(message):

    chat_type = message.chat.type

    us_group_id = message.chat.id
    us_group_name = message.chat.title

    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    username = message.from_user.username
    us_bot = message.from_user.is_bot
    us_lang_code = message.from_user.language_code
    us_is_premium = message.from_user.is_premium
    us_joined_game = datetime.datetime.now()

    use.db_table_val(
        type = chat_type, group_id = us_group_id, group_name = us_group_name,
        tele_id = us_id,
        first_name=us_name, last_name=us_sname, username=username, 
        is_bot=us_bot, lang_code=us_lang_code, is_premium=us_is_premium, joined_game=us_joined_game
    )

    print(chat_type, us_group_id, us_id)

    start_kb = types.InlineKeyboardMarkup()
    btn_to_add_to_group = types.InlineKeyboardButton(text="Добавить в группу", switch_inline_query="\nНапиши команду: /start")
    start_kb.add(btn_to_add_to_group)

    bot.send_message(message.chat.id,
        "Привет! 👋\nВ этой игре тебе нужно будет открывать коробки, в которых будет случайное количество монет. Нажими на кнопку: /menu и играй! Если хочешь, можешь добавить бота в группу:", 
        reply_markup=start_kb
    )


@bot.message_handler(commands=["menu"])
def menu(message):
    """Меню игры вызов командов /menu"""
    menu_kb = types.InlineKeyboardMarkup(row_width=2)

    leader_table = types.InlineKeyboardButton(text="Таблица рекордов 🏆", callback_data="leader_menu")
    daily_bonus = types.InlineKeyboardButton(text="Ежендевный бонус 🗓️", callback_data="daily")
    statistics = types.InlineKeyboardButton(text="Статистика 📈", callback_data="statistics")
    information = types.InlineKeyboardButton(text="Информация ℹ️", callback_data="info")
    play = types.InlineKeyboardButton(text="🎰 Играть! 🎲", callback_data="play")

    menu_kb.add(leader_table, daily_bonus, statistics, information, play)
    bot.send_message(message.chat.id, "Меню: ", reply_markup=menu_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "play")
def play(callback):

    levels = [
        rm.randint(1, 5), rm.randint(1, 5),
        rm.randint(6, 20), rm.randint(6, 20), rm.randint(6, 20), 
        rm.randint(21, 30), rm.randint(21, 30), rm.randint(21, 30), 
        rm.randint(31, 40), rm.randint(41, 50), rm.randint(51, 100)
    ]

    game_kb = types.InlineKeyboardMarkup(row_width=2)

    box1 = types.InlineKeyboardButton(text="1 📦", callback_data = "x " + str(rm.choice(levels) ) )
    box2 = types.InlineKeyboardButton(text="2 📦", callback_data = "x " + str(rm.choice(levels) ) )
    box3 = types.InlineKeyboardButton(text="3 📦", callback_data = "x " + str(rm.choice(levels) ) )
    box4 = types.InlineKeyboardButton(text="4 📦", callback_data = "x " + str(rm.choice(levels) ) )
    back = types.InlineKeyboardButton(text="Назад ↩️", callback_data="back")

    game_kb.row(box1, box2, box3, box4)
    game_kb.add(back)

    bot.send_message(callback.message.chat.id, "Выбери коробку: 📦", reply_markup=game_kb)

    @bot.callback_query_handler(func=lambda callback: (callback.data).split(" ")[0] == "x" and type( int( (callback.data).split(" ")[1] ) ) == int)
    def call_coins(callback):
        """Ожидание игрока нажать на коробку"""

        if callback.data == "back":
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.json["message_id"])
            menu(callback.message)

        elif (callback.data).split(" ")[0] == "x" and type( int( (callback.data).split(" ")[1] ) ) == int:
            callback.data = (callback.data).split(" ")[1]
            use.add_coins(callback.from_user.id, callback.message.chat.id, callback.message.chat.type, callback.message.date, callback.data)
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.json["message_id"])
            bot.send_message(callback.message.chat.id, f"Ты выиграл {callback.data} 💵 монет.")
            menu(callback.message)

        else:
            bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.json["message_id"]-1)
            not_understand(callback.message)


@bot.callback_query_handler(func=lambda callback: callback.data == "daily")
def daily_bonus(callback):
    daily_list = ["5", "5", "5", "10", "10", "10", "15", "15", "20", "25"]
    bonus = rm.choice(daily_list)

    use.add_daily_bonus(callback.message.chat.type, callback.from_user.id, callback.message.chat.id, callback.message.date, bonus)
    bot.send_message(callback.message.chat.id, f"Ты получил ежедневный бонус в размере {bonus} монет💵.")
    menu(callback.message)


@bot.callback_query_handler(func=lambda callback: callback.data == "statistics")
def statistics(callback):
    bot.send_message(callback.message.chat.id, callback.data+str(" статистика"))

    stat_player = use.statistics(callback.from_user.id)
    data_stat = [
        f"Всего игр: {stat_player[0][0]} 🎰",
        f"Всего полученных ежедневных бонусов: {stat_player[1][0]} 🗓️",
    ]

    ready_stat = ""
    for i in data_stat:
        ready_stat += str(i) + "\n"

    bot.send_message(callback.message.chat.id, ready_stat)


@bot.callback_query_handler(func=lambda callback: callback.data == "info")
def info(callback):
    got_info = use.info(callback.message.chat.type, callback.from_user.id, callback.message.chat.id)

    player_info = [
        f"Информация про тебя:\n",
        f"Имя: {got_info[0][2]}",
        f"Фамилия: {got_info[0][3]}",
        f"Username: @{got_info[0][4]}",
        f"ID твоего аккаунта: {got_info[0][0]}",
        f"Ты присоединился к игре: {got_info[0][8]}",
        f"У тебя монет: {got_info[0][9]}\n"
    ]

    ready_info = ""
    for i in player_info:
        ready_info += str(i) + "\n"

    if callback.message.chat.type == "supergroup":
        group_info = [
            f"Имя группы: {got_info[1][1]}",
            f"Количество играющих участников: {got_info[1][2]}",
            f"ID группы: {got_info[1][0]}",
            f"Монет у группы: {got_info[1][3]}"
        ]
        for i in group_info:
            ready_info += str(i) + "\n"

    info_kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Пригласить друга", switch_inline_query="\nНапиши команду: /start")
    btn2 = types.InlineKeyboardButton(text="Добавить в группу", switch_inline_query="\nНапиши команду: /start")
    info_kb.add(btn1, btn2)

    print(ready_info)
    bot.send_message(callback.message.chat.id, ready_info, reply_markup=info_kb)

    # @bot.callback_query_handler(func=lambda callback: callback.data == "forward_to")
    # def forward_to(callback):
    #     use.info_forward_to(callback.message.from_user.id)

    #     bot.send_message(callback.message.chat.id, "Спасибо за то что пригласил нового участника, ты получил свою награду: 250💵")

    menu(callback.message)

@bot.callback_query_handler(func=lambda callback: callback.data == "leader_menu")
def leader(callback):
    """Таблица лидеров: этой группы, всех игроков, всех групп"""

    # buttons_data_list
    bdl = [
        ("Глобальный Топ игроков в мире:", "Глобальный Топ игроков", "global_players"),  # 0
        ("Топ игроков в этой группе:", "Топ игроков в чате", "this_group"),              # 1
        ("Глобальный топ групп в мире:", "Глобальный топ групп", "global_groups")        # 2
    ]

    def reply_msg_top(callback, num, msg_title_data, btn1_data, btn2_data, top_num):
        leader_kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text=btn1_data[1], callback_data=btn1_data[2])
        btn2 = types.InlineKeyboardButton(text=btn2_data[1], callback_data=btn2_data[2])
        btn_back = types.InlineKeyboardButton(text="Назад в меню ↩️", callback_data="back")
        leader_kb.add(btn1, btn2)
        leader_kb.row(btn_back)

        got_top = use.get_leader(callback.from_user.id, callback.message.chat.id, callback.message.chat.type)

        list_top = [
            f"{msg_title_data[0]}"
        ]

        list_smile = ["🥇", "🥈", "🥉", " ", " "]
        x = 0
        while x != 10:
            try:
                list_top.append(f"{x+1}. {got_top[num][x][1]}, {got_top[num][x][-1]} {list_smile[x]}")
            except IndexError:
                break

            x = x + 1

        list_top.append(f"\nМесто в топе: {got_top[-1][top_num]}")

        ready_leader = ""
        for i in list_top:
            ready_leader += str(i) + "\n"

        bot.send_message(callback.message.chat.id, ready_leader, reply_markup=leader_kb)

    reply_msg_top(callback, 0, bdl[0], bdl[1], bdl[2], 0)

    @bot.callback_query_handler(func=lambda callback: callback.data == "global_players")
    def top_players(callback):
        reply_msg_top(callback, 0, bdl[0], bdl[1], bdl[2], 0)

    @bot.callback_query_handler(func=lambda callback: callback.data == "global_groups")
    def global_groups(callback):
        if callback.message.chat.type == "supergroup":
            reply_msg_top(callback, 2, bdl[2], bdl[0], bdl[1], 1)
        elif callback.message.chat.type == "private":
            bot.send_message(callback.message.chat.id, "Ты не в группе! Добавь бота в любую группу, чтобы эта кнопка заработала.")
            menu(callback.message)

    @bot.callback_query_handler(func=lambda callback: callback.data == "this_group")
    def top_this_group(callback):
        if callback.message.chat.type == "supergroup":
            reply_msg_top(callback, 1, bdl[1], bdl[0], bdl[2], 2)
        else:
            bot.send_message(callback.message.chat.id, "Ты не в группе! Добавь бота в любую группу, чтобы эта кнопка заработала.")
            menu(callback.message)

    @bot.callback_query_handler(func=lambda callback: callback.data == "back")
    def back(callback):
        menu(callback.message)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "Здесь ты можешь ввести команды: \n1./start \n2./menu \n...")

def handle(message):
	"""Прослушивание sql запроса из admin (либо слушает функции not_understand)"""
	if message.from_user.id == MYID:
		done = use.handle_command(message.text)

		if "Ошибка" in done[0:6]:
			bot.send_message(message.chat.id, done)
		else:
			v=""
			for i in done:
				for j in i:
					v = v + str(j)+", "
				v = v + str("\n")

			bot.send_message(message.chat.id, v)
			bot.send_message(message.chat.id, "Все готово")

		menu(message)

	else:
		not_admin(message)
		print("not admin(cmd)")

@bot.message_handler(commands=["admin"])
def admin(message):
	if message.from_user.id == MYID:
		akb = types.InlineKeyboardMarkup()
		cmd_btn = types.InlineKeyboardButton(text="/ Ввести команду /", callback_data="cmd")
		mailing_btn = types.InlineKeyboardButton(text="Рассылка 📧", callback_data="mail")
		coins4me_btn = types.InlineKeyboardButton(text="Монеты мнe not_work", callback_data="more_coins")
		add_sb = types.InlineKeyboardButton(text="Монеты игроку 💸 not work", callback_data="sb_money")
		back = types.InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")

		akb.row(cmd_btn, mailing_btn)
		akb.row(coins4me_btn, add_sb)
		akb.add(back)

		bot.send_message(message.chat.id, "Админ панель", reply_markup=akb)

		@bot.callback_query_handler(func=lambda callback: callback.data == "cmd")
		def cmd(callback):
			back_kb = types.InlineKeyboardMarkup()
			back_btn = types.InlineKeyboardButton(text="Back", callback_data="back")
			back_kb.add(back_btn)

			admin_cmd = bot.send_message(callback.message.chat.id, "Введи команду", reply_markup=back_kb)
			bot.register_next_step_handler(admin_cmd, handle)

		@bot.callback_query_handler(func=lambda callback: callback.data == "mail")
		def mailing_bot(callback):

			if callback.from_user.id == MYID:
				x = use.mailing()

				def handling_file(message):
					not_recieved = []
					bot.send_message(message.chat.id, "Запуск рассылки")
					if message.content_type == "photo":
						# bot.send_photo(message.chat.id, photo=message.json["photo"][0]["file_id"], caption=message.caption, parse_mode="HTML")

						for id in x:
							try:
								bot.send_photo(id, photo=message.json["photo"][0]["file_id"], caption=message.caption, parse_mode="HTML")
							except:
								use.if_id_not_exists(telegram_id=id[0])
								not_recieved.append(id)

					elif message.content_type == "video":
						# bot.send_video(message.chat.id, video=message.json["video"]["file_id"], caption=message.caption, parse_mode="HTML")
						for id in x:
							try:
								bot.send_video(id, photo=message.json["video"][0]["file_id"], caption=message.caption, parse_mode="HTML")
							except:
								use.if_id_not_exists(telegram_id=id[0])
								not_recieved.append(id)

					elif message.content_type == "text":
						# bot.send_message(message.chat.id, message.text)
						for id in x:
							try:
								print(id)
								bot.send_message(id[0], message.text)
								print(id)
							except:
								print(id)
								use.if_id_not_exists(telegram_id=id[0])
								not_recieved.append(id)
								print(id)

					elif message.content_type == "document":
						# bot.send_document(message.chat.id, message.json["document"]["file_id"], caption=message.caption)
						for id in x:
							try:
								bot.send_document(id, message.json["document"]["file_id"], caption=message.caption)
							except:
								use.if_id_not_exists(telegram_id=id[0])
								not_recieved.append(id)

					elif message.content_type == "voice":
						# bot.send_document(message.chat.id, message.json["voice"]["file_id"], caption=message.caption)
						for id in x:
							try:
								bot.send_voice(id, message.json["voice"]["file_id"], caption=message.caption)
							except:
								use.if_id_not_exists(telegram_id=id[0])
								not_recieved.append(id)

					else:
						bot.send_message("Я не знаю такого формата файла")

					bot.send_message(message.chat.id, f"Готово, кол-во получателей: {len(x)}. \n Кол-во неполучивших сообщение участников(не существует id):\n")
					if not_recieved != []:
						string_of_not_recieved = "Кол-во неполучивших сообщение участников(не существует id): \n"
						for i in not_recieved:
							string_of_not_recieved += str(i) + "\n"
						bot.send_message(message.chat.id, string_of_not_recieved)

				mail_file = bot.send_message(callback.message.chat.id, "Что разослать? (фото/видео, или просто текст)")
				bot.register_next_step_handler(mail_file, handling_file)

		@bot.callback_query_handler(func=lambda callback: callback.data == "back")
		def back(callback):
			if callback.from_user.id == MYID:
				menu(callback.message)
		"""
		@bot.callback_query_handler(func=lambda callback: callback.data == "more_coins")
		def coinsforme(callback):
			print("admin>coinsforme 1")
			if message.from_user.id == MYID:
					
				print("admin>coinsforme 1>if")
				def give_coins4me(message):
					try:
						message.text = int(message.text)
					except ValueError:
						print("valer")
						c4m = bot.send_message(message.chat.id, "Только цифры! Еще раз.")
						bot.register_next_step_handler(c4m, give_coins4me)
					print("admin>coinsforme 1>if>give_coins4me")
					if message.text == str and message.from_user.id == MYID:
						use.add_coins4me(message.text)
						print("all yes")
					elif message.from_user.id != MYID:
						print("!= MYID")
						not_admin(message)
					elif message.text != int:
						print("incorrect")
						print(message.text==str, message.from_user.id==MYID)
					use.add_coins4me(message.text)
				cfm = bot.send_message(callback.message.chat.id, "Сколько?")
				bot.register_next_step_handler(cfm, give_coins4me)
			else:
				print("admin>coinsforme 2")
				not_admin(message)
		"""
	else:
		not_admin(message)

sql_cmds = ["SELECT", "UPDATE", "INSERT", "DROP", "FROM", "DELETE"]
@bot.message_handler(content_types=["text", "photo", "video", "sticker", "emoji"])
def not_understand(message):
    if str(message.text).split(" ")[0].upper() in sql_cmds:
        handle(message)
    else:
        bot.send_message(message.chat.id, "Я тебя не понимаю, напиши /help")


bot.infinity_polling()