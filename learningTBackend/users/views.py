from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer

# Create your views here.



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
    'refresh': str(refresh),
    'access': str(refresh.access_token),
    }




class SignupView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()


        tokens = get_tokens_for_user(user)
        return Response({
        'user': {
        'email': user.email,
        'trial_limit': user.trial_limit,
        'trials_used': user.trials_used,
        },
        'tokens': tokens
        }, status=status.HTTP_201_CREATED)




class LoginView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']


        tokens = get_tokens_for_user(user)
        return Response({
        'user': {
        'email': user.email,
        'is_standard': user.is_standard,
        'is_premium': user.is_premium,
        'is_gold': user.is_gold,
        'trial_limit': user.trial_limit,
        'trials_used': user.trials_used,
        },
        'tokens': tokens
        })
    
    #Frontend will send: Authorization: Bearer <access_token>
    # POST /api/users/signup/ should be {
    # "email": "teacher@test.com",
    # "password": "strongpassword123"
    # }
    #Response: is 
#     {
    #   "user": {
    #     "email": "teacher@test.com",
    #     "trial_limit": 5,
    #     "trials_used": 0
    #   },
    #   "tokens": {
    #     "access": "...",
    #     "refresh": "..."
    #   }
    # } 