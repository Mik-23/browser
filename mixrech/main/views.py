import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


# Create your views here.
def site(request):
    return render(request, 'main/site.html')


def text_view(request):
    file_path = os.path.join(settings.BASE_DIR, 'main', 'robots.txt')
    print('dfgdgd',file_path)
    with open (file_path, 'r', encoding='utf-8') as f:
        return HttpResponse(f.read(), content_type='text/plain; charset=utf-8')
