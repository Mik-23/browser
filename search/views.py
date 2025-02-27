import time
import logging
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.shortcuts import render
from urllib.parse import quote
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from .ip_addres import get_ip
from decouple import config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_favicon(link):
    # Получаем фавикон
    try:
        response = requests.get(link, timeout=5)
        if response.status_code == 200:
            # Попробуйте извлечь фавикон из HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            icon = soup.find('link', rel='icon')
            if icon:
                # Если найден, возвращаем его URL
                return icon['href']
    except requests.exceptions.RequestException:
        return None  # Ошибка при запросе
    return None


def search_view(request):
    # Функция поиска в браузере
    folderid = config('FOLDERID')
    api_key = config('API_KEY')  # Замените на ваш API-ключ
    query = request.GET.get('query', '')
    print('ПОИСКОВЫЙ ЗАПРОС',query)
    encoded_query = quote(query.encode('utf-8'))
    page = request.GET.get('page', 1)  # Текущая страница (по умолчанию 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    offset = (page_number - 1) * 10
    keywords = ('porno', 'порно', 'порнография')
    results = []
    flag = True
    for keyword in keywords:
        url = f'https://yandex.ru/search/xml/html?folderid={folderid}&apikey={api_key}&query={keyword} {encoded_query}&offset={offset}'
        cache_key = f'search_results_{encoded_query}_{offset}'
        response = requests.get(url)
        #print(response.text)
        # Создаем список для хранения результатов
        if response.status_code == 200:
            # Если ip адреса нет в списке
            if 'Запрос пришёл с IP-адреса' in response.text and 'не входящего в список разрешённых для данного пользователя' in response.text:
                # Извлекаем ip адрес из XML ответа
                root = ET.fromstring(response.text)
                error_element = root.find('.//error')
                error_text = error_element.text
                ip = error_text.split('адреса ')[1].split(',')[0]
                # Добавляем ip адрес в Yandex Cloud
                get_ip(ip)
            start_time = time.time()
            soup = BeautifulSoup(response.text, 'html.parser')  # Парсим HTML-код
            logging.info("Время запроса: %.2f секунд", time.time() - start_time)
            # Извлечение всех ссылок и заголовков
            for item in tuple(soup.find_all('a')):  # Предположительно, ссылки представлены в теге <a>
                # print(item)
                link = item.get('href')  # Извлекаем URL из атрибута href
                # print('LINK', link)
                title = item.text  # Извлекаем текст ссылки
                favicon_url = get_favicon(link) # Получаем фавикон

                """Проверяем, что ссылку и текст можно извлечь, 
                а также извлекаем ссылки без доменов yandex.ru, ya.ru, google.ru, bing.com,
                без символов /video/preview, video/search, # и текст без символов
                Коммерческие предложения, дальше и, если текст содержит только цифры.
                Нужно это для корректного отображения ссылок в браузере"""

                if (link and title and 'yandex.ru' not in link and 'ya.ru' not in link
                    and link[0] != '#' and '/video/preview' not in link and 'google.ru' not in link
                    and 'bing.com' not in link and title != 'Коммерческие предложения'
                    and not title.isdigit() and title != 'дальше' and 'video/search' not in link):
                    results.append({'title': title, 'url': link, 'favicon': favicon_url})
            end_time = time.time()
            parsing_time = end_time - start_time
            logging.info("Время парсинга: %.2f секунд", parsing_time)
            cache.set(cache_key, results, timeout=60 * 5)
            # Разбиваем каждые 10 ответов по страницам
            len_results = len(results)
            start_index = (page_number - 1) * 10
            end_index = start_index + 10
            results = results[start_index:end_index]
            # Теперь вы можете вернуть список результатов

        else:
            flag = False
            print(f"Error: {response.status_code} - {response.text}")

    if not flag:
        return HttpResponse("Error occurred", status=response.status_code)
    else:
        return render(request, 'search/result.html',
                      {'results': results, 'query': query, 'page': page_number, 'total_results': len_results})


