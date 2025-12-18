from django.utils import timezone
from .models import Subscription
from .services import deactivate_subscription




def expire_subscriptions():
    now = timezone.now()
    expired = Subscription.objects.filter(is_active=True, expires_at__lt=now)


    for sub in expired:
        deactivate_subscription(sub.user)