from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# in DRF models are responsible for:
# Defines the schema (fields, constraints).
# Encapsulates business rules (e.g., trial limits, premium access).
# Provides methods for persistence (create_user, save).
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    # account status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # trial system
    trial_limit = models.PositiveIntegerField(default=5)
    trials_used = models.PositiveIntegerField(default=0)

    # subscription flags
    is_standard = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_gold = models.BooleanField(default=False)  # admin granted premium

    # gold access control
    gold_expires_at = models.DateTimeField(null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def has_trials_left(self):
        return self.trials_used < self.trial_limit

    def use_trial(self):
        if self.has_trials_left():
            self.trials_used += 1
            self.save(update_fields=['trials_used'])

    def has_premium_access(self):
        if self.is_gold:
            if self.gold_expires_at:
                return timezone.now() <= self.gold_expires_at
            return True
        return self.is_premium

    def __str__(self):
        return self.email


class Subscription(models.Model):
    PLAN_CHOICES = (
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)

    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    # PayPal identifiers
    paypal_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')

    paypal_order_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency}"

