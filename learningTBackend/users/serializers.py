from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,Subscription



#in DRF serializers are responsible for :
# Converts raw request data (request.data) into Python objects.
# Validates the data (e.g., password length, email uniqueness).
# Knows how to create or update model instances.
class SignupSerializer(serializers.ModelSerializer): # Serializer that maps request data to User model
    password = serializers.CharField(write_only=True, min_length=8) # Password field: must be at least 8 chars, not returned in responses

    class Meta: # Meta class defines serializer configuration
        model = User # Serializer is based on the custom User model
        fields = ('email', 'password') # Only include email and password fields in this serializer


    def create(self, validated_data): # Defines how a new User instance is created when serializer.save() is called
        return User.objects.create_user( # Uses UserManager's create_user method (hashes password securely)
        email=validated_data['email'],
        password=validated_data['password']
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        data['user'] = user
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('plan', 'started_at', 'expires_at', 'is_active')