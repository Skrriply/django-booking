from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from .models import Booking


class BookingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        required=True,
        initial=now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    end_time = forms.DateTimeField(
        required=True, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def clean(self) -> dict:
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
        model = Booking
        exclude = ['user', 'location', 'confirmed']
