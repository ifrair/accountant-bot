from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboard as keyboards
from calendar_util import recount as money_recount, get_datetime_string
from util import take_from_json, push_to_json, take_balance

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

    money_counts = take_from_json(config_json["money_count"])
    last_time = take_from_json(config_json["last_time"])
    push_to_json(config_json["money_counts_backup"], money_counts)
    push_to_json(config_json["last_time_backup"], last_time)

    events_text, errors_text = money_recount()

    events_text = f'Обработаны события:\n\n{events_text}' if events_text != '' else "Уроков не обнаружено"
    await message.answer(events_text)

    errors_text = f'Ошибки:\n\n{errors_text}' if errors_text != '' else "Ошибок не обнаружено"
    await message.answer(errors_text)

    money_counts = take_from_json(config_json["money_count"])
    message_text = take_balance(money_counts)
    await message.answer(message_text, reply_markup=keyboards.main_keyboard)


# One time rolls back last recount
@router.message(F.text == "Откатить последний пересчет")
async def recount_roll_back(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    last_time = take_from_json(config_json["last_time"])
    last_time_backup = take_from_json(config_json["last_time_backup"])
    if last_time == last_time_backup:
        await message.answer("Нечего откатывать")
        return
    money_counts_backup = take_from_json(config_json["money_counts_backup"])
    push_to_json(config_json["last_time"], last_time_backup)
    push_to_json(config_json["money_count"], money_counts_backup)
    money_message = take_balance(money_counts_backup)
    await message.answer(f"Откатили до {get_datetime_string(last_time_backup)}\n\n{money_message}",
                         reply_markup=keyboards.main_keyboard)



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
