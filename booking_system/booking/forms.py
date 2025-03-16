from typing import Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from .models import Booking, Review


class BookingForm(forms.ModelForm):
    """Форма для бронювання локації."""

    start_time = forms.DateTimeField(
        required=True,
        initial=now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    end_time = forms.DateTimeField(
        required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def clean(self) -> Dict[str, Any]:
        """
        Перевіряє чи дата початку бронювання не пізніше дати закінчення.

        Returns:
            Dict[str, Any]: Очищені дані форми.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('Дата закінчення має бути пізніше дати початку.')

            if start_time < now():
                raise ValidationError('Дата початку не може бути в минулому.')

        return cleaned_data

    class Meta:
        """Метаклас форми, який визначає метадані форми."""

        model = Booking
        exclude = ['user', 'location', 'confirmed']


class ReviewForm(forms.ModelForm):
    """Форма для відгуку."""

    class Meta:
        """Метаклас форми, який визначає метадані форми."""

        model = Review
        fields = ['rating', 'comment']
