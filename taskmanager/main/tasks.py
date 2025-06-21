import asyncio
import os
from datetime import timedelta
from django.db import transaction
import aiohttp
import django
import pytz
from celery import current_app
from celery import shared_task
from .models import Subscription,SubscriptionDevice
from asgiref.sync import async_to_sync
from django.core.cache import cache
import logging
from aiogram import Bot
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardMarkup
from aiogram.exceptions import TelegramForbiddenError, TelegramNetworkError, TelegramAPIError
from datetime import timedelta
from django.utils import timezone
load_dotenv()
logger = logging.getLogger(__name__)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.taskmanager.settings')  # Замените 'myproject' на ваш проект
django.setup()


ckb = InlineKeyboardBuilder()
buttons = InlineKeyboardButton(text="Подписка", callback_data="sub")
buttons2=InlineKeyboardButton(text="Отклонить",callback_data="menu")
ckb.add(buttons)
ckb.add(buttons2)
ckb.adjust(1)

wont_5 = InlineKeyboardBuilder()
won_buttons = InlineKeyboardButton(text="ХОЧУ 5 ДНЕЙ", callback_data="wont_5")
wont_5.add(won_buttons)
wont_5.adjust(1)

login = os.getenv("login_vpn")
password = os.getenv("password_vpn")
host = os.getenv("host_vpn")
TOKEN = os.getenv("TOKEN")

def send(user_id, text):
    async def inner():
        bot = Bot(token=TOKEN)
        try:
            await bot.send_message(chat_id=user_id, text=text, reply_markup=ckb.as_markup())
        finally:
            await bot.session.close()
    asyncio.run(inner())
# @shared_task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
# def send_reminder_after_20_days(user_id):
#     try:
#         logger.info(f"Запуск задачи напоминания через 20 дней для user_id: {user_id}")
#         async def send_reminder_message():
#             bot = Bot(token=os.getenv("TOKEN"))
#             try:
#                 await bot.send_message(
#                     chat_id=user_id,
#                     text="Здравствуйте! Мы заметили что Вы очень долгое время не пользовались Kedo VPN, и чтобы поддержать коммуникабельность мы дарим Вам 5 бонусных дней совершенно бесплатно!",
#                     reply_markup=wont_5.as_markup()  # Можно настроить кнопки для возобновления
#                 )
#                 logger.info(f"Напоминание отправлено user_id {user_id}")
#             except Exception as e:
#                 logger.error(f"Ошибка отправки напоминания user_id {user_id}: {str(e)}")
#             finally:
#                 await bot.session.close()
#         async_to_sync(send_reminder_message)()
#     except Exception as e:
#         logger.error(f"Ошибка в задаче напоминания для user_id {user_id}: {str(e)}")
#         raise


async def client_del(unique_code):
    header = {"Accept": "application/json"}
    data = {"username": login, "password": password}

    # Создаем асинхронную сессию
    async with aiohttp.ClientSession() as session:
        # Отправка POST запроса на авторизацию
        async with session.post(f"{host}/login", data=data) as login_response:
            if login_response.status != 200:
                print(f"Login failed: {login_response.status}")
                return None
            print("Login successful")

            # Получаем cookies из ответа (сессия будет автоматически сохранена в cookies)
            cookies = login_response.cookies

        # Формирование данных клиента
        data1 = {
            "id": 5,  # Возможно, вам нужно изменить это значение в зависимости от API
            "clientId": unique_code  # Здесь передаем идентификатор клиента для удаления
        }

        # Запрос на добавление клиента с cookies из авторизации
        async with session.post(f'{host}/panel/api/inbounds/{data1["id"]}/delClient/{data1["clientId"]}', headers=header,
                                cookies=cookies) as response:
            if response.status == 200:
                result = await response.json()
                print("Client del successfully:", result)
                return result
            else:
                print(f"Failed to del client. Status code: {response.status}, Error: {await response.text()}")
                return None