def image_view(request):
    folderid = config('FOLDERID')
    api_key = config('API_KEY')  # Замените на ваш API-ключ
    query = request.GET.get('query', '')
    page = request.GET.get('page', 1)
    print('ПОИСКОЫЙ ЗАПРОС КАРТИНКИ', query)
    encoded_query = quote(query.encode('utf-8'))
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1

    offset = (page_number - 1) * 10
    keywords = ('porno', 'порно', 'порнография')
    images = []
    flag = True
    for keyword in keywords:
        url = f'https://yandex.ru/images-xml/?folderid={folderid}&apikey={api_key}&text={keyword} {encoded_query}&offset={offset}&itype=all'
        headers = {
            "Content-Type": "application/xml",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')  # Парсим HTML-код
            # Извлечение всех изображений
            for item in soup.find_all('doc'):
                img_url = item.find('image-link').text if item.find('image-link') else None
                link_url = item.find('html-link').text if item.find('html-link') else None
                # Проверяем, что ссылку на картинку и сайт с картинкой можно извлечь
                if img_url and link_url:
                    images.append({'url': img_url, 'link': link_url})
                    print(f"Image URL: {img_url}")
            # print(images)
            # Теперь вы можете вернуть список изображений
        else:
            flag = False
            print(f"Error: {response.status_code} - {response.text}")

    if not flag:
        return HttpResponse("Error occurred", status=response.status_code)
    else:
        return render(request, 'search/images.html',
                      {'images': images, 'query': query, 'page': page_number})


def video_view(request):
    folderid = config('FOLDERID')
    api_key = config('API_KEY')  # Замените на ваш API-ключ
    query = request.GET.get('query', '')
    print('ПОИСКОЫЙ ЗАПРОС ВИДЕО', query)
    encoded_query = quote(query.encode('utf-8'))
    page = request.GET.get('page', 1)  # Текущая страница (по умолчанию 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1

    offset = (page_number - 1) * 10
    keywords = ('porno', 'порно', 'порнография')
    results = []
    flag = True
    for keyword in keywords:
        url = f'https://yandex.ru/search/xml/html?folderid={folderid}&apikey={api_key}&query=порно {encoded_query}&offset={offset}'
        time.sleep(3)
        response = requests.get(url)
        # print(response.text)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')  # Парсим HTML-код
            # Извлечение всех ссылок и заголовков
            for item in soup.find_all('a'):  # Предположительно, ссылки представлены в теге <a>
                link = item.get('href')  # Извлекаем URL из атрибута href
                # print('THUMBNAIL', thumbnail)
                video = ''
                print('LINK', link)

                """Проверяем, что ссылка не содержит доменов yandex.ru, и rutube.ru,
                извлекаем видео из ссылок http://noodlemagazine.com, http://semyana.cc,
                http://prostoporno.guru, https://www.xvideos-ru3.com, http://ukdevilz.com"""

                # Извлекаем текст ссылки
                title = item.text
                if ('yandex.ru' not in link and 'rutube.ru' not in link and ('video' in link or 'video' in title
                    or 'видео' in link or 'видео' in title
                    or 'http://noodlemagazine.com' in link or 'http://prostoporno.guru' in link
                    or 'http://ukdevilz.com' in link or 'http://semyana.cc' in link
                    or 'https://www.xvideos-ru3.com' in link or 'https://ebalka.ru' in link
                    or 'https://rusvideos.pro' in link)):
                    # Присваиваем переменной video ссылку
                    video = link

                print('VIDEO', video)
                print('TITLE', title)
                if video and title:  # Проверяем, что ссылку и текст можно извлечь
                    results.append({'title': title, 'url': video})
            images = []
            for img in soup.find_all('img'):
                thumbnail = img.get('src')
                images.append({'thumbnail': thumbnail})
            all_data = []
            if images == []:
                all_data = results
            else:
                for item, img in zip(results, images):
                    item.update(img)
                    all_data.append(item)
                print(all_data)
            print('RESULTS',results)
            # Теперь вы можете вернуть список результатов
        else:
            flag = False
            print(f"Error: {response.status_code} - {response.text}")

    if not flag:
        return HttpResponse("Error occurred", status=response.status_code)
    else:
        return render(request, 'search/videos.html', {'results': all_data, 'query': query, 'page': page_number})


def video_preview(request, id):
    # Пример: проверка параметров запроса
    age_verified = request.GET.get('age_verified', False)
    if not age_verified:
        return HttpResponseBadRequest("Доступ ограничен. Пожалуйста, подтвердите ваш возраст.")
