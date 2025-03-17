import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now


class Location(models.Model):
    """Локація, яку можна забронювати."""

    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], default=0
    )
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    amount = models.PositiveIntegerField()
    description = models.TextField()
    photo = models.URLField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def update_rating(self) -> None:
        """Оновлює рейтинг локації на основі всіх відгуків."""
        reviews = self.reviews.all()
        total_rating = sum(review.rating for review in reviews)
        self.rating = total_rating / reviews.count() if reviews.exists() else 0.0
        self.save()

    def update_like_count(self) -> None:
        """Оновлює кількість лайків для локації."""
        self.like_count = Reaction.objects.filter(reaction_type='like').count()
        self.save()

    def update_dislike_count(self) -> None:
        """Оновлює кількість дизлайків для локації."""
        self.dislike_count = Reaction.objects.filter(reaction_type='dislike').count()
        self.save()

    def is_booked(self) -> bool:
        """
        Перевіряє, чи заброньована локація в даний момент.

        Returns:
            bool: True, якщо локація заброньована, інакше False.
        """
        return self.bookings.filter(
            start_time__lte=now(), end_time__gte=now(), confirmed=True
        ).exists()

    def __str__(self) -> str:
        """
        Магічний метод, який повертає рядок з назвою локації.

        Returns:
            str: Назва локації.
        """
        return self.name

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['amount']


class Booking(models.Model):
    """Бронювання локації."""

    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location, related_name='bookings', on_delete=models.CASCADE
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    confirmed = models.BooleanField(default=False)
    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def total_days(self) -> int:
        """
        Розраховує кількість днів між початком та кінцем бронювання.

        Returns:
            int: Кількість днів.
        """
        return (self.end_time - self.start_time).days

    def total_price(self) -> float:
        """
        Повертає загальну вартість бронювання.

        Returns:
            float: Вартість бронювання.
        """
        return self.total_days() * self.location.price_per_night

    def __str__(self) -> str:
        """
        Магічний метод, який повертає рядок з описом бронювання.

        Returns:
            str: Опис бронювання.
        """
        return f'{self.user} booked {self.location} from {self.start_time} till {self.end_time}'

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['start_time']


class Review(models.Model):
    """Відгук про локацію."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    location = models.ForeignKey(
        Location, on_delete=models.DO_NOTHING, related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs) -> None:
        """Зберігає відгук та оновлює рейтинг локації."""
        super().save(*args, **kwargs)
        self.location.update_rating()

    def __str__(self) -> str:
        """
        Магічний метод, який повертає рядок з описом відгуку.

        Returns:
            str: Опис відгуку.
        """
        return f'Відгук від {self.user} на {self.location}'

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('user', 'location')
        ordering = ['-created_at']


class Reaction(models.Model):
    """Реакція користувача на локацію (лайк та дизлайк)."""

    REACTION_OPTIONS = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='reactions'
    )
    reaction_type = models.CharField(max_length=7, choices=REACTION_OPTIONS)

    def __str__(self) -> str:
        return f'{self.user} поставив {self.reaction_type} на {self.location}'

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'
        unique_together = ('user', 'location', 'reaction_type')


class Favourite(models.Model):
    """Улюблене користувача."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='favourites'
    )

    def __str__(self) -> str:
        """
        Магічний метод, який повертає опис улюбленого.

        Returns:
            str: Опис улюбленого.
        """
        return f'{self.user} додав {self.location} до улюблених'

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Favourite'
        verbose_name_plural = 'Favorites'
        unique_together = ('user', 'location')


class Advertisement(models.Model):
    """Реклама."""

    title = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Магічний метод, який повертає назву реклами.

        Returns:
            str: Назва реклами.
        """
        return self.title

    class Meta:
        """Метаклас моделі, який визначає метадані моделі."""

        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
