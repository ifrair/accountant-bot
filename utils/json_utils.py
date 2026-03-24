import json
import logging
from pathlib import Path


# function that pushes file to json
def push_to_json(json_name, file_to_push, is_token=False):
    json_name = take_correct_json_name(json_name)

    if is_token:
        with Path(json_name).open("w") as token:
            token.write(file_to_push)
        return

    if not Path(json_name).exists():
        logging.error(f"Файла с названием: ({json_name}) не существует")
        raise FileNotFoundError(f"НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}")

    with Path(json_name).open("w") as json_file:
        json.dump(file_to_push, json_file)


# function that returns opened json
def take_from_json(json_name):
    json_name = take_correct_json_name(json_name)
    if not Path(json_name).exists():
        logging.error(f"Файла с названием: ({json_name}) не существует")
        raise FileNotFoundError(f"НЕВЕРНОЕ НАИМЕНОВАНИЕ ФАЙЛА: {json_name}")
    with Path(json_name).open("r") as json_file:
        return json.load(json_file)


def take_correct_json_name(json_name):
    if json_name == "config":
        return "config.json"
    if json_name[-5:] != ".json":
        config_json = take_from_json("config.json")
        return config_json[json_name]
    return json_name
