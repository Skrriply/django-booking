from typing import Union

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm


def login_view(request: HttpRequest) -> Union[HttpResponse, Union[HttpResponseRedirect, HttpResponsePermanentRedirect]]:
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('booking:index')

        messages.error(request, 'Something went wrong...')
        return render(request, 'accounts/login_page.html', {'form': form})

    form = LoginForm()
    return render(request, 'accounts/login_page.html', {'form': form})

def register_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('booking:index')
        messages.warning(request, 'Sorry, but something went wrong...')

    form = RegisterForm()
    return render(request, 'accounts/register_page.html', {'form': form})

