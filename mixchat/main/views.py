from django.shortcuts import render, redirect


# Create your views here.
def chat(request):
    return render(request, 'main/chat.html')


def auth_in_chat(request):
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
