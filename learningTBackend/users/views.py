from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from users.services import activate_subscription
from users.serializers import SubscriptionSerializer
from .serializers import SignupSerializer, LoginSerializer
from paypalcheckoutsdk.subscriptions import SubscriptionsCreateRequest
from .paypal import paypal_client
# Create your views here.

# jwt token Flow in Practice
# Signup/Login → Server calls get_tokens_for_user(user) → returns {refresh, access}.
# Client stores tokens (usually in memory or secure storage).
# Client makes requests → sends Authorization: Bearer <access_token>.
# Access token expires → Client calls refresh endpoint with refresh token.
# Server issues new access token → Client continues without re-login.
# If the client sends an expired access token, DRF + SimpleJWT will reject it as long as you installed it and have the line  permission_classes = [IsAuthenticated] in your view.
# The response will be 401 Unauthorized with a message like "Token is invalid or expired".
# The client must then use the refresh token to get a new access token.
# So expiration is not checked manually in your view — it’s handled by the authentication middleware before your view runs.
# only what you need to do client must take care of requesting new tokens when recieves 401 unauthorized which happens by two options:
# 1- redirecting user to new login and login view takes care of refreshing token already 
# 2- client code when recieves 401 unauthorized should request api/token/refresh/(the url exists in project urls and points to DRF built in method for refresh token and it returns response ) and store the new token then send it again with new request all this should happen without user feels to provide smooth experience
# and if you have a question how the cient should distinguesh between 401 unauthorized returned from access token expiration or from the user is loggedout already
# the answer is client should check before sending request if there is access token stored or not because if it is not stored that user isnt logged in or he logged out(dont forget that client code always should delete access token when user logout )
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
    'refresh': str(refresh), # Long-lived token (used to get new access tokens) user should store to request access token with it, for more informations go importantly to project urls and read comments
    'access': str(refresh.access_token), # Short-lived token (used to authenticate requests) }
    }




class SignupView(APIView):
    # In Django REST Framework (DRF), every APIView (and its subclasses) can enforce permissions before executing the request handler (get, post, etc.).
    # permission_classes is a class attribute that tells DRF which permission rules to apply to this view.
    # Permissions are checked before the view’s logic runs. If the request doesn’t meet the permission requirements, DRF will return a 403 Forbidden response automatically.
    # AllowAny is a built-in DRF permission class.
    # It means: any user can access this view, whether authenticated or not.
    # Other Permission Examples:
    # IsAuthenticated → Only logged-in users can access.
    # IsAdminUser → Only admin users can access.
    # IsAuthenticatedOrReadOnly → Authenticated users can write, unauthenticated users can only read.
    permission_classes = [AllowAny]

    # in DRF Views are responsible for :
    # Handles the HTTP request/response cycle.
    # Decides what should happen when a request comes in.
    # Delegates actual data handling to serializers and models.
    # so Whenever you build an endpoint in DRF:
    # View: Receives request → instantiates serializer → validates → saves → returns response.
    # Serializer: Defines fields → validates → creates/updates model instance.
    # Model: Defines schema + business rules → persists data.
    def post(self, request):
        # now delegates data to serializer
        #note that serializer is not a method you call, it is a class you calls the method inside 
        serializer = SignupSerializer(data=request.data) # Initialize serializer with incoming request data (JSON payload)
        serializer.is_valid(raise_exception=True) # Validate data; if invalid, raise a 400 error automatically
        user = serializer.save() # Call serializer's save() → triggers create() → saves user to database 


        tokens = get_tokens_for_user(user) # Generate authentication tokens for the newly created user
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

# when Frontend calls this → PayPal popup opens
# after transaction success or canceled paypal send the confirmation by callin paypal webhooks that exists on users/webhooks.py
class CreatePayPalSubscription(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        plan_id = request.data.get('paypal_plan_id') # PayPal dashboard plan ID


        request_paypal = SubscriptionsCreateRequest()
        request_paypal.prefer('return=representation')
        request_paypal.request_body({
        "plan_id": plan_id,
        "subscriber": {
        "email_address": request.user.email
        },
        "application_context": {
        "brand_name": "Your App",
        "user_action": "SUBSCRIBE_NOW",
        "return_url": "https://yourfrontend.com/success",
        "cancel_url": "https://yourfrontend.com/cancel"
        }
        })


        response = paypal_client().execute(request_paypal)
        return Response(response.result.__dict__)
    
class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        plan = request.data.get('plan')
        if plan not in ('standard', 'premium'):
            return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)


        subscription = activate_subscription(request.user, plan)
        return Response({
            'message': 'Subscription activated',
            'subscription': SubscriptionSerializer(subscription).data
        })