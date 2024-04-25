from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#Админ меню
btnUsers = KeyboardButton('👤Пользователи')
btnPrizes = KeyboardButton('🎁Награды')
btnSms = KeyboardButton('📬Рассылка')
btnBalance = KeyboardButton('🍀Баланс сотрудников')
mainMenu = ReplyKeyboardMarkup(resize_keyboard = True).add(btnUsers, btnPrizes, btnSms, btnBalance)

