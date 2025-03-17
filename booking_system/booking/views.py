from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import make_aware, now

from .forms import BookingForm, ReviewForm
from .models import Booking, Dislike, Favourite, Like, Location, Review


def index(request: HttpRequest) -> HttpResponse:
    """
    Відображає головну сторінку зі списком локацій.

    Args:
        request (HttpRequest): Запит.

    Returns:
        HttpResponse: Відповідь сервера зі списком локацій.
    """
    locations = Location.objects.all()

    # Параметри сортування та фільтрування
    sort_by = request.GET.get('sort_by', 'name')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Сортування
    ordering_options = {
        'name': 'name',
        'price': 'price_per_night',
        'rating': '-rating',
    }
    if sort_by in ordering_options:
        locations = locations.order_by(ordering_options[sort_by])

    # Фільтрування за пошуковим запитом
    if query:
        locations = locations.filter(name__icontains=query)

    # Фільтрування за датами
    if start_date and end_date:
        start_dt = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_dt = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        booked_location_ids = Booking.objects.filter(
            confirmed=True, start_time__lt=end_dt, end_time__gt=start_dt
        ).values_list('location_id', flat=True)
        locations = locations.exclude(id__in=booked_location_ids)

    # Улюблені локації
    favourites = (
        Location.objects.filter(favourites__user=request.user)
        if request.user.is_authenticated
        else None
    )

    booked_location_ids = Booking.objects.filter(
        start_time__lte=now(), end_time__gte=now()
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
            'end_date': end_date,
            'favourites': favourites,
        },
    )


def location_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Відображає деталі локації та список відгуків.

    Args:
        request (HttpRequest): Запит.
        pk (int): Ідентифікатор локації.

    Returns:
        HttpResponse: Відповідь сервера з деталями локації.
    """
    location = get_object_or_404(Location, pk=pk)
    reviews = location.reviews.all()
    user_review = (
        Review.objects.filter(user=request.user, location=location).first()
        if request.user.is_authenticated
        else None
    )

    # Улюблені локації
    favourites = (
        Location.objects.filter(favourites__user=request.user)
        if request.user.is_authenticated
        else None
    )

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
            'favourites': favourites,
        },
    )


def send_activation_email(request: HttpRequest, booking: Booking) -> None:
    subject = f'Підтведіть бронювання: {booking.location.name}'
    base_url = f'{request.scheme}://{request.get_host()}'
    activation_link = f'{base_url}/activate/{booking.activation_code}/'

    message = f"""
    <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; text-align: center;">
            <div style="max-width: 500px; margin: auto; background-color: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">Підтвердження бронювання</h2>
                <p style="color: #555; line-height: 1.5;">Вітаємо, {booking.user}, дякуємо за ваше бронювання <strong>{booking.location.name}</strong>!</p>
                <p style="color: #555; line-height: 1.5;">Для його підтвердження, будь ласка, натисніть кнопку нижче:</p>
                <p style="margin: 20px 0;">
                    <a href="{activation_link}" style="display: inline-block; padding: 12px 24px; background-color: #28a745; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 5px;">Підтвердити бронювання</a>
                </p>
                <p style="color: #555; line-height: 1.5;">Ваше бронювання з <strong>{booking.start_time.strftime('%d.%m.%Y')}</strong> по <strong>{booking.end_time.strftime('%d.%m.%Y')}</strong>.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #777; line-height: 1.5;">Якщо ви не здійснювали це бронювання - проігноруйте цей лист.</p>
            </div>
        </body>
    </html>
    """

    send_mail(
        subject,
        '',
        settings.EMAIL_HOST_USER,
        [booking.user.email],
        html_message=message,
    )


def activate_booking(request: HttpRequest, code: int) -> HttpResponse:
    """
    Активує бронювання за кодом активації.

    Args:
        request (HttpRequest): Запит.
        code (int): Код активації.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    booking = get_object_or_404(Booking, activation_code=code)
    booking.confirmed = True
    booking.save()

    return render(request, 'activation_page.html', {'booking': booking.id})


