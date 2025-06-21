import os
from datetime import datetime
import pytz
from aiogram import Router, Bot, types, F
from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext
from typing import List, Dict, Any
from collections import defaultdict
from get_data import *
import kbds
from fsm_add_promocode import AddCompany

from payment import create_pay,check_pay
admin_page=Router()

admin_list=[1059422557,5003194129]



@admin_page.message(Command("newcamp"))
async def newcamp(message:types.Message,state:FSMContext):
    user_id=message.from_user.id
    if user_id in admin_list:
        await message.answer("Введите название кампании")
        await state.set_state(AddCompany.name)
@admin_page.message(Command("statistics"))
async def admin_statistics(message: types.Message) -> None:
    """Обработчик команды /statistics для администраторов."""
    user_id = message.from_user.id
    if user_id not in admin_list:
        await message.answer("Доступ запрещен: вы не администратор.")
        return

    try:
        # Получение данных
        alluser: List[Dict[str, Any]] = await getsubobj()
        gp: List = await getallpromo()

        # Инициализация счетчиков
        stats = defaultdict(int)
        stats.update({
            "lenalluser": len(alluser),
            "replenished": 0,
            "device": 0,
            "shared": 0,
            "referals": 0,
            "promocode": 0,
            "reclam": len(gp),
            "not_subscribe": 0,
            "subscribe": 0
        })

        # Подсчет статистики
        for user in alluser:
            # Проверка компании (рефералы и шаринг)
            company = user.get("company", "")
            if company and company.isdigit():
                stats["shared"] += 1
            elif company and company != "Default":
                stats["referals"] += 1

            # Сумма пополнений
            stats["replenished"] += user.get("replenished", 0)

            # Количество устройств
            # devices = await get_user_device({"user_id": user.get("user_id")})
            # stats["device"] += len(devices or [])

            # Промокоды
            promocode = user.get("promocode", "")
            if promocode and promocode != "BanUser":
                stats["promocode"] += 1

            # Неподписанные пользователи
            stats["not_subscribe"] += 1 if not user.get("pay", False) else 0
            stats["subscribe"] += 1 if user.get("pay", True) else 0
        # Формирование ответа
        response = (
            f"Пополнено: {stats['replenished']}\n"
            f"Пользователи: {stats['lenalluser']}\n"
            f"Есть подписка: {stats['subscribe']}\n"
            f"Нет подписки: {stats['not_subscribe']}\n"
            f"Рекламных: {stats['referals']}\n"
            f"Поделились: {stats['shared']}\n"

        )
        await message.answer(response)

    except Exception as e:
        await message.answer(f"Ошибка при получении статистики: {str(e)}")
        # await message.answer(
        #     f"Пополнено: {replenished}\nАктивные: {active}\nНеактивные: {notactive}\nПользователи: {lenalluser}\nПоделились: {shared}\nРекламные: {referals}\nУстройств: {device}\nПромокоды: {promocode}\nРеклама: {reclam}",
        # )

@admin_page.message(Command("advertis"))
async def admin(message: types.Message):
    user_id = message.from_user.id
    if user_id in admin_list:
        products = await getallpromo()
        if products:
            await show_product(callback=None, products=products, index=0, message=message)
        else:
            await message.answer(".")


@admin_page.callback_query(F.data.startswith("next_"))
async def next_product(callback: types.CallbackQuery):
    # Извлекаем индекс из callback.data
    index = int(callback.data.split("_")[1])
    products = await getallpromo()

    print(f"[DEBUG] Текущий индекс: {index}, Длина списка: {len(products)}")

    if index + 1 < len(products):  # Если следующий элемент существует
        await show_product(callback=callback, products=products, index=index + 1)
    else:
        await callback.answer("Это был последний элемент.", show_alert=True)


@admin_page.callback_query(F.data.startswith("prev_"))
async def previous_product(callback: types.CallbackQuery):
    # Извлекаем индекс из callback.data
    index = int(callback.data.split("_")[1])
    products = await getallpromo()

    print(f"[DEBUG] Текущий индекс: {index}, Длина списка: {len(products)}")

    if index > 0:  # Если предыдущий элемент существует
        await show_product(callback=callback, products=products, index=index - 1)
    else:
        await callback.answer("Это был первый элемент.", show_alert=True)


