from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model

from .forms import LoginForm
# Create your views here.


def login_view(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'accounts/login_page.html', {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('booking:index')

        messages.error(request, 'Something went wrong...')
        return render(request, 'accounts/login_page.html', {"form": form})