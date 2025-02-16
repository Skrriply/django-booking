import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0
    )
    amount = models.PositiveIntegerField()
    description = models.TextField()
    photo = models.URLField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'Place {self.name}, max amount: {self.amount}, description: {self.description}'

    def update_rating(self):
        reviews = self.reviews.all()
        total_rating = sum(review.rating for review in reviews)
        self.rating = total_rating / reviews.count() if reviews.exists() else 0.0
        self.save()

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['amount']


class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    location = models.ForeignKey(
        Location, related_name='bookings', on_delete=models.CASCADE
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    confirmed = models.BooleanField(default=False)  # type: ignore
    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self) -> str:
        return f'{self.user} booked {self.location} from {self.start_time} till {self.end_time}'

    def total_days(self) -> int:
        return (self.end_time - self.start_time).days  # type: ignore

    def total_price(self) -> float:
        return self.total_days * self.location.price_per_night  # type: ignore

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['start_time']


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    location = models.ForeignKey(
        Location, on_delete=models.DO_NOTHING, related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Review by {self.user.first_name} {self.user.last_name} for {self.location.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.location.update_rating()

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('user', 'location')
