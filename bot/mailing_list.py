from aiogram import Router, Bot, types, F
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import kbds

from get_data import *
mailing_router=Router()

class Mailing(StatesGroup):
    text=State()

@mailing_router.message(Mailing.text,F.text)
async def mailing_text(message:types.Message,state:FSMContext,bot:Bot):
    await state.update_data(text=message.text)
    await message.answer(message.text,
                           reply_markup=kbds.createkb({"Отправить": "send_mailing", "Отменить": "thanks"}))


# @mailing_router.callback_query(F.data.startswith('send_mailing'))
# async def send_mailing(call:types.CallbackQuery,bot:Bot,state:FSMContext):
#     await call.message.delete()
#     data=await state.get_data()
#     message_list = []
#     users = await getsubobj()
#     for user in users:
#         mess_id = await bot.send_message(user['user_id'],data['text'])
#         message_list.append({user['user_id']:mess_id.message_id})
#     await start_mailing_task({"mailing_data": message_list})
#     await state.clear()

@mailing_router.callback_query(F.data.startswith('send_mailing'))
async def send_mailing(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    message_list = []
    users = await getsubobj()

    for user in users:
        try:
            mess = await bot.send_message(user['user_id'], data['text'])
            message_list.append({user['user_id']: mess.message_id})

        except Exception as e:
            print(f"Ошибка при отправке пользователю {user['user_id']}: {e}")

    await start_mailing_task({"mailing_data": message_list})
    await state.clear()