from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, KeyboardButton

import keyboard
import keyboard as keyboards
from calendar_myad import recount as money_recount
from util import push_to_json, take_from_json, take_balance


class Add(StatesGroup):
    name = State()
    price = State()

class Substruct(StatesGroup):
    name = State()
    price = State()

class Addnew(StatesGroup):
    name = State()
    price = State()

class Delete(StatesGroup):
    name = State()

router = Router()

add_json_to_push = {}
sub_json_to_push = {}
in_sub_edit = False
in_add_edit = False

@router.message(CommandStart())
async def start(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await message.answer('Привет\nНапиши /help чтобы получить полный список команд',
                             reply_markup=keyboards.Main_keyboard)


@router.message(Command('help'))
async def get_help(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await message.answer("Команды:\nДобавить - Оплата ученика;\nВычесть - Вычесть сумму вручную\nДобавить ученика - добавить нового ученика\nУдалить ученика - Удалить ученика\nПроверить баланс - проверить баланс\nПересчитать - пересчитать с учетом новых занятий")

# adds all new lessons to balance
@router.message(F.text == "Пересчитать")
async def recount(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        errors = money_recount()
        money = take_from_json(config_json["money_count"])
        message_text = take_balance(money)
        await message.answer(message_text)
        if errors != '':
            await message.answer(f'Ошибки:\n{errors}')

# manualy increase someone's balance
@router.message(F.text == "Добавить")
async def add_money(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await state.set_state(Add.name)
        message_text = 'Выбери одного:\n'
        babosiki = take_from_json(config_json["money_count"])
        if babosiki == {}:
            await message.answer("Нету учеников")
            await state.clear()
            return
        else:
            for i in babosiki:
                message_text += f'`{i}`\n'
            message_text += '\nВыберите и пришлите 1 из этих учеников'
            await message.answer(message_text,
                                 parse_mode="MARKDOWN",
                                 reply_markup=types.ReplyKeyboardRemove())

# takes name of student
@router.message(Add.name)
async def get_name(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        data = take_from_json(config_json["money_count"])
        if message.text not in data:
            await message.answer('нету такого',
                                 reply_markup=keyboards.Main_keyboard)
            await state.clear()
            return
        await state.update_data(name=message.text)
        await state.set_state(Add.price)
        await message.answer('Теперь пришлите сколько оплачено')

# takes how much to increase
@router.message(Add.price)
async def get_price(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    global in_add_edit, add_json_to_push
    if message.from_user.id in config_json["ids"]:
        if not message.text.isnumeric():
            await message.answer('Неправильный ввод\nначните заного - Добавить',
                                 reply_markup=keyboards.Main_keyboard)
            await state.clear()
            return
        await state.update_data(price=message.text)
        data = await state.get_data()
        dat = take_from_json(config_json["money_count"])
        dat[data["name"]] += int(data["price"])
        await state.clear()
        add_json_to_push = dat
        in_add_edit = True
        await message.answer(text=f'Имя: {data["name"]}\nСумма: {data["price"]}',
                             reply_markup=keyboards.Add_edit)

# if user sad that everything good on increasing
@router.callback_query(F.data == 'add_ok')
async def add_ok(callback: CallbackQuery):
    config_json = take_from_json("config.json")
    global in_add_edit
    if in_add_edit:
        await callback.message.delete()
        await callback.message.answer(text='Успешно!',
                                         reply_markup=keyboards.Main_keyboard)
        in_add_edit = False
        push_to_json(config_json["money_count"], add_json_to_push)


# manualy decrease someone's balance
@router.message(F.text == 'Вычесть')
async def sub_struct(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await state.set_state(Substruct.name)
        message_text = 'Выбери одного:\n'
        babosiki = take_from_json(config_json["money_count"])
        if babosiki == {}:
            await message.answer('Нету учеников')
            await state.clear()
            return
        for i in babosiki:
            message_text += f'`{i}`\n'
        message_text += '\nВыберите и пришлите 1 из этих учеников'
        await message.answer(message_text,
                             parse_mode="MARKDOWN",
                             reply_markup=types.ReplyKeyboardRemove())

#same as add_name
@router.message(Substruct.name)
async def sub_name(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        data = take_from_json(config_json["money_count"])
        if message.text not in data:
            await message.answer('нету такого',
                                 reply_markup=keyboards.Main_keyboard)
            await state.clear()
            return
    await state.update_data(name=message.text)
    await state.set_state(Substruct.price)
    await message.answer('Теперь пришлите сколько нужно вычесть')

#same as add_price
@router.message(Substruct.price)
async def sub_price(message: Message, state: FSMContext):
    global sub_json_to_push, in_sub_edit
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        if not message.text.isnumeric():
            await message.answer('Неправильный ввод\nначните заного - Вычесть',
                                 reply_markup=keyboards.Main_keyboard)
            await state.clear()
            return
        await state.update_data(price=message.text)
        data = await state.get_data()
        dat = take_from_json(config_json["money_count"])
        dat[data["name"]] -= int(data["price"])
        sub_json_to_push = dat
        in_sub_edit = True
        await state.clear()
        await message.answer(text=f'Имя: {data["name"]}\nСумма вычета: {data["price"]}',
                             reply_markup=keyboards.Sub_edit)

#same as add_ok
@router.callback_query(F.data == 'sub_ok')
async def sub_ok(callback: CallbackQuery):
    config_json = take_from_json("config.json")
    global sub_json_to_push, in_sub_edit
    if in_sub_edit:
        await callback.message.delete()
        await callback.message.answer(text='Успешно!',
                                      reply_markup=keyboards.Main_keyboard)
        in_sub_edit = False
        push_to_json(config_json["money_count"], sub_json_to_push)

# if something went wrong on increasing or decreasing balance
@router.callback_query(F.data == 'wrong')
async def wrong(callback: CallbackQuery):
    await callback.message.delete()
    global in_sub_edit, in_add_edit
    await callback.message.answer(text='Начать заного - Добавить или Вычесть',
                                  reply_markup=keyboards.Main_keyboard)
    in_sub_edit = False
    in_add_edit = False

# adds new student
@router.message(F.text == 'Добавить ученика')
async def add_new(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await state.set_state(Addnew.name)
        await message.answer('Введите имя ученика:',
                             reply_markup=types.ReplyKeyboardRemove())

#same as add_name
@router.message(Addnew.name)
async def add_new_name(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await state.update_data(name = message.text)
        await state.set_state(Addnew.price)
        await message.answer('Пришлите баланс ученика:')

# just puts this balance on student
@router.message(Addnew.price)
async def add_new_price(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if not message.text.isnumeric():
        await message.answer('Неправильный ввод\nНачните заного - Добавить ученика',
                             reply_markup=keyboards.Main_keyboard)
        await state.clear()
        return
    await state.update_data(price=int(message.text))
    add_new_json = take_from_json(config_json["money_count"])
    data = await state.get_data()
    add_new_json[data["name"]] = data["price"]
    push_to_json(config_json["money_count"], add_new_json)
    await state.clear()
    await message.answer("Успешно!",
                         reply_markup=keyboards.Main_keyboard)

# delete student
@router.message(F.text == 'Удалить ученика')
async def delete(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        await state.set_state(Delete.name)
        message_text = 'Выбери одного:\n'
        babosiki = take_from_json(config_json["money_count"])
        if babosiki == {}:
            await message.answer('Нету учеников')
            await state.clear()
            return
        for i in babosiki:
            message_text += f'`{i}`\n'
        message_text += '\nВыберите и пришлите 1 из этих учеников'
        await message.answer(message_text,
                             parse_mode="MARKDOWN",
                             reply_markup=types.ReplyKeyboardRemove())

#takes name of student to delete
@router.message(Delete.name)
async def delete_name(message: Message, state: FSMContext):
    config_json = take_from_json("config.json")
    await state.update_data(name=message.text)
    delete_json = take_from_json(config_json["money_count"])
    if message.text not in delete_json:
        await message.answer('Нету такого\nНачните заного - Удалить ученика',
                             reply_markup=keyboards.Main_keyboard)
        await state.clear()
        return
    delete_json.pop(message.text)
    push_to_json(config_json["money_count"], delete_json)
    await message.answer('Успешно!',
                         reply_markup=keyboards.Main_keyboard)
    await state.clear()

#balance check (without any recounting from calendar)
@router.message(F.text == 'Проверить баланс')
async def balance(message: Message):
    config_json = take_from_json("config.json")
    if message.from_user.id in config_json["ids"]:
        money_count = take_from_json(config_json["money_count"])
        message_text = take_balance(money_count)
        if message_text == '':
            await message.answer("Ничего нету")
        else:
            await message.answer(message_text)
