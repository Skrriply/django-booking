from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.resolvers import Local
from django.utils.timezone import now

from .forms import BookingForm
from .models import Location, Booking



def send_activation_email(booking):
    subject = "Подтверждение публикации"
    message = f"Для подтверждения публикации перейдите по ссылке: http://127.0.0.1:8000/activate/{booking.activation_code}/"
    recipient_list = [booking.user.email]

    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()  # type: ignore
    sort_by = request.GET.get('sort_by', 'name')

    ordering_options = {
        'name': 'name',
        'price': 'price_per_night',
        'rating': '-rating',
    }

    if sort_by in ordering_options:
        locations = locations.order_by(ordering_options[sort_by])

    return render(
        request, 'index.html', context={'locations': locations, 'sort_by': sort_by}
    )


def location_detail(request: HttpRequest, pk: int) -> HttpResponse:
    location = get_object_or_404(Location, pk=pk)
    return render(request, 'location_detail.html', context={'location': location})


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
            send_activation_email(booking)
            booking.save()
            return redirect('booking:index')  # Adjust this route to match your URLs
    else:
        form = BookingForm(initial={'start_time': now()})

    return render(request, 'booking_form.html', {'form': form, 'location': location})

def activate_post(request, code):
    booking = get_object_or_404(Booking, activation_code=code)
    booking.confirmed = True
    booking.save()
    return HttpResponse("Пост успешно активирован!")
