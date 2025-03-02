from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now, make_aware
from django.core.mail import send_mail
from datetime import datetime
from .forms import BookingForm, ReviewForm
from .models import Location, Booking, Review, Like, Dislike, Favourite
from django.conf import settings
from django.db.models import Q, F


def send_activation_email(request, booking: Booking) -> None:
    subject = 'Підтвердження бронювання'
    base_url = f"{request.scheme}://{request.get_host()}"
    activation_link = f'{base_url}/activate/{booking.activation_code}/'
    
    message = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Підтвердження бронювання</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; text-align: center;">
        <div style="max-width: 500px; margin: auto; background-color: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333; margin-bottom: 20px;">Підтвердження бронювання</h2>
            <p style="color: #555; line-height: 1.5;">Дякуємо за ваше бронювання в <strong>{booking.location.name}</strong>!</p>
            <p style="color: #555; line-height: 1.5;">Для його підтвердження, будь ласка, натисніть кнопку нижче:</p>
            <p style="margin: 20px 0;">
                <a href="{activation_link}" style="display: inline-block; padding: 12px 24px; background-color: #28a745; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 5px;">Підтвердити бронювання</a>
            </p>
            <p style="color: #555; line-height: 1.5;">Ваше бронювання з <strong>{booking.start_time.strftime('%d.%m.%Y')}</strong> по <strong>{booking.end_time.strftime('%d.%m.%Y')}</strong>.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="font-size: 12px; color: #777; line-height: 1.5;">Якщо ви не здійснювали це бронювання, просто проігноруйте цей лист.</p>
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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if query:
        locations = locations.filter(name__icontains=query)
    if start_date and end_date:
        start_dt = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        end_dt = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))

        # Вибираємо тільки ті локації, які НЕ мають підтверджених бронювань у цей період
        booked_location_ids = Booking.objects.filter(
            confirmed=True
        ).filter(
            Q(start_time__lt=end_dt, end_time__gt=start_dt)
        ).values_list('location_id', flat=True)

        locations = locations.exclude(id__in=booked_location_ids)

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
            'start_date': start_date,
            'end_date': end_date
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
                form.add_error(None, 'Цей час уже зайнятий. Будь ласка, оберіть інший період.')
                return render(request, 'booking_form.html', {'form': form, 'location': location})

            send_activation_email(request, booking)
            booking.save()
            return redirect('booking:index')
    else:
        form = BookingForm(initial={'start_time': now()})

    return render(request, 'booking_form.html', {'form': form, 'location': location})

def like_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    like, created = Like.objects.get_or_create(user=request.user, location=location)
    
    if created:
        Location.objects.filter(id=location.id).update(like_count=F('like_count') + 1)
        if Dislike.objects.filter(user=request.user, location=location).exists():
            Dislike.objects.filter(user=request.user, location=location).delete()
            Location.objects.filter(id=location.id).update(dislike_count=F('dislike_count') - 1)
    else:
        like.delete()
        Location.objects.filter(id=location.id).update(like_count=F('like_count') - 1)

    return redirect("booking:location_detail", pk=location_id)

def dislike_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    dislike, created = Dislike.objects.get_or_create(user=request.user, location=location)

    if created:
        Location.objects.filter(id=location.id).update(dislike_count=F('dislike_count') + 1)
        if Like.objects.filter(user=request.user, location=location).exists():
            Like.objects.filter(user=request.user, location=location).delete()
            Location.objects.filter(id=location.id).update(like_count=F('like_count') - 1)
    else:
        dislike.delete()
        Location.objects.filter(id=location.id).update(dislike_count=F('dislike_count') - 1)

    return redirect("booking:location_detail", pk=location_id)

def favourite_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    favourite, created = Favourite.objects.get_or_create(user=request.user, location=location)

    if created:
        location.favourite = "fa-solid fa-heart-circle-minus"
    else:
        favourite.delete()
        location.favourite = "fa-solid fa-heart-circle-plus"

    location.save()
    return redirect("booking:location_detail", pk=location_id)




def activate_post(request: HttpRequest, code: int) -> HttpResponse:
    booking = get_object_or_404(Booking, activation_code=code)
    booking.confirmed = True
    booking.save()

    return render(request, 'activation_page.html', {'booking': booking.id})
