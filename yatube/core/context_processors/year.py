from django.utils import timezone


def year(request) -> dict:
    return {'year': timezone.now().year}
