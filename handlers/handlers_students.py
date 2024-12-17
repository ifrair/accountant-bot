from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import keyboard as keyboards
from utils import check_access, is_int, push_to_json, take_from_json, take_names, StateGuard


class AddNewStudent(StatesGroup):
    name = State()
    price = State()
    approving = State()


class DeleteStudent(StatesGroup):
    name = State()
    approving = State()


router = Router()


# adds new student
@router.message(F.text == 'Добавить ученика')
@check_access
async def add_new(message: Message, state: FSMContext):
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
    if not is_int(message.text):
        await message.answer('Неправильный ввод\nНачните заного - Добавить ученика',
                             reply_markup=keyboards.main_keyboard)
        await state.clear()
        return
    await state.update_data(price=int(message.text))
    await state.set_state(AddNewStudent.approving)
    message_data = await state.get_data()
    await message.answer(f"Добавить ученика: {message_data['name']} с балансом: {message_data['price']}?",
                         reply_markup=keyboards.add_student)


# if user sad that everything good on adding
@router.callback_query(F.data == 'approved adding')
async def approving_adding(callback: CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    await state.clear()

    money_counts = take_from_json("money_count")
    money_counts[message_data["name"]] = message_data["price"]
    push_to_json("money_count", money_counts)

    await callback.message.delete()
    await callback.message.answer(text='Успешно!', reply_markup=keyboards.main_keyboard)


# delete student
@router.message(F.text == 'Удалить ученика')
@check_access
async def delete_student(message: Message, state: FSMContext):
    money_counts = take_from_json("money_count")
    if money_counts == {}:
        await message.answer('Нет учеников', reply_markup=keyboards.main_keyboard)
        return

    await state.set_state(DeleteStudent.name)
    message_text = 'Выбери и пришли одного:\n' + take_names(money_counts)
    await message.answer(message_text,
                         parse_mode="MARKDOWN",
                         reply_markup=types.ReplyKeyboardRemove())


# takes name of student to delete
@router.message(DeleteStudent.name)
async def delete_name(message: Message, state: FSMContext):
    async with StateGuard(state) as guard:
        money_counts = take_from_json("money_count")
        if message.text not in money_counts:
            await message.answer('Нет такого\nНачните заного - Удалить ученика',
                                 reply_markup=keyboards.main_keyboard)
            await state.clear()
            return
        guard.unlock()

    await state.update_data(name=message.text)
    await state.set_state(DeleteStudent.approving)
    await message.answer(f'Удалить {message.text}?',
                         reply_markup=keyboards.delete_student)


# if user sad that everything good on deleting
@router.callback_query(F.data == 'approved deleting')
async def approving_deleting(callback: CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    await state.clear()

    money_counts = take_from_json("money_count")
    money_counts.pop(message_data['name'])
    push_to_json("money_count", money_counts)

    await callback.message.delete()
    await callback.message.answer(text='Успешно!', reply_markup=keyboards.main_keyboard)


# if canceled
@router.callback_query((F.data == 'wrong adding') | (F.data == 'wrong deleting'))
async def wrong_deleting(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    message_text = 'Начать заново - ' + ("Добавить" if callback.data == 'wrong adding' else "Удалить") + " Ученика"
    await callback.message.answer(text=message_text, reply_markup=keyboards.main_keyboard)
