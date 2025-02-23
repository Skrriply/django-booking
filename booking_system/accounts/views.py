from typing import Union
import random
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


def login_view(
    request: HttpRequest,
) -> Union[HttpResponse, Union[HttpResponseRedirect, HttpResponsePermanentRedirect]]:
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


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, 'You successfully loged out.')
    return redirect('booking:index')


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    bookings = user.bookings.all()  # Получаем все бронирования пользователя
    profile_image = random.choice(["https://znaj.ua/crops/73f946/360x0/1/0/2021/04/27/nFI7Mfj5D3syK7n0lz7AVAk2FFiLoGbTSHsHGSet.jpeg", 
                                  "https://img.freepik.com/premium-photo/man-without-face-impersonal-man-mannequin-anonymous-portrait-man-abstract-identity-illustration_91497-8366.jpg",
                                  "https://i1.sndcdn.com/artworks-fSYqOdPlOY4HvTOL-GjJEKw-t500x500.jpg",
                                  "https://media.slovoidilo.ua/media/publications/19/183871/183871-1_large.jpg",
                                  "https://static.wikia.nocookie.net/willcraft-animations/images/4/4f/Herobrine_111.png/revision/latest?cb=20170618083041",
                                  "https://w7.pngwing.com/pngs/340/946/png-transparent-avatar-user-computer-icons-software-developer-avatar-child-face-heroes-thumbnail.png",
                                  "https://mir-s3-cdn-cf.behance.net/project_modules/disp/ea7a3c32163929.567197ac70bda.png",
                                  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3xbitvBXWXb3Z86QjvGBcdvpBn5KFgrP8-g&s",
                                  "https://cs4.pikabu.ru/post_img/big/2015/05/03/3/1430621033_2071402264.jpg",
                                  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnsT8hJ0mRUsyIf9qaIhAFlJREWrh_1nrrqw&s"])
    return render(
        request, 'accounts/profile.html', {'user': user, 'bookings': bookings, "image": profile_image}
    )
