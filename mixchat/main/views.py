from datetime import datetime, timedelta
from .models import ChatUser
from django.shortcuts import render, redirect


# Create your views here.
def chat(request):
    return render(request, 'main/chat.html')


def auth_in_chat(request):
    users = ChatUser.objects.filter(is_active=False).all()
    if users:
        for user in users:
            update_date = datetime.now()
            date_joined = user.date_joined + timedelta(0, 10800)
            if update_date - date_joined.replace(tzinfo=None) >= timedelta(0, 3600):
                user.delete()
    return render(request, 'main/account.html')


def register_in_chat(request):
    return render(request, 'main/register_in_chat.html')


def successfully(request):
    return render(request, 'main/successfully.html')


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('chat')  # имя маршрута для views.chat
    else:
        return redirect('auth_in_chat')


def confirmation_code(request):
    return render(request, 'main/confirmation_code.html')
