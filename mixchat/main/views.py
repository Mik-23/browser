from django.shortcuts import render


# Create your views here.
def chat(request):
    return render(request, 'main/chat.html')


def auth_in_chat(request):
    return render(request, 'main/account.html')
