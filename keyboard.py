from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Пересчитать балансы"), KeyboardButton(text='Проверить баланс')],
    [KeyboardButton(text="Пополнить баланс"), KeyboardButton(text='Вычесть баланс')],
    [KeyboardButton(text='Добавить ученика'), KeyboardButton(text='Удалить ученика')]
],
    resize_keyboard=True
                            )
change_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заново давай', callback_data='wrong')],
    [InlineKeyboardButton(text='Все ок', callback_data='approved')]
])

add_new = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes'), InlineKeyboardButton(text="Нет", callback_data='no')]
])
