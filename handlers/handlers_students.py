from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import keyboard as keyboards
from util import push_to_json, take_from_json


class AddNewStudent(StatesGroup):
    name = State()
    price = State()


class DeleteStudent(StatesGroup):
    name = State()


router = Router()


# adds new student
@router.message(F.text == 'Добавить ученика')
async def add_new(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    await state.set_state(AddNewStudent.name)
    await message.answer('Введите имя ученика:',
                         reply_markup=types.ReplyKeyboardRemove())


# same as add_name
@router.message(AddNewStudent.name)
async def add_new_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddNewStudent.price)
    await message.answer('Пришлите баланс ученика:')


# just puts this balance on student
@router.message(AddNewStudent.price)
async def add_new_price(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if not message.text.isnumeric():
        await message.answer('Неправильный ввод\nНачните заного - Добавить ученика',
                             reply_markup=keyboards.main_keyboard)
        await state.clear()
        return
    await state.update_data(price=int(message.text))
    add_new_json = take_from_json(config_json["money_count"])
    data = await state.get_data()
    add_new_json[data["name"]] = data["price"]
    push_to_json(config_json["money_count"], add_new_json)
    await state.clear()
    await message.answer("Успешно!",
                         reply_markup=keyboards.main_keyboard)


# delete student
@router.message(F.text == 'Удалить ученика')
async def delete_student(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    await state.set_state(DeleteStudent.name)
    message_text = 'Выбери одного:\n'
    money_counts = take_from_json(config_json["money_count"])
    if money_counts == {}:
        await message.answer('Нет учеников', reply_markup=keyboards.main_keyboard)
        await state.clear()
        return
    for i in money_counts:
        message_text += f'`{i}`\n'
    message_text += '\nВыберите и пришлите 1 из этих учеников'
    await message.answer(message_text,
                         parse_mode="MARKDOWN",
                         reply_markup=types.ReplyKeyboardRemove())


# takes name of student to delete
@router.message(DeleteStudent.name)
async def delete_name(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    await state.update_data(name=message.text)
    delete_json = take_from_json(config_json["money_count"])
    if message.text not in delete_json:
        await message.answer('нет такого\nНачните заного - Удалить ученика',
                             reply_markup=keyboards.main_keyboard)
        await state.clear()
        return
    delete_json.pop(message.text)
    push_to_json(config_json["money_count"], delete_json)
    await message.answer('Успешно!',
                         reply_markup=keyboards.main_keyboard)
    await state.clear()
