import random
from .models import Advertisement

def advertisement_processor(request):
    if request.user.is_staff:
        return {}
    
    ads = list(Advertisement.objects.filter(is_active=True))
    left_advertisement = None
    right_advertisement = None

    if ads:
        if len(ads) >= 2:
            left_advertisement, right_advertisement = random.sample(ads, 2)
        else:
            if random.choice([True, False]):
                left_advertisement = ads[0]
            else:
                right_advertisement = ads[0]

    return {
        'left_advertisement': left_advertisement,
        'right_advertisement': right_advertisement,
    }
