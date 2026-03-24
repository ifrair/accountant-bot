from functools import wraps
from .json_utils import take_from_json
import logging

def check_access(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        config_json = take_from_json("config")
        if hasattr(event, "get_ids"):
            user_id = event.get_ids()[1]
        else:
            logging.info(f"Type of query {type(event)} is unsupportable")
            await event.message.answer("Недопустимый тип запроса")
            return

        if user_id not in config_json["users"]:
            logging.info(f"User {event.message.sender.user_id} has no access")
            await event.message.answer("Нет доступа")
            return
        return await handler(event, *args, **kwargs)
    return wrapper


def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False
