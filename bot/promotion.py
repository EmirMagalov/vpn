from datetime import datetime
import pytz
from aiogram import Router, Bot, types, F
from aiogram.filters import CommandStart,Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from get_data import *
import kbds
from datetime import datetime, timedelta
import asyncio
promotion_router=Router()
scheduler = AsyncIOScheduler()
import logging
task_time = None
async_task=None
promotion=False
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логов: DEBUG, INFO, WARNING, ERROR, CRITICAL
    stream=sys.stdout,   # Поток вывода логов (в стандартный вывод)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Формат логов
)

logger = logging.getLogger(__name__)
async def wait_until_task(bot):
    global async_task
    try:
        moscow_tz = pytz.timezone('Europe/Moscow')
        global task_time
        while True:
            now = datetime.now(moscow_tz)
            # Если текущее время >= времени выполнения
            if task_time and now >= task_time:
                print(f"next day task {task_time}")
                scheduler.add_job(task, 'cron', args=[bot], hour="10-20", minute="*",
                                  id="daily_task",timezone=moscow_tz)
                if async_task:
                    async_task=None
                    task_time = None
                break  # Завершаем цикл после выполнения задачи
            await asyncio.sleep(10)  # Проверяем каждые 10 секунд
    except asyncio.CancelledError:
       return
# Команда /schedule для установки задачи

async def schedule_command(bot):
    moscow_tz = pytz.timezone('Europe/Moscow')
    global task_time,async_task
    try:

        now = datetime.now(moscow_tz)
        task_time = moscow_tz.localize(
            datetime.combine(
                (now + timedelta(days=1)).date(),
                datetime.strptime("09:58", "%H:%M").time()
            )
        )
        # Запускаем задачу ожидания
        async_task=asyncio.create_task(wait_until_task(bot))
    except Exception as e:
        print("err")

async def push_time(call):
    t = await gettime()
    await putsubuser({
        "user_id": call.from_user.id,
        "look_promotion": f"{call.message.message_id},SKIP,"
    })
    l = {f'{i["time"]} + {int(i["time"].split(" ")[0]) * 10} дней' if i["time"].split(" ")[
                                                                          1] == "мес" else f'{i["time"]} + 120 дней': f'time_{(float(i["time"].split(" ")[0]) * 30) + int(i["time"].split(" ")[0]) * 10}_{i["time"]}_{float(i["time"].split(" ")[0]) * 200}_promo' if
    i["time"].split(" ")[
        1] == "мес" else f'time_{float(i["time"].split(" ")[0]) * 360 + 120}_{i["time"]}_{float(i["time"].split(" ")[0]) * (2400)}_promo'
         for i in t}

    l["Промокод"]="promcode_"
    l["Назад"]="menu"
    await call.message.edit_text(
        "*Прибыльные дни\\!* Сегодня с 10\\:00 до 20\\:00 при оплате любого профиля Вы получаете бонусные дни совершенно бесплатно\\!",
        reply_markup=kbds.createkb(l, 2, 2, back=True, mod=True),parse_mode="MarkdownV2")

@promotion_router.callback_query(F.data.startswith("promotion_cancel"))
async def promot_c(call:types.CallbackQuery,bot:Bot):
    global task_time,async_task,promotion
    job = scheduler.get_job("daily_task")
    if job:
        job.remove()
        # data = {
        #     "promotion": False
        # }
    promotion=False
        # await put_promotion(data)

    allus = await getsubobj()
    try:
        for i in allus:
            await putsubuser({
                "user_id": int(i['user_id']),
                "look_promotion": None
            })
    except:
        ...
    if async_task:
        task_time = None

        async_task=None

    await call.message.edit_text("Промо-акция отменена")
@promotion_router.message(Command("action"))
async def promot(message:types.Message,bot:Bot):
    global task_time,async_task
    if not scheduler.get_job("daily_task") and not async_task:
        await message.answer("Активировать промоакцию?",reply_markup=kbds.createkb({"Запустить":"promote_activate","Отменить":"thanks"}))
    else:
        await message.answer("Промоакция активирована", reply_markup=kbds.createkb(
            {"Оставить": "thanks","Отменить": "promotion_cancel"}))
    logger.info(task_time)
    logger.info(async_task)
    logger.info(datetime.now())



