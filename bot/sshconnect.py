import datetime
import json
import uuid
import os
from aiogram import Router, Bot, types, F
from dotenv import load_dotenv
load_dotenv()
import requests
ssh_page=Router ()

login = os.getenv("login_vpn")
password = os.getenv("password_vpn")
host = os.getenv("host_vpn")

header = []
data = {"username": login, "password": password}
ses = requests.Session()





def addClient(user_id=1):
    # ses.post(f"{host}/login", data=data)
    header = {"Accept": "application/json"}
    client_settings = {
        "clients": [
            {
                "id": str(uuid.uuid1()),
                "flow": "xtls-rprx-vision",
                "email": str(user_id),
                "limitIp": 0,
                "totalGB": 0,
                # "expiryTime": x_time,
                "enable": True,
                # "tgId": str(tg_id),
                "subId": "psx0686mi0v1eprv",
                "reset": 0
            }
        ]
    }

    # Преобразование структуры в строку JSON
    settings_str = json.dumps(client_settings)

    # Формирование данных запроса
    data1 = {
        "id": 1,
        "settings": settings_str
    }
    resource = ses.post(f'http://188.225.81.134:44126/cmDcNH3kC98JcLM/panel/api/inbounds/addClient', headers=header, json=data1)
    print(resource)
    return resource
# addClient()
def list():
    ses.post(f"{host}/login", data=data)
    response = ses.get(f'http://188.225.81.134:44126/cmDcNH3kC98JcLM/panel/api/inbounds/list', json=data)
    print(response.json())

def delClient():
    ses.post(f"{host}/login", data=data)
    header = {"Accept": "application/json"}
    data1 = {
        "id": 3,  # Возможно, вам нужно изменить это значение в зависимости от API
        "clientId": "6ee2a4cb-ee94-4c8a-9b02-1c4382cf3cef"  # Здесь передаем идентификатор клиента для удаления
    }
    resource = ses.post(f'{host}/panel/api/inbounds/{data1["id"]}/delClient/{data1["clientId"]}', headers=header)
    print(resource)
    return resource
delClient()