import datetime
from math import ceil
import yookassa
import asyncio
import uuid
from datetime import timedelta
import pytz
from aiogram.fsm.context import FSMContext
from aiogram import Router,Bot, types, F
from aiogram.filters import CommandStart,Command
import kbds
from payment import create_pay,check_pay,success_pay,create_payout
from fsm_promocode import AddCode

from get_data import *
from datetime import datetime
user_private_router=Router()



from promotion import task
bot_link=f"https://t.me/{os.getenv('link')}?start="
from  promotion import  scheduler



@user_private_router.message(CommandStart())
async def start(message:types.Message,bot:Bot,state:FSMContext):
    from promotion import scheduler, task_time
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz)


    print(task_time)
    await state.clear()
    # await ssh_connect_and_update_db()
    user_id = message.from_user.id
    u = await getuser(user_id)
    command_text = message.text
    company=""
    # print(await get_promotion())
    if u:
        print("user exists")

    else:
        data = {
            "user_id": user_id,
            "expires_at": (now + timedelta(days=0)).isoformat(),
            "days":2,
            "company": company
        }

        # Добавляем нового пользователя в базу данных
        await postuser(data)
        # Если пользователя нет в базе, обрабатываем команду
        args = command_text.split(maxsplit=1)[1] if len(command_text.split()) > 1 else None

        if args:

            if args.isdigit():
                company_data = {
                    "user_id": user_id,
                    "company": int(args)
                }
                print(args)
                param = args
                uparam = await getuser(param)
                ref_user_id = int(param)

                ref_user = await getuser(ref_user_id)
                if ref_user:
                    expires_at_str = ref_user.get("expires_at")


                    expires_at = None

                    if expires_at_str:
                        try:
                            # Пробуем распарсить как полную дату-время
                            expires_at = datetime.fromisoformat(expires_at_str).astimezone(moscow_tz)
                        except ValueError:
                            try:
                                # Если не получилось, возможно это просто время без даты
                                time_obj = datetime.strptime(expires_at_str, "%H:%M:%S.%f").time()
                            except ValueError:
                                try:
                                    time_obj = datetime.strptime(expires_at_str, "%H:%M:%S").time()
                                except Exception:
                                    time_obj = None

                            if time_obj:
                                # Объединяем с сегодняшней датой
                                expires_at = datetime.combine(now.date(), time_obj)
                                expires_at = moscow_tz.localize(expires_at)
                            else:
                                expires_at = now
                    else:
                        expires_at = now

                    # Добавляем 50 дней
                    new_expires_at = expires_at + timedelta(days=50)
                    if uparam['task']:
                        refdata = {
                            "user_id": ref_user_id,
                            "expires_at": new_expires_at.isoformat()
                        }
                    else:
                        refdata = {
                            "user_id": ref_user_id,
                            "days": uparam['days'] + 50
                        }
                    await bot.send_message(
                        ref_user_id,
                        "Поздравляем! За активность поделиться, на баланс Вашего бота начислено 50 бонусных дней совершенно бесплатно!",
                        reply_markup=kbds.createkb({"Отлично": "thanks"})
                    )

                    await putsubuser(refdata)

                else:
                    await bot.send_message(user_id, "Ошибка: не удалось найти реферера для начисления бонусов.")
            elif args.startswith("company_"):
                param = args.split("company_")
                print(param[1])
                company_data = {
                    "user_id": user_id,
                    "company": param[1]
                }


            else:
                company_data = {
                    "user_id": user_id,
                    "company": "Default"
                }
            u = await getuser(user_id)
            if not u["company"]:
                await putsubuser(company_data)
        else:
            u = await getuser(user_id)
            company_data = {
                "user_id": user_id,
                "company": 'Default'
            }
            if not u["company"]:
                await putsubuser(company_data)



    u = await getuser(user_id)

    moscow_tz = pytz.timezone("Europe/Moscow")
    moscow_time = datetime.now(moscow_tz)

    # Преобразуем строку в datetime с учётом часового пояса
    remaining_time_str = u.get('expires_at') # например, '2025-05-19T12:13:24+03:00'
    if u['task']:
        if remaining_time_str:
        # Преобразуем строку в datetime с учётом часового пояса
            expires_at = datetime.fromisoformat(remaining_time_str).astimezone(moscow_tz)

            # Вычисляем дельту между временем окончания и сейчас
            delta = expires_at - moscow_time
            total_seconds = max(delta.total_seconds(), 0)

            # Корректное вычисление дней, часов и минут
            days = int(total_seconds // 86400)  # целое число дней
            hours = int((total_seconds % 86400) // 3600)  # остаток часов
            minutes = int((total_seconds % 3600) // 60)  # остаток минут
        else:
            days = 0  # целое число дней
            hours = 0
             # остаток часов
            minutes = 0  # остаток минут
    else:
        days=u['days']
        hours = 0
        minutes = 0
    if message.from_user.id in [1059422557,7287871980]:
        remaining_text = f"Дней:{days}Часов:{hours}Минут:{minutes}"
    else:
        remaining_text = f"{days} КЕДОДНЕЙ"
    prom = await get_promotion()
    kbl= {"🕶 Подписка" : "sub", "❗️Подключить": "connect", "🚁 Поддержка": "url>>https://t.me/kedoask911",
         "⚡️ Поделиться": f"url*{bot_link}{user_id}"}
    if user_id==1059422557:
        kbl["Отключить"]="my_device"
    await message.answer(f"ВАША ПОДПИСКА {remaining_text}",reply_markup=kbds.sharekb(kbl))


@user_private_router.callback_query(F.data.startswith("menu"))
async def menu(call:types.CallbackQuery):
    user_id=call.from_user.id
    u = await getuser(user_id)
    moscow_tz = pytz.timezone("Europe/Moscow")
    moscow_time = datetime.now(moscow_tz)

    # Преобразуем строку в datetime с учётом часового пояса
    remaining_time_str = u.get('expires_at')  # например, '2025-05-19T12:13:24+03:00'
    if u['task']:
        if remaining_time_str:
        # Преобразуем строку в datetime с учётом часового пояса
            expires_at = datetime.fromisoformat(remaining_time_str).astimezone(moscow_tz)

            # Вычисляем дельту между временем окончания и сейчас
            delta = expires_at - moscow_time
            total_seconds = max(delta.total_seconds(), 0)

            # Корректное вычисление дней, часов и минут
            days = int(total_seconds // 86400)  # целое число дней
            hours = int((total_seconds % 86400) // 3600)  # остаток часов
            minutes = int((total_seconds % 3600) // 60)  # остаток минут
        else:
            days=0
    else:
        days = u['days']
        hours = 0
        minutes = 0

    remaining_text = f"{days} КЕДОДНЕЙ"


    await call.message.edit_text(f"ВАША ПОДПИСКА {remaining_text}",reply_markup=kbds.sharekb(
        {"🕶 Подписка" : "sub", "❗️Подключить": "connect", "🚁 Поддержка": "url>>https://t.me/kedoask911",
         "⚡️ Поделиться": f"url*{bot_link}{user_id}"}))
    #
    # await message.answer()

@user_private_router.callback_query(F.data.startswith("sub"))
async def sub_menu(call:types.CallbackQuery,state:FSMContext):
    from promotion import promotion
    await state.clear()
    user_id = call.from_user.id
    payment=call.data.split("_")[-1]

    if scheduler.get_job(f"paytask_{user_id}"):
        if payment:
            try:
                get_payment = await asyncio.to_thread(yookassa.Payment.find_one, payment)

                if get_payment.status == "pending":
                    idempotence_key = str(uuid.uuid4())

                    print(get_payment.status)
                    await call.answer("Покупка отменена!")


            except Exception as e:
                    print(e)
            


    # t= await gettime()
    t={30:72,90:189,180:324,360:540}

    l={ f"{day} дней {price}₽":f"time_{day}_{price}" for day,price in t.items()}





    l["Назад"]="menu"


    await call.message.edit_text("*Внезапная акция\\!* Сегодня с 10\\:00 до 20\\:00 при оплате любого профиля Вы получаете бонусные дни совершенно бесплатно\\!" if promotion else "Выберите профиль оплаты",reply_markup=kbds.createkb(l,2,2,back=True,mod=True),parse_mode="MarkdownV2")

@user_private_router.callback_query(F.data.startswith("time"))
async def time_menu(call:types.CallbackQuery,bot:Bot):

    user_id=call.from_user.id
    # from payment import pay
    from promotion import promotion
    c=call.data.split("_")
    # print(c)
    c_day=c[1]
    # print(c_time)
    # c_name=c[2]
    c_price=c[2]


    # try:
    #
    #     c_promo=c[4]
    #     if c_promo and not promotion:
    #         t = await gettime()
    #         l = {f'{i["time"]}' if i["time"].split(" ")[
    #                                    1] == "мес" else f'{i["time"]}': f'time_{float(i["time"].split(" ")[0]) * 30}_{i["time"]}_{float(i["time"].split(" ")[0]) * 200}' if
    #         i["time"].split(" ")[
    #             1] == "мес" else f'time_{float(i["time"].split(" ")[0]) * 360}_{i["time"]}_{float(i["time"].split(" ")[0]) * (2400)}'
    #              for i in t}
    #         await call.message.edit_text("Выберите профиль оплаты",reply_markup=kbds.createkb(l,2,2,back=True,mod=True),parse_mode="MarkdownV2")
    #         return
    #     print(c_promo)
    # except:
    #     ...
    end_time = datetime.now() + timedelta(minutes=10)
    link,payment=await create_pay(c_price)

    text= f"Оплата {c_day} дней составит"

    pay_message=await call.message.edit_text(f"{text} {c_price} рублей!\n\nПосле оплаты нажмите Подтвердить!",reply_markup = kbds.sharekb({
    f"Оплатить": f"url>>{link}",
    "Подтвердить": f"cf_{payment}cf_{c_price}cf_{c_day}",
    "Назад": f"sub_{payment}"}))


async def pay_task(pay_message_id,payment,price,day,user_id,bot:Bot,end_time):
    if datetime.now()>=end_time:
        try:
            get_payment = await asyncio.to_thread(yookassa.Payment.find_one, payment)
            if get_payment.status == "pending":
                idempotence_key = str(uuid.uuid4())
                await asyncio.to_thread(yookassa.Payment.cancel, payment, idempotence_key)
        except Exception as e:
            print(f"Error canceling payment: {e}")
        await bot.delete_message(user_id,pay_message_id)
        await bot.send_message(user_id,"Время покупки истекло!",reply_markup=kbds.createkb({"Меню":"menu"}))
        scheduler.remove_job(f"paytask_{user_id}")
        return
    if payment:
        try:
            get_payment = await asyncio.to_thread(yookassa.Payment.find_one, payment)


            if get_payment.status == 'waiting_for_capture':

                captured = await asyncio.to_thread(yookassa.Payment.capture, payment)


                if captured.status == 'succeeded':
                    result = await success_pay(user_id, price, day)
                    await bot.delete_message(user_id, pay_message_id)
                    if result:
                        await bot.send_message(user_id, "Оплата прошла успешно!",
                                               reply_markup=kbds.createkb({"Меню": "menu"}))
                    else:
                        await bot.send_message(user_id, "Что-то пошло не так",
                                               reply_markup=kbds.createkb({"Меню": "menu"}))
                    scheduler.remove_job(f"paytask_{user_id}")  # Удаляем задачу при успешной оплате
                else:
                    await bot.delete_message(user_id, pay_message_id)
                    await bot.send_message(user_id, "Что-то пошло не так", reply_markup=kbds.createkb({"Меню": "menu"}))
                    scheduler.remove_job(f"paytask_{user_id}")  # Удаляем задачу при неуспешной оплате
            else:
                ...
                # Не удаляем задачу, чтобы она продолжила проверку в следующей итерации
        except Exception as e:
            print(f"Error fetching payment: {e}")

            await bot.send_message(user_id, "Ошибка при проверке платежа", reply_markup=kbds.createkb({"Меню": "menu"}))
            scheduler.remove_job(f"paytask_{user_id}")  # Удаляем задачу при ошибке


@user_private_router.callback_query(F.data.startswith("promcode_"))
async def promocode(call:types.CallbackQuery,state:FSMContext):
    await call.message.edit_text("Активируй рекламный промокод!",reply_markup=kbds.createkb({"Назад":"sub"}))
    await state.set_state(AddCode.name)





@user_private_router.callback_query(F.data.startswith("connect"))
async def connect_menu(call:types.CallbackQuery):
    user_id=call.from_user.id

    device={"iPhone":1,"MacOS":2,"Android":3,"Windows":4}
    l={device_name:f'device_{device_id}_{device_name}' for device_name,device_id in device.items()}
    # l={i["name"]:f'device_{i["id"]}_{i["name"]}' for i in g}
    l["Назад"] = "menu"

    await call.message.edit_text("Выберите ваше устройство",reply_markup=kbds.createkb(l,mod=True))





@user_private_router.callback_query(F.data.startswith("device_"))
async def device_menu(call:types.CallbackQuery):
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz)
    user_id=call.from_user.id
    c_data = call.data.split("_")
    c_id=c_data[1]
    c_name=c_data[2]
    u=await getuser(user_id)

    if u.get("expires_at"):
        expires_at = datetime.fromisoformat(u["expires_at"]).astimezone(moscow_tz)
    else:
        expires_at = now.astimezone(moscow_tz)

    if expires_at > now or u.get("days")>0:
        if u.get("days")>0 and not u.get("task"):
            putdata = {
                "user_id":user_id,
                "task":True,
                "days":0,
                "expires_at":(now.astimezone(moscow_tz) + timedelta(days= u.get("days"))).isoformat(),
            }
            await putsubuser(putdata)

            # if u["task"]:
            #     print("задача запущена для этого пользователя")
            # else:
            #     ...
            #     await start_task(user_id)
            # await subdevpost(data)

        if u["unique_code"]:
            unique_code=u["unique_code"]

        else:

            unique_code = str(uuid.uuid4())
            putdata = {
                "user_id": user_id,
                "unique_code": unique_code
            }
            await putsubuser(putdata)

        await client_add(user_id,unique_code)

        # try:
        #
        vless = ""
        try:
            if c_data[3]:
                vless = f"\n\n<code>vless://{unique_code}@88.218.93.116:443?type=tcp&security=reality&pbk=uspoUEMq2eiqHZVEx-HfVfvg4cmSv2BD7KWScoMl8xY&fp=chrome&sni=yahoo.com&sid=3a8982c07635&spx=%2F&flow=xtls-rprx-vision#KEDOVPN-{user_id}</code>"



            if c_name == "Android":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция":f"instr_{c_id}_{c_name}",
                                               "Приложение":"url>>https://play.google.com/store/apps/details?id=com.v2raytun.android",
                                               "Скрыть":f'device_{c_id}_{c_name}_vless',"Назад":"connect"},mod=True),
                    parse_mode="HTML")

            elif c_name =="iPhone":
                await call.message.edit_text(
                   f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция":f"instr_{c_id}_{c_name}",
                                               "Приложение":"url>>https://apps.apple.com/ru/app/streisand/id6450534064",
                                               "Скрыть":f'device_{c_id}_{c_name}_vless',"Назад":"connect"},mod=True),
                    parse_mode="HTML")

            elif c_name == "MacOS":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция":f"instr_{c_id}_{c_name}",
                                               "Приложение":"url>>https://apps.apple.com/ru/app/streisand/id6450534064",
                                               "Скрыть":f'device_{c_id}_{c_name}_vless',"Назад":"connect"},mod=True),
                    parse_mode="HTML")

            elif c_name == "Windows":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция":f"instr_{c_id}_{c_name}",
                                               "Приложение":"url>>https://storage.v2raytun.com/v2RayTun_Setup.exe",
                                               "Скрыть":f'device_{c_id}_{c_name}_vless',"Назад":"connect"},mod=True),
                    parse_mode="HTML")

        except:
            vless=""
            if c_name == "Android":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция": f"instr_{c_id}_{c_name}",
                                               "Приложение": "url>>https://play.google.com/store/apps/details?id=com.v2raytun.android",
                                               "Подключить": f'device_{c_id}_{c_name}_vless', "Назад": "connect"},mod=True),
                    parse_mode="HTML")

            elif c_name == "iPhone":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция": f"instr_{c_id}_{c_name}",
                                               "Приложение": "url>>https://apps.apple.com/ru/app/streisand/id6450534064",
                                               "Подключить": f'device_{c_id}_{c_name}_vless', "Назад": "connect"},mod=True),
                    parse_mode="HTML")

            elif c_name == "MacOS":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция": f"instr_{c_id}_{c_name}",
                                               "Приложение": "url>>https://apps.apple.com/ru/app/streisand/id6450534064",
                                               "Подключить": f'device_{c_id}_{c_name}_vless', "Назад": "connect"},mod=True),
                    parse_mode="HTML")

            elif c_name == "Windows":
                await call.message.edit_text(
                    f'➡️ VPN активирован! Осталось 3 шага:\n\n1️⃣Скачайте установите прокси-клиент\n<b>✅Приложение</b>\n\n2️⃣Скопируйте созданный ключ-ссылку\n<b>✅Подключить</b>{vless}\n\n3️⃣Вставьте ключ-ссылку в приложение\n<b>✅Инструкция</b>',
                    reply_markup=kbds.sharekb({"Инструкция": f"instr_{c_id}_{c_name}",
                                               "Приложение": "url>>https://storage.v2raytun.com/v2RayTun_Setup.exe",
                                               "Подключить": f'device_{c_id}_{c_name}_vless', "Назад": "connect"},mod=True),
                    parse_mode="HTML")

    else:
        await call.message.edit_text("Для активации выбранного Вами устройства необходима подписка",reply_markup=kbds.createkb({"Подписка":"sub","Назад":"menu"}))

