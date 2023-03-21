import stripe
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, request, HttpResponseRedirect
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
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
from django.conf import settings
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserTokenObtainPairSerializer
from rest_framework.response import Response
# from djstripe.models import Customer, Plan, Product


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

        # Create Stripe Customer
        # customer = Customer.create(subscriber=user)
        # print(('customer: ', customer))

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


# class CreateSubscription(APIView):
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         user = data.get('user')
#         plan = data.get('plan')
#         user = CustomUser.objects.get(username=user)

#         customer = Customer.objects.filter(subscriber=user).last()
#         print('customer: ',customer)
#         # customer = Customer.get_or_create(subscriber='vkc@gmail.com')
#         stripe.api_key = 'sk_test_51KE6cuSBJuQTVpmljGzB82yTGKVeThVDItCIT2h8n6B5JDRR3SHmz3Lo8Imr2aWyhYe5d4ezGoQrZnDtr4UbkS7q00GPmhRvYp'
#         price = Product.objects.get(name=plan).prices.last().id #plan: Basic or Pro
#         print('price: ',price)
#         p = Plan.objects.last()
#         checkout_session = stripe.checkout.Session.create(
#             # payment_method_types=['card'],
#             customer=customer.id,
#             line_items = [{
#                 "price": price,
#                 "quantity":1
#             }],
#             mode='subscription',
#             success_url=f'http://127.0.0.1:3000/companies'
#         )
#         print((checkout_session))
#         return Response({'sessionId': checkout_session['id'],'checkout_url':checkout_session['url']})