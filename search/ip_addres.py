import requests
from decouple import config


"""Функция для добавления ip адреса от в список, разрешённых для пользователя,
    который расположен в Yandex Cloud"""


def get_ip(ip):
    url = 'https://console.yandex.cloud/gateway/root/searchApi/updateConsumer'
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://console.yandex.cloud",
        "Cookie": config('COOKIE'),
        "X-Csrf-Token": config('X_CSRF_TOKEN')
    }
    body = {'consumerId': config('CONSUMERID'),
            'ip': [ip],
            'searchType':"SEARCH_TYPE_RU",
            'updateMask':{'paths': ["ip", "search_type"]}
            }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        print("Успешный запрос")
        # Обработка ответа
        return response.json()
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)