@shared_task
def check_subscriptions() -> None:
    """Проверяет подписки и уведомляет пользователей об их истечении."""
    try:
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = timezone.now().astimezone(moscow_tz)

        # Оптимизированный запрос
        subs = Subscription.objects.filter(expires_at__isnull=False,task=True)

        notify_points = [
            (86400, "Обращаем внимание, через 24 часа заканчивается Ваша подписка!", "24h"),
            (43200, "Обращаем внимание, через 12 часов заканчивается Ваша подписка!", "12h"),
            (21600, "Обращаем внимание, через 6 часов заканчивается Ваша подписка!", "6h"),
            (10800, "Обращаем внимание, через 3 часа заканчивается Ваша подписка!", "3h"),
        ]

        for sub in subs:
            try:
                delta = sub.expires_at - now
                seconds = delta.total_seconds()

                # Уведомления
                for limit, msg, key in notify_points:
                    cache_key = f"notified_{key}_{sub.user_id}"
                    if limit - 900 < seconds <= limit and not cache.get(cache_key):
                        try:
                            send(sub.user_id, msg)
                            cache.set(cache_key, True, timeout=900)
                            logger.info(f"Уведомление отправлено для user_id {sub.user_id}: {msg}")
                        except TelegramForbiddenError:
                            logger.warning(f"Не удалось отправить уведомление для user_id {sub.user_id}: пользователь заблокировал бота")
                        except TelegramNetworkError:
                            logger.error(f"Ошибка сети при отправке уведомления для user_id {sub.user_id}")
                        except Exception as e:
                            logger.error(f"Неизвестная ошибка при отправке уведомления для user_id {sub.user_id}: {str(e)}")

                # Подписка истекла
                if sub.expires_at <= now and sub.task:
                    try:
                        sub.task = False
                        sub.pay = False
                        sub.save(update_fields=["task", "pay"])
                        try:
                            result = async_to_sync(client_del)(sub.unique_code)
                            logger.info(f"Ключ удален для user_id {sub.user_id}")
                        except Exception as e:
                            logger.error(f"Ошибка удаления ключа для user_id {sub.user_id}: {str(e)}")

                        try:
                            send(sub.user_id, "Ваша подписка истекла и ключ был удален. После оплаты обновите ключ.")
                            logger.info(f"Уведомление об истечении подписки отправлено для user_id {sub.user_id}")
                        except TelegramForbiddenError:
                            logger.warning(f"Не удалось отправить уведомление об истечении для user_id {sub.user_id}: пользователь заблокировал бота")
                        except TelegramNetworkError:
                            logger.error(f"Ошибка сети при отправке уведомления об истечении для user_id {sub.user_id}")
                        except Exception as e:
                            logger.error(f"Неизвестная ошибка при отправке уведомления об истечении для user_id {sub.user_id}: {str(e)}")

                        # Очистка кэша
                        for _, _, key in notify_points:
                            cache.delete(f"notified_{key}_{sub.user_id}")
                    except Exception as e:
                        logger.error(f"Ошибка обработки истекшей подписки для user_id {sub.user_id}: {str(e)}")

            except Exception as e:
                logger.error(f"Ошибка обработки подписки для user_id {sub.user_id}: {str(e)}")
                continue  # Продолжаем обработку следующей подписки

    except Exception as e:
        logger.error(f"Критическая ошибка выполнения check_subscriptions: {str(e)}")
        raise  # Перебрасываем критическую ошибку для повторного выполнения Celery

from celery.result import AsyncResult

@shared_task(acks_late=True)
def stop_task(user_id):
    task_id = cache.get(f"task_{user_id}")  # Получаем task_id из кэша
    if task_id:
        try:

            result = AsyncResult(task_id)
            print(f"Задача для user_id {user_id} имеет статус {result.state}.")

            if result.state in ['PENDING', 'STARTED']:

                current_app.control.revoke(task_id, terminate=True, signal='SIGTERM')  # Прерывание с использованием сигнала
                subscription = Subscription.objects.get(user_id=user_id)
                subscription.task = False
                subscription.save()
                logger.info(f"Задача для user_id {user_id} с task_id {task_id} отменена.")

                cache.delete(f"task_{user_id}")
                logger.info(f"task_id удален из кэша для user_id {user_id}")
            else:
                logger.warning(f"Задача для user_id {user_id} уже завершена. Статус: {result.state}")

                cache.delete(f"task_{user_id}")
                logger.info(f"task_id удален из кэша для user_id {user_id} (задача завершена).")
        except Exception as e:
            logger.error(f"Ошибка при остановке задачи для user_id {user_id}: {e}")

            cache.delete(f"task_{user_id}")
            logger.error(f"task_id удален из кэша для user_id {user_id} (ошибка).")
    else:
        logger.warning(f"Для user_id {user_id} активных задач не найдено.")






@shared_task
def mailing_list(mailing_data):
    asyncio.run(send_all_deletions(mailing_data))


async def send_all_deletions(mailing_data):
    bot = Bot(token=os.getenv("TOKEN"))
    semaphore = asyncio.Semaphore(10)  # Ограничим до 10 одновременных удалений

    async def delete_one(user_id, message_id):
        async with semaphore:
            try:
                print(f"Удаляю сообщение {message_id} у {user_id}")
                await bot.delete_message(chat_id=int(user_id), message_id=int(message_id))
                await asyncio.sleep(0.1)  # Пауза между удалениями одного пользователя
            except Exception as e:
                print(f"❌ Не удалось удалить сообщение {message_id} у {user_id}: {e}")

    try:
        tasks = []
        for data in mailing_data:
            for user_id, message_id in data.items():
                tasks.append(delete_one(user_id, message_id))

        await asyncio.gather(*tasks)
    finally:
        await bot.session.close()