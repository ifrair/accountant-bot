from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import keyboard as keyboards
from utils import check_access, is_int, push_to_json, take_from_json, take_names, StateGuard


class ChangeBalance(StatesGroup):
    is_add = State()
    name = State()
    price = State()
    approve = State()


router = Router()


# manually increase someone's balance
@router.message((F.text == "Пополнить баланс") | (F.text == "Вычесть баланс"))
@check_access
async def change_money(message: Message, state: FSMContext):
    money_counts = take_from_json("money_count")
    if money_counts == {}:
        await message.answer("Нет учеников")
        return
    await state.set_state(ChangeBalance.is_add)
    await state.update_data(is_add=(message.text == "Пополнить баланс"))
    await state.set_state(ChangeBalance.name)
    message_text = 'Выбери одного:\n' + take_names(money_counts) + '\nВыбери и пришли одного из этих учеников'
    await message.answer(message_text,
                         parse_mode="MARKDOWN",
                         reply_markup=types.ReplyKeyboardRemove())


# takes name of student
@router.message(ChangeBalance.name)
async def get_name(message: Message, state: FSMContext):
    async with StateGuard(state) as guard:
        money_counts = take_from_json("money_count")
        if message.text not in money_counts:
            await message.answer('Нет такого',
                                 reply_markup=keyboards.main_keyboard)
            return
        guard.unlock()
    await state.update_data(name=message.text)
    await state.set_state(ChangeBalance.price)
    message_data = await state.get_data()
    await message.answer('Теперь пришли сколько ' + ('оплачено' if message_data['is_add'] else 'вычесть'))


# takes how much to increase
@router.message(ChangeBalance.price)
async def get_price(message: Message, state: FSMContext):
    if not is_int(message.text):
        await message.answer('Неправильный ввод\nНачни заново - Пополнить или Вычесть',
                             reply_markup=keyboards.main_keyboard)
        await state.clear()
        return
    message_data = await state.get_data()
    await state.update_data(price=message.text)
    await state.set_state(ChangeBalance.approve)
    await message.answer(text=f'Имя: {message_data["name"]}\nСумма: {message.text}',
                         reply_markup=keyboards.change_edit)


# if user sad that everything good on changing
@router.callback_query(F.data == 'approved changes')
async def approving_changes(callback: CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    await state.clear()
    
    money_counts = take_from_json("money_count")
    money_counts[message_data["name"]] += int(message_data["price"]) * (1 if message_data['is_add'] else -1)
    push_to_json("money_count", money_counts)

    await callback.message.delete()
    await callback.message.answer(text='Успешно!', reply_markup=keyboards.main_keyboard)


# if something went wrong on increasing or decreasing balance
@router.callback_query(F.data == 'wrong changes')
async def wrong_changes(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(text='Начать заново - Пополнить или Вычесть',
                                  reply_markup=keyboards.main_keyboard)
