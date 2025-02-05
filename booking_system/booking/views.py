from .forms import LocationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .models import Location


def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()  # type: ignore
    return render(request, 'index.html', context={'locations': locations})


def location_detail(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_detail.html', context={'location': location})


def create_location(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False) 
            location.user = request.user  
            location.save()  
            return redirect('booking:index')  
    else:
        form = LocationForm(request.GET)

    return render(request, 'location_form.html', {'form': form})

# def info_page(request: HttpRequest) -> HttpResponse:
#     return render(request, 'info_page.html')
