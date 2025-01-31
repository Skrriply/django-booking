from django.shortcuts import get_object_or_404, render

from .models import Location


def index(request):
    locations = Location.objects.all()  # type: ignore
    return render(request, 'index.html', {'locations': locations})


def location_detail(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'location_detail.html', {'location': location})

def info_page(request):
    return render(request, "info_page.html")
