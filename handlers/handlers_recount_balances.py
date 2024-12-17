from aiogram import F, Router
from aiogram.types import Message

import keyboard as keyboards
from utils import check_access, take_from_json, push_to_json, take_balances, recount_money, get_datetime_string

router = Router()


# adds all new lessons to balance
@router.message(F.text == "Пересчитать балансы")
@check_access
async def recount(message: Message):
    money_counts = take_from_json("money_count")
    last_time = take_from_json("last_time")
    push_to_json("money_counts_backup", money_counts)
    push_to_json("last_time_backup", last_time)

    events_text, errors_text, money_sum, hours_sum = recount_money()

    events_text = f'Обработаны события:\n\n{events_text}' if events_text != '' else "Уроков не обнаружено"
    await message.answer(events_text)

    money_text = (f'Всего заработано: {money_sum} руб\n'
                  f'Отработано: {hours_sum} часов\n'
                  f'В среднем: {int(money_sum / hours_sum)} руб/ч')
    await message.answer(money_text)

    errors_text = f'Ошибки:\n\n{errors_text}' if errors_text != '' else "Ошибок не обнаружено"
    await message.answer(errors_text)

    money_counts = take_from_json("money_count")
    message_text = take_balances(money_counts)
    await message.answer(message_text, reply_markup=keyboards.main_keyboard)


# One time rolls back last recount
@router.message(F.text == "Откатить последний пересчет")
@check_access
async def recount_roll_back(message: Message):
    last_time = take_from_json("last_time")
    last_time_backup = take_from_json("last_time_backup")
    if last_time == last_time_backup:
        await message.answer("Нечего откатывать")
        return
    money_counts_backup = take_from_json("money_counts_backup")
    push_to_json("last_time", last_time_backup)
    push_to_json("money_count", money_counts_backup)
    money_message = take_balances(money_counts_backup)
    await message.answer(f"Откатили до {get_datetime_string(last_time_backup)}\n\n{money_message}",
                         reply_markup=keyboards.main_keyboard)
