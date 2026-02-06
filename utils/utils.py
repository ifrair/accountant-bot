from aiogram.types import Message
from functools import wraps
from .json_utils import take_from_json


def check_access(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        config_json = take_from_json("config")
        if message.from_user.username not in config_json["users"]:
            await message.answer("Нет доступа")
            return
        return await handler(message, *args, **kwargs)
    return wrapper


def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False
