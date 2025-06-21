from datetime import datetime, timedelta

import pytz
from aiogram import Router, Bot, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import kbds
from get_data import *
import asyncio
fsm_router=Router()

class AddCode(StatesGroup):
    name=State()

async def update_promocode_try(user_id):
    u = await getuser(user_id)
    data={
        "user_id":user_id,
        "try_promocode":int(u["try_promocode"])+1
    }
    await putsubuser(data)

@fsm_router.message(AddCode.name,F.text)
async def fsm_name(message:types.Message, state:FSMContext,bot:Bot):
    user_id = message.from_user.id
    u = await getuser(user_id)
    # data = await state.get_data()
    print(message.text)
    # n = data.get('n', u["try_promocode"])
    # print(f"Текущие попытки: {n}")

        # return

    data={
        "promo":message.text
    }

    a=await get_promocode(data)
    print(a)

    if a and u['company'] == a["slug"] :
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        expires_str = u.get("expires_at")  # например: '2025-05-20 13:00:00'

        # Если нет expires_at, ставим с текущего времени
        try:
            expires_at = datetime.fromisoformat(expires_str)
        except:
            expires_at = now

        # Берём большее из now и expires_at (если подписка уже истекла — начинаем с now)
        base = max(now, expires_at)

        # Прибавляем дни из промокода
        new_expires = base + timedelta(days=a["days"])

        # Обработка списка активированных промокодов
        try:
            used_promos = u["promocode"].split(",")
        except:
            used_promos = []

        if message.text in used_promos:
            await asyncio.sleep(2)
            await message.delete()
        else:
            gdata = {
                "user_id": user_id,
                "expires_at": new_expires.isoformat(),
                "promocode": f'{u["promocode"]},{message.text}'
            }

            await putsubuser(gdata)
            await state.clear()
            await asyncio.sleep(2)
            await message.delete()
            await message.answer(
                f'Вы выиграли {a["days"]} бонусных дней',
                reply_markup=kbds.createkb({"Спасибо": "menu"})
            )

    else:
        await asyncio.sleep(2)
        await message.delete()
        # n += 1  # Увеличиваем количество попыток
        # # await state.update_data(n=n)
        # # await update_promocode_try(user_id)
        # if n == 1:
        #     await message.answer("Промокод неверный (2 попытки)", reply_markup=kbds.createkb({"Назад": "sub"}))
        #     # n += 1
        #     await update_promocode_try(user_id)
        #     await state.update_data(n=n)
        #
        # elif n == 2:
        #     await message.answer("Промокод неверный (1 попытка)", reply_markup=kbds.createkb({"Назад": "sub"}))
        #     # n += 1
        #     await state.update_data(n=n)
        #     await update_promocode_try(user_id)
        #     # return
        # elif n == 3:
        #     await message.answer("Промокод неверный", reply_markup=kbds.createkb({"Назад": "sub"}))
            # putdata = {
            #     "user_id": user_id,
            #     "promocode": "BanUser"
            # }
            #
            # await putsubuser(putdata)
            # await state.clear()

        # await message.answer("Промокод неверный (3 попытки)")

