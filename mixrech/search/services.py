import os
from dotenv import load_dotenv
import base64
import time
import logging
import requests
import subprocess
from django.http import HttpResponse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def search(search_query, page):
    # Функция поиска в браузере
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')
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
        "responseFormat": "FORMAT_XML",
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        start_time = time.time()
        encode_response = response.json()["rawData"]
        # декодируем из base64
        decoded_bytes = base64.b64decode(encode_response)
        # преобразуем байты в строку (UTF-8)
        xml_data = decoded_bytes.decode('utf-8')
        # Парсим XML
        root = ET.fromstring(xml_data)

        # Ищем все документы
        for doc in root.findall('.//doc'):
            url_elem = doc.find('url')
            title_elem = doc.find('title')
            domain = doc.find('domain')
            print(f'https://{domain.text}/favicon.ico')
            header = ''.join([title for title in title_elem.itertext()])
            if 'Украин' in header or 'украин' in header:
                continue
            else:
                results.append({
                    'url': url_elem.text if url_elem is not None else '',
                    'title': header if header is not None else '',
                    'favicon_url': f'https://{domain.text}/favicon.ico'
                })
        return results
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponse("Error occurred", status=response.status_code)


def image(service_request, search_query):
    # Функция поиска фото
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')
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
    # Функция поиска по фото 
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')
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


def convert_webm_to_ogg(input_path: str, output_path: str):
     # Преобразование формата аудиофайла webm в ogg
    ffmpeg_path = '/usr/bin/ffmpeg'
    print('Вывести команду')
    command = [
        ffmpeg_path,
        '-y',
        '-i', input_path,
        '-c:a', 'libopus',
        output_path
    ]
    print('Начало конвертации')

    try:
        print('Попытка')
        subprocess.run(command, check=True)
        print(f"Конвертация завершена: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации: {e.stderr.decode()}")


def voice_search(file):
    # Голосовой поиск
    folderid = os.getenv('FOLDERID')
    api_key = os.getenv('API_KEY')
    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?topic=general&folderId={folderid}'
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "audio/ogg"
    }
    file.seek(0)
    data = file.read()
    input_webm = 'audio.webm'
    # Запись бинарных данных во входной файл
    with open(input_webm, 'wb') as f_out:
        f_out.write(data)
    convert_webm_to_ogg(input_webm, 'audio.ogg')
    print('Успешно')
    with open('audio.ogg', 'rb') as f:
        ogg_data = f.read()
    print(ogg_data)
    response = requests.post(url, headers=headers, data=ogg_data)

    try:
        print(response.json())
        return response.json()
    except Exception as e:
        print(f"Ошибка при разборе ответа: {e}")
        print(response.text)
        return None






