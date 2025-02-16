from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.resolvers import Local
from django.utils.timezone import now

from .forms import BookingForm
from .models import Location, Booking

from django.utils.timezone import now
from django.db.models import Q

from django.utils.timezone import now
from django.db.models import Q

def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()
    sort_by = request.GET.get('sort_by', 'name')

    ordering_options = {
        'name': 'name',
        'price': 'price_per_night',
        'rating': '-rating',
    }

    if sort_by in ordering_options:
        locations = locations.order_by(ordering_options[sort_by])

    # Знаходження локацій з активними бронюваннями
    booked_location_ids = Booking.objects.filter(
        Q(start_time__lte=now(), end_time__gte=now())
    ).values_list('location_id', flat=True)

    return render(
        request, 
        'index.html', 
        context={'locations': locations, 'sort_by': sort_by, 'booked_location_ids': booked_location_ids}
    )


def location_detail(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_detail.html', context={'location': location})


# def create_location(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         form = LocationForm(request.POST)
#         if form.is_valid():
#             form.save()  # Save the new Location instance
#             return redirect('booking:index')  # Redirect to location list after success
#     else:
#         form = LocationForm()

#     return render(request, 'location_form.html', {'form': form})


def find_location(id: int) -> Location:
    location = Location.objects.filter(id=id).first()  # type: ignore
    return location


@login_required()
def create_booking(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, id=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # type: ignore
            booking.location = location
            booking.confirmed = False
            booking.save()
            return redirect('booking:index')  # Adjust this route to match your URLs
    else:
        form = BookingForm(initial={'start_time': now()})

    return render(request, 'booking_form.html', {'form': form, 'location': location})