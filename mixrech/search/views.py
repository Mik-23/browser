import base64
from django.shortcuts import render
from .services import search, image, video, search_by_image


def search_view(request):
    # Функция поиска в браузере
    search_query = request.GET.get('query', '')
    print('ПОИСКОВЫЙ ЗАПРОС', search_query)
    page = request.GET.get('page', 1)  # Текущая страница (по умолчанию 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    results = search(search_query, page)
    len_results = len(results)
    return render(request, 'search/result.html',
                      {'results': results, 'query': search_query, 'page': page_number, 'total_results': len_results})


def image_view(request):
    # Функция поиска фото
    search_query = request.GET.get('query', '')
    page = request.GET.get('page', 1)
    print('ПОИСКОВЫЙ ЗАПРОС КАРТИНКИ', search_query)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    images = image(request)
    return render(request, 'search/images.html',
                      {'images': images, 'query': search_query, 'page': page_number})


def video_view(request):
    # Функция поиска видео
    search_query = request.GET.get('query', '')
    page = request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    all_data = video(request)
    return render(request, 'search/videos.html',
                      {'results': all_data, 'query': search_query, 'page': page_number})


def search_by_image_view(request):
    img_file = request.FILES.get('image')
    print('ПОИСК ПО ИЗОБРАЖЕНИЮ: ', img_file)
    if img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        encoded_image = request.session.get('encoded_image')
    print(request.GET.get('section'))
    section = request.GET.get('section')
    page = request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    results = search_by_image(request, encoded_image)
    return render(request, 'search/result_image_search.html',
                      {'results': results, 'query': img_file,
                        'page': page_number, 'encoded_image': encoded_image, 'section': section})


def news_view(request):
    # Функция поиска в браузере
    query = request.GET.get('query', '')
    print('ПОИСКОВЫЙ ЗАПРОС', query)
    page = request.GET.get('page', 1)  # Текущая страница (по умолчанию 1)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    news_query = 'Новости' + query
    results = search(news_query, page)
    len_results = len(results)
    return render(request, 'search/result.html',
                      {'results': results, 'query': query, 'page': page_number, 'total_results': len_results})