@user_private_router.callback_query(F.data.startswith("instr_"))
async def instr(call:types.CallbackQuery):
    device=call.data.split("_")
    device_id=device[1]
    device_name=device[2]
    device_inst={"Android":"➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к Android. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение v2RayTun.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в v2RayTun. Дайте разрешение на получение уведомлений. Теперь справа вверху приложения нажмите на плюс и выберите: Импорт из буфера обмена и ваша конфигурация добавится в прокси-клиент и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
                 "iPhone":"➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к iPhone. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение Streisand.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в Streisand. Теперь справа вверху Streisand нажмите на плюс и выберите: Добавить из буфера, дайте разрешение на вставку и ваша конфигурация добавится в прокси-клиент и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
                 "MacOS":"➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к MacOS. Для начала нажмите кнопку Приложение, которое Вас перенаправит на страницу прокси-клиента. Скачайте и установите приложение Streisand.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в Streisand. Запустите Streisand, нажмите на плюс в правом верхнем углу и выбираем: Добавить из буфера обмена и нажимаем Подключить и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно.",
                 "Windows":"➡️ Здравствуйте, Вы находитесь в разделе Подключить, тем самым активировали VPN данного устройства, этот раздел поможет Вам подключить VPN к Windows. Для начала нажмите кнопку Приложение, которое скачает Вам прокси-клиент в папку «Загрузки». Установите приложение v2RayTun.\n\n➡️ Далее нажмите кнопку Подключить и скопируйте одним нажатием конфигурацию, которую необходимо добавить в v2RayTun. Запустите v2RayTun, нажмите на плюс в правом верхнем углу и выбираем: Импорт из буфера обмена и нажимаем Подключить и теперь VPN к работе готов.\n\n➡️ Так же хотел напомнить о реферальной программе. Если Вам понравится Kedo VPN, свободно делитесь приложением через кнопку Поделиться в Главном меню и получайте по 50 бонусных дней за каждого пользователя бесплатно."}
    await call.message.edit_text(device_inst[device_name],reply_markup=kbds.sharekb({"Скрыть": f"device_{device_id}_{device_name}",
                                               "Приложение": "url>>https://storage.v2raytun.com/v2RayTun_Setup.exe",
                                               "Подключить": f'device_{device_id}_{device_name}_vless', "Назад": "connect"},mod=True),)
    await call.answer()
