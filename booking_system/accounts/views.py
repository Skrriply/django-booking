from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import CustomPasswordChangeForm, LoginForm, ProfileUpdateForm, RegisterForm


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Відображає сторінку входу в обліковий запис.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
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
    """
    Відображає сторінку реєстрації.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('booking:index')

    return render(request, 'accounts/register_page.html', {'form': form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Виходить з облікового запису користувача.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    logout(request)
    messages.success(request, 'Ви успішно вийшли з облікового запису.')

    return redirect('booking:index')


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Відображає сторінку профілю користувача.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    user = request.user
    bookings = user.bookings.all()

    return render(
        request, 'accounts/profile.html', {'user': user, 'bookings': bookings}
    )


@login_required
def profile_update_view(request: HttpRequest) -> HttpResponse:
    """
    Відображає сторінку редагування профілю користувача.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user)
        if profile_form.is_valid():
            password = profile_form.cleaned_data.get('password')
            if authenticate(username=user.username, password=password):
                profile_form.save()
                messages.success(request, 'Ваш профіль було успішно оновлено.')
                return redirect('accounts:profile_update')
            else:
                messages.error(request, 'Неправильний пароль.')
    else:
        profile_form = ProfileUpdateForm(instance=user)

    return render(
        request,
        'accounts/profile_update.html',
        {'profile_form': profile_form},
    )


@login_required
def password_change_view(request: HttpRequest) -> HttpResponse:
    """
    Відображає сторінку зміни пароля користувача.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    user = request.user
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль було успішно змінено.')
            return redirect('accounts:password_change')
    else:
        password_form = CustomPasswordChangeForm(user)

    return render(
        request,
        'accounts/password_change.html',
        {'password_form': password_form},
    )
