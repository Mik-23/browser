import requests
from bs4 import BeautifulSoup


def mixrech(query):
    # Отправить код подтверждения на номер телефона
    url = (f'https://mixrech.com/search/?query={query}')

    response = requests.get(url)
    if response.status_code == 200:
        print("Успешный запрос")
        text_html = response.text
        soup = BeautifulSoup(text_html, 'html.parser')  # Парсим HTML-код
        links = [item.a for item in soup.find_all('h3')]
        titles = [item.text.strip() for item in soup.find_all('h3')]
        hrefs = [item.get('href') for item in links]
        return dict(zip(titles, hrefs))
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

mixrech('вода')