import os
from dotenv import load_dotenv
import logging
import requests
import subprocess
from django.http import HttpResponse


load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def search(search_query, page):
    # Функция поиска в браузере
    url = f'https://{os.getenv('SEARCH_SERVER')}/search'
    body = {'q': search_query,
            'format': 'json',
            'pageno': page}
    response = requests.post(url, data=body)
    results = response.json()['results']
    list_results = []
    for res in results:
        list_results.append({'url': res['url'],
                             'title': res['title'],
                             'favicon_url': 'https://' + res['parsed_url'][1] + '/favicon.ico'})
    return list_results


def image(page, search_query):
    # Функция поиска фото
    url = f'https://{os.getenv('SEARCH_SERVER')}/search'
    body = {'q': search_query,
            'format': 'json',
            'categories': 'images',
            'pageno': page}
    response = requests.post(url, data=body)
    results = response.json()['results']
    list_results = []
    for res in results:
        list_results.append({'url': res['img_src'],
                             'link': res['url']})
    return list_results


def video(page, search_query):
    # Функция поиска видео
    url = f'https://{os.getenv('SEARCH_SERVER')}/search'
    body = {'q': search_query,
            'format': 'json',
            'categories': 'videos',
            'pageno': page}
    response = requests.post(url, data=body)
    results = response.json()['results']
    list_results = []
    for res in results:
        list_results.append({'url': res['url'],
                             'title': res['title'],
                             'thumbnail': res['thumbnail']})
    return list_results


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
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        images = response.json()["images"]
        for image in images:
            if section == None:
                try:
                    results.append({'link': image['url'], 'title': image['pageTitle'], 'url': image['pageUrl']})
                except KeyError:
                    continue
            elif section == 'Похожее':
                results.append({'link': image['url']})
            elif section == 'Сайты':
                try:
                    results.append({'title': image['pageTitle'], 'url': image['pageUrl']})
                except KeyError:
                    continue
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
    response = requests.post(url, headers=headers, data=ogg_data)

    try:
        return response.json()
    except Exception as e:
        print(f"Ошибка при разборе ответа: {e}")
        print(response.text)
        return None






