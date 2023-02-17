from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import UserRegistrationView, UserObtainTokenPairView, UserTokenVerifyView, CreateSubscription

urlpatterns = [
    path('token/', UserObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('token/verify', UserTokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('subscribe/', CreateSubscription.as_view(), name='create_subscription')
]