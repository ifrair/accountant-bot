import asyncio
from aiogram import Dispatcher, Bot
from handlers import handlers
from utils import take_from_json

import logging

config = take_from_json("config")
Token = config["Token"]

dp = Dispatcher()
bot = Bot(token=Token)


async def main():
    for handler in handlers:
        dp.include_router(handler)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename=config["logs"], filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
