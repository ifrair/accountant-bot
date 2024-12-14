import json
import logging
from os.path import exists


def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


# function that returns opened json
def take_from_json(json_name):
    try:
        if not exists(json_name):
            logging.error(f'Файла с названием: ({json_name}) не существует')
        with open(json_name) as json_file:
            json_data = json.load(json_file)
        return json_data
    except FileNotFoundError:
        raise FileNotFoundError(f'НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}')


# function that pushes file to json
def push_to_json(json_name, file_to_push, its_token=False):
    try:
        if not exists(json_name):
            logging.error(f'Файла с названием: ({json_name}) не существует')
        if its_token:
            with open(json_name, "w") as token:
                token.write(file_to_push)
            return
        with open(json_name, "w") as json_file:
            json.dump(file_to_push, json_file)
    except FileNotFoundError:
        raise FileNotFoundError(f'НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}')


def take_balance(money):
    message_text = ''
    for name in sorted(money):
        message_text += (('Долг' if money[name] < 0 else 'Остаток') +
                         f' {name} равен: {money[name]} руб\n')
    return message_text


def take_names(money):
    message_text = ''
    for name in sorted(money):
        message_text += f'`{name}`\n'
    return message_text


# controls state cleaning with context manager
class StateGuard:
    def __init__(self, state):
        self.state = state
        self.is_locked = False

    async def __aenter__(self):
        self.is_locked = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.is_locked:
            await self.state.clear()

    def unlock(self):
        self.is_locked = False