@login_required
def create_booking(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Створює бронювання для локації.

    Args:
        request (HttpRequest): Запит.
        pk (int): Ідентифікатор локації.

    Returns:
        HttpResponse: Відповідь сервера з формою бронювання.
    """
    location = get_object_or_404(Location, pk=pk)
    form = BookingForm(request.POST or None, initial={'start_time': now()})

    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.user = request.user
        booking.location = location
        booking.confirmed = False

        if Booking.objects.filter(
            location=location,
            confirmed=True,
            start_time__lt=booking.end_time,
            end_time__gt=booking.start_time,
        ).exists():
            form.add_error(
                None, 'Цей час уже зайнятий. Будь ласка, оберіть інший період.'
            )
        else:
            send_activation_email(request, booking)
            booking.save()
            return redirect('booking:index')

    return render(request, 'booking_form.html', {'form': form, 'location': location})


@login_required
def delete_review(request: HttpRequest, review_id: int) -> HttpResponse:
    """
    Видаляє відгук користувача.

    Args:
        request (HttpRequest): Запит.
        review_id (int): Ідентифікатор відгуку.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    review = get_object_or_404(Review, pk=review_id)

    if review.user == request.user or request.user.is_staff:
        location_id = review.location.id
        review.delete()
        review.location.update_rating()
        return redirect('booking:location_detail', pk=location_id)

    return HttpResponse(status=403)


# TODO: Виправити IntegrityError
@login_required
def like_location(request: HttpRequest, location_id: int) -> HttpResponse:
    """
    Обробляє лайк користувача для локації.

    Args:
        request (HttpRequest): Запит.
        location_id (int): Ідентифікатор локації.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    location = get_object_or_404(Location, pk=location_id)
    like, created = Like.objects.get_or_create(user=request.user, location=location)

    if created:
        Location.objects.filter(pk=location.id).update(like_count=F('like_count') + 1)
        if Dislike.objects.filter(user=request.user, location=location).exists():
            Dislike.objects.filter(user=request.user, location=location).delete()
            Location.objects.filter(pk=location.id).update(
                dislike_count=F('dislike_count') - 1
            )
    else:
        like.delete()
        Location.objects.filter(pk=location.id).update(like_count=F('like_count') - 1)

    return redirect('booking:location_detail', pk=location_id)


@login_required
def dislike_location(request: HttpRequest, location_id: int) -> HttpResponse:
    """
    Обробляє дизлайк користувача для локації.

    Args:
        request (HttpRequest): Запит.
        location_id (int): Ідентифікатор локації.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    location = get_object_or_404(Location, pk=location_id)
    dislike, created = Dislike.objects.get_or_create(
        user=request.user, location=location
    )

    if created:
        Location.objects.filter(pk=location.id).update(
            dislike_count=F('dislike_count') + 1
        )
        if Like.objects.filter(user=request.user, location=location).exists():
            Like.objects.filter(user=request.user, location=location).delete()
            Location.objects.filter(pk=location.id).update(
                like_count=F('like_count') - 1
            )
    else:
        dislike.delete()
        Location.objects.filter(pk=location.id).update(
            dislike_count=F('dislike_count') - 1
        )

    return redirect('booking:location_detail', pk=location_id)


@login_required
def favourite_location(request: HttpRequest, location_id: int) -> HttpResponse:
    """
    Обробляє додавання до улюблених локацій.

    Args:
        request (HttpRequest): Запит.
        location_id (int): Ідентифікатор локації.

    Returns:
        HttpResponse: Відповідь сервера.
    """
    location = get_object_or_404(Location, pk=location_id)
    favourite, created = Favourite.objects.get_or_create(
        user=request.user, location=location
    )

    if not created:
        favourite.delete()

    return redirect('booking:location_detail', pk=location_id)
