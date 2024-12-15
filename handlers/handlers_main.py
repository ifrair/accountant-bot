from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboard as keyboards
from utils import take_from_json

router = Router()


@router.message(Command('help'))
async def get_help(message: Message):
    config_json = take_from_json("config")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    await message.answer("""Команды:
    Пополнить баланс - Оплата ученика;
    Вычесть баланс - Вычесть сумму вручную
    Добавить ученика - добавить нового ученика
    Удалить ученика - Удалить ученика
    Проверить балансы - проверить баланс
    Пересчитать балансы - пересчитать с учетом новых занятий""",
                         reply_markup=keyboards.main_keyboard)


@router.message()
async def start(message: Message):
    config_json = take_from_json("config")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    await message.answer('Привет\nНапиши /help чтобы получить полный список команд',
                         reply_markup=keyboards.main_keyboard)
