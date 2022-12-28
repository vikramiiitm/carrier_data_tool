from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, request, HttpResponseRedirect
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from .exceptions import *
from carrier_data_tool.utils import set_username
from . import forms
from . import models
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserTokenObtainPairSerializer
from rest_framework.response import Response


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny,]
    authentication_classes = []
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'status code': status_code,
            'message': str(user.username) + ' registered successfully',
        }
        return Response(response, status=status_code)

class UserObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenObtainPairSerializer
    # throttle_classes = (LoginRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserTokenVerifyView(TokenVerifyView):
    permission_classes = (AllowAny,)
    serializer_class = TokenVerifySerializer