from aiogram import Bot, Dispatcher, executor, types
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from admin_markup import mainMenu
from user_markup import UsermainMenu

import datetime
import func
import db

always_admin = 11111

TOKEN = 'token'
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class UserState(StatesGroup):
    userid = State()
    info = State()
    sum = State()

class UserState2(StatesGroup):
    userid = State()
    info = State()
    sum = State()

class PrizeState(StatesGroup):
    name = State()
    sum = State()
    count = State()

class EditPrizeState(StatesGroup):
    sum = State()
    count = State()
    id = State()

class Spam(StatesGroup):
    text = State()

class Sms(StatesGroup):
    id = State()
    sms = State()

class UserEdit(StatesGroup):
    id = State()
    name = State()

async def on_startup(_):
    await db.db_start()
    print('Бот запущен')

@dp.message_handler(commands=['start'])
async def bot_message(message: types.Message):

    if (message.from_user.id == always_admin):
        is_admin = 1
        await db.cmd_start_db(message.from_user.id, message.from_user.full_name, message.from_user.username, is_admin)
    else:
        is_admin = 0
        await db.cmd_start_db(message.from_user.id, message.from_user.full_name, message.from_user.username, is_admin)
    
    check = await db.check_admin(message.from_user.id)
    if (check == 1):
        await bot.send_message(message.chat.id, f"Здравствуйте! Выберите действие", reply_markup=mainMenu)
    else:
        await bot.send_message(message.chat.id, f"Здравствуйте! Выберите действие", reply_markup=UsermainMenu)

#Админ-часть --------------------------------------------------------------------------------------------------------------------
#----------------------------------------пользователи-------------------------------------------------------------
@dp.message_handler(text=['👤Пользователи'])
async def all_users(message: types.Message):

    check = await db.check_admin(message.from_user.id)
    if (check == 1):
        await message.answer("👤Выберите пользователя:", reply_markup=await func.get_users(0))


#Обработчик Далее/назад
@dp.callback_query_handler(text_startswith="users_swipe:", state="*")
async def NextOrBack(call: types.CallbackQuery, state: FSMContext):
    
    remover = int(call.data.split(":")[1])
    await call.message.edit_text("👤Выберите пользователя:", reply_markup=await func.get_users(remover))

#Обработчик Возврата к пользователям
@dp.callback_query_handler(text_startswith="back_to_users", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("👤Выберите пользователя:", reply_markup=await func.get_users(0))
    
#О пользователе
@dp.callback_query_handler(text_startswith="users_open:", state="*")
async def user_info(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    check = await db.check_admin(user_id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("➕Начислить бусты", callback_data=f"boosts_add:{user_id}"),
            InlineKeyboardButton("➖Списать бусты", callback_data=f"boosts_remove:{user_id}"),
        )
    keyboard.add(
            InlineKeyboardButton("📊Начисления/Списания", callback_data=f"stats:{user_id}"),
        )
    keyboard.add(
            InlineKeyboardButton("📬Личное сообщение", callback_data=f"sms:{user_id}:"),
        )
    if (check == 0):
        keyboard.add(
            InlineKeyboardButton("✏️Сменить имя", callback_data=f"set_name:{user_id}"),
            InlineKeyboardButton("🔧Назначить админиом", callback_data=f"set_admin:{user_id}:1"),
        )
    elif (check == 1):
        keyboard.add(
            InlineKeyboardButton("✏️Сменить имя", callback_data=f"set_name:{user_id}"),
            InlineKeyboardButton("🔧Убрать админа", callback_data=f"set_admin:{user_id}:0"),
        )
    keyboard.add(
            InlineKeyboardButton("🗑Удалить пользователя", callback_data=f"remove_user:{user_id}"),
        )
    keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"back_to_users"),
        )
    check = await db.users_info(user_id)
    if (check[0][2] == 1):
        admin = 'Да'
    else:
        admin = 'Нет'
    await call.message.edit_text(f"👤Выбран пользователь: {check[0][0]} \nАдминистратор: {admin} \nБаланс: {check[0][3]}🍀 \nДействия:", reply_markup=keyboard)

#Очистка истории
@dp.callback_query_handler(text_startswith="clear_history:", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"users_open:{user_id}"),
        )
    await db.history_clear(user_id, history=None)
    await call.message.edit_text("🗑 История очищена", reply_markup=keyboard)

