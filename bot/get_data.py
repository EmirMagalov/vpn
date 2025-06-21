import json
import os
from dotenv import load_dotenv
import aiohttp
from aiogram import Bot
load_dotenv()

local_url="127.0.0.1:8000"
docker_url="host.docker.internal:8000"
linux="172.17.0.1:8000"

url=os.getenv("API")
# url=linux

API_SUB_GET=f"http://{url}/api/sub/"
API_SUB_USER=f"http://{url}/api/sub/getusersub/?user_id="
API_SUB_ADD=f"http://{url}/api/sub/subpost/"
API_TIME_GET=f"http://{url}/api/time/"
API_DEVICE_GET=f"http://{url}/api/device/"
API_SUBDEV_POST=f'http://{url}/api/subdevice/'
API_SUBDEV_GET=f'http://{url}/api/subdevice/getsubdev/'
API_SUB_PUT=f"http://{url}/api/sub/subput/"
API_SUBDEV_DEL=f"http://{url}/api/subdevice/deletesubdev/"
API_PROMO_GET=f"http://{url}/api/promo/getpromocode/"
API_PROMO_PUT=f"http://{url}/api/promo/promocodeput/"
API_PROMO_ALL=f"http://{url}/api/promo/"
API_SUB_COMPANY=f"http://{url}/api/sub/getusercompany/"
API_SUB_PROMO=f"http://{url}/api/sub/getuserpromo/"
API_PROMO_POST=f"http://{url}/api/promo/postpromocode/"
API_SUB_NOTPROMO=f"http://{url}/api/sub/getusernotpromo/"
API_CELERY_START=f"http://{url}/start-task/"
API_CELERY_END=f"http://{url}/stop-task/"
API_PROMOTION_GET=f"http://{url}/api/promotion/getpromotion/"
API_PROMOTION_PUT=f"http://{url}/api/promotion/putpromotion/"
API_CELERY_mailing=f"http://{url}/start_mailing_task/"
login = os.getenv("login_vpn")
password = os.getenv("password_vpn")
host = os.getenv("host_vpn")


async def get_promotion():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_PROMOTION_GET) as response:
            if response.status == 200:
                return await response.json()
            else:
                print("error")
async def put_promotion(data):
    async with aiohttp.ClientSession() as session:
        async with session.put(API_PROMOTION_PUT,json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                print("error")
###################################################################################################################################################################################
async def client_add(user_id,unique_code):
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
        client_settings = {
            "clients": [
                {
                    "id": unique_code,
                    "flow": "xtls-rprx-vision",
                    "email": str(user_id),
                    "limitIp": 0,
                    "totalGB": 0,
                    "enable": True,
                    "subId": user_id,
                    "reset": 0,



                }
            ]
        }

        # Преобразуем структуру в строку JSON
        settings_str = json.dumps(client_settings)

        # Формируем данные запроса
        data1 = {
            "id": 5,
            "settings": settings_str
        }

        # Запрос на добавление клиента с cookies из авторизации
        async with session.post(f'{host}/panel/api/inbounds/addClient', headers=header, json=data1,
                                cookies=cookies) as response:
            if response.status == 200:
                result = await response.json()
                print("Client added successfully:", result)
                print(result)
            else:
                print(f"Failed to add client. Status code: {response.status}, Error: {await response.text()}")
                return None

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


# async def get_inbounds():
#     header = {"Accept": "application/json"}
#     data = {"username": login, "password": password}
#
#     # Создаем асинхронную сессию
#     async with aiohttp.ClientSession() as session:
#         # Отправка POST запроса на авторизацию
#         async with session.post(f"{host}/login", data=data) as login_response:
#             if login_response.status != 200:
#                 print(f"Login failed: {login_response.status}")
#                 return None
#             print("Login successful")
#
#             # Получаем cookies из ответа (сессия будет автоматически сохранена в cookies)
#             cookies = login_response.cookies
#         async with session.get(f'{host}/panel/api/inbounds/list',
#                                 headers=header,
#                                 cookies=cookies) as response:
#             if response.status == 200:
#                 result = await response.json()
#                 # print("Client del successfully:", result)
#                 return result
#             else:
#                 print(f"Failed to del client. Status code: {response.status}, Error: {await response.text()}")
#                 return None
# async def get_inbounds_id():
#     header = {"Accept": "application/json"}
#     data = {"username": login, "password": password}
#
#     # Создаем асинхронную сессию
#     async with aiohttp.ClientSession() as session:
#         # Отправка POST запроса на авторизацию
#         async with session.post(f"{host}/login", data=data) as login_response:
#             if login_response.status != 200:
#                 print(f"Login failed: {login_response.status}")
#                 return None
#             print("Login successful")
#
#             # Получаем cookies из ответа (сессия будет автоматически сохранена в cookies)
#             cookies = login_response.cookies
#         async with session.get(f'{host}/panel/api/inbounds/get/43773dfb-2a70-495b-a020-f27060c1a9f7',
#                                 headers=header,
#                                 cookies=cookies) as response:
#             if response.status == 200:
#                 result = await response.json()
#                 # print("Client del successfully:", result)
#                 return result
#             else:
#                 print(f"Failed to del client. Status code: {response.status}, Error: {await response.text()}")
#                 return None

########################################################################################################################################################################3


async def start_task(user_id):

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_CELERY_START}{user_id}/") as response:  # Используем POST-запрос
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"Error: {response.status}")
                return None

