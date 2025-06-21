import uuid

import pytz
from aiogram import Router, Bot, types, F
from aiogram.types import LabeledPrice
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from get_data import *
import kbds
import yookassa
from dotenv import load_dotenv
load_dotenv()
user_payment_router = Router()
# scheduler = AsyncIOScheduler()
# scheduler.start()
# active_payments = {}
# my_token="381764678:TEST:101703"
# prod="381764678:TEST:102901"



# test_link="https://t.me/vpn_bot_check_bot"
prod_link="https://t.me/kedovpnbot"



async def create_pay(amount):
    yookassa.Configuration.account_id=os.getenv("api_id")
    yookassa.Configuration.secret_key=os.getenv("api_key")
    receipt = {
        "items": [
            {
                "description": "Тестовый товар",  # Описание товара
                "quantity": 1,  # Количество
                "amount": {
                    "value": amount,  # Сумма товара
                    "currency": "RUB"  # Валюта
                },
                "vat_code": 1,  # НДС (например, 1 — без НДС)
                "payment_mode": "full_payment",  # Способ оплаты
                "payment_subject": "commodity",
            }
        ],
        "email": "example@example.com",  # E-mail покупателя (по желанию)
        "tax_system": 1  # Система налогообложения (например, 1 — общая система)
    }

    payment=yookassa.Payment.create({
        "amount":{
            "value":amount,
            "currency":"RUB",
        },
        "confirmation":{
            "type":"redirect",
            "return_url":prod_link
        },
        "description":"TEst",
        "capture":True,
        "receipt": receipt
    })
    url=payment.confirmation.confirmation_url
    return url,payment.id

async def check_pay(id):
    payment=yookassa.Payment.find_one(id)
    if payment.status=='succeeded':
        return True
    else:
        return False



async def create_payout(amount: str, account_number: str, order_id: str = "1"):
    yookassa.Configuration.account_id = 508808
    yookassa.Configuration.secret_key = "test_*gj0vOVizBTSGzBkBNAtE6TkswkAzuo9An_1e0grb88AY"
    idempotence_key = str(uuid.uuid4())
    payout = yookassa.Payout.create({
        "amount": {
            "value": "2.00",
            "currency": "RUB"
        },
        "payout_destination_data": {
            "type": "yoo_money",
            "account_number": "4100116075156746"
        },
        "description": "Выплата по заказу № 37",
        "metadata": {
            "order_id": "37"
        }
    }, idempotence_key)

    return payout
from django.core.cache import cache
@user_payment_router.callback_query(F.data.startswith("cf_"))
async def check(call:types.CallbackQuery):
    from private import menu
    user_id=call.from_user.id
    pd=call.data.split("cf_")
    print("PD",pd[1])
    print("PD",pd[2])
    print("PD",pd[3])
    try:
        answ=await check_pay(pd[1])
        if answ:
            u = await getuser(user_id)
            expires_at_str = u.get('expires_at')

            moscow_tz = pytz.timezone("Europe/Moscow")
            now = datetime.now(moscow_tz)

            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str).astimezone(moscow_tz)
                except Exception:
                    expires_at = now
            else:
                expires_at = now

            # Если срок истек, обновляем от текущего времени, иначе от expires_at
            if expires_at < now:
                expires_at = now

            # Добавляем дни из pd[3]
            days_to_add = int(pd[3])
            new_expires_at = expires_at + timedelta(days=days_to_add)
            data = {
                "user_id": user_id,
                "pay": True,
                "replenished": int(u.get("replenished", 0)) + int(float(pd[2])),
            }

            if u['task']:
                data["expires_at"] = new_expires_at.isoformat()
            else:
                data["days"] = u['days'] + days_to_add
            await client_add(user_id, u["unique_code"])
            await putsubuser(data)
            await menu(call)
        else:
            await call.answer("Оплата не прошла")
    except:
        await call.answer("Что-то пошло не так")
        await menu(call)


async def success_pay(user_id,price,day):

    from private import menu
    # user_id = call.from_user.id
    # pd = call.data.split("cf_")
    #
    # print("PD", pd[1])#payment
    # print("PD", pd[2])#price
    # print("PD", pd[3])#day
    try:


        u = await getuser(user_id)
        # await call.answer("Оплата прошла успешно")
        remaining_time_str = u['days']  # Например, '00:00:31'

        # Преобразуем строку времени в timedelta (если строка в формате "00:00:31")
        # Проверяем, есть ли разделение на дни и время
        if ' ' in remaining_time_str:
            days, time = remaining_time_str.split()  # Разделяем по пробелу
        else:
            days, time = '0', remaining_time_str  # Если только время без дней

        # Проверяем, что в строке времени правильный формат (часы:минуты:секунды)
        time_parts = time.split(":")

        if len(time_parts) != 3:
            raise ValueError("Некорректный формат времени. Ожидается формат 'часы:минуты:секунды'.")

        # Преобразуем части времени в целые числа
        hours, minutes, seconds = map(int, time_parts)

        # Преобразуем дни в целое число
        days = int(days)

        # Создаем объект timedelta для оставшегося времени (с учетом дней)
        remaining_time = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        # Добавляем количество дней
        updated_time = remaining_time + timedelta(days=int(day))

        # Преобразуем обновленное время в строку формата "дни:часы:минуты:секунды"
        updated_time_str = str(updated_time)

        data = {
            "user_id": user_id,
            "pay": True,
            "replenished": int(u["replenished"]) + int(float(price)),
            "days": updated_time_str
        }
        await putsubuser(data)
        return True
    #         await menu(call)
    #     else:
    #         await call.answer("Оплата не прошла")
    except:
        print("ERRR")
        return False

    #     await call.answer("Что-то пошло не так")
    #     await menu(call)