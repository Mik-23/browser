import os
from dotenv import load_dotenv
import base64
import time
import logging
import requests
from django.http import HttpResponse
from bs4 import BeautifulSoup


load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def search(search_query, page):
    # Функция поиска в браузере
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')  # Замените на ваш API-ключ
    print('ПОИСКОВЫЙ ЗАПРОС', search_query)
    print('Страница номер: ', page)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    results = []
    url = 'https://searchapi.api.cloud.yandex.net/v2/web/search'

    headers = {"Authorization": f"Api-Key {api_key}"}

    body = {
        "query": {
          "searchType": "SEARCH_TYPE_COM",
          "queryText": search_query,
          "familyMode": "FAMILY_MODE_NONE",
          "page": page_number,
          "fixTypoMode": "FIX_TYPO_MODE_ON"
        },
        "folderId": folderid,
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "responseFormat": "FORMAT_HTML",
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        start_time = time.time()
        encode_response = response.json()["rawData"]
        # декодируем из base64
        decoded_bytes = base64.b64decode(encode_response)
        # преобразуем байты в строку (UTF-8)
        text_html = decoded_bytes.decode('utf-8')
        soup = BeautifulSoup(text_html)  # Парсим HTML-код
        logging.info("Время запроса: %.2f секунд", time.time() - start_time)
        # Извлечение всех ссылок и заголовков
        links = [item.get('href') for item in soup.find_all('a')]
        titles = [item.text for item in soup.find_all('a')]
        # Заводим переменные счётчик и элемент
        count = 1
        favicon_count = 0
        favicon_url = ''
        for index, (link, title) in enumerate(zip(links, titles)):
            """Если элемент отличается от ссылки из списка, то увеличиваем счётчик 
            и присваиваем элементу значение ссылки из списка. В противном случае оставляем счётчик равным 1"""
            if index % 2 == 0:
                count += 1
            else:
                count = 1

            """Проверяем, что ссылку и текст можно извлечь, 
            а также извлекаем ссылки без доменов yandex.ru, ya.ru, google.ru, bing.com,
            без символов /video/preview, video/search, # и текст без символов
            Коммерческие предложения, дальше и, если текст содержит только цифры.
            Нужно это для корректного отображения ссылок в браузере"""

            if (link and title and 'yandex.ru' not in link and 'ya.ru' not in link
                and link[0] != '#' and '/video/preview' not in link and 'google.ru' not in link
                and 'bing.com' not in link and title != 'Коммерческие предложения' and not title.isdigit()
                and title != 'дальше' and 'video/search' not in link and count == 1
                and '/search' not in link):
                # Находим фавиконы
                for elem in link:
                    # Извлекаем основной адрес ссылки
                    if '/' in elem:
                        favicon_count += 1
                    favicon_url += elem

                    if favicon_count == 3:
                        break
                favicon_url = favicon_url + 'favicon.ico'
                results.append({'title': title, 'url': link, 'favicon_url': favicon_url})
                favicon_url = ''
                favicon_count = 0
        print(len(results))
        len_results = len(results)
        print(results)
        return results
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponse("Error occurred", status=response.status_code)


def image(service_request):
    # Функция поиска фото
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')  # Замените на ваш API-ключ
    search_query = service_request.GET.get('query', '')
    page = service_request.GET.get('page', 1)
    print('ПОИСКОВЫЙ ЗАПРОС КАРТИНКИ', search_query)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    images = []
    url = 'https://searchapi.api.cloud.yandex.net/v2/image/search'

    headers = {"Authorization": f"Api-Key {api_key}"}

    body = {
        "query": {
            "searchType": "SEARCH_TYPE_COM",
            "queryText": search_query,
            "familyMode": "FAMILY_MODE_NONE",
            "page": page_number,
            "fixTypoMode": "FIX_TYPO_MODE_ON"
        },
        "folderId": folderid,
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        encode_response = response.json()["rawData"]
        # декодируем из base64
        decoded_bytes = base64.b64decode(encode_response)
        # преобразуем байты в строку (UTF-8)
        text_xml = decoded_bytes.decode('utf-8')
        soup = BeautifulSoup(text_xml, 'lxml')  # Парсим HTML-код
        # Извлечение всех изображений
        for item in soup.find_all('doc'):
            img_url = item.find('image-link').text if item.find('image-link') else None
            link_url = item.find('html-link').text if item.find('html-link') else None
            # Проверяем, что ссылку на картинку и сайт с картинкой можно извлечь
            if img_url and link_url:
                images.append({'url': img_url, 'link': link_url})
                # print(f"Image URL: {img_url}")
        # print(images)

        return images
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponse("Error occurred", status=response.status_code)


def video(service_request):
    # Функция поиска видео
    api_key = os.getenv('OTHER_API_KEY')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')
    search_query = service_request.GET.get('query', '')
    page = service_request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    url = f'https://customsearch.googleapis.com/customsearch/v1/?q=видео {search_query}&page={page_number}&cx={search_engine_id}&key={api_key}'
    headers = {"Authorization": f"Api-Key {api_key}"}
    response = requests.get(url, headers=headers)
    print(page)
    if response.status_code == 200:
        all_data = []
        items = response.json()["items"]
        for item in items:
            try:
                thumbnail = item["pagemap"]["cse_thumbnail"][0]["src"]
            except KeyError:
                thumbnail = None
            all_data.append({'url': item["link"], 'title':item["title"], 'thumbnail': thumbnail})

        return all_data

    else:
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponse("Error occurred", status=response.status_code)


def search_by_image(service_request, encoded_image):
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')  # Замените на ваш API-ключ
    print(service_request.GET.get('section'))
    section = service_request.GET.get('section')
    page = service_request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    results = []
    print(page)
    url = 'https://searchapi.api.cloud.yandex.net/v2/image/search_by_image'

    headers = {"Authorization": f"Api-Key {api_key}"}

    body = {
        "folderId": folderid,
        "data": encoded_image,
        "page": page_number
    }
    print(body)
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        images = response.json()["images"]
        for image in images:
            if section == None:
                results.append({'link': image['url'], 'title': image['pageTitle'], 'url': image['pageUrl']})
            elif section == 'Похожее':
                results.append({'link': image['url']})
            elif section == 'Сайты':
                results.append({'title': image['pageTitle'], 'url': image['pageUrl']})
        service_request.session['encoded_image'] = encoded_image
        return results
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponse("Error occurred", status=response.status_code)
