import logging

from maxapi import Router
from maxapi.context import MemoryContext
from maxapi.types import Command, MessageCallback, MessageCreated

import keyboard as keyboards
from utils import check_access

router = Router(router_id="main")


@router.message_created(None, Command("help"))
@check_access
async def get_help(event: MessageCreated):
    await event.message.answer(
        """Команды:
        1) Показать балансы
        2) Сделать отчет
        3) Пополнить баланс - внести данные об оплате ученика
        4) Вычесть баланс - вычесть сумму баланса ученика вручную
        5) Добавить ученика
        6) Удалить ученика
        7) Пересчитать балансы - изменение балансов с учетом событий из календаря с момента прошлого пересчета
        8) Откатить последний пересчет""",
        attachments=[keyboards.main_keyboard],
    )


@router.message_created(None)
@check_access
async def start(event: MessageCreated):
    await event.message.answer(
        "Привет!\nНапиши /help чтобы получить описание команд",
        attachments=[keyboards.main_keyboard],
    )


# if something went wrong or pushed cancel button
@router.message_callback()
@check_access
async def cancel_wrong_button(event: MessageCallback, context: MemoryContext):
    await context.clear()
    await event.message.delete()
    await event.message.answer("Отменено")
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])


@router.message_created()
@check_access
async def wrong_message(event: MessageCreated):
    logging.info(f"Wrong message: {event.message.body.text}")
