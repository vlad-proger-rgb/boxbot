import sqlite3 as sq
import traceback
import sys


def create_tables():
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()

		cur.execute("""CREATE TABLE IF NOT EXISTS users(
			telegram_id INTEGER PRIMARY KEY,
			group_id INTEGER,
			first_name TEXT,
			last_name TEXT,
			username TEXT,
			is_bot TEXT,
			language_code TEXT,
			is_premium TEXT,
			joined_game INTEGER,
			coins INTEGER NOT NULL DEFAULT 0
		)""")
		cur.execute("""CREATE TABLE IF NOT EXISTS groups(
			group_id INTEGER PRIMARY KEY,
			group_name TEXT,
			users_count INTEGER,
			group_coins INTEGER NOT NULL DEFAULT 0
		)""")
		cur.execute("""CREATE TABLE IF NOT EXISTS history_games(
			game_id INTEGER PRIMARY KEY,
			telegram_id INTEGER,
			game_date INTEGER,
			game_coins INTEGER
		)
		""")
		cur.execute("""CREATE TABLE IF NOT EXISTS history_daily(
			daily_id INTEGER PRIMARY KEY,
			telegram_id INTEGER,
			daily_date INTEGER,
			daily_coins INTEGER
		)""")

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		con.close()


def db_table_val(type: str, group_id: str, group_name: str, tele_id: str, first_name: str, last_name: str, username: str, is_bot: str, lang_code: str, is_premium: str, joined_game: str):
	"""Записывает данные пользователя, IntegrityError"""
	def update_group_by_id():
		count_of_group = cur.execute("SELECT count(telegram_id), sum(coins) FROM users WHERE group_id = ?", (group_id,))
		data_of_group = count_of_group.fetchall()[0]

		update_group = "UPDATE groups SET group_name = ?, users_count = ?, group_coins = ? WHERE group_id = ?"
		data_update = (group_name, data_of_group[0], data_of_group[1], group_id)
		cur.execute(update_group, data_update)

	def update_user_by_id():
		update_data_by_tg_id = "UPDATE users SET group_id = ?, first_name = ?, last_name = ?, username = ?, is_bot = ?, language_code = ?, is_premium = ? WHERE telegram_id = ?"
		data = (group_id, first_name, last_name, username, is_bot, lang_code, is_premium, tele_id)
		cur.execute(update_data_by_tg_id, data)
		con.commit()

	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()
		cur.execute("INSERT INTO users(telegram_id) VALUES(?)", (tele_id,))
		con.commit()

		update_user_by_id()

		update_joined = "UPDATE users SET joined_game = ? WHERE telegram_id = ?"
		data_joined = (joined_game, tele_id)
		cur.execute(update_joined, data_joined)

		if type == "supergroup":
			cur.execute("INSERT INTO groups(group_id) VALUES(?)", (group_id,))
			update_group_by_id()

		con.commit()
		cur.close()

	except sq.IntegrityError:
		print("Не уникальный id")
		update_user_by_id()
		con.commit()

		if type == "supergroup":
			try:
				cur.execute("INSERT INTO groups(group_id) VALUES(?)", (group_id,))
				update_group_by_id()
			except sq.IntegrityError:
				update_group_by_id()

		con.commit()
		cur.close()
		print("Значения добавлены в таблицу(старт, except Integrity Error)")

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con: con.close()


def add_coins(telegram_id: int, group_id: str, type: str, message_date: int, new_coins: int):
	"""Добавляет монеты в таблицу (Играть)"""
	try:
		con = sq.connect("database.db")
		cur = con.cursor()

		add_coins_command = "UPDATE users SET coins = coins + ? WHERE telegram_id = ?"
		data_1 = (new_coins, telegram_id)
		cur.execute(add_coins_command, data_1)
		con.commit()

		add_to_games = "INSERT INTO history_games(telegram_id, game_date, game_coins) VALUES(?, ?, ?)"
		data_2 = (telegram_id, message_date, new_coins)
		cur.execute(add_to_games, data_2)

		if type == "supergroup":
			cur.execute("UPDATE groups SET group_coins = (SELECT sum(coins) FROM users WHERE group_id = ?) WHERE group_id = ?", (group_id, group_id))

		con.commit()
		cur.close()
		print(f"Добавлено {new_coins} монет в таблицу игроку {telegram_id}")

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
			print("Соединение с SQLite закрыто(Добавление монет в таблицу)")


def add_daily_bonus(type: str, telegram_id: str, group_id: str, bonus_date: str, bonus: str):
	"""Добавление ежедневного бонуса в таблицы users и daily_history"""
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()

		daily_add_users = "UPDATE users SET coins = coins + ? WHERE telegram_id = ?"
		vars_daily_users = (bonus, telegram_id)
		cur.execute(daily_add_users, vars_daily_users)

		if type == "supergroup":
			cur.execute("UPDATE groups SET group_coins = (SELECT sum(coins) FROM users WHERE group_id = ?) WHERE group_id = ?", (group_id, group_id))

		daily_add_history = "INSERT INTO history_daily(telegram_id, daily_date, daily_coins) VALUES(?, ?, ?)"
		vars_daily_history = (telegram_id, bonus_date, bonus)
		cur.execute(daily_add_history, vars_daily_history)

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
			print("Соединение с SQLite закрыто(Ежедневный бонус в таблицу)")

