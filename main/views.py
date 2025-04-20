from django.shortcuts import render


# Create your views here.
def site(request):
    return render(request, 'main/site.html', {'title': 'MixRech'})


def account(request):
    return render(request, 'main/account.html')