@user_private_router.message(F.video)
async def video(mess:types.Message):
    await mess.reply(f"{mess.video.file_name}\n\n{mess.video.file_id}")
# file_id = ""
# @user_private_router.callback_query(F.data.startswith("download_exe"))
# async def exe(call:types.CallbackQuery,bot:Bot):
#     global file_id
#     user_id=call.from_user.id
#     if file_id!="":
#         await bot.send_document(user_id,file_id)
#     else:
#         fid=await bot.send_document(user_id,FSInputFile("NekoRay.exe"))
#         file_id=fid.document.file_id

@user_private_router.callback_query(F.data.startswith("deact_"))
async def deact(call:types.CallbackQuery):
    user_id = call.from_user.id
    # c=call.data.split("_")[1]
    u = await getuser(user_id)
    # data={
    #     "user_id":user_id,
    #     "device":c
    # }
    # user_data={
    #     "user_id": user_id,
    # }
    # ud = await get_user_device(user_data)
    # print(len(ud))
    # if len(ud)==1:
    putdata = {
        "user_id": user_id,
        "unique_code": "",
        "task":False,
        "pay":False
    }
    await putsubuser(putdata)
    await client_del(u["unique_code"])
    await deact_task(user_id)
    # await del_user_dev(data)
    await menu(call)
    # await call.message.edit_text("У вас нет активных устройств",reply_markup=kbds.createkb({"Назад":"menu"}))