def statistics(telegram_id):
	try:
		con = sq.connect("database.db")
		cur = con.cursor()

		count_of_games = cur.execute("SELECT count(telegram_id) FROM history_games WHERE telegram_id = ?", (telegram_id,)).fetchall()
		print(count_of_games)

		count_of_daily = cur.execute("SELECT count(telegram_id) FROM history_daily WHERE telegram_id = ?", (telegram_id,)).fetchall()
		print(count_of_daily)

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
			count_of_games.append(count_of_daily[0])
			print(count_of_games)
			print("Соединение с SQLite закрыто(Статистика finally)")
			return count_of_games



def get_leader(telegram_id: str, group_id: str, type: str):
	"""
	Таблица лидеров
	"""
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()

		players = cur.execute("""
			SELECT telegram_id, first_name, username, coins 
			FROM users 
			ORDER BY coins DESC
			LIMIT 5
		""")
		players = players.fetchall()

		groups = cur.execute("""
			SELECT group_id, group_name, users_count, group_coins 
			FROM groups 
			ORDER BY group_coins DESC
			LIMIT 5
		""")
		groups = groups.fetchall()

		players_in_group = cur.execute("""
			SELECT telegram_id, first_name, coins
			FROM users WHERE group_id = ?
			ORDER BY coins DESC
			LIMIT 5
		""", (group_id,))
		players_in_group = players_in_group.fetchall()


		player_list_info = [] # место игрока в топах
		res_list = [players, groups, player_list_info]


		x1 = 0
		for player_info in players:
			if player_info[0] == telegram_id:
				res_list[-1].append( x1 + 1 ) # место в топе
			x1 += 1

		x2 = 0
		for group in groups:
			if type == "supergroup":
				if group[0] == group_id:
					res_list[-1].append( x2 + 1 )

			x2 += 1


		if type == "supergroup":

			cur.execute("""
				SELECT telegram_id, first_name, coins
				FROM users WHERE group_id = ?
				ORDER BY coins DESC
			""", (group_id,))

			players_in_group = cur.fetchall()

			x3 = 0
			for player in players_in_group:
				if player[x3] == telegram_id:
					res_list[-1].append( x3 + 1 )
				x3 += 1

			res_list.insert(1, players_in_group)

			res_list[-1].append(players_in_group[2])


		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
			print(res_list)
			print("Соединение с SQLite закрыто(таблица лидеров)")
			return res_list


def handle_command(cmd_text: str):
	"""
	Обрабатывается sql-запрос из сообщения
	если есть слово myid, заменяется на 1401875023
	если ошибка в запросе, то отправляется текст ошибки
	"""
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()

		if "myid" in cmd_text.split(" "):
			r = ""
			for i in cmd_text.split(" "):
				if i == "myid":
					i = 1401875023
				r = r + str(i) + " "

			cmd_text = r

		done = cur.execute(cmd_text)
		done = done.fetchall()

		if done == []:
			done = [ ["Запрос выполнен"] ]

		con.commit()
		cur.close()

	except sq.Error as error:
		exc = [
			f"Ошибка при работе с SQLite: {error}",
			f"Класс исключения: {error.__class__}",
			f"Исключение: {error.args}",
		]
		done = ""
		for i in exc:
			done += str(i) + "\n"

	finally:
		if con:
			con.close()
			print("admin cmd hadle_command finally")
			return done

def mailing():
	try:
		con = sq.connect("database.db")
		cur = con.cursor()

		users_to_mailing = cur.execute("SELECT telegram_id FROM users").fetchall()
		groups_to_mailing = cur.execute("SELECT group_id FROM groups").fetchall()

		users_to_mailing.append(groups_to_mailing[0])
		print(users_to_mailing)

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		con.close()	
		print("admin mailing finally")
		return users_to_mailing

def if_id_not_exists(telegram_id: str):
	print("if_id_not_exists before")
	try:
		con = sq.connect("database.db")
		cur = con.cursor()

		cur.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		con.close()	
		print("admin mailing finally")


"""
def add_coins4me(how_coins: int):
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()
	
		cur.execute("UPDATE users SET coins = coins + ? WHERE telegram_id = 1401875023", (how_coins,))
		con.commit()
		cur.close()
		
	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
"""

def info(type: str, tele_id: str, group_id: str):
	try:
		con = sq.connect("database.db", check_same_thread=False)
		cur = con.cursor()

		select_user_info = cur.execute("SELECT * FROM users WHERE telegram_id = ?", (tele_id,))
		selected_data = select_user_info.fetchall()

		if type == "supergroup":
			select_group_info = cur.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
			select_group_info = select_group_info.fetchall()

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		if con:
			con.close()
			print("Соединение с SQLite закрыто(info finally)")
			try:
				selected_data.append(select_group_info[0])
			except UnboundLocalError:
				return selected_data
			except IndexError:
				return selected_data

			return selected_data


def info_forward_to(telegram_id):
	try:
		con = sq.connect("database.db")
		cur = con.cursor()

		cur.execute("UPDATE users SET coins = coins + 250 WHERE telegram_id = ?", (telegram_id, ))

		con.commit()
		cur.close()

	except sq.Error as error:
		print("Ошибка при работе с SQLite", error)
		print("Класс исключения: ", error.__class__)
		print("Исключение", error.args)
		print("Печать подробноcтей исключения SQLite: ")
		exc_type, exc_value, exc_tb = sys.exc_info()
		print(traceback.format_exception(exc_type, exc_value, exc_tb))

	finally:
		con.close()	
		print("info_forward_to finally")

create_tables()
print("DB created")
