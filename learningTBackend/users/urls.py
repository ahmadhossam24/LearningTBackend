from django.urls import path
from . import views
from .webhooks import paypal_webhook

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('upgrade/', views.UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
    path('paypal/create/', views.CreatePayPalSubscription.as_view()),
    path('paypal/webhook/', paypal_webhook),
]