@promotion_router.callback_query(F.data.startswith("look_promotion"))
async def look_promotion(call:types.CallbackQuery,bot:Bot):
    user_id = call.from_user.id
    # await putsubuser({
    #     "user_id": user_id,
    #     "look_promotion": None
    # })
    # gu = await getuser(user_id)
    # if gu.get("look_promotion"):
    #     l = [i for i in gu["look_promotion"].split(",") if i]
    #
    #     if l and len(l) > 1:
    #         newl = l[:-1]
    #         print(newl)
    #         for j in newl:
    #             try:
    #                 await bot.delete_message(chat_id=user_id, message_id=int(j))
    #             except:
    #                 ...
    await push_time(call)




@promotion_router.callback_query(F.data.startswith("promote_activate"))
async def promote_activate(call:types.CallbackQuery,bot:Bot):
    global task_time
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz).time()
    # chat_id = call.message.chat.id
    #
    if now.hour >= 10 and now.minute >= 1:
        if not scheduler.get_job("daily_task") and not async_task:
            await schedule_command(bot)
        #     # await task(bot)
        #     today = datetime.now()
        #     current_day_of_week = today.weekday()  # Возвращает день недели (0 - понедельник, 6 - воскресенье)
        #
        #     # Прибавляем 1 к текущему дню недели (если сегодня воскресенье, то следующий день будет понедельник)
        #     next_day_of_week = (current_day_of_week + 1) % 7
        #
        #     # Устанавливаем время на 8:00 следующего дня
        #     scheduler.add_job(task, 'cron', day_of_week=next_day_of_week, args=[bot] ,hour="10-20", minute="*",
        #                   id="daily_task")
            await call.message.answer("Промоакция активирована", reply_markup=kbds.createkb(
                {"Оставить": "thanks", "Отменить": "promotion_cancel"}))
        else:
            await call.message.answer("Промоакция активирована",reply_markup=kbds.createkb({"Оставить":"thanks","Отменить":"promotion_cancel"}))
    else:
        if not scheduler.get_job("daily_task") and not task_time:
            scheduler.add_job(task, 'cron',  args=[bot], hour="10-20", minute="*",
                              id="daily_task",timezone=moscow_tz)

            await call.message.answer("Промоакция активирована", reply_markup=kbds.createkb(
                {"Оставить": "thanks", "Отменить": "promotion_cancel"}))
        # await message.answer("Задача успешно запущена с 15:15 до 19:00.")
        else:
            await call.message.answer("Промоакция активирована",reply_markup=kbds.createkb({"Оставить":"thanks","Отменить":"promotion_cancel"}))
    await call.message.delete()