async def deact_task(user_id):
    async with aiohttp.ClientSession() as session:

        async with session.post(f"{API_CELERY_END}{user_id}/") as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"Error: {response.status}")
                return None


async def start_mailing_task(data):
    async with aiohttp.ClientSession() as session:

        async with session.post(API_CELERY_mailing,json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                print(f"Error: {response.status}")
                return None
# async def subdevget(user_id):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{API_SUBDEV_GET}{user_id}") as response:
#             if response.status == 200:
#                 result = await response.json()
#
#                 return result



            # else:
                # print("error here")


async def get_user_device(data):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_SUBDEV_GET,params=data) as response:
            if response.status == 200:
                result=await response.json()
                return result
            else:
                print("error")
async def getpromouser(data):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_SUB_PROMO}",params=data) as response:
            if response.status == 200:
                result = await response.json()

                return result
            else:
                print("error")

async def getnotpromouser(data):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_SUB_NOTPROMO}",params=data) as response:
            if response.status == 200:
                result = await response.json()

                return result
            else:
                print("error")

async def getallpromo(id=None):
    async with aiohttp.ClientSession() as session:
        if id:
            href=f"{API_PROMO_ALL}{id}/"
        else:
            href = f"{API_PROMO_ALL}"

        async with session.get(href) as response:
            if response.status == 200:
                result = await response.json()

                return result
            else:
                print("error")
async def putpromo(data):
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_PROMO_PUT}",json=data) as response:
            if response.status == 200:
                return await response.json()



            else:
                print("error")

async def get_promocode(data):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_PROMO_GET}",params=data) as response:
            if response.status == 200:
                result = await response.json()

                return result



            else:
                print("error")

async def del_user_dev(data):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_SUBDEV_DEL}",params=data) as response:
            if response.status == 200:

                return await response.json()
            else:
                error_message = await response.text()
                print(f"Error: {response.status}, {error_message}")
                return None

async def get_user_company(data):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_SUB_COMPANY}", params=data) as response:
            if response.status == 200:

                return await response.json()
            else:
                error_message = await response.text()
                print(f"Error: {response.status}, {error_message}")
                return None

async def putsubuser(data):
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_SUB_PUT}",json=data) as response:
            if response.status == 200:
                return await response.json()



            else:
                print("error")

async def getsubobj():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_SUB_GET}") as response:
            if response.status == 200:
                result = await response.json()


                return result



            else:
                print("error")

async def getuser(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_SUB_USER}{user_id}") as response:
            if response.status == 200:
                result = await response.json()


                return result



            else:
                print("error here")


async def getdevice():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_DEVICE_GET}") as response:
            if response.status == 200:
                result = await response.json()


                return result



            else:
                print("error")
async def get_one_device(params):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_DEVICE_GET}{params}") as response:
            if response.status == 200:
                result = await response.json()


                return result



            else:
                print("error")

async def gettime():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_TIME_GET}") as response:
            if response.status == 200:
                result = await response.json()


                return result



            else:
                print("error")

async def postuser(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_SUB_ADD, json=data) as response:
            if response.status == 201:

                return await response.json()
            else:
                error_message = await response.text()
                print(f"Error: {response.status}, {error_message}")
                return None
async def postpromo(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_PROMO_POST, json=data) as response:
            if response.status == 201:

                return await response.json()
            else:
                error_message = await response.text()
                print(f"Error: {response.status}, {error_message}")
                return None
async def subdevpost(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_SUBDEV_POST, json=data) as response:
            if response.status == 201:

                return await response.json()
            else:
                error_message = await response.text()
                print(f"Error: {response.status}, {error_message}")
                return None