from maxapi import F, Router
from maxapi.types import MessageCallback

import keyboard as keyboards
from utils import (
    check_access,
    get_datetime_string,
    push_to_json,
    recount_money,
    take_balances,
    take_from_json,
)

router = Router()


# adds all new lessons to balance
@router.message_callback(None, F.callback.payload == "recalculate_balances")
@check_access
async def recount(event: MessageCallback):
    await event.message.delete()
    last_time = take_from_json("last_time")
    events_text, errors_text, money_sum, hours_sum = recount_money()

    events_text = f"Обработаны события:\n\n{events_text}" if events_text != "" else "Новых уроков не обнаружено"
    events_text = f"Успешно пересчитано ✅ c {get_datetime_string(last_time)}\n" + events_text
    await event.message.answer(events_text)

    money_text = (
        f"Всего заработано: {money_sum} руб\n"
        f"Отработано: {hours_sum} часов\n"
        f"В среднем: {int(money_sum / max(0.25, hours_sum))} руб/ч"
    )
    await event.message.answer(money_text)

    errors_text = f"Ошибки:\n\n{errors_text}" if errors_text != "" else "Ошибок не обнаружено"
    await event.message.answer(errors_text)

    money_counts = take_from_json("money_count")
    message_text = take_balances(money_counts)
    await event.message.answer(message_text)
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])


# One time rolls back last recount
@router.message_callback(None, F.callback.payload == "rollback_recalculation")
@check_access
async def recount_roll_back(event: MessageCallback):
    await event.message.delete()
    last_time = take_from_json("last_time")
    last_time_backup = take_from_json("last_time_backup")
    if last_time == last_time_backup:
        await event.message.answer(
            "Нечего откатывать\nЧто для Вас сделать?",
            attachments=[keyboards.main_keyboard],
        )
        return
    money_counts_backup = take_from_json("money_counts_backup")
    push_to_json("last_time", last_time_backup)
    push_to_json("money_count", money_counts_backup)
    money_message = take_balances(money_counts_backup)
    await event.message.answer(f"Откатили до {get_datetime_string(last_time_backup)}\n\n{money_message}")
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])
