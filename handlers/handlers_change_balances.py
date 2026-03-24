from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import MessageCallback, MessageCreated

import keyboard as keyboards
from utils import check_access, is_int, push_to_json, take_from_json


class ChangeBalance(StatesGroup):
    name = State()
    price = State()
    approve = State()


router = Router(router_id="change_balances")


# change someone's balance
@router.message_callback(
    None,
    (F.callback.payload == "add_balance") | (F.callback.payload == "subtract_balance"),
)
@check_access
async def change_money(event: MessageCallback, context: MemoryContext):
    money_counts = take_from_json("money_count")
    await event.message.delete()
    if money_counts == {}:
        await event.message.answer(
            "У вас нет учеников.\nЧто для Вас сделать?",
            attachments=[keyboards.main_keyboard],
        )
        return
    await context.update_data(is_add=(event.callback.payload == "add_balance"))
    await context.set_state(ChangeBalance.name)
    keyboard = keyboards.get_students_keyboard(money_counts)
    await event.message.answer(
        ("Пополняем" if (event.callback.payload == "add_balance") else "Вычитаем") + " баланс...\nВыбери ученика:\n",
        attachments=[keyboard],
    )


# takes name of student
@router.message_callback(ChangeBalance.name)
@check_access
async def get_name(event: MessageCallback, context: MemoryContext):
    response = event.callback.payload
    await event.message.delete()
    if response == "cancel_operation" or response not in take_from_json("money_count"):
        await context.clear()
        await event.message.answer(text="Отменено\nЧто для Вас сделать?", attachments=[keyboards.main_keyboard])
        return
    await context.update_data(name=response)
    await context.set_state(ChangeBalance.price)
    message_data = await context.get_data()
    await event.message.answer(
        ("Пополняем" if message_data["is_add"] else "Вычитаем")
        + f" {response}...\nТеперь напиши сколько "
        + ("оплачено" if message_data["is_add"] else "вычесть")
    )


# takes how much to change
@router.message_created(ChangeBalance.price)
@check_access
async def get_price(event: MessageCreated, context: MemoryContext):
    price = event.message.body.text
    if not is_int(price):
        await event.message.answer("Отменено. Некорректная сумма")
        await event.message.answer("Попробуй еще раз", attachments=[keyboards.main_keyboard])
        await context.clear()
        return
    await context.update_data(price=int(price))
    await context.set_state(ChangeBalance.approve)
    message_data = await context.get_data()
    await event.message.answer(
        text=f"{message_data['name']} {('оплатил' if message_data['is_add'] else 'вычитаем')} {message_data['price']}?",
        attachments=[keyboards.change_edit],
    )


# if user sad that everything good on changing
@router.message_callback(F.callback.payload == "approved_changes")
@check_access
async def approving_changes(event: MessageCallback, context: MemoryContext):
    message_data = await context.get_data()
    await context.clear()

    money_counts = take_from_json("money_count")
    money_counts[message_data["name"]] += message_data["price"] * (1 if message_data["is_add"] else -1)
    push_to_json("money_count", money_counts)

    await event.message.delete()
    await event.message.answer(
        text="Успешно!✅ "
        + ("Оплачено" if message_data["is_add"] else "Вычтено")
        + f" {message_data['name']} на сумму {message_data['price']}"
    )
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])
