from django.contrib import admin

from .models import Booking, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'description']
    search_fields = ['name']
    ordering = ['amount']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'start_time', 'end_time', 'confirmed']
    list_filter = ['confirmed', 'location']
    search_fields = ['user__username', 'location__name']
    ordering = ['start_time']
