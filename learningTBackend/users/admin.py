from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User




@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User


    list_display = (
    'email',
    'is_active',
    'is_standard',
    'is_premium',
    'is_gold',
    'trials_used',
    'trial_limit',
    )


    list_filter = ('is_active', 'is_standard', 'is_premium', 'is_gold')
    search_fields = ('email',)
    ordering = ('-date_joined',)


    fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Access', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    ('Subscription', {'fields': ('is_standard', 'is_premium', 'is_gold', 'gold_expires_at')}),
    ('Trials', {'fields': ('trial_limit', 'trials_used')}),
    ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )


    add_fieldsets = (
    (None, {
    'classes': ('wide',),
    'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
    }),
    )


    filter_horizontal = ('groups', 'user_permissions')
