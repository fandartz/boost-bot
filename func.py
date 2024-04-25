from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import db
import math
#Вывод всех пользователей
async def get_users(remover):

    list_users = await db.users()
    keyboard = InlineKeyboardMarkup()
    if remover >= len(list_users): remover -= 5

    for count, a in enumerate(range(remover, len(list_users))):
        if count < 5:
            keyboard.add(InlineKeyboardButton(f"👤 {list_users[a][0]}", callback_data=f"users_open:{list_users[a][1]}"))
    
    #Если пользователей меньше 5, то нет кнопок далее/назад
    if len(list_users) <= 5:
        pass
    #Если больше 5 и это 1 страница, то кнопка далее
    elif len(list_users) > 5 and remover < 5:
        keyboard.add(
            InlineKeyboardButton(f"💎 ", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"users_swipe:{remover + 5}"),
        )
    #Если последняя страница, то кнопка назад
    elif remover + 5 >= len(list_users):
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"users_swipe:{remover - 5}"),
            InlineKeyboardButton(f"💎 ", callback_data="..."),
        )
    #Если есть ещё пользователи, то кнопки назад и далее
    else:
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"users_swipe:{remover - 5}"),
            InlineKeyboardButton(f"💎 ", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"users_swipe:{remover + 5}"),
        )

    return keyboard


#Вывод Товаров
async def get_all_prizes(id, remover):
    check_admin = await db.check_admin(id)
    list_prize = await db.get_prizes()
    keyboard = InlineKeyboardMarkup()
    if remover >= len(list_prize): remover -= 5
    if len(list_prize) == 0:
        keyboard.add(
            InlineKeyboardButton(f"💎 Пока что нет наград :( 💎", callback_data="..."),
        )
    else:
        for count, a in enumerate(range(remover, len(list_prize))):
            if count < 5:
                keyboard.add(
                    InlineKeyboardButton(f"🎁 {list_prize[a][1]}", callback_data=f"prize_open:{list_prize[a][0]}:{id}"),
                )
    
    #Если товаров меньше 5, то нет кнопок далее/назад
    if len(list_prize) <= 5:
        pass
    #Если товаров 5 и это 1 страница, то кнопка далее
    elif len(list_prize) > 5 and remover < 5:
        keyboard.add(
            InlineKeyboardButton(f"💎 ", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"prize_swipe:{remover + 5}:{id}"),
        )
    #Если последняя страница, то кнопка назад
    elif remover + 5 >= len(list_prize):
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"prize_swipe:{remover - 5}:{id}"),
            InlineKeyboardButton(f"💎 ", callback_data="..."),
        )
    #Если есть ещё товары, то кнопки назад и далее
    else:
        keyboard.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"prize_swipe:{remover - 5}:{id}"),
            InlineKeyboardButton(f"💎 ", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"prize_swipe:{remover + 5}:{id}"),
        )
    if (check_admin == 1):
        keyboard.add(
            InlineKeyboardButton(f"➕Добавить награду", callback_data="prize_add"),
        )
    return keyboard