#Удаление пользователя
@dp.callback_query_handler(text_startswith="remove_user:", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"back_to_users"),
        )
    await db.remove_user(user_id)
    await call.message.edit_text("🗑Пользователь удалён", reply_markup=keyboard)

#Назначение админом
@dp.callback_query_handler(text_startswith="set_admin:", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    admin = int(call.data.split(":")[2])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"back_to_users"),
        )
    await db.make_admin(admin, user_id)
    if (admin == 1):
        await call.message.edit_text("🔧Пользователь назначен админом", reply_markup=keyboard)
    elif (admin == 0):
        await call.message.edit_text("🔧Пользователь убран из админов", reply_markup=keyboard)

#История
@dp.callback_query_handler(text_startswith="stats:", state="*")
async def user_info(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    check = await db.users_info(user_id)
    arr = check[0][4]
    if arr != None:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"users_open:{user_id}"),
            InlineKeyboardButton("🗑 Очистить историю", callback_data=f"clear_history:{user_id}"),
        )
        parse = arr.strip('[]').split(',')
        history = ""
        for count in range(len(parse)):
            history = history + f"\n {parse[count]}"
        await call.message.edit_text(f"👤История пользователя: {history}", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"users_open:{user_id}"),
        )
        await call.message.edit_text(f"👤История пользователя: \nИстории пока что нет :(", reply_markup=keyboard)
#----------------------------------------бусты-------------------------------------------------------------
#Добавление бустов причина
@dp.callback_query_handler(text_startswith="boosts_add:", state="*")
async def add_boosts(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    await call.message.edit_text(f"Укажите причину")
    await state.update_data(userid=user_id)
    await UserState.info.set()

#Добавление бустов сумма
@dp.message_handler(state=UserState.info)
async def add_info(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)
    await message.answer("Укажите сумму начисления (числом)")
    await UserState.sum.set() # либо же UserState.adress.set()

#Зачисление бустов на баланс
@dp.message_handler(state=UserState.sum)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    data = await state.get_data()
    check = await db.users_info(data['userid'])
    today = datetime.date.today()

    list_users = await db.users()
    for count in range(len(list_users)):
        if (list_users[count][2] == 0):
            try:
                await bot.send_message(chat_id=list_users[count][1], text=f"👤Коллеге: {check[0][0]} \nНачислено: {data['sum']} 🍀\nПричина: {data['info']}")
            except:
                pass
    summ = check[0][3] + int(data['sum'])
    await db.update_balance(data['userid'], summ)
    
    if check[0][4] == None:
        sum = data['sum']
        info = data['info']
        history = f'{today}|Начислено:  {sum} 🍀|Причина: {info}'
    elif(check[0][4] == ''):
        sum = data['sum']
        info = data['info']
        history = f'{today}|Начислено:  {sum} 🍀|Причина: {info}'
    else:
        arr = check[0][4]
        parse = arr.strip('[]').split(',')
        sum = data['sum']
        info = data['info']
        history = ''
        for count in range(len(parse)):
            history = history + f'{parse[count]},'
        history = history + f'{today}|Начислено:  {sum} 🍀|Причина: {info}'
    await db.history_add(data['userid'], history)
    await state.finish()

    await message.answer("Баланс пользователя обновлён", reply_markup=mainMenu)

#Списание бустов
@dp.callback_query_handler(text_startswith="boosts_remove:", state="*")
async def remove_boosts(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split(":")[1])
    await call.message.edit_text(f"Укажите причину")
    await state.update_data(userid=user_id)
    await UserState2.info.set()

#Списание бустов сумма
@dp.message_handler(state=UserState2.info)
async def add_info(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)
    await message.answer("Укажите сумму списания (числом)")
    await UserState2.sum.set() # либо же UserState.adress.set()

#Списание бустов с баланса
@dp.message_handler(state=UserState2.sum)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    data = await state.get_data()
    check = await db.users_info(data['userid'])
    today = datetime.date.today()

    list_users = await db.users()
    for count in range(len(list_users)):
        if (list_users[count][2] == 0):
            try:
                await bot.send_message(chat_id=list_users[count][1], text=f"👤У коллеги: {check[0][0]} \nСписано: {data['sum']} 🍀\nПричина: {data['info']}")
            except:
                pass
    summ = check[0][3]-int(data['sum'])
    await db.update_balance(data['userid'], summ)
    
    if check[0][4] == None:
        sum = data['sum']
        info = data['info']
        history = f'{today}|Списано:  {sum} 🍀|Причина: {info}'
    elif(check[0][4] == ''):
        sum = data['sum']
        info = data['info']
        history = f'{today}|Списано:  {sum} 🍀|Причина: {info}'
    else:
        arr = check[0][4]
        parse = arr.strip('[]').split(',')
        sum = data['sum']
        info = data['info']
        history = ''
        for count in range(len(parse)):
            history = history + f'{parse[count]},'
        history = history + f'{today}|Списано:  {sum} 🍀|Причина: {info}'
    await db.history_add(data['userid'], history)
    await db.update_balance(data['userid'], summ)
    await state.finish()

    await message.answer("Баланс пользователя обновлён", reply_markup=mainMenu)



#----------------------------------------Товары-------------------------------------------------------------

@dp.message_handler(text=['🎁Награды'])
async def all_users(message: types.Message):

    check = await db.check_admin(message.from_user.id)
    if (check == 1):
        await message.answer("🎁Выберите награду:", reply_markup=await func.get_all_prizes(message.from_user.id, 0))


#О товаре
@dp.callback_query_handler(text_startswith="prize_open:", state="*")
async def prize_info(call: types.CallbackQuery, state: FSMContext):
    id_prize = int(call.data.split(":")[1])
    id = int(call.data.split(":")[2])
    check = await db.check_admin(id)
    if (check == 1):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✏️Редактировать", callback_data=f"prize_edit:{id_prize}"),
            InlineKeyboardButton("🗑Удалить", callback_data=f"prize_remove:{id_prize}:{id}"),
        )
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"back_to_prizes:{id}"),
        )
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("🛒Купить", callback_data=f"prize_buy:{id_prize}:{id}"),
        )
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"back_to_prizes:{id}"),
        )
    check2 = await db.prizes_info(id_prize)

    await call.message.edit_text(f"🎁Выбрана награда: {check2[0][0]} \nЦена: {check2[0][1]} 🍀 \nОсталось: {check2[0][2]} шт.\nВыберите действие", reply_markup=keyboard)