@user_private_router.callback_query(F.data.startswith("my_device"))
async def my_device(call:types.CallbackQuery):
    user_id=call.from_user.id
    user_data=await getuser(user_id)
    print(user_data)
    l={}
    if user_data['task']:
        l["Отключить"]="deact_{cd_name}"
    l["Назад"] = "menu"
    await call.message.edit_text("Управление активацией конфигураций",reply_markup=kbds.createkb(l))
    # data={
    #     "user_id":user_id
    # }
    # d = await getdevice()
    # l1=[i["id"] for i in d]
    # # print(l1)
    # ud= await get_user_device(data)
    # l = {i["device_name"]: f'devicesett_{i["device_name"]}_{user_id}' for i in ud}
    # if ud:
    #     sorted_l = {
    #         k: v
    #         for k, v in sorted(
    #             l.items(),
    #             key=lambda item: next(d["device_id"] for d in ud if d["device_name"] == item[0])
    #         )
    #     }
    #
    #     sorted_l["Назад"] = "menu"
    #     await call.message.edit_text("Ваши активные устройства", reply_markup=kbds.createkb(sorted_l, 1, 1, back=True))
    # else:
    #     await call.message.edit_text("Ваши устройства неактивны",reply_markup=kbds.createkb({"Назад":"menu"},1,1))

