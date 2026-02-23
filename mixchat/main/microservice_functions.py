import requests
from bs4 import BeautifulSoup
from .mqtt_functions import connection, publish
from .mqtt_subscribe import subscribe, print_message


def mixrech(query):
    # Функция для взаимодействия с поисковой системой
    url = (f'https://mixrech.com/search/?query={query}')

    response = requests.get(url)
    if response.status_code == 200:
        print("Успешный запрос")
        text_html = response.text
        soup = BeautifulSoup(text_html, 'html.parser')  # Парсим HTML-код
        links = [item.a for item in soup.find_all('div', class_='result-url')]
        titles = [item.text.strip() for item in soup.find_all('div', class_='result-title')]
        hrefs = [item.get('href') for item in links]
        return dict(zip(titles, hrefs))
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)


def send_to_mqtt(msg):
    connection()
    publish(msg)


def get_mqtt():
    subscribe()
    return print_message()
