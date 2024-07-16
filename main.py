import os
import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.fsm.strategy import FSMStrategy


from middlewares.dp import DataBaseSession

from dotenv import load_dotenv

from handlers.user_handlers import router

from database.models import async_main, session_maker


async def main():
    await async_main()
    
    load_dotenv()  
    bot = Bot(token=os.getenv('TOKEN'))
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher(fsm_strategy = FSMStrategy.USER_IN_CHAT)
    dp.include_router(router=router)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    
    
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')