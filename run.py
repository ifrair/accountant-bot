import asyncio
from aiogram import Dispatcher, Bot
from util import take_from_json
from handlers.handlers_main import router as router_main
from handlers.handlers_students import router as router_students
from handlers.handlers_change_balances import router as router_change_balances

import logging

config = take_from_json("config.json")
Token = config["Token"]

dp = Dispatcher()
bot = Bot(token=Token)


async def main():
    dp.include_router(router_students)
    dp.include_router(router_change_balances)
    dp.include_router(router_main)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename=config["logs"], filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
