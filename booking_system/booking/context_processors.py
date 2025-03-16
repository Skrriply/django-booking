import random
from typing import Dict

from django.http import HttpRequest

from .models import Advertisement


def advertisement_processor(request: HttpRequest) -> Dict[str, Advertisement]:
    """
    Повертає контекст з рекламою.

    Args:
        request (HttpRequest): Запит.

    Returns:
        Dict[str, Advertisement]: Контекст з рекламою.
    """
    if request.user.is_staff:
        return {}

    ads = list(Advertisement.objects.filter(is_active=True))
    left_advertisement = right_advertisement = None

    if len(ads) >= 2:
        left_advertisement, right_advertisement = random.sample(ads, 2)
    elif ads:
        left_advertisement = ads[0] if random.choice([True, False]) else None
        right_advertisement = ads[0] if left_advertisement is None else None

    return {
        'left_advertisement': left_advertisement,
        'right_advertisement': right_advertisement,
    }
