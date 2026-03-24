from maxapi import F, Router
from maxapi.types import MessageCallback

import keyboard as keyboards
from utils import check_access, get_datetime_string, take_from_json, take_balances, make_report

router = Router(router_id="reports")


# balance check (without any recounting from calendar)
@router.message_callback(None, F.callback.payload == 'show_balances')
@check_access
async def get_balance(event: MessageCallback):
    money_counts = take_from_json("money_count")
    message_text = take_balances(money_counts)
    message_text += f"\nПоследний пересчет {get_datetime_string(take_from_json("last_time"))}"
    if message_text == '':
        message_text = "Ничего нет"
    await event.message.delete()
    await event.message.answer(message_text)
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])


@router.message_callback(None, F.callback.payload == 'make_report')
@check_access
async def send_report(event: MessageCallback):
    message_text = make_report()
    await event.message.delete()
    await event.message.answer(message_text)
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])

