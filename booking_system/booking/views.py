from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Location


def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()  # type: ignore
    return render(request, 'index.html', context={'locations': locations})


def location_detail(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_detail.html', context={'location': location})



# def info_page(request: HttpRequest) -> HttpResponse:
#     return render(request, 'info_page.html')
