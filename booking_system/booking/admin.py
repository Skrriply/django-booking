from django.contrib import admin

from .models import Advertisement, Booking, Location, Review


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'amount',
        'description',
        'city',
        'country',
        'price_per_night',
    ]
    search_fields = ['name']
    ordering = ['amount']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'start_time', 'end_time', 'confirmed']
    list_filter = ['confirmed', 'location']
    search_fields = ['user__username', 'location__name']
    ordering = ['start_time']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'location__name']
    ordering = ['-created_at']

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')