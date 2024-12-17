from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboard as keyboards
from utils import check_access

router = Router()


@router.message(Command('help'))
@check_access
async def get_help(message: Message):
    await message.answer("""Команды:
    Пополнить баланс - Оплата ученика;
    Вычесть баланс - Вычесть сумму вручную
    Добавить ученика - добавить нового ученика
    Удалить ученика - Удалить ученика
    Проверить балансы - проверить баланс
    Пересчитать балансы - пересчитать с учетом новых занятий""",
                         reply_markup=keyboards.main_keyboard)


@router.message()
@check_access
async def start(message: Message):
    await message.answer('Привет\nНапиши /help чтобы получить полный список команд',
                         reply_markup=keyboards.main_keyboard)
