from django.shortcuts import render

def test_layout(request):
    return render(request, "base/base.html")

def home(request):
    return render(request, "home.html")

def contact(request):
    return render(request, "contact.html")