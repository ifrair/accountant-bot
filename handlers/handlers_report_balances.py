from aiogram import F, Router
from aiogram.types import Message

import keyboard as keyboards
from utils import check_access, take_from_json, take_balances, make_report

router = Router()


# balance check (without any recounting from calendar)
@router.message(F.text == 'Показать балансы')
@check_access
async def get_balance(message: Message):
    money_counts = take_from_json("money_count")
    message_text = take_balances(money_counts)
    if message_text == '':
        message_text = "Ничего нет"
    await message.answer(message_text, reply_markup=keyboards.main_keyboard)


@router.message(F.text == 'Сделать отчет')
@check_access
async def send_report(message: Message):
    message_text = make_report()
    await message.answer(message_text, reply_markup=keyboards.main_keyboard)
