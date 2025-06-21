import os
import asyncio
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher,types
from private import user_private_router
from payment import user_payment_router
from fsm_promocode import fsm_router
from adminpage import admin_page
# from sshconnect import ssh_page
from fsm_add_promocode import fsm_company
from mailing_list import mailing_router
from promotion import promotion_router,scheduler
from aiogram.methods import DeleteWebhook
import django
from dotenv import load_dotenv

# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'taskmanager'))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.taskmanager.settings')
# django.setup()
load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))
# scheduler = AsyncIOScheduler()
dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_payment_router)
dp.include_router(fsm_router)
dp.include_router(fsm_company)
dp.include_router(mailing_router)
dp.include_router(admin_page)
# dp.include_router(ssh_page)
dp.include_router(promotion_router)
async def main():
    scheduler.start()
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__=="__main__":
    asyncio.run(main())