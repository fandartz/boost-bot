from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#Пользовательское меню
btnUsers = KeyboardButton('👤Профиль')
btnPrizes = KeyboardButton('🎁Список наград')
btnBalance = KeyboardButton('🍀Баланс сотрудников')
UsermainMenu = ReplyKeyboardMarkup(resize_keyboard = True).add(btnUsers, btnPrizes, btnBalance)