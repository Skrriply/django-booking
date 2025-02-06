from django import forms
from .models import Location, Booking
from django.utils.timezone import now



class LocationForm(forms.ModelForm):
    name = forms.CharField(max_length=30, min_length=3, required=True)
    country = forms.CharField(max_length=20, required=True)
    city = forms.CharField(max_length=20, required=True)
    region = forms.CharField(max_length=20, required=True)
    street = forms.CharField(max_length=30, required=True)
    rating = forms.DecimalField(max_digits=5, decimal_places=2,
                                 required=True)
    amount = forms.IntegerField(required=True)
    description = forms.CharField(max_length=100, required=True)
    photo = forms.URLField(required=True)
    price_per_night = forms.DecimalField(max_digits=10, 
                                         decimal_places=2)
    class Meta:
        model = Location
        fields = '__all__'

class BookingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        required=True,
        initial=now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Booking
        exclude = ['user', 'location', 'confirmed']
