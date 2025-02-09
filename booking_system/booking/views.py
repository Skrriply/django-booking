from .forms import LocationForm, BookingForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
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
            form.save()  # Save the new Location instance
            return redirect('booking:index')  # Redirect to location list after success
    else:
        form = LocationForm()

    return render(request, 'location_form.html', {'form': form})

def find_location(id):
    location = Location.objects.filter(id = id).first()
    return location
@login_required()
def create_booking(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, id=pk)
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.location = location
            booking.confirmed = False
            booking.save()
            return redirect('booking:index')  # Adjust this route to match your URLs
    else:
        form = BookingForm(initial={'start_time': now()})
    
    return render(request, 'booking_form.html', {'form': form, 'location': location})

# def info_page(request: HttpRequest) -> HttpResponse:
#     return render(request, 'info_page.html')
