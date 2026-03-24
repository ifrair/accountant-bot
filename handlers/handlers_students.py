from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import MessageCallback, MessageCreated

import keyboard as keyboards
from utils import check_access, is_int, push_to_json, take_from_json


class AddNewStudent(StatesGroup):
    name = State()
    price = State()
    approving = State()


class DeleteStudent(StatesGroup):
    name = State()
    approving = State()


router = Router(router_id="students")


# adds new student
@router.message_callback(None, F.callback.payload == "add_student")
@check_access
async def add_new(event: MessageCallback, context: MemoryContext):
    await context.set_state(AddNewStudent.name)
    await event.message.delete()
    await event.message.answer("Добавление нового ученика...\nВведите имя ученика:")


# same as add_name
@router.message_created(F.message.body.text, AddNewStudent.name)
@check_access
async def add_new_name(event: MessageCreated, context: MemoryContext):
    name = event.message.body.text
    await context.update_data(name=name)
    await context.set_state(AddNewStudent.price)
    await event.message.delete()
    await event.message.answer(f"Пришлите баланс {name}:")


# just puts this balance on student
@router.message_created(F.message.body.text, AddNewStudent.price)
@check_access
async def add_new_price(event: MessageCreated, context: MemoryContext):
    text = event.message.body.text
    if not is_int(text):
        await context.clear()
        await event.message.answer("Отменено. Некорректная сумма")
        await event.message.answer("Попробуй еще раз", attachments=[keyboards.main_keyboard])
        return
    await context.update_data(price=int(text))
    await context.set_state(AddNewStudent.approving)
    message_data = await context.get_data()
    await event.message.answer(
        f"Добавить ученика: {message_data['name']} с балансом: {message_data['price']}?",
        attachments=[keyboards.add_student],
    )


# if user sad that everything good on adding
@router.message_callback(F.callback.payload == "approved_adding", AddNewStudent.approving)
@check_access
async def approving_adding(event: MessageCallback, context: MemoryContext):
    message_data = await context.get_data()
    await context.clear()

    money_counts = take_from_json("money_count")
    money_counts[message_data["name"]] = message_data["price"]
    push_to_json("money_count", money_counts)

    await event.message.delete()
    await event.message.answer(text="Успешно!")
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])


# delete student
@router.message_callback(None, F.callback.payload == "delete_student")
@check_access
async def delete_student(event: MessageCallback, context: MemoryContext):
    money_counts = take_from_json("money_count")
    await event.message.delete()
    if money_counts == {}:
        await event.message.answer(
            "У вас нет учеников.\nЧто для Вас сделать?",
            attachments=[keyboards.main_keyboard],
        )
        return
    await context.set_state(DeleteStudent.name)
    keyboard = keyboards.get_students_keyboard(money_counts)
    await event.message.answer("Удаляем ученика...\nВыбери одного:\n", attachments=[keyboard])


# takes name of student to delete
@router.message_callback(DeleteStudent.name)
@check_access
async def delete_name(event: MessageCallback, context: MemoryContext):
    response = event.callback.payload
    await event.message.delete()
    if response == "cancel_operation" or response not in take_from_json("money_count"):
        await context.clear()
        await event.message.answer(text="Отменено\nЧто для Вас сделать?", attachments=[keyboards.main_keyboard])
        return
    await context.update_data(name=response)
    await context.set_state(DeleteStudent.approving)
    await event.message.answer(f"Удалить {response}?", attachments=[keyboards.delete_student])


# if user sad that everything good on deleting
@router.message_callback(F.callback.payload == "approved_deleting", DeleteStudent.approving)
@check_access
async def approving_deleting(event: MessageCallback, context: MemoryContext):
    message_data = await context.get_data()
    await context.clear()

    money_counts = take_from_json("money_count")
    money_counts.pop(message_data["name"])
    push_to_json("money_count", money_counts)

    await event.message.delete()
    await event.message.answer(f"Успешно удален {message_data['name']}")
    await event.message.answer("Что для Вас сделать?", attachments=[keyboards.main_keyboard])
