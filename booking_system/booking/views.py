from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Location


def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()  # type: ignore
    return render(request, 'index.html', {'locations': locations})


def location_detail(request: HttpRequest, location_id: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'location_detail.html', {'location': location})


def info_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'info_page.html')
