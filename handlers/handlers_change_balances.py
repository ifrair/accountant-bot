from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import keyboard as keyboards
from util import push_to_json, take_from_json, StateGuard


class ChangeBalance(StatesGroup):
    is_add = State()
    name = State()
    price = State()
    approve = State()


router = Router()


# manually increase someone's balance
@router.message((F.text == "Пополнить баланс") | (F.text == "Вычесть баланс"))
async def change_money(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.username not in config_json["users"]:
        await message.answer("Нет доступа")
        return
    money_counts = take_from_json(config_json["money_count"])
    if money_counts == {}:
        await message.answer("Нет учеников")
        return
    await state.set_state(ChangeBalance.is_add)
    await state.update_data(is_add=(message.text == "Пополнить баланс"))
    await state.set_state(ChangeBalance.name)
    message_text = 'Выбери одного:\n'
    for i in money_counts:
        message_text += f'`{i}`\n'
    message_text += '\nВыбери и пришли одного из этих учеников'
    await message.answer(message_text,
                         parse_mode="MARKDOWN",
                         reply_markup=types.ReplyKeyboardRemove())


# takes name of student
@router.message(ChangeBalance.name)
async def get_name(message: Message, state: FSMContext):
    async with StateGuard(state) as guard:
        config_json = take_from_json("config.json")
        money_counts = take_from_json(config_json["money_count"])
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
    if not message.text.isnumeric():
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
@router.callback_query(F.data == 'approved')
async def approving(callback: CallbackQuery, state: FSMContext):
    message_data = await state.get_data()
    await state.clear()
    config_json = take_from_json("config.json")
    money_counts = take_from_json(config_json["money_count"])
    money_counts[message_data["name"]] += int(message_data["price"]) * (1 if message_data['is_add'] else -1)
    await callback.message.delete()
    await callback.message.answer(text='Успешно!', reply_markup=keyboards.main_keyboard)
    push_to_json(config_json["money_count"], money_counts)


# if something went wrong on increasing or decreasing balance
@router.callback_query(F.data == 'wrong')
async def wrong(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(text='Начать заного - Пополнить или Вычесть',
                                  reply_markup=keyboards.main_keyboard)
