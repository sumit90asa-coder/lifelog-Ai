from django.shortcuts import render, redirect


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'journal/login.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'journal/register.html')


def dashboard(request):
    return render(request, 'journal/dashboard.html')


def insights_page(request):
    return render(request, 'journal/insights.html')


def entries_page(request):
    return render(request, 'journal/entries_page.html')


def profile_page(request):
    return render(request, 'journal/profile.html')