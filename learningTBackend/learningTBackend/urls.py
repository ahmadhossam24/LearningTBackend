"""
URL configuration for learningTBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView, )

urlpatterns = [
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # login 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # refresh and this should be called from client when 
    # user logged in but access token expired and client needs new one to send it with request: 
    # for more details go to comments above get_tokens_for_user view in users/views.py 
    # the request and response shape for this view is 
    # POST /api/token/refresh/ 
    # Content-Type: application/json 
    # { "refresh": "<refresh_token_here>" }
    # response :
    # { "access": "<new_access_token_here>" }
    # If the refresh token is expired or invalid, the server responds with 401 Unauthorized (or sometimes Token is invalid or expired).
    # At this point, the client cannot silently renew the session anymore.
    # The only option is to redirect the user back to login so they can re‑authenticate with their credentials and get a fresh pair of tokens.

]
