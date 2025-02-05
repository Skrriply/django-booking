from django.contrib import admin
from django.urls import path

from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.index, name='index'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    #path('information/', views.info_page, name='hotel_info'),
]
