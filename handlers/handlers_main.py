from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboard as keyboards
from calendar_util import recount as money_recount
from util import take_from_json, take_balance

router = Router()


@router.message(Command('help'))
async def get_help(message: Message):
    config_json = take_from_json("config.json")
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


# adds all new lessons to balance
@router.message(F.text == "Пересчитать балансы")
async def recount(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    errors = money_recount()
    money = take_from_json(config_json["money_count"])
    message_text = take_balance(money)
    await message.answer(message_text)
    errors = f'Ошибки:\n{errors}' if errors != '' else "Ошибок не обнаружено"
    await message.answer(errors, reply_markup=keyboards.main_keyboard)


# balance check (without any recounting from calendar)
@router.message(F.text == 'Проверить балансы')
async def balance(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    money_counts = take_from_json(config_json["money_count"])
    message_text = take_balance(money_counts)
    if message_text == '':
        message_text = "Ничего нет"
    await message.answer(message_text, reply_markup=keyboards.main_keyboard)


@router.message()
async def start(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    await message.answer('Привет\nНапиши /help чтобы получить полный список команд',
                         reply_markup=keyboards.main_keyboard)
