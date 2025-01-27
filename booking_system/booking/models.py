from django.contrib.auth.models import User
from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=50)
    amount = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f'Place {self.name}, max amount: {self.amount}, description: {self.description}'

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

    def __str__(self):
        return f'{self.user} booked {self.location} from {self.start_time} till {self.end_time}'

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['start_time']