async def show_product(callback: types.CallbackQuery, products, index: int, message: types.Message = None):
    # Получаем текущий продукт
    current_product = products[index]

    # Создаем кнопки навигации
    btns = {}
    if index > 0:
        btns["⬅️ Назад"] = f"prev_{index}"
    if index + 1 < len(products):
        btns["Вперед ➡️"] = f"next_{index}"

    btns["Ссылка"] = f"url*https://t.me/{os.getenv('link')}?start=company_{current_product['slug']}"
    reply_markup = kbds.sharekb(btns)
    given_date = datetime.fromisoformat(current_product["added_time"])

    # Форматируем дату в классическом виде: 26 мая 2025
    date = given_date.strftime("%d.%m.%Y")
    # data={
    #     'promo':gp["name"]
    # }
    # usersprom=await getpromouser(data)
    # usersnotprom=await getnotpromouser(data)
    # if not usersprom:
    #     usersprom=[]
    # if not usersnotprom:
    #     usersnotprom = []
    # usersall=await getsubobj()
    data={
        "company":current_product["slug"]
    }
    replenished=0
    active=0
    notactive=0
    not_subscribe=0
    uc=await get_user_company(data)
    lencomp=len(uc)
    for i in uc:
        replenished+=i['replenished']
        if i["pay"] is True :
            active+=1
        else:
            notactive+=1
        if not i['pay']:
            not_subscribe+=1
    # Отправляем или редактируем сообщение


    given_date=current_product["added_time"]
    given_date = datetime.fromisoformat(given_date)
    timezone = pytz.timezone("Europe/Moscow")
    current_date = datetime.now(timezone)
    time_difference = current_date - given_date

    col_vved_promo=0
    user_promo=await getsubobj()
    print(current_product["promo"])
    for ii in user_promo:
        print(ii["promocode"])
        if ii["promocode"] == f'{current_product["promo"]}':
            col_vved_promo+=1
    if callback:

        await callback.message.edit_text(f"Создана: {date}\nНазвание: {current_product['name']}\nПополнено: {replenished}\nЕсть подписка: {active}\nНет подписки: {not_subscribe}\nПользователи: {lencomp}",
            reply_markup=reply_markup
        )
    else:
        await message.answer(
            f"Создана: {date}\nНазвание: {current_product['name']}\nПополнено: {replenished}\nЕсть подписка: {active}\nНет подписки: {not_subscribe}\nПользователи: {lencomp}",
            reply_markup=reply_markup
        )


@admin_page.callback_query(F.data.startswith("details_"))
async def details(call:types.CallbackQuery):
    from private import bot_link
    c=call.data.split("_")[1]
    gp=await getallpromo(c)

    filtered_data = list(filter(lambda x: x is not None, gp["added_time"]))
    date = "".join(filtered_data).split("T")[0].replace("-", ".")
    date_parts = date.split(".")
    reversed_date = ".".join(date_parts[::-1])
    # data={
    #     'promo':gp["name"]
    # }
    # usersprom=await getpromouser(data)
    # usersnotprom=await getnotpromouser(data)
    # if not usersprom:
    #     usersprom=[]
    # if not usersnotprom:
    #     usersnotprom = []
    # usersall=await getsubobj()
    data={
        "company":gp["name"]
    }
    replenished=0
    active=0
    notactive=0
    uc=await get_user_company(data)
    lencomp=len(uc)
    for i in uc:
        replenished+=i['replenished']
        if i["pay"] is True:
            active+=1
        else:
            notactive+=1



    await call.message.edit_text(f"Компания: {gp['id']}/{reversed_date}\nНазвание: {gp['name']}\nПромокод: {gp['promo']}\nБонусных: {gp['days']} дней\nАктивные: {active}\nНеактивные: {notactive}\nПользователи: {lencomp}",reply_markup=kbds.sharekb(
        {"Назад": f"promoback_{c}","Ссылка":f"url*{bot_link}company_{gp['name']}"}))


@admin_page.callback_query(F.data.startswith("promoback_"))
async def backpromo(call:types.CallbackQuery):
    c = call.data.split("_")[1]
    gap=await getallpromo(c)
    await call.message.edit_text(f"Название компании:\n\n{gap['name']}",reply_markup=kbds.createkb({"Описание":f"details_{gap['id']}"}))



