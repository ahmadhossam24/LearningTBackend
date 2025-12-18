from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.permissions import CanGenerateTest
# Create your views here.

class GenerateTestView(APIView):
    permission_classes = [IsAuthenticated, CanGenerateTest]


    def post(self, request):
        user = request.user


        # ---- PLACE YOUR TEST GENERATION LOGIC HERE ----
        # generate HTML file, images, AI voice, etc.


        # Decrease trial ONLY for free users
        if not user.has_premium_access():
            user.use_trial()


        return Response({
        'message': 'Test generated successfully',
        'trials_used': user.trials_used,
        'trial_limit': user.trial_limit,
        'premium_access': user.has_premium_access(),
        }, status=status.HTTP_201_CREATED)
    

