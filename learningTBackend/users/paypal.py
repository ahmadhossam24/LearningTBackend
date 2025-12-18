from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from django.conf import settings
# STEP  – PayPal Subscription Integration (Backend Only)


# This step wires PayPal **correctly** using webhooks. Frontend NEVER activates subscriptions directly.

def paypal_client():
    if settings.PAYPAL_MODE == 'live':
        env = LiveEnvironment(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET
        )
    else:
        env = SandboxEnvironment(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET
        )
    return PayPalHttpClient(env)