@user_private_router.callback_query(F.data.startswith("devicesett_"))
async def my_devicesett(call:types.CallbackQuery):
    user_id=call.from_user.id
    cd=call.data.split("_")
    cd_name=cd[1]
    cd_user_id=cd[2]
    data={
        "user_id":user_id
    }
    ud= await get_user_device(data)
    l=[i["added_time"] if i["device_name"]==cd_name else None for i in ud]
    filtered_data = list(filter(lambda x: x is not None, l))
    date="".join(filtered_data).split("T")[0].replace("-",".")
    date_parts = date.split(".")
    reversed_date = ".".join(date_parts[::-1])


    await call.message.edit_text(f"Устройство: {cd_name}\n\nПользователь: {cd_user_id}\n\nВремя активации: {reversed_date}",reply_markup=kbds.createkb({"Конфигурация":f"conf_{cd_name}","Отключить":f"deact_{cd_name}","Назад":"menu"},1,1,back=True))


@user_private_router.callback_query(F.data.startswith("conf_"))
async def conf(call:types.CallbackQuery):
    user_id=call.from_user.id
    device=call.data.split("_")[1]
    u = await getuser(user_id)
    unique_code=u["unique_code"]
    await call.message.edit_text(f"`vless://{unique_code}@88.218.93.116:443?type=tcp&security=reality&pbk=uspoUEMq2eiqHZVEx-HfVfvg4cmSv2BD7KWScoMl8xY&fp=chrome&sni=yahoo.com&sid=3a8982c07635&spx=%2F&flow=xtls-rprx-vision#KEDOVPN-{user_id}`",parse_mode="Markdown",reply_markup=kbds.createkb({"Назад":f"devicesett_{device}_{user_id}"}))

