import asyncio
import logging

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext

from handlers import routers
from utils import take_from_json

config = take_from_json("config")
token = config["token"]

dp = Dispatcher(storage=MemoryContext)
bot = Bot(token=token)


async def main():
    dp.include_routers(*routers)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename=config["logs"],
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
