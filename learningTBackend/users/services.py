from django.utils import timezone
from .models import Subscription, User

# STEP : Subscription activation & management (Standard / Premium)
# ===============================================================


# Goal:
# - Upgrade free users to standard or premium
# - Handle expiration
# - Single source of truth for subscription status


def activate_subscription(user: User, plan: str, duration_days: int = 30):
    """
    Activate or update a user's subscription.
    plan: 'standard' or 'premium'
    duration_days: default monthly subscription
    """


    expires_at = timezone.now() + timezone.timedelta(days=duration_days)


    subscription, created = Subscription.objects.get_or_create(
    user=user,
    defaults={
    'plan': plan,
    'started_at': timezone.now(),
    'expires_at': expires_at,
    'is_active': True,
    }
    )


    if not created:
        subscription.plan = plan
        subscription.started_at = timezone.now()
        subscription.expires_at = expires_at
        subscription.is_active = True
        subscription.save()


    # update user flags
    user.is_standard = plan == 'standard'
    user.is_premium = plan == 'premium'
    user.save(update_fields=['is_standard', 'is_premium'])


    return subscription




def deactivate_subscription(user: User):
    """
    Downgrade user to free plan
    """
    try:
        subscription = user.subscription
        subscription.is_active = False
        subscription.save(update_fields=['is_active'])
    except Subscription.DoesNotExist:
        pass


    user.is_standard = False
    user.is_premium = False
    user.save(update_fields=['is_standard', 'is_premium'])