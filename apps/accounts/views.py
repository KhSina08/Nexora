from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, "accounts/login.html")

def register_view(request):
    return render(request, "accounts/register.html")

@login_required
def dashboard(request):
    """صفحه حساب کاربری — فعلاً ساده؛ بعداً با قالب my-account وولمارت تکمیل میشود."""
    return render(request, "accounts/dashboard.html")