async def task(bot:Bot):
    moscow_tz = pytz.timezone('Europe/Moscow')
    """Функция, выполняющая задачу"""
    global promotion,async_task,task_time
    now = datetime.now(moscow_tz).time()

    if now.hour == 10 and now.minute == 0:
        # data={
        #     "promotion":True
        # }
        #
        # await put_promotion(data)
        promotion=True
        allus = await getsubobj()
        for i in allus:
            try:
                messp = await bot.send_message(int(i['user_id']),
                                               "*Внезапная акция\\!* Сегодня с 10\\:00 до 20\\:00 при оплате любого профиля Вы получаете бонусные дни совершенно бесплатно\\!",
                                               reply_markup=kbds.createkb(
                                                   {"Посмотреть": "look_promotion", "Отклонить": "menu"}),
                                               parse_mode="MarkdownV2")
                if i['look_promotion']:
                    await putsubuser({
                        "user_id": i['user_id'],
                        "look_promotion": i['look_promotion'] + f"{messp.message_id},"
                    })
                else:
                    await putsubuser({
                        "user_id": i['user_id'],
                        "look_promotion": f"{messp.message_id},"
                    })
            except:
                ...
    if now.hour == 15 and now.minute == 0:

        allus = await getsubobj()
        for i in allus:

            try:
                # gu = await getuser(int(i['user_id']))

                if "SKIP" not in  [j1 for j1 in i["look_promotion"].split(",")]:

                    messp = await bot.send_message(int(i['user_id']),
                                                   "*Успейте забрать\\!* Сегодня с 10\\:00 до 20\\:00 при оплате любого профиля Вы получаете бонусные дни совершенно бесплатно\\!",
                                                   reply_markup=kbds.createkb(
                                                       {"Посмотреть": "look_promotion", "Отклонить": "menu"}),parse_mode="MarkdownV2")
                    if i['look_promotion']:
                        await putsubuser({
                            "user_id": i['user_id'],
                            "look_promotion": i['look_promotion'] + f"{messp.message_id},"
                        })
                    else:
                        await putsubuser({
                            "user_id": i['user_id'],
                            "look_promotion": f"{messp.message_id},"
                        })

                    gu = await getuser(int(i['user_id']))
                    if gu.get("look_promotion"):

                        l = [i for i in gu["look_promotion"].split(",") if i]

                        if l and len(l) > 1:
                            newl = l[:-1]
                            for j in newl:
                                try:
                                    await bot.delete_message(chat_id=int(i['user_id']), message_id=int(j))
                                except:
                                    ...
            except:
                ...
    if now.hour == 18 and now.minute == 0:
        allus = await getsubobj()
        for i in allus:
            try:
                # gu = await getuser(int(i['user_id']))

                if "SKIP" not in  [j1 for j1 in i["look_promotion"].split(",")]:
                    messp = await bot.send_message(int(i['user_id']),
                                                   "*Акция на исходе\\!* Сегодня с 10\\:00 до 20\\:00 при оплате любого профиля Вы получаете бонусные дни совершенно бесплатно\\!",
                                                   reply_markup=kbds.createkb(
                                                       {"Посмотреть": "look_promotion", "Отклонить": "menu"}),parse_mode="MarkdownV2")


                    if i['look_promotion']:
                        await putsubuser({
                            "user_id": i['user_id'],
                            "look_promotion": i['look_promotion'] + f"{messp.message_id},"
                        })
                    else:
                        await putsubuser({
                            "user_id": i['user_id'],
                            "look_promotion": f"{messp.message_id},"
                        })

                    gu = await getuser(int(i['user_id']))
                    if gu.get("look_promotion"):
                        l = [i for i in gu["look_promotion"].split(",") if i]

                        if l and len(l) > 1:
                            newl = l[:-1]
                            for j in newl:
                                try:
                                    await bot.delete_message(chat_id=int(i['user_id']), message_id=int(j))
                                except:
                                    ...
            except:
                ...
                    # finally:
                        # await bot.delete_message(chat_id=int(i['user_id']), message_id=int(j))
    if now.hour == 19 and now.minute == 59:
        job = scheduler.get_job("daily_task")
        promotion = False
        if job:
            job.remove()

        if async_task:
            task_time = None

            async_task = None
            # data = {
            #     "promotion": False
            # }
            # await put_promotion(data)
        allus = await getsubobj()
        try:
            for i in allus:
                # await bot.send_message(int(i['user_id']),
                #                                "🔥 Внезапная акция! Сегодня с 08:00 до 23:00 при оплате любого профиля Вы получаете бонусные дни совершенно бессплатно!",
                #                                reply_markup=kbds.createkb(
                #                                    {"Посмотреть": "look_promotion", "Пропустить": "skip_promotion"}))

                gu = await getuser(int(i['user_id']))
                if gu.get("look_promotion"):
                    l = [i for i in gu["look_promotion"].split(",") if i]

                    # if l and len(l) > 1:

                    for j in l:
                        try:
                            await bot.delete_message(chat_id=int(i['user_id']), message_id=int(j))
                        except:
                            ...

                await putsubuser({
                    "user_id": int(i['user_id']),
                    "look_promotion": None
                })

        except:
            ...
        # return