#Удаление товара
@dp.callback_query_handler(text_startswith="prize_remove:", state="*")
async def remove_prize(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    id2 = int(call.data.split(":")[2])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 К наградам", callback_data=f"back_to_prizes:{id2}"),
        )
    await db.remove_prizes(id)
    await call.message.edit_text(f"Награда удалена!", reply_markup=keyboard)

#Добавить награду название
@dp.callback_query_handler(text_startswith="prize_add", state="*")
async def add_prizename(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"Укажите название награды")
    await PrizeState.name.set()

#Добавить награду сумма
@dp.message_handler(state=PrizeState.name)
async def add_prizesum(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Укажите сумму награды (числом)")
    await PrizeState.sum.set() # либо же UserState.adress.set()

#Добавить награду сумма
@dp.message_handler(state=PrizeState.sum)
async def add_prizecount(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    await message.answer("Укажите количество наград(числом)")
    await PrizeState.count.set() # либо же UserState.adress.set()

#Добавление награды в базу
@dp.message_handler(state=PrizeState.count)
async def add_prizesum(message: types.Message, state: FSMContext):
    await state.update_data(count=message.text)
    data = await state.get_data()
    await db.add_prize(data['name'], int(data['sum']), int(data['count']))
    await state.finish()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 К наградам", callback_data=f"back_to_prizes:{message.from_user.id}"),
        )
    await message.answer("Награда добавлена", reply_markup=keyboard)

#Редактирование награды
@dp.callback_query_handler(text_startswith="prize_edit:", state="*")
async def prize_sum(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    await state.update_data(id=id)
    await call.message.edit_text("Укажите новую цену награды")
    await EditPrizeState.sum.set()

#Добавить награду сумма
@dp.message_handler(state=EditPrizeState.sum)
async def add_prizecount(message: types.Message, state: FSMContext):
    await state.update_data(sum=message.text)
    await message.answer("Укажите новое количество наград(числом)")
    await EditPrizeState.count.set() # либо же UserState.adress.set()

#Добавление награды в базу
@dp.message_handler(state=EditPrizeState.count)
async def prize_sum_edit(message: types.Message, state: FSMContext):
    await state.update_data(count=message.text)
    data = await state.get_data()
    await db.update_prize(int(data['id']), int(data['sum']))
    await db.update_prize_count(int(data['id']), int(data['count']))
    await state.finish()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
            InlineKeyboardButton("👈 К наградам", callback_data=f"back_to_prizes:{message.from_user.id}"),
        )
    await message.answer("Награда обновлена", reply_markup=keyboard)

#Обработчик Возврата к товарам
@dp.callback_query_handler(text_startswith="back_to_prizes:", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    await call.message.edit_text("🎁Выберите награду:", reply_markup=await func.get_all_prizes(id, 0))

#Обработчик Далее/назад в товарах
@dp.callback_query_handler(text_startswith="prize_swipe:", state="*")
async def NextOrBackPrize(call: types.CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    id = int(call.data.split(":")[2])
    await call.message.edit_text("🎁Выберите награду:", reply_markup=await func.get_all_prizes(id, remover))

#------------------------------------------------рассылка------------------------------------------------

@dp.message_handler(text=['📬Рассылка'])
async def spam_users(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👈 Отмена", callback_data=f"spam_cancel:{message.from_user.id}"),
    )
    check = await db.check_admin(message.from_user.id)
    if (check == 1):
        await message.answer("Отправьте ваше сообщение", reply_markup=keyboard)
        await Spam.text.set()

#Возврат в рассылке
@dp.callback_query_handler(text_startswith="spam_cancel:", state="*")
async def NextOrBackPrize(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    await state.reset_state()
    await call.message.delete()
    await call.message.answer("Отменено! Выберите действие", reply_markup=mainMenu)

#Возврат из ЛС
@dp.callback_query_handler(text_startswith="sms_back:", state="*")
async def NextOrBackPrize(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    await state.reset_state()
    await call.message.delete()
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👈 Вернуться", callback_data=f"users_open:{id}"),
    )
    await call.message.answer("Отменено", reply_markup=keyboard)

#Отправка сообщений всем юзерам
@dp.message_handler(content_types=['any'], state=Spam.text)
async def spam_all_users(message: types.Message, state: FSMContext):
    list_users = await db.users()
    for count in range(len(list_users)):
        if (list_users[count][2] == 0):
            try:
                await bot.copy_message(chat_id=list_users[count][1], from_chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass
    await state.finish()
    await message.answer("📬Сообщение успешно отправлено!", reply_markup=mainMenu)

#ЛС конкретному юзеру
@dp.callback_query_handler(text_startswith="sms:", state="*")
async def profile(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Отмена", callback_data=f"sms_back:{id}"),
    )
    await state.update_data(id=id)
    await call.message.edit_text("Отправьте ваше сообщение для данного пользователя", reply_markup=keyboard)
    await Sms.sms.set()

#Отправка лс конкретному юзеру
@dp.message_handler(content_types=['any'], state=Sms.sms)
async def spam_all_users(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data['id']
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👈 Вернуться", callback_data=f"users_open:{chat_id}"),
    )
    try:
        await bot.copy_message(chat_id=chat_id, from_chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass
    await state.finish()
    await message.answer("📬Сообщение успешно отправлено!", reply_markup=keyboard)
#Админка----------------------------------------------------------------------------------------------------

#Пользователи-----------------------------------------------------------------------------------------------
#Профиль
@dp.message_handler(text=['👤Профиль'])
async def user_profile(message: types.Message):
    check = await db.users_info(message.from_user.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✏️Установить имя", callback_data=f"set_name:{message.from_user.id}"),
    )
    keyboard.add(
        InlineKeyboardButton("📊Начисления.Списания", callback_data=f"user_stat:{message.from_user.id}"),
    )
    await message.answer(f"👤Ваш профиль:\nВаше имя: {check[0][0]} \nВаш баланс: {check[0][3]}🍀 \nВыберите действие:", reply_markup=keyboard)


#Редактирование профиля
@dp.callback_query_handler(text_startswith="set_name:", state="*")
async def profile(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split(":")[1])
    await state.update_data(id=id)
    await call.message.edit_text("Введите желаемое имя:")
    await UserEdit.name.set()

#Установка имени
@dp.message_handler(state=UserEdit.name)
async def change_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    id=data['id']
    await db.update_user(id, data['name'])
    await state.finish()
    check = await db.check_admin(message.from_user.id)
    if (check == 1):
        await message.answer("Имя изменено!", reply_markup=mainMenu)
    else:
        await message.answer("Имя изменено!", reply_markup=UsermainMenu)


#История
@dp.callback_query_handler(text_startswith="user_stat:", state="*")
async def user_info(call: types.CallbackQuery, state: FSMContext,):
    user_id = int(call.data.split(":")[1])
    check_hist = await db.get_history(user_id)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👈 Выход", callback_data="user_back"),
    )

    check = await db.users_info(user_id)
    arr = check[0][4]
    if arr != None:
        parse = arr.strip('[]').split(',')
        history = ""
        for count in range(len(parse)):
            history = history + f"\n {parse[count]}"
        await call.message.edit_text(f"👤История: {history}", reply_markup=keyboard)
    else:
        await call.message.edit_text(f"👤История: \nИстории пока что нет :(", reply_markup=keyboard)

#Обработчик Возврата у пользователя
@dp.callback_query_handler(text_startswith="user_back", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Здравствуйте! Выберите действие:", reply_markup=UsermainMenu)

#Список наград для пользователя
@dp.message_handler(text=['🎁Список наград'])
async def all_users(message: types.Message):
    await message.answer("🎁Выберите награду:", reply_markup=await func.get_all_prizes(message.from_user.id, 0))


#Покупка награды
@dp.callback_query_handler(text_startswith="prize_buy:", state="*")
async def Back(call: types.CallbackQuery, state: FSMContext):
    id_prize = int(call.data.split(":")[1])
    id = int(call.data.split(":")[2])
    today = datetime.date.today()

    prizes = await db.prizes_info(id_prize)
    if (prizes[0][2] > 0):
        user = await db.users_info(id)
        if (user[0][3]>=prizes[0][1]):
            new_count = prizes[0][2] - 1
            new_balance = user[0][3] - prizes[0][1]
            await db.update_balance(id, new_balance)
            await db.update_prize_count(id_prize, new_count)
            await call.message.edit_text("🎁Награда приобретена!")
            list_users = await db.users()
            for count in range(len(list_users)):
                try:
                    await bot.send_message(chat_id=list_users[count][1], text=f"👤Коллега: {user[0][0]} \n🎁Приобрёл: {prizes[0][0]}")
                except:
                    pass
            if user[0][4] == None:
                history = f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            elif(user[0][4] == ''):
                history = f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            else:
                arr = user[0][4]
                parse = arr.strip('[]').split(',')
                history = ''
                for count in range(len(parse)):
                    history = history + f'{parse[count]},'
                history = history + f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            await db.history_add(id, history)
        else:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("👈 К наградам", callback_data=f"back_to_prizes:{id}"),
            )
            await call.message.edit_text("Недостаточно средств :(", reply_markup=keyboard)
    elif (prizes[0][2] == 1):
        user = await db.users_info(id)
        if (user[0][3]>=prizes[0][1]):
            new_count = prizes[0][2] - 1
            new_balance = user[0][3] - prizes[0][1]
            await db.update_balance(id, new_balance)
            await db.remove_prizes(id_prize)
            await call.message.edit_text("🎁Награда приобретена!")
            list_users = await db.admin_ids()
            for count in range(len(list_users)):
                try:
                    await bot.send_message(chat_id=list_users[count][0], text=f"👤Коллега: {user[0][0]} \n🎁Приобрёл: {prizes[0][0]}")
                except:
                    pass
            if user[0][4] == None:
                history = f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            elif(user[0][4] == ''):
                history = f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            else:
                arr = user[0][4]
                parse = arr.strip('[]').split(',')
                history = ''
                for count in range(len(parse)):
                    history = history + f'{parse[count]},'
                history = history + f'{today}|Покупка: {prizes[0][0]}|Сумма: {prizes[0][1]}🍀'
            await db.history_add(id, history)
    elif (prizes[0][2] == 0):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("👈 К наградам", callback_data=f"back_to_prizes:{id}"),
        )
        await call.message.edit_text("🎁Данная награда закончилась :(", reply_markup=keyboard)

#Список баланса всех пользователей
@dp.message_handler(text=['🍀Баланс сотрудников'])
async def all_users(message: types.Message):
    check2 = await db.users()
    balance = ''
    for count in range(len(check2)):
        balance = balance + f"\nСотрудник: {check2[count][0]}. Баланс: {check2[count][3]}🍀"
    check = await db.check_admin(message.from_user.id)
    
    if (check == 1):
        await message.answer(f"Баланс всех сотрудников: {balance}", reply_markup=mainMenu)
    else:
        await message.answer(f"Баланс всех сотрудников: {balance}", reply_markup=UsermainMenu)
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)