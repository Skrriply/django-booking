from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


def login_view(request: HttpRequest) -> HttpResponse:
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect('booking:index')
        messages.error(request, "Неправильне ім'я користувача або пароль.")

    return render(request, 'accounts/login_page.html', {'form': form})


def register_view(request: HttpRequest) -> HttpResponse:
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('booking:index')

    return render(request, 'accounts/register_page.html', {'form': form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, 'Ви успішно вийшли з облікового запису.')

    return redirect('booking:index')


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    bookings = user.bookings.all()

    return render(
        request, 'accounts/profile.html', {'user': user, 'bookings': bookings}
    )
