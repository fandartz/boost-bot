import sqlite3 as sq

db = sq.connect('db.db')
cur = db.cursor()

#Запуск БД
async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "userid INTEGER,"
                "name TEXT,"
                "username TEXT,"
                "is_admin INTEGER,"
                "balance INTEGER,"
                "history TEXT(10000))")
    cur.execute("CREATE TABLE IF NOT EXISTS prizes("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "name TEXT,"
                "price INTEGER,"
                "count INTEGER)")
    db.commit()
    
#добавление пользователя в БД
async def cmd_start_db(user_id, user_name, username, is_admin):
    user = cur.execute(f"SELECT * FROM accounts WHERE userid == {user_id}").fetchone()
    if not user:
        cur.execute("INSERT INTO accounts (userid, name, username, is_admin, balance) VALUES (?, ?, ?, ?, ?);", (user_id, f"{user_name}", f"{username}", is_admin, 0))
        db.commit()

#Проверка на админа
async def check_admin(user_id):
    user = cur.execute('SELECT is_admin FROM accounts WHERE userid = ?',(user_id,))
    result = cur.fetchone()[0]
    return result

#Назначить админом
async def make_admin(admin, user_id):
    user = cur.execute("UPDATE accounts SET is_admin = ? WHERE userid = ?", (admin, user_id,))
    result = cur.fetchall()
    return result

#Получение id админов
async def admin_ids():
    user = cur.execute('SELECT userid FROM accounts WHERE is_admin = 1')
    result = cur.fetchall()
    return result

#получение id и имя аккаунта
async def users():
    user = cur.execute('SELECT name, userid, is_admin, balance FROM accounts')
    result = cur.fetchall()
    return result

#получение данных об аккаунте
async def users_info(user_id):
    user = cur.execute('SELECT name, username, is_admin, balance, history FROM accounts WHERE userid = ?',(user_id,))
    result = cur.fetchall()
    return result

#Смена имени пользователя
async def update_user(user_id, name):
    user = cur.execute("UPDATE accounts SET name = ? WHERE userid = ?", (name, user_id,))
    db.commit()

#обновление баланса
async def update_balance(user_id, summ):
    user = cur.execute("UPDATE accounts SET balance = ? WHERE userid = ?", (summ, user_id,))
    db.commit()

#получение товаров
async def get_prizes():
    user = cur.execute('SELECT id, name, price, count FROM prizes')
    result = cur.fetchall()
    return result

#получение данных о товаре
async def prizes_info(id):
    user = cur.execute('SELECT name, price, count FROM prizes WHERE id = ?',(id,))
    result = cur.fetchall()
    return result

#Удаление товаров
async def remove_prizes(id):
    cur.execute('DELETE FROM prizes WHERE id = ?',(id,))
    db.commit()

#Удаление пользователя
async def remove_user(id):
    cur.execute('DELETE FROM accounts WHERE userid = ?',(id,))
    db.commit()


#Добавление товара
async def add_prize(name, price, count):
    cur.execute("INSERT INTO prizes (name, price, count) VALUES (?, ?, ?);", (f"{name}", price, count))
    db.commit()

#обновление суммы награды
async def update_prize(id, summ):
    user = cur.execute("UPDATE prizes SET price = ? WHERE id = ?", (summ, id,))
    db.commit()

#обновление кол-во наград
async def update_prize_count(id, count):
    user = cur.execute("UPDATE prizes SET count = ? WHERE id = ?", (count, id,))
    db.commit()

#получение истории
async def get_history(userid):
    user = cur.execute('SELECT history FROM accounts WHERE userid = ?',(userid,))
    result = cur.fetchone()[0]
    return result

#Добавление истории
async def history_add(user_id, history):
    user = cur.execute("UPDATE accounts SET history = ? WHERE userid = ?", (history, user_id,))
    db.commit()

#Очистка истории
async def history_clear(user_id, history):
    user = cur.execute("UPDATE accounts SET history = ? WHERE userid = ?", (history, user_id,))
    db.commit()


