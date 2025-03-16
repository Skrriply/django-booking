from django.urls import path

from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.index, name='index'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    path('location/<int:pk>/book', views.create_booking, name='create_booking'),
    path('activate/<uuid:code>/', views.activate_booking, name='activation'),
    path('like/<int:location_id>/', views.like_location, name='like_location'),
    path('dislike/<int:location_id>/', views.dislike_location, name='dislike_location'),
    path(
        'favourite/<int:location_id>/',
        views.favourite_location,
        name='favourite_location',
    ),
]
