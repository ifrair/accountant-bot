import json
import logging
import os

# function that returns opened json
def take_from_json(json_name):
    try:
        if os.path.exists(json_name) == False:
            logging.error(f'Файла с названием: ({json_name}) не существует')
        with open(json_name) as jsonfil:
            jsonfile = json.load(jsonfil)
        return jsonfile
    except:
        raise Exception(f'НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}')

# function that pushes file to json
def push_to_json(json_name, file_to_push, its_token = False):
    try:
        if os.path.exists(json_name) == False:
            logging.error(f'Файла с названием: ({json_name}) не существует')
        if its_token:
            with open(json_name, "w") as token:
                token.write(file_to_push)
            return
        with open(json_name, "w") as json_file:
            json.dump(file_to_push, json_file)
    except:
        raise Exception(f'НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}')

# takes balance
def take_balance(money):
    message_text = ''
    for i in money:
        if money[i] < 0:
            message_text += f'Долг {i} равен: {money[i]} руб\n'
        elif money[i] >= 0:
            message_text += f'Остаток {i} равен: {money[i]} руб\n'
    return message_text

