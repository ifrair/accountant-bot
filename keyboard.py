from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

Main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Пересчитать"), KeyboardButton(text='Проверить баланс')],
    [KeyboardButton(text="Добавить"), KeyboardButton(text='Вычесть')],
    [KeyboardButton(text='Добавить ученика'), KeyboardButton(text='Удалить ученика')]
],
    resize_keyboard=True
                            )
Add_edit = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='Заново давай', callback_data = 'wrong')],
    [InlineKeyboardButton(text='Все ок', callback_data= 'add_ok')]
])
Sub_edit = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='Заново давай', callback_data = 'wrong')],
    [InlineKeyboardButton(text='Все ок', callback_data='sub_ok')]
])

Add_new = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text='Да', callback_data='yes'), InlineKeyboardButton(text="Нет", callback_data='no')]
])