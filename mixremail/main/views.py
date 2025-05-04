from django.shortcuts import render


# Create your views here.
def mail(request):
    return render(request, 'main/mail.html')


def account(request):
    return render(request, 'main/account.html')
