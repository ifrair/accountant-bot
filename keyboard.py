from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Пересчитать балансы"), KeyboardButton(text='Проверить балансы')],
    [KeyboardButton(text="Пополнить баланс"), KeyboardButton(text='Вычесть баланс')],
    [KeyboardButton(text='Добавить ученика'), KeyboardButton(text='Удалить ученика')],
    [KeyboardButton(text='Откатить последний пересчет')]
],
    resize_keyboard=True
                            )
change_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заново давай', callback_data='wrong changes')],
    [InlineKeyboardButton(text='Все ок', callback_data='approved changes')]
])

add_student = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заново давай', callback_data='wrong adding')],
    [InlineKeyboardButton(text='Да', callback_data='approved adding')]
])

delete_student = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заново давай', callback_data='wrong deleting')],
    [InlineKeyboardButton(text='Да', callback_data='approved deleting')]
])
