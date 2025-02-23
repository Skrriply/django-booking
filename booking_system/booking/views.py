from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.core.mail import send_mail
from .forms import BookingForm, ReviewForm
from .models import Location, Booking, Review
from django.conf import settings
from django.db.models import Q


def send_activation_email(request, booking: Booking) -> None:
    subject = 'Підтвердження бронювання'
    base_url = f"{request.scheme}://{request.get_host()}"
    activation_link = f'{base_url}/activate/{booking.activation_code}/'
    
    message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px #ddd;">
                <h2 style="color: #333;">Підтвердження бронювання</h2>
                <p>Дякуємо за ваше бронювання! Для його підтвердження, будь ласка, натисніть кнопку нижче:</p>
                <p style="text-align: center;">
                    <a href="{activation_link}" style="display: inline-block; padding: 10px 20px; background-color: #28a745; color: #ffffff; text-decoration: none; font-size: 16px; border-radius: 5px;">Підтвердити бронювання</a>
                </p>
                <hr style="border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #777;">Якщо ви не здійснювали це бронювання, просто проігноруйте цей лист.</p>
            </div>
        </body>
    </html>
    """
    recipient_list = [booking.user.email]

    send_mail(subject, "", settings.EMAIL_HOST_USER, recipient_list, html_message=message)
#def find_mistake_in_booking(obj) -> bool:



def index(request: HttpRequest) -> HttpResponse:
    locations = Location.objects.all()
    sort_by = request.GET.get('sort_by', 'name')
    query = request.GET.get('q', '')

    if query:
        locations = locations.filter(name__icontains=query)

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
        context={
            'locations': locations,
            'sort_by': sort_by,
            'booked_location_ids': booked_location_ids,
            'query': query,
        },
    )


def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    reviews = location.reviews.all()
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            user=request.user, location=location
        ).first()

    if request.method == 'POST' and not user_review:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.location = location
            review.save()
            return redirect('booking:location_detail', pk=pk)
    else:
        review_form = ReviewForm()

    return render(
        request,
        'location_detail.html',
        context={
            'location': location,
            'reviews': reviews,
            'review_form': review_form,
            'user_review': user_review,
        },
    )


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


            overlapping_bookings = Booking.objects.filter(
                location=location,
                confirmed=True
            ).filter(
                Q(start_time__lt=booking.end_time, end_time__gt=booking.start_time)
            )
            if overlapping_bookings.exists():
                return render(request, 'booking_form.html', {'form': form, 'location': location})

            send_activation_email(request, booking)
            booking.save()
            return redirect('booking:index')
    else:
        form = BookingForm(initial={'start_time': now()})

    return render(request, 'booking_form.html', {'form': form, 'location': location})


def activate_post(request: HttpRequest, code: int) -> HttpResponse:
    booking = get_object_or_404(Booking, activation_code=code)
    booking.confirmed = True
    booking.save()

    return HttpResponse('Бронювання успішно підтверджено!')
