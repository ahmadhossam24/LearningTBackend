import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import User, Payment
from .services import activate_subscription,deactivate_subscription

# PayPal Webhook
# PayPal calls this when payment happens.
# PayPal sends webhook events for many situations, including:
# BILLING.SUBSCRIPTION.ACTIVATED → when a subscription is successfully created/approved.
# BILLING.SUBSCRIPTION.CANCELLED → when a user cancels their subscription.
# BILLING.SUBSCRIPTION.EXPIRED → when a subscription naturally expires.
# PAYMENT.SALE.COMPLETED → when a payment is successfully processed.
# PAYMENT.SALE.DENIED → when a payment fails.
# so You must register this view URL in PayPal’s dashboard (e.g., https://yourbackend.com/paypal/webhook/).
@csrf_exempt
def paypal_webhook(request):
    data = json.loads(request.body)
    event_type = data.get('event_type')
    resource = data.get('resource', {})


    if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
        email = resource['subscriber']['email_address']
        plan_id = resource['plan_id']
        subscription_id = resource['id']


        user = User.objects.get(email=email)


        plan = 'premium' if 'PREMIUM' in plan_id else 'standard'
        activate_subscription(user, plan)


        user.subscription.paypal_subscription_id = subscription_id
        user.subscription.save()


    if event_type == 'PAYMENT.SALE.COMPLETED':
        Payment.objects.create(
        user=user,
        amount=resource['amount']['total'],
        currency=resource['amount']['currency'],
        paypal_order_id=resource['id'],
        status='completed'
        )


    if event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
        deactivate_subscription(user)


    return JsonResponse({'status': 'ok'})