@user_private_router.callback_query(F.data.startswith("instr"))
async def instr_menu(call:types.CallbackQuery):
    await call.message.edit_text("1️⃣Базовая информация\n\n2️⃣Реферальные бонусы\n\n3️⃣Поддержка клиентов",reply_markup=kbds.createkb({"1":"podinstr_1","2":"podinstr_2","3":"podinstr_3","Назад":"menu"},3,3,back=True))

@user_private_router.callback_query(F.data.startswith("podinstr"))
async def podinstr(call:types.CallbackQuery):
    c=call.data.split("_")[1]
    try:
        if c == "1":
            await call.message.edit_text("В Kedo VPN отсутствуют ограничения на скорость и количество трафика, можете смотреть YouTube стабильно в 4k, сервис не имеет скрытой системы подписок, профиль покупается разом."
                                         , reply_markup=kbds.createkb({"1":"podinstr_1","2":"podinstr_2","3":"podinstr_3","Назад":"instr"},3,3,back=True))
        if c=="2":
            await call.message.edit_text('Спасайте своих друзей от некачественных и дорогих vpn сервисов. Свободно делитесь Kedo VPN через «Поделиться» и получайте по 50 бонусных дней за каждого пользователя.',reply_markup=kbds.createkb({"1":"podinstr_1","2":"podinstr_2","3":"podinstr_3","Назад":"instr"},3,3,back=True))

        if c=="3":
            await call.message.edit_text("Если при работе с ботом возникли сложности или вы просто хотите задать вопрос, обращайтесь в наше бюро поддержки @kedoask911 и мы постараемся ответить на ваш вопрос.",reply_markup=kbds.createkb({"1":"podinstr_1","2":"podinstr_2","3":"podinstr_3","Назад":"instr"},3,3,back=True))
    except:
        ...




@user_private_router.callback_query(F.data.startswith("wont_5"))
async def wont_5(call:types.CallbackQuery):
    user_id=call.from_user.id
    # u=await getuser(user_id)
    data = {
        "user_id": user_id,
        "days": 5 * 24 * 60 * 60,

    }


    # Добавляем нового пользователя в базу данных
    await putsubuser(data)
    await call.message.edit_text("Поздравляем! На Ваш баланс зачислено 5 бонусных дней!",reply_markup=kbds.createkb({"Отлично":"thanks"}))

@user_private_router.callback_query(F.data.startswith("thanks"))
async def thanks(call:types.CallbackQuery,state:FSMContext):
    await call.message.delete()
    await state.clear()





from mailing_list import Mailing
@user_private_router.message(Command("mailing"))
async def startm(message:types.Message,state:FSMContext):
    await message.answer("Введите пожалуйста текст для рассылки пользователям")
    await state.set_state(Mailing.text)


@user_private_router.message(Command("payout"))
async def payout(message:types.Message):
    await create_payout("100","5555555555554477","1")